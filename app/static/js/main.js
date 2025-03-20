// Main JavaScript for PlumberLeads

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('header nav ul');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Email validation
            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                if (input.value && !validateEmail(input.value)) {
                    showError(input, 'Please enter a valid email address');
                    isValid = false;
                }
            });
            
            // Required fields validation
            const requiredInputs = form.querySelectorAll('[required]');
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    showError(input, 'This field is required');
                    isValid = false;
                }
            });
            
            // Password confirmation validation
            const passwordInput = form.querySelector('input[name="password"]');
            const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
            
            if (passwordInput && confirmPasswordInput) {
                if (passwordInput.value !== confirmPasswordInput.value) {
                    showError(confirmPasswordInput, 'Passwords do not match');
                    isValid = false;
                }
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    
    // Clear error message when input changes
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearError(this);
        });
    });
    
    // Functions for form validation
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function showError(input, message) {
        clearError(input);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        
        const parentElement = input.parentElement;
        parentElement.appendChild(errorElement);
        input.classList.add('is-invalid');
    }
    
    function clearError(input) {
        const parentElement = input.parentElement;
        const errorElement = parentElement.querySelector('.error-message');
        
        if (errorElement) {
            parentElement.removeChild(errorElement);
        }
        
        input.classList.remove('is-invalid');
    }
    
    // Flash message timeout
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentElement) {
                    message.parentElement.removeChild(message);
                }
            }, 500);
        }, 5000);
    });

    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Form validation helper
function validateForm(formElement) {
    if (!formElement.checkValidity()) {
        formElement.classList.add('was-validated');
        return false;
    }
    return true;
}

// Format currency helper
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date helper
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Confirm action helper
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// AJAX helper function
function fetchData(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };

    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error:', error);
            throw error;
        });
} 