// ==========================================
// 1. TRANSACTION VERIFICATION LOGIC
// ==========================================

// Simulated Database
const transactions = [
    {
        id: 'TXN-8842-XJ9',
        data: 'ENCRYPTED::ae91-5541-b221::AMOUNT::5400',
        receivedHash: '0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
        actualDataHash: '0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069' 
    },
    {
        id: 'TXN-9911-BAD',
        data: 'ENCRYPTED::ff00-1122-3344::AMOUNT::99000',
        receivedHash: '0x3a20914e50882d645391c7d23531b25028018240590e092109852277119e7561',
        actualDataHash: '0x9999999999999999999999999999999999999999999999999999999999999999' // Mismatch
    },
    {
        id: 'TXN-3321-AZ2',
        data: 'ENCRYPTED::cc11-8899-0011::AMOUNT::1250',
        receivedHash: '0x1c8b3f0b2d184025816922649080512809182309128309128309128309128301',
        actualDataHash: '0x1c8b3f0b2d184025816922649080512809182309128309128309128309128301' 
    }
];

let currentTxIndex = null;

function openVerification(index) {
    currentTxIndex = index;
    const tx = transactions[index];
    
    // Populate Modal
    document.getElementById('modalTxnId').textContent = tx.id;
    document.getElementById('modalData').textContent = tx.data;
    document.getElementById('modalReceivedHash').textContent = tx.receivedHash;
    
    // Reset Button
    const btn = document.getElementById('verifyBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('btnLoader');
    btnText.style.display = 'block';
    loader.style.display = 'none';
    btn.disabled = false;

    document.getElementById('verifyModal').classList.add('active');
}

function processVerification() {
    if (currentTxIndex === null) return;

    const btn = document.getElementById('verifyBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('btnLoader');

    // Show Loader
    btnText.style.display = 'none';
    loader.style.display = 'block';
    btn.disabled = true;

    // Simulate Computation Delay
    setTimeout(() => {
        const tx = transactions[currentTxIndex];
        document.getElementById('verifyModal').classList.remove('active');

        if (tx.receivedHash === tx.actualDataHash) {
            // Success
            document.getElementById('successHashDisplay').textContent = tx.actualDataHash;
            document.getElementById('successModal').classList.add('active');
            // Trigger notification for success verification
            showPaymentPopup('VERIFIED', tx.id);
        } else {
            // Fail
            document.getElementById('failHashDisplay').textContent = tx.actualDataHash;
            document.getElementById('failModal').classList.add('active');
        }

    }, 1500);
}

function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.classList.remove('active');
    });
}

// Close on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        closeAllModals();
    }
}

// ==========================================
// 2. NOTIFICATION POPUP LOGIC
// ==========================================
// Note: Audio file path would need to be relative to the static folder or external
const notificationSound = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3'); 
let popupTimeoutId;

function showPaymentPopup(amount, sender) {
    const popup = document.getElementById('paymentPopup');
    const amountEl = document.getElementById('popupAmount');
    const senderEl = document.getElementById('popupSender');

    // Format the amount/message display
    amountEl.textContent = amount.startsWith('+$') || amount.startsWith('VERIFIED') ? amount : `+$${amount}`;
    senderEl.textContent = `from ${sender}`;

    // Play Sound
    try {
        notificationSound.volume = 0.5;
        notificationSound.currentTime = 0;
        // Playing audio is often restricted without prior user interaction
        notificationSound.play().catch(e => console.log("Audio play failed: ", e));
    } catch (e) {
        // Handle error gracefully
    }

    popup.classList.add('active');

    // Reset Animation
    const progress = popup.querySelector('.toast-progress');
    progress.style.transition = 'none';
    progress.style.transform = 'scaleX(0)';
    setTimeout(() => {
        progress.style.transition = 'transform 5s linear';
        progress.style.transform = 'scaleX(1)';
    }, 10);

    // Auto Hide
    clearTimeout(popupTimeoutId);
    popupTimeoutId = setTimeout(() => {
        closePopup();
    }, 5000);
}

function closePopup() {
    document.getElementById('paymentPopup').classList.remove('active');
}

// Function attached to the 'Test Received Popup' button
function simulatePayment() {
    const amount = (Math.random() * 5000 + 100).toFixed(2);
    const senders = ["Alice Corp", "Mike Ross", "Crypto Wallet", "Jessica P."];
    const randomSender = senders[Math.floor(Math.random() * senders.length)];
    
    showPaymentPopup(amount, randomSender);
}