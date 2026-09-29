from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EvidenceAlbumConfigSettings(models.TransientModel):
    _name = "wd.evidence.album.config.settings"
    _inherit = "res.config.settings"
    _description = "Media Album Settings"

    zip_max_files = fields.Integer(
        string="Maximum ZIP files",
        config_parameter="wd_evidence_album.zip.max_files",
        default=50,
    )
    zip_max_total_bytes = fields.Integer(
        string="Maximum ZIP total bytes",
        config_parameter="wd_evidence_album.zip.max_total_bytes",
        default=100 * 1024 * 1024,
    )
    zip_max_memory_bytes = fields.Integer(
        string="Maximum ZIP memory bytes",
        config_parameter="wd_evidence_album.zip.max_memory_bytes",
        default=128 * 1024 * 1024,
    )
    zip_timeout_seconds = fields.Integer(
        string="ZIP timeout (seconds)",
        config_parameter="wd_evidence_album.zip.timeout_seconds",
        default=60,
    )
    zip_max_concurrency = fields.Integer(
        string="Maximum concurrent ZIP downloads",
        config_parameter="wd_evidence_album.zip.max_concurrency",
        default=2,
    )

    @api.constrains(
        "zip_max_files",
        "zip_max_total_bytes",
        "zip_max_memory_bytes",
        "zip_timeout_seconds",
        "zip_max_concurrency",
    )
    def _check_positive_limits(self):
        for settings in self:
            values = (
                settings.zip_max_files,
                settings.zip_max_total_bytes,
                settings.zip_max_memory_bytes,
                settings.zip_timeout_seconds,
                settings.zip_max_concurrency,
            )
            if any(value < 1 for value in values):
                raise ValidationError("ZIP resource limits must be positive.")
