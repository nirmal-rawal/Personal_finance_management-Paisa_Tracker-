/**
 * Expense Form JavaScript
 * Handles all client-side functionality for the expense form
 */

// Document ready handler
$(document).ready(function() {
    // Set today's date as default in the date field
    $('#date').val(new Date().toISOString().split('T')[0]);

    // Initialize drag and drop functionality for receipt upload
    initDragAndDrop();
    
    // Initialize file upload handlers
    initFileUpload();
    
    // Initialize category selection handler
    initCategorySelection();
});

/**
 * Initialize drag and drop functionality for the receipt upload area
 */
function initDragAndDrop() {
    const dragDropArea = document.getElementById('drag-drop-area');
    
    // Prevent default drag behaviors for these events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, highlight, false);
    });

    // Remove highlight when item leaves
    ['dragleave', 'drop'].forEach(eventName => {
        dragDropArea.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dragDropArea.addEventListener('drop', handleDrop, false);
}

/**
 * Prevent default drag and drop behaviors
 * @param {Event} e - The event object
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Highlight the drop area when files are dragged over it
 */
function highlight() {
    $('#drag-drop-area').addClass('bg-primary bg-opacity-10');
}

/**
 * Remove highlight from drop area
 */
function unhighlight() {
    $('#drag-drop-area').removeClass('bg-primary bg-opacity-10');
}

/**
 * Handle files dropped onto the drop area
 * @param {Event} e - The drop event
 */
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
        $('#receipt-upload')[0].files = files;
        handleFileUpload(files[0]);
    }
}

/**
 * Initialize file upload button and input handlers
 */
function initFileUpload() {
    // Handle receipt scanning button click
    $('#scan-receipt-btn').click(function() {
        $('#receipt-upload').click();
    });
    
    // Handle file selection via file input
    $('#receipt-upload').change(function() {
        if (this.files && this.files[0]) {
            handleFileUpload(this.files[0]);
        }
    });
}

/**
 * Process the uploaded file and send to server for scanning
 * @param {File} file - The file to upload
 */
function handleFileUpload(file) {
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showAlert('File size should be less than 5MB', 'danger');
        return;
    }
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showAlert('Only JPG, JPEG, or PNG images are allowed', 'danger');
        return;
    }
    
    // Show scanning indicator
    $('#scanning-indicator').removeClass('d-none');
    $('#scan-result-alert').addClass('d-none');
    
    // Create FormData and send to server
    const formData = new FormData();
    formData.append('receipt', file);
    formData.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val());
    
    // AJAX request to scan receipt
    $.ajax({
        url: $('#expense-form').data('scan-url') || '/scan-receipt/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            // Auto-fill form with scanned data
            if (data.amount) {
                $('#amount').val(parseFloat(data.amount).toFixed(2));
            }
            if (data.date) {
                $('#date').val(data.date);
            }
            if (data.description) {
                $('#description').val(data.description);
            }
            if (data.category) {
                $('#category').val(data.category.toLowerCase());
                if (data.category === 'Other') {
                    $('#custom-category-group').show();
                }
            }
            
            // Hide scanning indicator
            $('#scanning-indicator').addClass('d-none');
            $('#scan-result-alert').removeClass('d-none');
            
            // Focus on amount field
            $('#amount').focus();
            
            // Show preview of uploaded image
            showImagePreview(file);
        },
        error: function(xhr) {
            // Hide scanning indicator
            $('#scanning-indicator').addClass('d-none');
            
            // Show error message
            let errorMsg = 'Failed to scan receipt. Please try again.';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            showAlert(errorMsg, 'danger');
        }
    });
}

/**
 * Display a preview of the uploaded image
 * @param {File} file - The uploaded file
 */
function showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        $('#drag-drop-area').html(`
            <img src="${e.target.result}" class="img-thumbnail mb-2" style="max-height: 120px;">
            <p class="text-success fw-medium mb-1">Receipt ready for processing</p>
            <button type="button" class="btn btn-sm btn-outline-secondary mt-2" onclick="resetUploader()">
                <i class="fas fa-redo me-1"></i> Upload different file
            </button>
        `);
    }
    reader.readAsDataURL(file);
}

/**
 * Initialize category selection handler
 */
function initCategorySelection() {
    $('#category').change(function() {
        if ($(this).val() === 'Other') {
            $('#custom-category-group').show();
            $('#custom_category').prop('required', true);
        } else {
            $('#custom-category-group').hide();
            $('#custom_category').prop('required', false);
        }
    });
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (e.g., 'danger', 'success')
 */
function showAlert(message, type) {
    const alert = $(`<div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`);
    $('.scan-section').append(alert);
    setTimeout(() => alert.alert('close'), 5000);
}

/**
 * Reset the file uploader to its initial state
 * (Exposed globally to be called from HTML)
 */
window.resetUploader = function() {
    $('#drag-drop-area').html(`
        <i class="fas fa-cloud-upload-alt"></i>
        <p class="drag-drop-text">Drag & drop your receipt here or</p>
        <button type="button" id="scan-receipt-btn" class="btn btn-scan scanning-animation">
            <i class="fas fa-camera me-2"></i> Upload Receipt
        </button>
        <p class="drag-drop-hint">Supports JPG, PNG (Max 5MB)</p>
    `);
    $('#receipt-upload').val('');
    $('#scan-result-alert').addClass('d-none');
    
    // Reinitialize event listeners
    $('#scan-receipt-btn').click(function() {
        $('#receipt-upload').click();
    });
};