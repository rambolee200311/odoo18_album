import base64
import io
import re
import threading
import time
import zipfile
import json

from PIL import Image
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class EvidenceAlbumPortal(http.Controller):
    """Portal entry points. Authorization is deliberately completed before attachment sudo."""

    _PAGE_SIZE = 12
    _ZIP_CONFIG = {
        "max_files": ("wd_evidence_album.zip.max_files", 50),
        "max_total_bytes": ("wd_evidence_album.zip.max_total_bytes", 100 * 1024 * 1024),
        "max_memory_bytes": ("wd_evidence_album.zip.max_memory_bytes", 128 * 1024 * 1024),
        "timeout_seconds": ("wd_evidence_album.zip.timeout_seconds", 60),
        "max_concurrency": ("wd_evidence_album.zip.max_concurrency", 2),
    }
    _zip_slots_lock = threading.Lock()
    _active_zip_downloads = 0

    def _portal_user(self):
        user = request.env.user
        if not user.has_group("base.group_portal"):
            raise NotFound()
        return user

    def _authorized_album(self, album_id):
        user = self._portal_user()
        album = request.env["wd.evidence.album"].browse(album_id).exists()
        if not album or album.state != "published" or album.customer_id.commercial_partner_id != user.partner_id.commercial_partner_id:
            raise NotFound()
        if album.is_expired():
            raise NotFound()
        return album

    def _authorized_item(self, item_id):
        item = request.env["wd.evidence.album.item"].browse(item_id).exists()
        if not item or not item.album_id:
            raise NotFound()
        self._authorized_album(item.album_id.id)
        if item.availability_state != "available" or not item.attachment_id.id:
            raise NotFound()
        return item

    @classmethod
    def _config_int(cls, key):
        parameter, default = cls._ZIP_CONFIG[key]
        parameters = request.env["ir.config_parameter"].sudo()
        value = parameters.get_param(parameter)
        if value is None:
            value = default
            parameters.set_param(parameter, default)
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid ZIP resource configuration: %s." % parameter)
        if value < 1:
            value = default
            parameters.set_param(parameter, default)
        return value

    @staticmethod
    def _safe_zip_name(filename, used_names):
        name = re.sub(r"[\x00-\x1f\x7f]", "_", filename or "media")
        name = name.replace("\\", "_").replace("/", "_")
        name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
        name = name or "media"
        stem, dot, suffix = name.rpartition(".")
        if not dot:
            stem, suffix = name, ""
        candidate = name
        counter = 2
        while candidate.casefold() in used_names:
            candidate = "%s_%s%s%s" % (stem, counter, "." if suffix else "", suffix)
            counter += 1
        used_names.add(candidate.casefold())
        return candidate

    def _batch_items(self, item_ids):
        if not isinstance(item_ids, list) or not item_ids:
            raise ValueError("Select at least one media item.")
        if any(isinstance(item_id, bool) or not isinstance(item_id, int) for item_id in item_ids):
            raise ValueError("The batch download request must contain Item IDs only.")
        if len(set(item_ids)) != len(item_ids):
            raise ValueError("The batch download request contains duplicate Item IDs.")
        items = request.env["wd.evidence.album.item"].browse(item_ids).exists()
        if len(items) != len(item_ids):
            raise NotFound()
        albums = items.mapped("album_id")
        pages = items.mapped("page_id")
        if len(albums) != 1 or len(pages) != 1:
            raise ValueError("Select media from one Page only.")
        self._authorized_album(albums.id)
        for item in items:
            if item.page_id != pages or item.availability_state != "available" or not item.attachment_id:
                raise NotFound()
        return items

    def _zip_payload(self, items):
        max_files = self._config_int("max_files")
        max_total_bytes = self._config_int("max_total_bytes")
        max_memory_bytes = self._config_int("max_memory_bytes")
        timeout_seconds = self._config_int("timeout_seconds")
        if len(items) > max_files:
            raise ValueError("The selected media exceeds the maximum file count.")
        started = time.monotonic()
        payloads = []
        total_bytes = 0
        for item in items:
            attachment = item.attachment_id.sudo()
            payload = base64.b64decode(attachment.datas or b"")
            total_bytes += len(payload)
            if total_bytes > max_total_bytes or total_bytes > max_memory_bytes:
                raise ValueError("The selected media exceeds the configured size limit.")
            if time.monotonic() - started > timeout_seconds:
                raise TimeoutError("The ZIP generation timed out.")
            payloads.append((attachment.name, payload))
        output = io.BytesIO()
        used_names = set()
        try:
            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for filename, payload in payloads:
                    if time.monotonic() - started > timeout_seconds:
                        raise TimeoutError("The ZIP generation timed out.")
                    archive.writestr(self._safe_zip_name(filename, used_names), payload)
            result = output.getvalue()
            if len(result) > max_memory_bytes:
                raise ValueError("The generated ZIP exceeds the configured memory limit.")
            return result
        finally:
            output.close()

    @classmethod
    def _acquire_zip_slot(cls, limit):
        with cls._zip_slots_lock:
            if cls._active_zip_downloads >= limit:
                return False
            cls._active_zip_downloads += 1
            return True

    @classmethod
    def _release_zip_slot(cls):
        with cls._zip_slots_lock:
            cls._active_zip_downloads = max(cls._active_zip_downloads - 1, 0)

    @http.route(
        ["/my/media-albums/batch-download", "/my/evidence-albums/batch-download"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def evidence_batch_download(self, **kwargs):
        self._portal_user()
        raw_item_ids = request.httprequest.form.get("item_ids")
        try:
            item_ids = json.loads(raw_item_ids or "null")
            items = self._batch_items(item_ids)
            if not self._acquire_zip_slot(self._config_int("max_concurrency")):
                raise ValueError("Too many ZIP downloads are running. Try again later.")
            try:
                payload = self._zip_payload(items)
            finally:
                self._release_zip_slot()
        except (ValueError, TimeoutError) as error:
            return request.make_response(
                json.dumps({"error": str(error)}),
                status=400,
                headers=[("Content-Type", "application/json")],
            )
        headers = [
            ("Content-Type", "application/zip"),
            ("Content-Disposition", 'attachment; filename="evidence-media.zip"'),
            ("Content-Length", str(len(payload))),
            ("Cache-Control", "no-store"),
        ]
        return request.make_response(payload, headers=headers)

    @http.route(["/my/media-albums", "/my/evidence-albums"], type="http", auth="user", website=True)
    def evidence_albums(self, page=1, search="", sort="published_desc", **kwargs):
        self._portal_user()
        try:
            page = max(int(page), 1)
        except (TypeError, ValueError):
            page = 1
        domain = [
            ("state", "=", "published"),
            ("customer_id", "=", request.env.user.partner_id.commercial_partner_id.id),
        ]
        search = (search or "").strip()
        if search:
            domain += [
                "|", "|",
                ("name", "ilike", search),
                ("description", "ilike", search),
                ("customer_id.name", "ilike", search),
            ]
        order = {
            "published_desc": "published_at desc, id desc",
            "published_asc": "published_at asc, id asc",
            "name_asc": "name asc, id asc",
            "name_desc": "name desc, id desc",
        }.get(sort, "published_at desc, id desc")
        visible = request.env["wd.evidence.album"].search(
            domain, order=order,
        ).filtered(lambda album: not album.is_expired())
        total = len(visible)
        offset = (page - 1) * self._PAGE_SIZE
        albums = visible[offset:offset + self._PAGE_SIZE]
        album_stats = {}
        for album in albums:
            items = album.page_ids.mapped("item_ids").filtered(
                lambda item: item.attachment_id.id and item.availability_state == "available"
            )
            album_stats[album.id] = {
                "pages": len(album.page_ids),
                "photos": len(items.filtered(lambda item: item.media_type == "image")),
                "videos": len(items.filtered(lambda item: item.media_type == "video")),
                "cover": {
                    "id": items[0].id,
                    "media_type": items[0].media_type,
                    "filename": items[0].attachment_id.sudo().name,
                } if items else None,
            }
        total_pages = (total + self._PAGE_SIZE - 1) // self._PAGE_SIZE
        return request.render(
            "wd_evidence_album.portal_album_list",
            {
                "albums": albums,
                "album_stats": album_stats,
                "page": page,
                "total_pages": total_pages,
                "search": search,
                "sort": sort if sort in {"published_desc", "published_asc", "name_asc", "name_desc"} else "published_desc",
                "page_name": "evidence_album",
                "has_previous": page > 1,
                "has_next": page < total_pages,
            },
        )

    @http.route(["/my/media-albums/<int:album_id>", "/my/evidence-albums/<int:album_id>"], type="http", auth="user", website=True)
    def evidence_album(self, album_id, **kwargs):
        album = self._authorized_album(album_id)
        pages = []
        total_photos = 0
        total_videos = 0
        for page in album.page_ids:
            items = page.item_ids.filtered(
                lambda item: item.attachment_id.id and item.availability_state == "available"
            )
            item_data = []
            for item in items:
                attachment = item.attachment_id.sudo()
                item_data.append({
                    "id": item.id,
                    "media_type": item.media_type,
                    "note": item.note,
                    "mimetype": attachment.mimetype,
                    "filename": attachment.name,
                })
            photo_count = sum(item["media_type"] == "image" for item in item_data)
            video_count = sum(item["media_type"] == "video" for item in item_data)
            total_photos += photo_count
            total_videos += video_count
            pages.append({
                "id": page.id,
                "index": len(pages),
                "title": page.title,
                "description": page.description,
                "items": item_data,
                "item_count": len(item_data),
                "photo_count": photo_count,
                "video_count": video_count,
            })
        return request.render(
            "wd_evidence_album.portal_album",
            {
                "album": album,
                "pages": pages,
                "total_photos": total_photos,
                "total_videos": total_videos,
                "page_name": "evidence_album",
            },
        )

    @http.route(
        ["/my/media-albums/items/<int:item_id>/media", "/my/evidence-albums/items/<int:item_id>/media"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "HEAD"],
    )
    def evidence_media(self, item_id, **kwargs):
        item = self._authorized_item(item_id)
        # Only after all portal, partner, state, expiry and availability checks.
        attachment = item.attachment_id.sudo()
        payload = base64.b64decode(attachment.datas or b"")
        return self._binary_response(payload, attachment.mimetype, attachment.name, download=False)

    @http.route(
        ["/my/media-albums/items/<int:item_id>/download", "/my/evidence-albums/items/<int:item_id>/download"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "HEAD"],
    )
    def evidence_download(self, item_id, **kwargs):
        item = self._authorized_item(item_id)
        attachment = item.attachment_id.sudo()
        payload = base64.b64decode(attachment.datas or b"")
        return self._binary_response(payload, attachment.mimetype, attachment.name, download=True)

    @http.route(
        ["/my/media-albums/items/<int:item_id>/media/thumb", "/my/evidence-albums/items/<int:item_id>/media/thumb"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "HEAD"],
    )
    def evidence_thumbnail(self, item_id, **kwargs):
        item = self._authorized_item(item_id)
        attachment = item.attachment_id.sudo()
        payload = base64.b64decode(attachment.datas or b"")
        if item.media_type == "image":
            try:
                with Image.open(io.BytesIO(payload)) as image:
                    image.thumbnail((480, 480))
                    output = io.BytesIO()
                    image.convert("RGB").save(output, format="JPEG", quality=75, optimize=True)
                    payload, mimetype = output.getvalue(), "image/jpeg"
            except (OSError, ValueError):
                raise NotFound()
        else:
            # Videos are intentionally not transcoded; the poster is a lightweight placeholder.
            payload, mimetype = b"", "image/svg+xml"
        response = request.make_response(payload, headers=[("Content-Type", mimetype), ("Cache-Control", "private, max-age=300")])
        if request.httprequest.method == "HEAD":
            response.response = []
        return response

    @staticmethod
    def _binary_response(payload, mimetype, filename, download=False):
        size = len(payload)
        headers = [("Content-Type", mimetype or "application/octet-stream"), ("Accept-Ranges", "bytes"), ("Content-Length", str(size))]
        if download:
            safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", filename or "media")
            headers.append(("Content-Disposition", 'attachment; filename="%s"' % safe_name))
        range_header = request.httprequest.headers.get("Range")
        status = 200
        body = payload
        if range_header:
            bounds = EvidenceAlbumPortal._range_bounds(range_header, size)
            if bounds is None:
                return request.make_response(b"", status=416, headers=[("Content-Range", "bytes */%s" % size)])
            start, end = bounds
            body, status = payload[start : end + 1], 206
            headers = [h for h in headers if h[0] != "Content-Length"]
            headers.extend([("Content-Range", "bytes %s-%s/%s" % (start, end, size)), ("Content-Length", str(len(body)))])
        response = request.make_response(body, status=status, headers=headers)
        if request.httprequest.method == "HEAD":
            response.response = []
        return response

    @staticmethod
    def _range_bounds(value, size):
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
        if not match or size == 0:
            return None
        start_text, end_text = match.groups()
        if start_text:
            start = int(start_text)
            end = int(end_text) if end_text else size - 1
        else:
            suffix = int(end_text or 0)
            if suffix == 0:
                return None
            start, end = max(size - suffix, 0), size - 1
        if start >= size or start > end:
            return None
        return start, min(end, size - 1)
