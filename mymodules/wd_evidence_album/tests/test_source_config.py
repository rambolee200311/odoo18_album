from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEvidenceAlbumSourceConfig(TransactionCase):
    def test_field_candidate_populates_field_name(self):
        model = self.env["ir.model"].search([("model", "=", "wd.evidence.album.source.config")], limit=1)
        field = self.env["ir.model.fields"].search([
            ("model_id", "=", model.id),
            ("name", "=", "label"),
        ], limit=1)
        config = self.env["wd.evidence.album.source.config"].new({
            "model_id": model.id,
            "label": "Demo",
        })
        config.field_id = field
        config._onchange_field_id()
        self.assertEqual(config.field_name, "label")

    def test_text_field_is_rejected_by_resolver_validation(self):
        model = self.env["ir.model"].search([("model", "=", "wd.evidence.album.source.config")], limit=1)
        config = self.env["wd.evidence.album.source.config"].new({
            "model_id": model.id,
            "field_name": "label",
            "label": "Demo",
        })
        with self.assertRaises(ValidationError):
            config._validate_configuration()
