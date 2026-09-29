from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestEvidenceAlbumPreview(TransactionCase):
    def setUp(self):
        super().setUp()
        self.album = self.env["wd.evidence.album"].create({
            "name": "Preview album",
            "customer_id": self.env.user.partner_id.commercial_partner_id.id,
        })

    def test_draft_album_returns_backend_preview_action(self):
        action = self.album.action_preview_portal()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["url"], "/odoo/evidence-albums/%s/preview" % self.album.id)
        self.assertEqual(action["target"], "new")

    def test_published_album_cannot_use_prepublication_preview(self):
        self.album._action_write({"state": "published"})
        with self.assertRaises(UserError):
            self.album.action_preview_portal()
