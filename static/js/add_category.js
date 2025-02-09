document.addEventListener("DOMContentLoaded", function () {
    let categorySelect = document.getElementById("category-select");
    let customCategoryGroup = document.getElementById("custom-category-group");

    categorySelect.addEventListener("change", function () {
        if (this.value === "Other") {
            customCategoryGroup.classList.remove("d-none");
        } else {
            customCategoryGroup.classList.add("d-none");
        }
    });
});
