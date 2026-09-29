/** @odoo-module **/

import { Component, mount, onMounted, onWillUnmount, useEffect, useRef, useState, xml } from "@odoo/owl";

class EvidenceAlbumViewer extends Component {
    static template = xml`
        <div t-ref="controls" class="o_evidence_album_controls d-flex gap-2 mb-3">
            <div class="d-flex gap-2 align-items-center">
                <select class="form-select w-auto" aria-label="Filter media" t-on-change="onFilterChange">
                    <option value="all">All</option>
                    <option value="image">Images</option>
                    <option value="video">Videos</option>
                </select>
            </div>
            <div class="d-flex gap-2 align-items-center ms-auto">
                <label class="btn btn-outline-secondary mb-0">
                    <input t-ref="selectAll" type="checkbox" class="form-check-input me-1"
                           t-on-change="toggleCurrentPageSelection"/>
                    Select all
                </label>
                <button class="btn btn-primary" t-on-click="downloadSelected" t-att-disabled="!state.selected.length">
                    Download
                </button>
            </div>
        </div>
    `;

    setup() {
        this.state = useState({ page: 0, filter: "all", lightbox: null, selected: [] });
        this.controls = useRef("controls");
        this.selectAllRef = useRef("selectAll");
        this.root = null;
        this.onPageTabClick = (event) => {
            const tab = event.target.closest(".o_evidence_album_page_tab");
            if (!tab) return;
            this.selectPage(Number(tab.dataset.pageIndex));
        };
        useEffect(
            () => this.updateSelectAllState(),
            () => [this.state.page, this.state.selected.length],
        );
        this.selectPage = (index) => {
            this.state.page = index;
            this.clearSelection();
            this.props.pages.forEach((page, pageIndex) => {
                page.hidden = pageIndex !== index;
            });
            this.root?.querySelectorAll(".o_evidence_album_page_tab").forEach((tab, tabIndex) => {
                const active = tabIndex === index;
                tab.classList.toggle("active", active);
                tab.classList.toggle("fw-semibold", active);
                tab.classList.toggle("border-bottom", active);
                tab.classList.toggle("border-primary", active);
                tab.classList.toggle("text-muted", !active);
                tab.setAttribute("aria-selected", active ? "true" : "false");
            });
            this.setFilter(this.state.filter);
        };
        this.setFilter = (filter) => {
            this.state.filter = filter;
            const page = this.props.pages[this.state.page];
            page?.querySelectorAll("[data-media-type]").forEach((node) => {
                node.hidden = filter !== "all" && node.dataset.mediaType !== filter;
            });
        };
        this.onFilterChange = (event) => this.setFilter(event.target.value);
        this.onImageClick = (event) => {
            const image = event.target.closest("img");
            if (!image) return;
            event.preventDefault();
            this.openLightbox(image);
        };
        this.onSelectionChange = (event) => {
            const checkbox = event.target.closest(".o_evidence_album_item_select");
            if (!checkbox) return;
            const itemId = Number(checkbox.dataset.itemId);
            if (checkbox.checked) {
                if (!this.state.selected.includes(itemId)) {
                    this.state.selected = [...this.state.selected, itemId];
                }
            } else {
                this.state.selected = this.state.selected.filter((selectedId) => selectedId !== itemId);
            }
            checkbox.closest("[data-media-type]")?.classList.toggle("border", checkbox.checked);
            checkbox.closest("[data-media-type]")?.classList.toggle("border-primary", checkbox.checked);
            checkbox.closest("[data-media-type]")?.classList.toggle("rounded", checkbox.checked);
        };
        onMounted(() => {
            this.root = this.controls.el.closest(".o_evidence_album_viewer");
            this.root?.addEventListener("click", this.onImageClick);
            this.root?.addEventListener("change", this.onSelectionChange);
            this.root?.addEventListener("click", this.onPageTabClick);
            this.selectPage(0);
        });
        onWillUnmount(() => {
            this.root?.removeEventListener("click", this.onImageClick);
            this.root?.removeEventListener("change", this.onSelectionChange);
            this.root?.removeEventListener("click", this.onPageTabClick);
        });
    }

