// 1. Get References to HTML Elements
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('loginBtn');
const popup = document.getElementById('popup');
const popupIcon = document.getElementById('popupIcon');
const popupMessage = document.getElementById('popupMessage');
const overlay = document.getElementById('overlay');
const loginForm = document.getElementById('loginForm');

// 2. Input Validation (Restrict to Numbers Only)
// This runs every time you type a character
usernameInput.addEventListener('input', function(e) {
    this.value = this.value.replace(/[^0-9]/g, '');
});

passwordInput.addEventListener('input', function(e) {
    this.value = this.value.replace(/[^0-9]/g, '');
});

// 3. Handle Login Button Click
loginBtn.addEventListener('click', function(e) {
    // Prevent the default button click for a moment so we can check inputs
    e.preventDefault(); 

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    // -- Client-Side Checks --
    
    // Check if empty
    if (username === '' || password === '') {
        showPopup('error', '⚠️', 'Please fill all fields!');
        return;
    }

    // Check Account Number length
    if (username.length < 6) {
        showPopup('error', '⚠️', 'Account number must be at least 6 digits!');
        return;
    }

    // Check PIN length
    if (password.length !== 4) {
        showPopup('error', '⚠️', 'PIN must be exactly 4 digits!');
        return;
    }

    // -- Success! Submit to Python --
    // If we reach here, inputs are valid format. 
    // We submit the form so Python can check if the password is correct.
    loginForm.submit(); 
});

// 4. Popup Logic
function showPopup(type, icon, message) {
    popup.className = 'popup ' + type;
    popupIcon.textContent = icon;
    popupMessage.innerHTML = message;
    
    overlay.classList.add('show');
    popup.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        overlay.classList.remove('show');
        popup.classList.remove('show');
    }, 3000);
}

// 5. SERVER MESSAGE CHECKER (The "Bridge" Fix)
// This runs automatically when the page reloads after Python sends data back.
document.addEventListener('DOMContentLoaded', function() {
    
    // Look for the hidden div we added in HTML
    const messageContainer = document.getElementById('server-message');
    
    if (messageContainer) {
        // Read the message Python put inside the data-message attribute
        const messageText = messageContainer.getAttribute('data-message');
        
        // If there is a message, trigger the popup immediately
        if (messageText && messageText !== "") {
            showPopup('error', '⚠️', messageText);
        }
    }
});