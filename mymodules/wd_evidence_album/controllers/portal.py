import base64
import io
import re

from PIL import Image
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class EvidenceAlbumPortal(http.Controller):
    """Portal entry points. Authorization is deliberately completed before attachment sudo."""

    _PAGE_SIZE = 12

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

    @http.route("/my/evidence-albums", type="http", auth="user", website=True)
    def evidence_albums(self, page=1, **kwargs):
        self._portal_user()
        try:
            page = max(int(page), 1)
        except (TypeError, ValueError):
            page = 1
        domain = [
            ("state", "=", "published"),
            ("customer_id", "=", request.env.user.partner_id.commercial_partner_id.id),
        ]
        visible = request.env["wd.evidence.album"].search(
            domain, order="published_at desc, id desc",
        ).filtered(lambda album: not album.is_expired())
        offset = (page - 1) * self._PAGE_SIZE
        albums = visible[offset:offset + self._PAGE_SIZE]
        has_next = len(visible) > offset + self._PAGE_SIZE
        return request.render(
            "wd_evidence_album.portal_album_list",
            {
                "albums": albums,
                "page": page,
                "page_name": "evidence_album",
                "has_previous": page > 1,
                "has_next": has_next,
            },
        )

    @http.route("/my/evidence-albums/<int:album_id>", type="http", auth="user", website=True)
    def evidence_album(self, album_id, **kwargs):
        album = self._authorized_album(album_id)
        pages = []
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
            pages.append({
                "id": page.id,
                "title": page.title,
                "description": page.description,
                "items": item_data,
            })
        return request.render(
            "wd_evidence_album.portal_album",
            {"album": album, "pages": pages, "page_name": "evidence_album"},
        )

    @http.route(
        "/my/evidence-albums/items/<int:item_id>/media",
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
        "/my/evidence-albums/items/<int:item_id>/download",
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
        "/my/evidence-albums/items/<int:item_id>/media/thumb",
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
