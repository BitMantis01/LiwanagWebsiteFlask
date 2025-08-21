// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
    initUserMenu();
    initMobileNav();
    initAlerts();
});

// Sidebar functionality
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }
}

// User menu dropdown
function initUserMenu() {
    const userMenuToggle = document.getElementById('user-menu-toggle');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuToggle.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
    }
}

// Mobile navigation
function initMobileNav() {
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', function() {
            sidebar.classList.add('show');
            mobileOverlay.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', function() {
            closeMobileNav();
        });
    }
    
    // Close mobile nav with escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileNav();
        }
    });
}

function closeMobileNav() {
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (sidebar) sidebar.classList.remove('show');
    if (mobileOverlay) mobileOverlay.classList.remove('show');
    document.body.style.overflow = '';
}

// Alert functionality
function initAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                dismissAlert(alert);
            });
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                dismissAlert(alert);
            }
        }, 5000);
    });
}

function dismissAlert(alert) {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 300);
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    
    const icon = getAlertIcon(type);
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button class="alert-close" onclick="dismissAlert(this.parentElement)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        const flashMessages = contentArea.querySelector('.flash-messages') || 
                            createFlashContainer(contentArea);
        flashMessages.appendChild(notification);
        
        // Auto-dismiss
        setTimeout(() => {
            if (notification.parentElement) {
                dismissAlert(notification);
            }
        }, 5000);
    }
}

function createFlashContainer(contentArea) {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    contentArea.insertBefore(container, contentArea.firstChild);
    return container;
}

function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        warning: 'exclamation-triangle',
        danger: 'times-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Chart utilities (for future use)
function createChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (ctx && typeof Chart !== 'undefined') {
        return new Chart(ctx, config);
    }
    return null;
}

// Data formatting utilities
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatMeasurement(value, unit) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    return `${value}${unit}`;
}

// Session management
function completeSession(sessionId) {
    if (confirm('Are you sure you want to mark this session as completed?')) {
        // This would typically make an API call
        showNotification('Session marked as completed', 'success');
    }
}

// Profile picture handling
function loadProfilePicture(username) {
    const avatars = document.querySelectorAll('img[alt="Profile"]');
    avatars.forEach(avatar => {
        avatar.src = `/avatar/${username}`;
        avatar.onerror = function() {
            // Fallback to default avatar
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzIiIGN5PSIzMiIgcj0iMzIiIGZpbGw9IiMyNTYzZWIiLz4KPHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4PSIxNiIgeT0iMTYiPgo8cGF0aCBkPSJNMTIgMTJDMTQuNDg1MyAxMiAxNi41IDkuOTg1MjggMTYuNSA3LjVDMTYuNSA1LjAxNDcyIDE0LjQ4NTMgMyAxMiAzQzkuNTE0NzIgMyA3LjUgNS4wMTQ3MiA3LjUgNy41QzcuNSA5Ljk4NTI4IDkuNTE0NzIgMTIgMTIgMTJaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMjEgMjFWMTkuNUMyMSAxNi43MzEgMTguNzcxNCAxNC41IDE2IDE0LjVIOEMzLjU4NTc5IDE0LjUgMC4yNTkzNzUgMTcuNzQxOCAwLjAzODE1MSAyMC45NDIyVjIxSDIxWiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+Cjwvc3ZnPgo=';
        };
    });
}

// Initialize profile pictures on page load
document.addEventListener('DOMContentLoaded', function() {
    const username = document.querySelector('.user-name')?.textContent;
    if (username) {
        loadProfilePicture(username.toLowerCase().replace(/\s+/g, ''));
    }
});

// Responsive table handling
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

// Search functionality (for future use)
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            // Implement search logic here
        }, 300));
    }
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.dashboardUtils = {
    showNotification,
    completeSession,
    formatTimestamp,
    formatMeasurement,
    createChart,
    closeMobileNav
};
