import secrets

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
            if vals.get("state", "draft") != "draft":
                raise UserError("An album must start in Draft.")
            if any(vals.get(field) for field in ("token", "published_at", "revoked_at", "reviewed_by")):
                raise UserError("Publication fields can only be set by album actions.")
            if not vals.get("album_number"):
                vals["album_number"] = self.env["ir.sequence"].next_by_code(
                    "wd.evidence.album"
                )
        try:
            with self.env.cr.savepoint():
                return super().create(vals_list)
        except IntegrityError as error:
            if error.diag.constraint_name == "wd_evidence_album_token_uniq":
                raise ValidationError("The album token must be unique.") from error
            raise

    def write(self, vals):
        vals = dict(vals)
        self._normalize_customer(vals)
        protected_fields = {
            "state",
            "token",
            "published_at",
            "revoked_at",
            "reviewed_by",
        }
        if protected_fields.intersection(vals) and not self.env.context.get(
            "_evidence_album_action_write"
        ):
            raise UserError("Use the dedicated album action to change publication fields.")
        if (
            "valid_until" in vals
            and any(record.state == "published" for record in self)
            and not self.env.context.get("_evidence_album_action_write")
        ):
            raise UserError("Use the dedicated validity action for published albums.")
        try:
            with self.env.cr.savepoint():
                return super().write(vals)
        except IntegrityError as error:
            if error.diag.constraint_name == "wd_evidence_album_token_uniq":
                raise ValidationError("The album token must be unique.") from error
            raise

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

    def _check_single_action(self):
        if len(self) != 1:
            raise UserError("Album actions must be called for exactly one album.")
        self.ensure_one()

    def _check_write_access(self):
        self.check_access_rights("write")
        self.check_access_rule("write")

    def _check_reviewer_access(self):
        self._check_write_access()
        if not self.env.user.has_group("wd_evidence_album.group_album_reviewer"):
            raise UserError("Only album reviewers or managers may perform this action.")

    def _action_write(self, vals):
        return self.with_context(_evidence_album_action_write=True).write(vals)

    def _check_state(self, expected, message):
        if self.state != expected:
            raise UserError(message)

    def _check_not_empty(self):
        if not self.page_ids or not self.page_ids.mapped("item_ids"):
            raise UserError("An empty album cannot be approved or published. Add a page and media first.")

    def _check_publishable(self):
        self._check_not_empty()
        items = self.page_ids.mapped("item_ids")
        items.refresh_availability()
        if any(
            not item.attachment_id or item.availability_state != "available"
            for item in items
        ):
            raise UserError("All album media must be available before publication.")
        media = self.env["wd.evidence.album.media"]
        for item in items:
            media_type, _attachment = media.validate_attachment(item.attachment_id)
            if media_type != item.media_type:
                raise UserError("An album item has an inconsistent media type.")

    def _next_token(self):
        for _attempt in range(10):
            token = secrets.token_urlsafe(32)
            if not self.search_count([("token", "=", token)]):
                return token
        raise UserError("Could not generate a unique album token.")

    def action_submit_review(self):
        self._check_single_action()
        self._check_write_access()
        self._check_state("draft", "Only draft albums can be submitted for review.")
        self._action_write({"state": "pending_review"})
        return True

    def action_approve(self):
        self._check_single_action()
        self._check_reviewer_access()
        self._check_state("pending_review", "Only albums pending review can be approved.")
        self._check_not_empty()
        self._action_write({
            "state": "approved",
            "reviewed_by": self.env.user.id,
        })
        return True

    def action_reject(self):
        self._check_single_action()
        self._check_reviewer_access()
        self._check_state("pending_review", "Only albums pending review can be rejected.")
        self._action_write({
            "state": "draft",
            "reviewed_by": self.env.user.id,
        })
        return True

    def action_publish(self):
        self._check_single_action()
        self._check_reviewer_access()
        self._check_state("approved", "Only approved albums can be published.")
        self._check_publishable()
        self._action_write({
            "state": "published",
            "token": self._next_token(),
            "published_at": fields.Datetime.now(),
        })
        return True

    def action_revoke(self):
        self._check_single_action()
        self._check_reviewer_access()
        self._check_state("published", "Only published albums can be revoked.")
        self._action_write({
            "state": "revoked",
            "revoked_at": fields.Datetime.now(),
        })
        return True

    def action_reset_token(self):
        self._check_single_action()
        self._check_reviewer_access()
        self._check_state("published", "Only published albums can reset a token.")
        self._action_write({"token": self._next_token()})
        return True

    def action_open_extend_validity(self):
        self._check_single_action()
        self._check_write_access()
        if not self.env.user.has_group("wd_evidence_album.group_album_manager"):
            raise UserError("Only album managers may extend validity.")
        self._check_state("published", "Only published albums can extend validity.")
        return {
            "type": "ir.actions.act_window",
            "name": "Extend Album Validity",
            "res_model": "wd.evidence.album.extend.validity.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_album_id": self.id},
        }

    def action_extend_validity(self, new_valid_until):
        self._check_single_action()
        self._check_write_access()
        if not self.env.user.has_group("wd_evidence_album.group_album_manager"):
            raise UserError("Only album managers may extend validity.")
        self._check_state("published", "Only published albums can extend validity.")
        new_valid_until = fields.Datetime.to_datetime(new_valid_until)
        if not new_valid_until or new_valid_until <= fields.Datetime.now():
            raise ValidationError("The new validity must be later than the current server time.")
        self._action_write({"valid_until": new_valid_until})
        return True

    def is_expired(self, now=None):
        self._check_single_action()
        if not self.valid_until:
            return False
        reference = fields.Datetime.to_datetime(now or fields.Datetime.now())
        return reference >= fields.Datetime.to_datetime(self.valid_until)

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
