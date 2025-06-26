// edit-subscription.js

import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { loadSubscriptions } from './dashboard.js';

document.addEventListener('DOMContentLoaded', () => {
    const editSubscriptionModal = document.getElementById('editSubscriptionModal');
    const editSubscriptionForm = document.getElementById('editSubscriptionForm');
    const editSubscriptionIdInput = document.getElementById('editSubscriptionId');

    const editServiceSelect = document.getElementById('editService');
    const editCategorySelect = document.getElementById('editCategory');
    const editRenovationTypeSelect = document.getElementById('editRenovationType'); 
    const editStartingDateInput = document.getElementById('editStartingDate');
    const editMonthlyPriceInput = document.getElementById('editMonthlyPrice');
    const unsubscribeNote = editSubscriptionModal.querySelector('.unsubscribe-note');

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

    let editFlatpickrInstance;
    if (editStartingDateInput) {
        editFlatpickrInstance = flatpickr(editStartingDateInput, {
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "F j, Y",
            appendTo: editSubscriptionModal,
            onOpen: (selectedDates, dateStr, instance) => {
                editStartingDateInput.style.pointerEvents = 'auto';
            },
            onClose: (selectedDates, dateStr, instance) => {
            }
        });
    }

    window.openEditSubscriptionModal = async (subscriptionData) => {
        editSubscriptionIdInput.value = subscriptionData.service_name;
        editMonthlyPriceInput.value = subscriptionData.monthly_price || '';

        populateDropdown(editServiceSelect, services, 'Select Service Name', subscriptionData.service_name);
        populateDropdown(editCategorySelect, categories, 'Select Category', subscriptionData.category);
        
        populateDropdown(editRenovationTypeSelect, renovationTypes, 'Select Type', 'Monthly');
        editRenovationTypeSelect.value = 'Monthly'; 
        editRenovationTypeSelect.disabled = true;

        if (editFlatpickrInstance) {
            editFlatpickrInstance.setDate(subscriptionData.starting_date, true);
        }

        openModal('editSubscriptionModal');
    };


    if (editSubscriptionForm) {
        editSubscriptionForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const token = localStorage.getItem("access_token");
            if (!token) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Not Authenticated',
                    text: 'You are not authenticated. Please log in again.',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = "/auth/";
                });
                return;
            }

            const currentServiceName = editSubscriptionIdInput.value;
            const formData = new FormData(editSubscriptionForm);
            const data = Object.fromEntries(formData.entries());

            const updatedSubscriptionData = {
                service_name: data.service_name,
                monthly_price: parseFloat(data.monthly_price),
                category: data.category,
                starting_date: data.starting_date,
                renovation_type: 'Monthly'
            };

            console.log('Updating subscription data:', updatedSubscriptionData);

            try {
                const response = await fetch(endpoints.subscriptions.update(currentServiceName), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(updatedSubscriptionData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                }

                const result = await response.json();
                console.log('Subscription Updated:', result);
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Subscription updated successfully!',
                    confirmButtonText: 'OK'
                });
                closeModal('editSubscriptionModal');
                await loadSubscriptions();
            } catch (error) {
                console.error('Error updating subscription:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: `Error updating subscription: ${error.message}. Please try again.`,
                    confirmButtonText: 'OK'
                });
            }
        });
    }

    if (unsubscribeNote) {
        unsubscribeNote.addEventListener('click', async () => {
            const token = localStorage.getItem("access_token");
            if (!token) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Not Authenticated',
                    text: 'You are not authenticated. Please log in again.',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = "/auth/";
                });
                return;
            }

            const serviceName = editSubscriptionIdInput.value;

            Swal.fire({
                title: 'Are you sure?',
                text: `Do you really want to cancel the subscription ${serviceName}?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, cancel it!',
                cancelButtonText: 'No'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const response = await fetch(endpoints.subscriptions.delete(serviceName), {
                            method: 'DELETE',
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });

                        if (!response.ok) {
                            const errorData = await response.json();
                            throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                        }

                        console.log('Subscription Deleted:', serviceName);
                        Swal.fire(
                            'Cancelled!',
                            'Your subscription has been cancelled successfully.',
                            'success'
                        );
                        closeModal('editSubscriptionModal');
                        await loadSubscriptions();
                    } catch (error) {
                        console.error('Error deleting subscription:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error!',
                            text: `Error cancelling subscription: ${error.message}. Please try again.`,
                            confirmButtonText: 'OK'
                        });
                    }
                }
            });
        });
    }
});