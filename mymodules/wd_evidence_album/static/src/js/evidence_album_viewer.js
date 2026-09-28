/** @odoo-module **/

import { Component, mount, onMounted, onWillUnmount, useRef, useState, xml } from "@odoo/owl";

class EvidenceAlbumViewer extends Component {
    static template = xml`
        <div t-ref="controls" class="o_evidence_album_controls d-flex gap-2 mb-3">
            <t t-foreach="props.pages" t-as="page" t-key="page.dataset.page">
                <button class="btn btn-outline-primary" t-on-click="() => this.selectPage(props.pages.indexOf(page))">
                    Page <t t-esc="props.pages.indexOf(page) + 1"/>
                </button>
            </t>
            <button class="btn btn-outline-secondary" t-on-click="() => this.setFilter('all')">All</button>
            <button class="btn btn-outline-secondary" t-on-click="() => this.setFilter('image')">Images</button>
            <button class="btn btn-outline-secondary" t-on-click="() => this.setFilter('video')">Videos</button>
        </div>
    `;

    setup() {
        this.state = useState({ page: 0, filter: "all", lightbox: null });
        this.controls = useRef("controls");
        this.root = null;
        this.selectPage = (index) => {
            this.state.page = index;
            this.props.pages.forEach((page, pageIndex) => {
                page.hidden = pageIndex !== index;
            });
        };
        this.setFilter = (filter) => {
            this.state.filter = filter;
            const page = this.props.pages[this.state.page];
            page?.querySelectorAll("[data-media-type]").forEach((node) => {
                node.hidden = filter !== "all" && node.dataset.mediaType !== filter;
            });
        };
        this.onImageClick = (event) => {
            const image = event.target.closest("img");
            if (!image) return;
            event.preventDefault();
            this.openLightbox(image);
        };
        onMounted(() => {
            this.root = this.controls.el.closest(".o_evidence_album_viewer");
            this.root?.addEventListener("click", this.onImageClick);
            this.selectPage(0);
        });
        onWillUnmount(() => this.root?.removeEventListener("click", this.onImageClick));
    }

    openLightbox(image) {
        const images = [...this.root.querySelectorAll("img")];
        let index = images.indexOf(image);
        const overlay = document.createElement("div");
        overlay.className = "o_evidence_album_lightbox position-fixed top-0 start-0 w-100 h-100 bg-dark d-flex align-items-center justify-content-center";
        overlay.style.zIndex = "1050";
        const preview = document.createElement("img");
        preview.className = "mw-100 mh-100";
        const show = () => { preview.src = images[index].src.replace("/thumb", ""); };
        const close = () => overlay.remove();
        const previous = document.createElement("button");
        previous.className = "btn btn-light position-absolute start-0 m-3";
        previous.textContent = "‹";
        previous.onclick = () => { index = (index + images.length - 1) % images.length; show(); };
        const next = document.createElement("button");
        next.className = "btn btn-light position-absolute end-0 m-3";
        next.textContent = "›";
        next.onclick = () => { index = (index + 1) % images.length; show(); };
        overlay.append(previous, preview, next);
        overlay.onclick = (event) => { if (event.target === overlay) close(); };
        document.body.appendChild(overlay);
        show();
        preview.ondblclick = () => preview.requestFullscreen?.();
    }
}

document.querySelectorAll(".o_evidence_album_controls_mount").forEach((element) => {
    mount(
        EvidenceAlbumViewer,
        element,
        { props: { pages: [...element.closest(".o_evidence_album_viewer").querySelectorAll("[data-page]")] } },
    );
});
