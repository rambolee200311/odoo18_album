from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError


class EvidenceAlbum(models.Model):
    _name = "wd.evidence.album"
    _description = "Evidence Album"
    _order = "create_date desc, id desc"

    _ALLOWED_STATES = {
        "draft",
        "pending_review",
        "approved",
        "published",
        "revoked",
    }

    album_number = fields.Char(
        string="Album Number",
        readonly=True,
        copy=False,
        index=True,
    )
    name = fields.Char(required=True)
    customer_id = fields.Many2one("res.partner", required=True, index=True)
    description = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_review", "Pending Review"),
            ("approved", "Approved"),
            ("published", "Published"),
            ("revoked", "Revoked"),
        ],
        required=True,
        default="draft",
        index=True,
    )
    token = fields.Char(index=True)
    valid_until = fields.Datetime(index=True)
    published_at = fields.Datetime(readonly=True)
    revoked_at = fields.Datetime(readonly=True)
    reviewed_by = fields.Many2one("res.users", readonly=True)
    page_ids = fields.One2many(
        "wd.evidence.album.page",
        "album_id",
        string="Pages",
        order="sequence, id",
        copy=True,
    )

    _sql_constraints = [
        (
            "wd_evidence_album_number_uniq",
            "unique(album_number)",
            "The album number must be unique.",
        ),
        (
            "wd_evidence_album_token_uniq",
            "unique(token)",
            "The album token must be unique.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._normalize_customer(vals)
            if not vals.get("album_number"):
                vals["album_number"] = self.env["ir.sequence"].next_by_code(
                    "wd.evidence.album"
                )
        try:
            with self.env.cr.savepoint():
                return super().create(vals_list)
        except IntegrityError as error:
            raise ValidationError(
                "The album token must be unique."
            ) from error

    def write(self, vals):
        vals = dict(vals)
        self._normalize_customer(vals)
        try:
            with self.env.cr.savepoint():
                return super().write(vals)
        except IntegrityError as error:
            raise ValidationError(
                "The album token must be unique."
            ) from error

    @api.model
    def _normalize_customer(self, vals):
        customer_id = vals.get("customer_id")
        if customer_id:
            partner = self.env["res.partner"].browse(customer_id).exists()
            if not partner:
                raise ValidationError("The selected customer does not exist.")
            vals["customer_id"] = partner.commercial_partner_id.id

    @api.constrains("state")
    def _check_state(self):
        for record in self:
            if record.state not in self._ALLOWED_STATES:
                raise ValidationError("Invalid evidence album state.")

    def unlink(self):
        if any(record.state == "published" for record in self):
            raise UserError("A published album cannot be deleted directly.")
        return super().unlink()

    def _deferred_action(self, action_name):
        raise UserError(
            "%s is reserved for the CC-03 implementation." % action_name
        )

    def action_submit_review(self):
        return self._deferred_action("Submit for review")

    def action_approve(self):
        return self._deferred_action("Approve")

    def action_reject(self):
        return self._deferred_action("Reject")

    def action_publish(self):
        return self._deferred_action("Publish")

    def action_revoke(self):
        return self._deferred_action("Revoke")

    def action_reset_token(self):
        return self._deferred_action("Reset token")

    def create_page_from_source(
        self,
        source_config,
        source_record_id,
        title=False,
        description=False,
        attachment_ids=None,
    ):
        self.ensure_one()
        self.check_access_rights("write")
        self.check_access_rule("write")
        source_config.ensure_one()
        attachments, snapshot = source_config.resolve_record_attachments(source_record_id)
        if attachment_ids is not None:
            selected = attachments & self.env["ir.attachment"].browse(attachment_ids)
            if set(selected.ids) != set(attachment_ids):
                raise UserError(
                    "Only attachments from the configured source field may be selected."
                )
            attachments = selected
        if not attachments:
            raise UserError("The source record has no attachments.")
        if attachment_ids is not None:
            attachments = attachments & self.env["ir.attachment"].browse(attachment_ids)
            if not attachments:
                raise UserError("Select at least one source attachment.")
        mapped = source_config.map_record_values(source_record_id)
        media = self.env["wd.evidence.album.media"]
        for attachment in attachments:
            media.validate_attachment(attachment)
            if self.env["wd.evidence.album.item"].search_count(
                [("album_id", "=", self.id), ("attachment_id", "=", attachment.id)]
            ):
                raise UserError("An attachment can only appear once in an album.")
        page = self.env["wd.evidence.album.page"].create(
            {
                "album_id": self.id,
                "title": title or mapped["title"],
                "description": mapped["description"] if description is False else description,
            }
        )
        self.env["wd.evidence.album.item"].create(
            [
                dict(
                    snapshot,
                    page_id=page.id,
                    attachment_id=attachment.id,
                    source_type="record",
                    media_type=media.validate_attachment(attachment)[0],
                    availability_state="available",
                )
                for attachment in attachments
            ]
        )
        return page

    def action_open_create_page_from_source(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Create Page from Source",
            "res_model": "wd.evidence.album.source.page.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_album_id": self.id},
        }
