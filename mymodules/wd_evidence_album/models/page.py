from odoo import api, fields, models
from odoo.exceptions import UserError


class EvidenceAlbumPage(models.Model):
    _name = "wd.evidence.album.page"
    _description = "Evidence Album Page"
    _order = "sequence, id"
    _rec_name = "title"

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

    def _check_editable(self):
        self.ensure_one()
        self.album_id.check_access_rights("write")
        self.album_id.check_access_rule("write")

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Page",
            "res_model": "wd.evidence.album.page",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }

    def add_source_attachments(self, source_config, source_record_id, attachment_ids):
        self.ensure_one()
        self._check_editable()
        source_config = source_config.ensure_one()
        attachments, snapshot = source_config.resolve_record_attachments(source_record_id)
        selected = attachments & self.env["ir.attachment"].browse(attachment_ids)
        if set(selected.ids) != set(attachment_ids):
            raise UserError("Only attachments from the configured source field may be selected.")
        if not selected:
            raise UserError("Select at least one source attachment.")
        media = self.env["wd.evidence.album.media"]
        for attachment in selected:
            media.validate_attachment(attachment)
            if self.env["wd.evidence.album.item"].search_count(
                [("album_id", "=", self.album_id.id), ("attachment_id", "=", attachment.id)]
            ):
                raise UserError("An attachment can only appear once in an album.")
        return self.env["wd.evidence.album.item"].create([
            dict(
                snapshot,
                page_id=self.id,
                attachment_id=attachment.id,
                source_type="record",
                media_type=media.validate_attachment(attachment)[0],
                availability_state="available",
            )
            for attachment in selected
        ])

    def create_upload_item(self, attachment_vals):
        self.ensure_one()
        self._check_editable()
        attachment = self.env["ir.attachment"].create(dict(attachment_vals, res_model=False, res_id=False))
        try:
            media_type, _attachment = self.env["wd.evidence.album.media"].validate_attachment(attachment)
            return self.env["wd.evidence.album.item"].create({
                "page_id": self.id, "attachment_id": attachment.id,
                "source_type": "upload", "media_type": media_type,
                "availability_state": "available",
            })
        except Exception:
            attachment.unlink()
            raise

    def action_open_add_source_items(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Add Source Attachments",
            "res_model": "wd.evidence.album.source.items.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_page_id": self.id},
        }

    def action_open_upload(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Upload Media",
            "res_model": "wd.evidence.album.upload.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_page_id": self.id},
        }
