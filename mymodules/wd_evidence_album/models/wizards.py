import mimetypes
import uuid

from odoo import api, fields, models
from odoo.exceptions import UserError


class EvidenceAlbumSourceRecordOption(models.TransientModel):
    _name = "wd.evidence.album.source.record.option"
    _description = "Evidence Album Source Record Option"
    _rec_name = "name"

    wizard_token = fields.Char(required=True, index=True)
    name = fields.Char(required=True, readonly=True)
    record_ref = fields.Reference(
        selection="_source_reference_selection",
        required=True,
        readonly=True,
    )

    @api.model
    def _source_reference_selection(self):
        configs = self.env["wd.evidence.album.source.config"].search(
            [("active", "=", True)]
        )
        models = configs.mapped("model_id").filtered(
            lambda model: model.model in self.env.registry
        )
        return [(model.model, model.name) for model in models]


class EvidenceAlbumSourcePageWizard(models.TransientModel):
    _name = "wd.evidence.album.source.page.wizard"
    _description = "Create evidence album page from source"

    album_id = fields.Many2one("wd.evidence.album", required=True)
    wizard_token = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: uuid.uuid4().hex,
    )
    source_config_id = fields.Many2one(
        "wd.evidence.album.source.config",
        required=True,
        domain=[("active", "=", True)],
    )
    source_record_option_id = fields.Many2one(
        "wd.evidence.album.source.record.option",
        required=True,
        string="Source Record",
        domain="[('wizard_token', '=', wizard_token)]",
    )
    title = fields.Char(required=True)
    description = fields.Text()
    select_all = fields.Boolean(string="Use all current attachments", default=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Selected attachments")

    def _source_record(self):
        self.ensure_one()
        if not self.source_record_option_id:
            return self.env[self.source_config_id.model_id.model].browse()
        record = self.source_record_option_id.record_ref
        if record._name != self.source_config_id.model_id.model:
            raise UserError("The source record does not match the selected Source Config.")
        return record

    @api.onchange("source_config_id")
    def _onchange_source(self):
        self.attachment_ids = [(5, 0, 0)]
        self.source_record_option_id = False
        self.env["wd.evidence.album.source.record.option"].search(
            [("wizard_token", "=", self.wizard_token)]
        ).unlink()
        if not self.source_config_id:
            return
        source_model = self.env[self.source_config_id.model_id.model]
        self.env["wd.evidence.album.source.record.option"].create(
            [
                {
                    "wizard_token": self.wizard_token,
                    "name": record.display_name,
                    "record_ref": "%s,%s" % (record._name, record.id),
                }
                for record in source_model.search([])
            ]
        )

    @api.onchange("source_record_option_id")
    def _onchange_source_record(self):
        self.attachment_ids = [(5, 0, 0)]
        if not self.source_config_id or not self.source_record_option_id:
            return
        record = self._source_record()
        attachments, _snapshot = self.source_config_id.resolve_record_attachments(record.id)
        mapped = self.source_config_id.map_record_values(record.id)
        self.title = mapped["title"]
        self.description = mapped["description"]
        self.attachment_ids = [(6, 0, attachments.ids)]
        return {"domain": {"attachment_ids": [("id", "in", attachments.ids)]}}

    def action_create(self):
        self.ensure_one()
        if not self.select_all and not self.attachment_ids:
            raise UserError("Select at least one source attachment.")
        record = self._source_record()
        page = self.album_id.create_page_from_source(
            self.source_config_id,
            record.id,
            title=self.title,
            description=self.description,
            attachment_ids=None if self.select_all else self.attachment_ids.ids,
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "wd.evidence.album.page",
            "res_id": page.id,
            "view_mode": "form",
            "target": "current",
        }


class EvidenceAlbumSourceItemsWizard(models.TransientModel):
    _name = "wd.evidence.album.source.items.wizard"
    _description = "Add source attachments to evidence page"

    page_id = fields.Many2one("wd.evidence.album.page", required=True)
    wizard_token = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: uuid.uuid4().hex,
    )
    source_config_id = fields.Many2one(
        "wd.evidence.album.source.config",
        required=True,
        domain=[("active", "=", True)],
    )
    source_record_option_id = fields.Many2one(
        "wd.evidence.album.source.record.option",
        required=True,
        string="Source Record",
        domain="[('wizard_token', '=', wizard_token)]",
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Selected attachments")

    def _source_record(self):
        self.ensure_one()
        if not self.source_record_option_id:
            return self.env[self.source_config_id.model_id.model].browse()
        record = self.source_record_option_id.record_ref
        if record._name != self.source_config_id.model_id.model:
            raise UserError("The source record does not match the selected Source Config.")
        return record

    @api.onchange("source_config_id")
    def _onchange_source(self):
        self.attachment_ids = [(5, 0, 0)]
        self.source_record_option_id = False
        self.env["wd.evidence.album.source.record.option"].search(
            [("wizard_token", "=", self.wizard_token)]
        ).unlink()
        if not self.source_config_id:
            return
        source_model = self.env[self.source_config_id.model_id.model]
        self.env["wd.evidence.album.source.record.option"].create(
            [
                {
                    "wizard_token": self.wizard_token,
                    "name": record.display_name,
                    "record_ref": "%s,%s" % (record._name, record.id),
                }
                for record in source_model.search([])
            ]
        )

    @api.onchange("source_record_option_id")
    def _onchange_source_record(self):
        self.attachment_ids = [(5, 0, 0)]
        if not self.source_config_id or not self.source_record_option_id:
            return
        record = self._source_record()
        attachments, _snapshot = self.source_config_id.resolve_record_attachments(record.id)
        self.attachment_ids = [(6, 0, attachments.ids)]
        return {"domain": {"attachment_ids": [("id", "in", attachments.ids)]}}

    def action_add(self):
        self.ensure_one()
        record = self._source_record()
        self.page_id.add_source_attachments(
            self.source_config_id, record.id, self.attachment_ids.ids
        )
        return {"type": "ir.actions.act_window_close"}


class EvidenceAlbumUploadWizard(models.TransientModel):
    _name = "wd.evidence.album.upload.wizard"
    _description = "Upload evidence album media"

    page_id = fields.Many2one("wd.evidence.album.page", required=True)
    file = fields.Binary(required=True, string="File")
    filename = fields.Char(required=True)

    def action_upload(self):
        self.ensure_one()
        mimetype = mimetypes.guess_type(self.filename or "")[0]
        self.page_id.create_upload_item(
            {"name": self.filename, "datas": self.file, "mimetype": mimetype or ""}
        )
        return {"type": "ir.actions.act_window_close"}


class EvidenceAlbumExtendValidityWizard(models.TransientModel):
    _name = "wd.evidence.album.extend.validity.wizard"
    _description = "Extend evidence album validity"

    album_id = fields.Many2one("wd.evidence.album", required=True, readonly=True)
    valid_until = fields.Datetime(required=True, string="New valid until")

    def action_extend(self):
        self.ensure_one()
        self.album_id.action_extend_validity(self.valid_until)
        return {"type": "ir.actions.act_window_close"}
