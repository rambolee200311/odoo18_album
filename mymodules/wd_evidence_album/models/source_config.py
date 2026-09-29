from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.mail import html2plaintext
from psycopg2 import IntegrityError


class EvidenceAlbumSourceConfig(models.Model):
    _name = "wd.evidence.album.source.config"
    _description = "Media Album Source Configuration"
    _order = "label, id"
    _rec_name = "label"

    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Source Field Candidate",
        domain="[('model_id', '=', model_id)]",
        help="Optional UI helper to pick an existing field on the selected model.",
    )
    field_name = fields.Char(required=True)
    label = fields.Char(required=True)
    title_field_name = fields.Char()
    description_field_name = fields.Char()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "wd_evidence_album_source_model_field_uniq",
            "unique(model_id, field_name)",
            "The source model and field combination must be unique.",
        ),
    ]

    def init(self):
        defaults = {
            "wd_evidence_album.zip.max_files": 50,
            "wd_evidence_album.zip.max_total_bytes": 100 * 1024 * 1024,
            "wd_evidence_album.zip.max_memory_bytes": 128 * 1024 * 1024,
            "wd_evidence_album.zip.timeout_seconds": 60,
            "wd_evidence_album.zip.max_concurrency": 2,
        }
        parameters = self.env["ir.config_parameter"].sudo()
        for key, value in defaults.items():
            if parameters.get_param(key) is None:
                parameters.set_param(key, value)


    @api.onchange("model_id")
    def _onchange_model_id(self):
        if not self.model_id:
            self.field_id = False
            return
        if self.field_id and self.field_id.model_id != self.model_id:
            self.field_id = False

    @api.onchange("field_id")
    def _onchange_field_id(self):
        if self.field_id:
            self.field_name = self.field_id.name

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            if vals.get("field_id") and not vals.get("field_name"):
                field = self.env["ir.model.fields"].browse(vals["field_id"]).exists()
                if field:
                    vals["field_name"] = field.name
        try:
            with self.env.cr.savepoint():
                records = super().create(vals_list)
        except IntegrityError as error:
            raise ValidationError(
                "The source model and field combination must be unique."
            ) from error
        records._validate_for_resolver()
        return records

    def write(self, vals):
        vals = dict(vals)
        if vals.get("field_id") and "field_name" not in vals:
            field = self.env["ir.model.fields"].browse(vals["field_id"]).exists()
            if field:
                vals["field_name"] = field.name
        try:
            with self.env.cr.savepoint():
                result = super().write(vals)
        except IntegrityError as error:
            raise ValidationError(
                "The source model and field combination must be unique."
            ) from error
        if any(key in vals for key in (
            "model_id",
            "field_name",
            "title_field_name",
            "description_field_name",
            "active",
        )):
            self._validate_for_resolver()
        return result

    def _validate_for_resolver(self):
        for config in self:
            config._validate_configuration()
        return True

    def _validate_configuration(self):
        self.ensure_one()
        if not self.model_id:
            raise ValidationError("A source model is required.")
        model_name = self.model_id.model
        if model_name not in self.env.registry:
            raise ValidationError("The configured source model is not loaded.")
        source_model = self.env[model_name]
        if not self.field_name:
            raise ValidationError("A source attachment field is required.")
        source_field = source_model._fields.get(self.field_name)
        if not source_field:
            raise ValidationError("The configured source field does not exist.")
        if (
            source_field.type != "many2many"
            or source_field.comodel_name != "ir.attachment"
        ):
            raise ValidationError(
                "The source field must be a Many2many to ir.attachment."
            )
        for field_name in (
            self.title_field_name,
            self.description_field_name,
        ):
            if field_name:
                field = source_model._fields.get(field_name)
                if not field:
                    raise ValidationError(
                        "The mapped source field does not exist: %s" % field_name
                    )
                if field.type not in ("char", "text", "html", "many2one", "selection"):
                    raise ValidationError(
                        "The mapped source field type is not supported: %s" % field_name
                    )
                try:
                    source_model.check_field_access_rights("read", [field_name])
                except AccessError as error:
                    raise UserError(
                        "The mapped source field is not readable: %s" % field_name
                    ) from error
        try:
            source_model.check_access_rights("read")
        except AccessError as error:
            raise UserError(
                "The current user cannot read the configured source model."
            ) from error
        return True

    def resolve_record_attachments(self, record_id):
        """Resolve one source record using ordinary (non-sudo) permissions."""
        self.ensure_one()
        self._validate_configuration()
        if not self.active:
            raise UserError("The source configuration is disabled.")
        source_model = self.env[self.model_id.model]
        record = source_model.browse(record_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        if not record.exists():
            raise UserError("The configured source record does not exist.")
        record.ensure_one()
        attachments = record[self.field_name]
        return attachments, {
            "source_model": self.model_id.model,
            "source_record_id": record.id,
            "source_field_name": self.field_name,
        }

    def map_record_values(self, record_id):
        self.ensure_one()
        self._validate_configuration()
        source_model = self.env[self.model_id.model]
        record = source_model.browse(record_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        if not record.exists():
            raise UserError("The configured source record does not exist.")
        record.ensure_one()
        values = {}
        for output, field_name in (
            ("title", self.title_field_name),
            ("description", self.description_field_name),
        ):
            if not field_name:
                raise UserError(
                    "A %s field must be configured; default mapping is not available."
                    % output
                )
            field = source_model._fields[field_name]
            source_model.check_field_access_rights("read", [field_name])
            value = record[field_name]
            if field.type in ("char", "text"):
                values[output] = value or False
            elif field.type == "html":
                values[output] = html2plaintext(value or "") or False
            elif field.type == "many2one":
                values[output] = value.display_name if value else False
            elif field.type == "selection":
                values[output] = value or False
            else:
                raise UserError("The mapped %s field type is not supported." % output)
        return values
