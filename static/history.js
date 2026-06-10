// Placeholder JavaScript for filter interaction
document.querySelectorAll('.filter-button').forEach(button => {
    button.addEventListener('click', function() {
        // 1. Update active state on buttons
        document.querySelectorAll('.filter-button').forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        
        const selectedFilter = this.textContent.trim().toLowerCase();
        const transactionList = document.querySelector('.transaction-list');
        const items = transactionList.querySelectorAll('.transaction-item');

        console.log('Filter applied:', selectedFilter);

        // 2. Filter the transaction list
        items.forEach(item => {
            const itemType = item.dataset.type; // Uses the data-type attribute set in HTML
            
            if (selectedFilter === 'all transactions') {
                item.style.display = 'flex';
            } else if (itemType && selectedFilter.includes(itemType)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
});