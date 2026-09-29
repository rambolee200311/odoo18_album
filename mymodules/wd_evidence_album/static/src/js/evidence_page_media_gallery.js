/** @odoo-module **/

import { Component, onPatched, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { FileInput } from "@web/core/file_input/file_input";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";

export class EvidencePageMediaGallery extends Component {
    static template = "wd_evidence_album.EvidencePageMediaGallery";
    static components = { FileInput };
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);
        this.state = useState({ preview: null, metadata: {}, metadataKey: "" });
        this.openPreview = (item) => {
            this.state.preview = item;
        };
        this.closePreview = () => {
            this.state.preview = null;
        };
        this.onKeydown = (event) => {
            if (event.key === "Escape") {
                this.closePreview();
            }
        };
        document.addEventListener("keydown", this.onKeydown);
        onWillStart(() => this.loadMetadata());
        onPatched(() => this.loadMetadata());
        onWillUnmount(() => document.removeEventListener("keydown", this.onKeydown));
    }

    get items() {
        return this.props.record.data[this.props.name].records
            .map((record) => {
                const attachment = record.data.attachment_id;
                const attachmentId = attachment?.resId || attachment?.[0];
                if (!attachmentId) {
                    return null;
                }
                return {
                    id: record.resId,
                    attachmentId,
                    mediaType: record.data.media_type,
                    note: record.data.note || "",
                    name: this.state.metadata[attachmentId]?.name
                        || attachment.data?.display_name
                        || attachment.display_name
                        || "",
                    mimetype: this.state.metadata[attachmentId]?.mimetype || "",
                };
            })
            .filter(Boolean);
    }

    async loadMetadata() {
        const ids = this.items.map((item) => item.attachmentId);
        const key = ids.join(",");
        if (key === this.state.metadataKey) {
            return;
        }
        this.state.metadataKey = key;
        if (!ids.length) {
            this.state.metadata = {};
            return;
        }
        const records = await this.orm.searchRead(
            "ir.attachment",
            [["id", "in", ids]],
            ["name", "mimetype"],
        );
        this.state.metadata = Object.fromEntries(records.map((record) => [record.id, record]));
    }

    getUrl(id, download = false) {
        return `/web/content/${id}${download ? "?download=true" : ""}`;
    }

    get canEdit() {
        return this.props.record.data.album_state === "draft";
    }

    get hasRecordId() {
        return Boolean(this.props.record.resId);
    }

    async onFileUploaded(files) {
        for (const file of files) {
            if (file.error) {
                this.notification.add(file.error, { type: "danger" });
                continue;
            }
            try {
                await this.orm.call(
                    "wd.evidence.album.page",
                    "create_item_from_attachment",
                    [[this.props.record.resId], file.id],
                );
            } catch (error) {
                this.notification.add(
                    error.data?.message || error.message || _t("Could not upload the media."),
                    { type: "danger" },
                );
            }
        }
        await this.props.record.load();
    }

    async removeMedia(item) {
        if (!this.canEdit) {
            return;
        }
        const record = this.props.record.data[this.props.name].records.find(
            (candidate) => candidate.resId === item.id
        );
        if (!record) {
            return;
        }
        try {
            await this.operations.removeRecord(record);
            if (this.state.preview?.id === item.id) {
                this.closePreview();
            }
        } catch (error) {
            this.notification.add(
                error.data?.message || error.message || _t("Could not remove the media."),
                { type: "danger" },
            );
        }
    }

    isVideo(item) {
        return item?.mimetype?.startsWith("video/") || item?.mediaType === "video";
    }

}

registry.category("fields").add("evidence_page_media_gallery", {
    component: EvidencePageMediaGallery,
    supportedTypes: ["one2many"],
});
