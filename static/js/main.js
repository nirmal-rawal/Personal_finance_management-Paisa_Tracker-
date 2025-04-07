console.log('77 my name is nirmal rawal from jumla', 77);
// Check for new notifications when page loads
document.addEventListener('DOMContentLoaded', function() {
    fetch('/notifications/unread/')
        .then(response => response.json())
        .then(data => {
            const countBadge = document.getElementById('unread-count');
            if (countBadge) {
                countBadge.textContent = data.unread_count;
            }
            
            // Optionally show a toast for new notifications
            if (data.unread_count > 0) {
                data.notifications.forEach(notification => {
                    if (!notification.is_read) {
                        showToast(notification.message, notification.url);
                    }
                });
            }
        });
});

function showToast(message, url) {
    // Implement your toast notification UI here
    console.log("New notification:", message);
    // You can use Bootstrap toasts or any other notification system
}