    clearSelection() {
        this.state.selected = [];
        this.root?.querySelectorAll(".o_evidence_album_item_select:checked").forEach((checkbox) => {
            checkbox.checked = false;
            checkbox.closest("[data-media-type]")?.classList.remove("border", "border-primary", "rounded");
        });
    }

    toggleCurrentPageSelection(event) {
        const page = this.props.pages[this.state.page];
        const itemIds = [...(page?.querySelectorAll(".o_evidence_album_item_select") || [])]
            .map((checkbox) => Number(checkbox.dataset.itemId));
        const selected = new Set(this.state.selected);
        if (event.target.checked) {
            itemIds.forEach((itemId) => selected.add(itemId));
        } else {
            itemIds.forEach((itemId) => selected.delete(itemId));
        }
        this.state.selected = [...selected];
        page?.querySelectorAll(".o_evidence_album_item_select").forEach((checkbox) => {
            checkbox.checked = event.target.checked;
            checkbox.closest("[data-media-type]")?.classList.toggle("border", event.target.checked);
            checkbox.closest("[data-media-type]")?.classList.toggle("border-primary", event.target.checked);
            checkbox.closest("[data-media-type]")?.classList.toggle("rounded", event.target.checked);
        });
    }

    updateSelectAllState() {
        const checkbox = this.selectAllRef.el;
        if (!checkbox) return;
        const page = this.props.pages[this.state.page];
        const itemIds = [...(page?.querySelectorAll(".o_evidence_album_item_select") || [])]
            .map((item) => Number(item.dataset.itemId));
        const selectedCount = itemIds.filter((itemId) => this.state.selected.includes(itemId)).length;
        checkbox.checked = itemIds.length > 0 && selectedCount === itemIds.length;
        checkbox.indeterminate = selectedCount > 0 && selectedCount < itemIds.length;
    }

    async downloadSelected() {
        const token = window.odoo?.csrf_token;
        const body = new URLSearchParams({
            item_ids: JSON.stringify(this.state.selected),
            csrf_token: token || "",
        });
        const response = await fetch("/my/media-albums/batch-download", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body,
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            window.alert(error.error || "The selected media could not be downloaded.");
            return;
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "evidence-media.zip";
        link.click();
        URL.revokeObjectURL(url);
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

function mountEvidenceAlbumViewers() {
    document.querySelectorAll(".o_evidence_album_controls_mount").forEach((element) => {
        if (element.dataset.mounted === "1") {
            return;
        }
        const root = element.closest(".o_evidence_album_viewer");
        if (!root) {
            return;
        }
        element.dataset.mounted = "1";
        mount(
            EvidenceAlbumViewer,
            element,
            { props: { pages: [...root.querySelectorAll("[data-page]")] } },
        );
    });
}

function bindEvidenceAlbumPageTabs() {
    document.querySelectorAll(".o_evidence_album_viewer").forEach((root) => {
        if (root.dataset.tabsBound === "1") {
            return;
        }
        const tabs = [...root.querySelectorAll(".o_evidence_album_page_tab")];
        const pages = [...root.querySelectorAll("[data-page]")];
        if (!tabs.length || !pages.length) {
            return;
        }
        const selectPage = (index) => {
            pages.forEach((page, pageIndex) => {
                page.hidden = pageIndex !== index;
            });
            tabs.forEach((tab, tabIndex) => {
                const active = tabIndex === index;
                tab.classList.toggle("active", active);
                tab.classList.toggle("fw-semibold", active);
                tab.setAttribute("aria-selected", active ? "true" : "false");
            });
        };
        tabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                selectPage(Number(tab.dataset.pageIndex));
            });
        });
        root.dataset.tabsBound = "1";
        selectPage(0);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        mountEvidenceAlbumViewers();
        bindEvidenceAlbumPageTabs();
    }, { once: true });
} else {
    mountEvidenceAlbumViewers();
    bindEvidenceAlbumPageTabs();
}
