// js/new_subscription_modal.js

import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { loadSubscriptions } from './dashboard.js';

// Global variables within this module for access by the reset function
let newServiceSelect;
let newCategorySelect;
let newRenovationTypeSelect; // This will be restricted
let newStartingDateInput;
let newFlatpickrInstance;
let newSubscriptionForm;

// Fixed data for dropdowns (decided on the frontend)
const services = [
    { value: 'Netflix', text: 'Netflix' },
    { value: 'Spotify', text: 'Spotify' },
    { value: 'Amazon Prime', text: 'Amazon Prime' },
    { value: 'YouTube Premium', text: 'YouTube Premium' },
    { value: 'Discord Nitro', text: 'Discord Nitro' },
    { value: 'Microsoft 365', text: 'Microsoft 365' },
    { value: 'Adobe Creative Cloud', text: 'Adobe Creative Cloud' },
    { value: 'Disney+', text: 'Disney+' },
    { value: 'HBO Max', text: 'HBO Max' },
    { value: 'Apple Music', text: 'Apple Music' },
    { value: 'Google Drive', text: 'Google Drive' },
    { value: 'GitHub Copilot', text: 'GitHub Copilot' },
    { value: 'ChatGPT Plus', text: 'ChatGPT Plus' },
    { value: 'Another Service', text: 'Another Service' }
];

const categories = [
    { value: 'Entertainment', text: 'Entertainment' },
    { value: 'Music', text: 'Music' },
    { value: 'Productivity', text: 'Productivity' },
    { value: 'Gaming', text: 'Gaming' },
    { value: 'Cloud Storage', text: 'Cloud Storage' },
    { value: 'Development', text: 'Development' },
    { value: 'Education', text: 'Education' },
    { value: 'Health', text: 'Health' },
    { value: 'Other', text: 'Other' }
];

// --- ONLY MONTHLY RENOVATION TYPE ALLOWED ---
const renovationTypes = [
    { value: 'Monthly', text: 'Monthly' }
];

function populateDropdown(selectElement, dataArray, placeholderText, selectedValue = null) {
    selectElement.innerHTML = `<option value="">${placeholderText}</option>`;
    dataArray.forEach(item => {
        const option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.text;
        if (selectedValue !== null && String(item.value) === String(selectedValue)) {
            option.selected = true;
        }
        selectElement.appendChild(option);
    });
}

// Exported function to reset and initialize form fields
export function resetNewSubscriptionForm() {
    if (newSubscriptionForm) {
        newSubscriptionForm.reset(); // Resets all HTML form fields
    }
    // Repopulate dropdowns with default options
    populateDropdown(newServiceSelect, services, 'Select Service Name');
    populateDropdown(newCategorySelect, categories, 'Select Category');
    
    // Always populate Renovation Type with 'Monthly' and ensure it's selected and disabled
    populateDropdown(newRenovationTypeSelect, renovationTypes, 'Select Type', 'Monthly');
    newRenovationTypeSelect.value = 'Monthly'; // Explicitly set
    newRenovationTypeSelect.disabled = true; // Disable the dropdown

    // Clear the selected date in Flatpickr
    if (newFlatpickrInstance) {
        newFlatpickrInstance.clear();
    }
    console.log("New Subscription Form reset.");
}


document.addEventListener('DOMContentLoaded', () => {
    const newSubscriptionModal = document.getElementById('newSubscriptionModal');
    newSubscriptionForm = document.getElementById('newSubscriptionForm');

    newServiceSelect = document.getElementById('newService');
    newCategorySelect = document.getElementById('newCategory');
    newRenovationTypeSelect = document.getElementById('newRenovationType'); // Assign to global variable
    newStartingDateInput = document.getElementById('newStartingDate');

    // Initial population for newRenovationTypeSelect when the page loads
    // This is important because resetNewSubscriptionForm might not be called on initial load
    populateDropdown(newRenovationTypeSelect, renovationTypes, 'Select Type', 'Monthly');
    newRenovationTypeSelect.value = 'Monthly';
    newRenovationTypeSelect.disabled = true;


    if (newStartingDateInput) {
        newFlatpickrInstance = flatpickr(newStartingDateInput, {
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "F j, Y",
            appendTo: newSubscriptionModal,
            onOpen: (selectedDates, dateStr, instance) => {
                // newStartingDateInput.style.pointerEvents = 'auto'; // Removed: Can cause issues
            },
            onClose: (selectedDates, dateStr, instance) => {
                // newStartingDateInput.style.pointerEvents = 'none'; // Removed: Can cause issues
            }
        });
    }

    if (newSubscriptionForm) {
        newSubscriptionForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const token = localStorage.getItem("access_token");
            if (!token) {
                Swal.fire({
                    icon: 'error',
                    title: 'Authentication Error',
                    text: 'Access token not found. Please log in again.',
                    confirmButtonText: 'OK',
                    customClass: { confirmButton: 'button-primary' },
                    buttonsStyling: false
                }).then(() => {
                    window.location.href = "/auth/";
                });
                return;
            }

            const formData = new FormData(newSubscriptionForm);
            const data = Object.fromEntries(formData.entries());

            const newSubscriptionData = {
                service_name: data.service_name,
                monthly_price: parseFloat(data.monthly_price),
                category: data.category,
                starting_date: data.starting_date,
                renovation_type: 'Monthly' // IMPLICITLY SET TO MONTHLY
            };

            console.log('Sending new subscription data:', newSubscriptionData);

            try {
                const response = await fetch(endpoints.subscriptions.add, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(newSubscriptionData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                }

                const result = await response.json();
                console.log('New Subscription Added:', result);

                Swal.fire({
                    title: 'Success!',
                    text: 'Subscription added successfully!',
                    icon: 'success',
                    confirmButtonText: 'OK',
                    customClass: { confirmButton: 'button-primary' },
                    buttonsStyling: false
                }).then(() => {
                    closeModal('newSubscriptionModal');
                    loadSubscriptions(); // Reload table and dashboards
                });

            } catch (error) {
                console.error('Error adding new subscription:', error);
                Swal.fire({
                    title: 'Error!',
                    text: `Error please make sure to fill all the fields, and try again later.`,
                    icon: 'error',
                    confirmButtonText: 'OK',
                    customClass: { confirmButton: 'button-primary' },
                    buttonsStyling: false
                });
            }
        });
    }

    const cancelBtn = document.getElementById('cancel-btn-modal');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            closeModal('newSubscriptionModal');
        });
    }
});