from odoo import api, fields, models
from odoo.exceptions import UserError


class EvidenceAlbumPage(models.Model):
    _name = "wd.evidence.album.page"
    _description = "Evidence Album Page"
    _order = "sequence, id"

    album_id = fields.Many2one(
        "wd.evidence.album",
        required=True,
        ondelete="cascade",
        index=True,
    )
    title = fields.Char(required=True)
    description = fields.Text()
    sequence = fields.Integer(default=10, required=True, index=True)
    item_ids = fields.One2many(
        "wd.evidence.album.item",
        "page_id",
        string="Items",
        order="sequence, id",
        copy=True,
    )

    def write(self, vals):
        if "album_id" in vals:
            target_album_id = vals["album_id"]
            if any(record.album_id.id != target_album_id for record in self):
                raise UserError("A page cannot be moved to another album.")
        return super().write(vals)
