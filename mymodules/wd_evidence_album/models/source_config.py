from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError


class EvidenceAlbumSourceConfig(models.Model):
    _name = "wd.evidence.album.source.config"
    _description = "Evidence Album Source Configuration"
    _order = "label, id"

    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
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

    @api.model_create_multi
    def create(self, vals_list):
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
