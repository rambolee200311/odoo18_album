import base64
import binascii
import struct

from odoo import api, models
from odoo.exceptions import UserError


class EvidenceAlbumMedia(models.AbstractModel):
    _name = "wd.evidence.album.media"
    _description = "Media Album media services"

    @api.model
    def validate_attachment(self, attachment):
        """Validate both the advertised media and its actual file signature."""
        attachment.ensure_one()
        if not attachment.exists() or not attachment.datas:
            raise UserError("The attachment is empty or unavailable.")
        name = (attachment.name or "").lower()
        mimetype = (attachment.mimetype or "").lower()
        extension_mimes = {
            ".jpg": ("image/jpeg", "image"),
            ".jpeg": ("image/jpeg", "image"),
            ".png": ("image/png", "image"),
            ".mp4": ("video/mp4", "video"),
        }
        extension = next(
            (suffix for suffix in extension_mimes if name.endswith(suffix)), None
        )
        if not extension or mimetype != extension_mimes[extension][0]:
            raise UserError("The attachment must have a matching JPG, PNG, or MP4 MIME type.")
        try:
            payload = base64.b64decode(attachment.datas, validate=True)
        except (binascii.Error, ValueError, TypeError) as error:
            raise UserError("The attachment content cannot be read.") from error
        if not payload:
            raise UserError("The attachment is empty or unavailable.")
        valid = False
        if extension in (".jpg", ".jpeg"):
            valid = payload[:2] == b"\xff\xd8" and payload[-2:] == b"\xff\xd9"
        elif extension == ".png":
            valid = payload.startswith(b"\x89PNG\r\n\x1a\n")
        else:
            valid = len(payload) >= 12 and payload[4:8] == b"ftyp"
            if valid:
                box_size = struct.unpack(">I", payload[:4])[0]
                valid = box_size == 0 or box_size >= 8
        if not valid:
            raise UserError("The attachment content does not match its media type.")
        return extension_mimes[extension][1], attachment
