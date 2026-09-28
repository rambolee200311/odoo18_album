from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


class EvidenceAlbumItem(models.Model):
    _name = "wd.evidence.album.item"
    _description = "Evidence Album Item"
    _order = "sequence, id"

    page_id = fields.Many2one(
        "wd.evidence.album.page",
        required=True,
        ondelete="cascade",
        index=True,
    )
    album_id = fields.Many2one(
        "wd.evidence.album",
        related="page_id.album_id",
        store=True,
        readonly=True,
        index=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        ondelete="set null",
        index=True,
    )
    source_type = fields.Selection(
        [("record", "Business Record"), ("upload", "Direct Upload")],
        required=True,
    )
    source_model = fields.Char(readonly=True)
    source_record_id = fields.Integer(readonly=True)
    source_field_name = fields.Char(readonly=True)
    media_type = fields.Selection(
        [("image", "Image"), ("video", "Video")],
        required=True,
    )
    sequence = fields.Integer(default=10, required=True, index=True)
    note = fields.Text()
    availability_state = fields.Selection(
        [("available", "Available"), ("unavailable", "Unavailable")],
        required=True,
        default="unavailable",
    )

    _sql_constraints = [
        (
            "wd_evidence_album_item_album_attachment_uniq",
            "unique(album_id, attachment_id)",
            "An attachment can only appear once in an album.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        try:
            with self.env.cr.savepoint():
                records = super().create(vals_list)
        except IntegrityError as error:
            raise ValidationError(
                "An attachment can only appear once in an album."
            ) from error
        records._refresh_availability()
        return records

    def write(self, vals):
        try:
            with self.env.cr.savepoint():
                result = super().write(vals)
        except IntegrityError as error:
            raise ValidationError(
                "An attachment can only appear once in an album."
            ) from error
        self._refresh_availability()
        return result

    def _refresh_availability(self):
        for record in self:
            expected = "available" if record.attachment_id else "unavailable"
            if record.availability_state != expected:
                super(EvidenceAlbumItem, record).write(
                    {"availability_state": expected}
                )
        return True

    def refresh_availability(self):
        self._refresh_availability()
        return self

    def unlink(self):
        if any(item.album_id.state != "draft" for item in self):
            raise UserError("Media can only be removed from a draft album.")
        upload_attachment_ids = self.filtered(
            lambda item: item.source_type == "upload" and item.attachment_id
        ).mapped("attachment_id").ids
        result = super().unlink()
        if upload_attachment_ids:
            attachments = self.env["ir.attachment"].browse(upload_attachment_ids).exists()
            remaining_items = self.search([
                ("attachment_id", "in", attachments.ids),
            ])
            remaining_items._refresh_availability()
            referenced_ids = remaining_items.mapped("attachment_id").ids
            removable = attachments.filtered(
                lambda attachment: (
                    not attachment.res_model
                    and attachment.id not in referenced_ids
                )
            )
            removable.unlink()
        return result

    @api.model
    def create_validated(self, vals):
        attachment = self.env["ir.attachment"].browse(vals.get("attachment_id")).exists()
        if not attachment:
            raise ValidationError("A valid attachment is required.")
        media_type, _attachment = self.env["wd.evidence.album.media"].validate_attachment(
            attachment
        )
        vals = dict(vals, media_type=media_type, availability_state="available")
        return self.create(vals)

    @api.constrains("page_id", "album_id")
    def _check_album_consistency(self):
        for record in self:
            if record.page_id.album_id != record.album_id:
                raise ValidationError(
                    "An item must belong to the album of its page."
                )

    @api.constrains(
        "source_type",
        "source_model",
        "source_record_id",
        "source_field_name",
    )
    def _check_source_snapshot(self):
        for record in self:
            source_values = (
                record.source_model,
                record.source_record_id,
                record.source_field_name,
            )
            if record.source_type == "record" and not all(source_values):
                raise ValidationError(
                    "Record items require a complete source snapshot."
                )
            if record.source_type == "upload" and any(source_values):
                raise ValidationError(
                    "Upload items cannot contain a source snapshot."
                )


class EvidenceAlbumAttachment(models.Model):
    _inherit = "ir.attachment"

    def _refresh_evidence_items(self, attachment_ids):
        if attachment_ids:
            self.env["wd.evidence.album.item"].sudo().search(
                [("attachment_id", "in", attachment_ids)]
            )._refresh_availability()

    @api.model_create_multi
    def create(self, vals_list):
        attachment = super().create(vals_list)
        self._refresh_evidence_items(attachment.ids)
        return attachment

    def write(self, vals):
        result = super().write(vals)
        self._refresh_evidence_items(self.ids)
        return result

    def unlink(self):
        items = self.env["wd.evidence.album.item"].sudo().search(
            [("attachment_id", "in", self.ids)]
        )
        result = super().unlink()
        items.invalidate_recordset(["attachment_id"])
        items._refresh_availability()
        return result
