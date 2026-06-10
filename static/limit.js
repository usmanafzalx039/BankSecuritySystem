// Formatting function for currency
const formatCurrency = (num) => {
    // Check if num is defined and not null before calling replace
    if (num === undefined || num === null) return '0';
    // Use Intl.NumberFormat to add thousands separators
    return new Intl.NumberFormat('en-US').format(num);
};

// Configuration for limits
const limits = [
    { rangeId: 'range-online', displayId: 'val-online', usageId: 'display-online' },
    { rangeId: 'range-atm', displayId: 'val-atm', usageId: 'display-atm' },
    { rangeId: 'range-intl', displayId: 'val-intl', usageId: 'display-intl' },
    { rangeId: 'range-pos', displayId: 'val-pos', usageId: 'display-pos' }
];

// Attach listeners for range sliders
limits.forEach(limit => {
    const rangeInput = document.getElementById(limit.rangeId);
    const valueDisplay = document.getElementById(limit.displayId);
    const usageDisplay = document.getElementById(limit.usageId);

    if (rangeInput && valueDisplay && usageDisplay) {
        // Initialize displays with formatted values
        valueDisplay.textContent = formatCurrency(rangeInput.value);
        usageDisplay.textContent = formatCurrency(rangeInput.value);

        rangeInput.addEventListener('input', function() {
            const formattedVal = formatCurrency(this.value);
            valueDisplay.textContent = formattedVal;
            usageDisplay.textContent = formattedVal; // Update the denominator in "Used / Limit"
        });
    }
});

// Sidebar Navigation Animation logic
document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', function() {
        const targetText = this.textContent.trim();
        if(!this.classList.contains('active')) {
            // In a real Flask app, you'd use window.location.href = `/route`
            console.log(`Navigating to ${targetText}`);
        }
    });
});

// Save Button Logic
document.querySelector('.save-btn').addEventListener('click', function() {
    const btn = this;
    const originalText = btn.textContent;
    
    // Change text to "Updated"
    btn.textContent = "Updated";
    
    // Change to a BRIGHTER neon purple to indicate success/action
    btn.style.background = "linear-gradient(135deg, rgba(192, 132, 252, 0.9), rgba(168, 85, 247, 0.9))";
    btn.style.boxShadow = "0 0 25px rgba(192, 132, 252, 0.6)";
    
    setTimeout(() => {
        btn.textContent = originalText;
        // Revert styles back to the CSS defaults
        btn.style.background = ""; 
        btn.style.boxShadow = "";
    }, 2000);
});