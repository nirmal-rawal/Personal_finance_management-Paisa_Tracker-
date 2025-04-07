document.addEventListener('DOMContentLoaded', function() {
    // Mark notification as read when clicked
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.id;
            if (!this.classList.contains('read')) {
                fetch(`/notifications/mark-read/${notificationId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.classList.add('read');
                        updateUnreadCount();
                    } else {
                        console.error('Failed to mark notification as read:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });
    
    // Mark all notifications as read
    const markAllReadBtn = document.querySelector('.mark-all-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI to show all notifications as read
                    document.querySelectorAll('.list-group-item-primary').forEach(item => {
                        item.classList.remove('list-group-item-primary');
                    });
                    updateUnreadCount();
                    
                    // Show success toast
                    showToast('success', data.message || 'All notifications marked as read');
                } else {
                    console.error('Failed to mark all as read:', data.error);
                    showToast('error', data.error || 'Failed to mark all notifications as read');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('error', 'An error occurred while marking notifications as read');
            });
        });
    }
    
    // Update unread count badge
    function updateUnreadCount() {
        fetch('/notifications/unread/', {
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            const countBadge = document.getElementById('unread-count');
            if (countBadge) {
                const previousCount = parseInt(countBadge.textContent || 0);
                countBadge.textContent = data.unread_count;
                
                // Show toast for new notifications if count increased
                if (data.unread_count > previousCount && data.notifications && data.notifications.length > 0) {
                    showNewNotificationToast(data.notifications[0]);
                }
            }
        })
        .catch(error => {
            console.error('Error fetching unread count:', error);
        });
    }
    
    // Show toast for new notification
    function showNewNotificationToast(notification) {
        const toast = document.createElement('div');
        toast.className = 'notification-toast position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '11';
        toast.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">New Notification</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${notification.message}
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        
        // Auto-remove toast after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    // Show generic toast message
    function showToast(type, message) {
        const toast = document.createElement('div');
        toast.className = `toast-container position-fixed top-0 end-0 p-3`;
        toast.style.zIndex = '11';
        toast.innerHTML = `
            <div class="toast show align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        
        // Auto-remove toast after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Check for new notifications every 60 seconds
    setInterval(updateUnreadCount, 60000);
    
    // Initial check
    updateUnreadCount();
});