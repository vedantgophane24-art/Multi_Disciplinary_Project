// This file is loaded on every page.
// You can add interactive features here.

console.log("Smart Recycler JS Loaded.");

// --- Main DOMContentLoaded Listener ---
// This one block of code runs all our page setup logic
document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Logic for Dynamic Donation Form ---
    const donationTypeSelect = document.getElementById('donation_type_select');
    const clothesFields = document.getElementById('clothes-fields');
    const moneyFields = document.getElementById('money-fields');

    // This function shows/hides the correct fields
    function toggleDonationFields() {
        if (!donationTypeSelect || !clothesFields || !moneyFields) {
            // Failsafe: if we're not on the donate page, do nothing
            return; 
        }

        const selectedType = donationTypeSelect.value;

        if (selectedType === 'Money') {
            // Show money fields, hide clothes fields
            moneyFields.style.display = 'block';
            clothesFields.style.display = 'none';
        } else {
            // Show clothes fields (which now includes image)
            moneyFields.style.display = 'none';
            clothesFields.style.display = 'block';
        }
    }

    // Add a 'listener' to the dropdown.
    // When it changes, run our function.
    if (donationTypeSelect) {
        donationTypeSelect.addEventListener('change', toggleDonationFields);
    }

    // Run the function once on page load to set the correct initial state
    toggleDonationFields();


    // --- 2. Logic for Stepper Buttons ---
    const minusBtn = document.getElementById('stepper-minus');
    const plusBtn = document.getElementById('stepper-plus');
    const weightInput = document.getElementById('weight_input');

    if (minusBtn && plusBtn && weightInput) {
        
        minusBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Stop form submission
            let currentValue = parseFloat(weightInput.value) || 0;
            if (currentValue >= 0.5) { // Min step is 0.5
                weightInput.value = (currentValue - 0.5).toFixed(1);
            } else {
                weightInput.value = "0.0";
            }
        });

        plusBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Stop form submission
            let currentValue = parseFloat(weightInput.value) || 0;
            weightInput.value = (currentValue + 0.5).toFixed(1);
        });
    }

});