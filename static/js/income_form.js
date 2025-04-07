$(document).ready(function() {
    // Handle source selection change
    $('#source-select').change(function() {
        if ($(this).val() === 'Other') {
            $('#custom-source-group').removeClass('d-none').show();
            $('#custom_source').prop('required', true);
        } else {
            $('#custom-source-group').hide();
            $('#custom_source').prop('required', false);
        }
    });

    // Handle receipt scanning
    const dragDropArea = $('#drag-drop-area');
    const receiptUpload = $('#receipt-upload');
    const scanReceiptBtn = $('#scan-receipt-btn');
    const scanningIndicator = $('#scanning-indicator');
    const scanResultAlert = $('#scan-result-alert');

    // Handle drag and drop
    dragDropArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });

    dragDropArea.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });

    dragDropArea.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        if (e.originalEvent.dataTransfer.files.length) {
            receiptUpload[0].files = e.originalEvent.dataTransfer.files;
            handleReceiptUpload();
        }
    });

    scanReceiptBtn.on('click', function() {
        receiptUpload.click();
    });

    receiptUpload.on('change', handleReceiptUpload);

    function handleReceiptUpload() {
        const file = receiptUpload[0].files[0];
        if (!file) return;

        // Validate file type and size
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPG, PNG)');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert('File size should be less than 5MB');
            return;
        }

        // Show scanning indicator
        scanningIndicator.removeClass('d-none');
        scanResultAlert.addClass('d-none');

        // Prepare form data
        const formData = new FormData();
        formData.append('receipt', file);
        formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());

        // Make AJAX request
        $.ajax({
            url: '/incomes/scan-income-receipt/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.error) {
                    alert('Error: ' + response.error);
                } else {
                    // Auto-fill the form
                    $('#amount').val(response.amount);
                    $('#description').val(response.description);
                    $('#date').val(response.date);
                    
                    // Set the source
                    const sourceSelect = $('#source-select');
                    const sourceOption = sourceSelect.find(`option[value="${response.source}"]`);
                    
                    if (sourceOption.length) {
                        sourceOption.prop('selected', true);
                    } else {
                        sourceSelect.val('Other');
                        $('#custom-source-group').show();
                        $('#custom_source').val(response.source);
                    }
                    
                    // Show success message
                    scanResultAlert.removeClass('d-none');
                }
            },
            error: function(xhr, status, error) {
                alert('Error scanning document: ' + error);
            },
            complete: function() {
                scanningIndicator.addClass('d-none');
            }
        });
    }
});