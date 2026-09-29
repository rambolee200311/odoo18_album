/** @odoo-module **/

document.querySelectorAll(".o_evidence_album_list").forEach((list) => {
    const form = list.querySelector("form");
    const search = list.querySelector('input[name="search"]');
    const sort = list.querySelector('select[name="sort"]');
    const cards = [...list.querySelectorAll(".o_evidence_album_list_card")];
    if (!form || !search) return;

    const filterCards = () => {
        const query = search.value.trim().toLocaleLowerCase();
        cards.forEach((card) => {
            card.parentElement.hidden = query && !card.dataset.search.toLocaleLowerCase().includes(query);
        });
    };
    search.addEventListener("input", filterCards);
    form.addEventListener("submit", (event) => event.preventDefault());
    sort?.addEventListener("change", () => form.submit());
    filterCards();
});
