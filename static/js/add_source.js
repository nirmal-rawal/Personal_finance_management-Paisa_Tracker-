document.addEventListener("DOMContentLoaded", function() {
    const sourceSelect = document.getElementById("source-select");
    const customSourceGroup = document.getElementById("custom-source-group");
    const customSourceInput = document.getElementById("custom-source");

    sourceSelect.addEventListener("change", function() {
        if (sourceSelect.value === "Other") {
            customSourceGroup.classList.remove("d-none"); // Show the custom source field
            customSourceInput.setAttribute("required", true); // Make it required
        } else {
            customSourceGroup.classList.add("d-none"); // Hide the custom source field
            customSourceInput.removeAttribute("required"); // Remove the required attribute
        }
    });
});