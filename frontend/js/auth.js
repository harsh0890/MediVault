// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginFormElement = document.getElementById('loginFormElement');
const registerFormElement = document.getElementById('registerFormElement');
const showLoginLink = document.getElementById('showLogin');
const showRegisterLink = document.getElementById('showRegister');
const messageDiv = document.getElementById('message');
const emergencyBtn = document.getElementById('emergencyBtn');
const emergencyPanel = document.getElementById('emergencyPanel');

// Emergency button toggle
emergencyBtn.addEventListener('click', () => {
    emergencyBtn.classList.toggle('expanded');
    emergencyPanel.classList.toggle('show');
});

// Switch between login and register forms
showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.remove('active');
    registerForm.classList.add('active');
    clearMessage();
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.classList.remove('active');
    loginForm.classList.add('active');
    clearMessage();
});

// Login form submission
loginFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessage();
    
    const user_id = document.getElementById('loginUserId').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!user_id || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage('Login successful! Redirecting...', 'success');
            // Redirect to dashboard after 1 second
            setTimeout(() => {
                window.location.href = data.redirect_url || '/dashboard';
            }, 1000);
        } else {
            showMessage(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    }
});

// Register form submission
registerFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessage();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    
    if (!name || !email || !password || !confirmPassword) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showMessage('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error');
        return;
    }
    
    // TODO: Will connect to backend API when authentication is implemented
    // const response = await fetch('/api/auth/register', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ name, email, password })
    // });
    
    showMessage('Registration functionality will be implemented in next step', 'success');
});

// Helper functions
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type} show`;
    
    setTimeout(() => {
        clearMessage();
    }, 5000);
}

function clearMessage() {
    messageDiv.classList.remove('show');
    messageDiv.textContent = '';
}
