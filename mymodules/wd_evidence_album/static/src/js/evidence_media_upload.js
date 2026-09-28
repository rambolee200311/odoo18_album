/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { FileUploader } from "@web/views/fields/file_handler";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";

export class EvidenceMediaUpload extends Component {
    static template = "wd_evidence_album.EvidenceMediaUpload";
    static components = { FileUploader };
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    get attachments() {
        return this.props.record.data[this.props.name]?.records || [];
    }

    async onUploaded(file) {
        const [attachmentId] = await this.orm.create("ir.attachment", [{
            name: file.name,
            datas: file.data,
            mimetype: file.type || "application/octet-stream",
            res_model: this.props.record.resModel,
            res_id: this.props.record.resId || false,
        }]);
        const ids = this.attachments.map((record) => record.resId).filter(Boolean);
        await this.props.record.update({
            [this.props.name]: [[6, 0, [...ids, attachmentId]]],
        });
    }

    async removeAttachment(attachment) {
        const attachmentId = attachment.resId;
        await this.props.record.update({
            [this.props.name]: [[3, attachmentId]],
        });
        await this.orm.unlink("ir.attachment", [attachmentId]);
    }

    isVideo(attachment) {
        return (attachment.data.mimetype || "").startsWith("video/");
    }

    getUrl(attachment) {
        return `/web/content/${attachment.resId}`;
    }
}

registry.category("fields").add("evidence_media_upload", {
    component: EvidenceMediaUpload,
    supportedTypes: ["many2many"],
});
