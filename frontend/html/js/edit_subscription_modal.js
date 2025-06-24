import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { loadSubscriptions } from './dashboard.js'; // <-- MUDANÇA AQUI: Importa como export nomeado

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

    // --- Dados fixos para os dropdowns (decididos no frontend) ---
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
        { value: 'Monthly', text: 'Monthly' },
        { value: 'Annually', text: 'Annually' },
        { value: 'Weekly', text: 'Weekly' },
        { value: 'Quarterly', text: 'Quarterly' },
        { value: 'One-time', text: 'One-time' }
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
                // editStartingDateInput.style.pointerEvents = 'none';
            }
        });
    }

    window.openEditSubscriptionModal = async (subscriptionData) => {
        editSubscriptionIdInput.value = subscriptionData.service_name;
        editMonthlyPriceInput.value = subscriptionData.monthly_price || '';

        populateDropdown(editServiceSelect, services, 'Select Service Name', subscriptionData.service_name);
        populateDropdown(editCategorySelect, categories, 'Select Category', subscriptionData.category);
        populateDropdown(editRenovationTypeSelect, renovationTypes, 'Select Type', subscriptionData.renovation_type || 'Monthly');

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
                alert("Você não está autenticado.");
                window.location.href = "/auth/";
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
                alert('Subscrição atualizada com sucesso!');
                closeModal('editSubscriptionModal');
                // Chama loadSubscriptions importada
                await loadSubscriptions();
            } catch (error) {
                console.error('Error updating subscription:', error);
                alert(`Erro ao atualizar subscrição: ${error.message}. Por favor, tente novamente.`);
            }
        });
    }

    if (unsubscribeNote) {
        unsubscribeNote.addEventListener('click', async () => {
            const token = localStorage.getItem("access_token");
            if (!token) {
                alert("Você não está autenticado.");
                window.location.href = "/auth/";
                return;
            }

            const serviceName = editSubscriptionIdInput.value;

            if (confirm(`Tem certeza que deseja cancelar a subscrição ${serviceName}?`)) {
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
                    alert('Subscrição cancelada com sucesso!');
                    closeModal('editSubscriptionModal');
                    // Chama loadSubscriptions importada
                    await loadSubscriptions();
                } catch (error) {
                    console.error('Error deleting subscription:', error);
                    alert(`Erro ao cancelar subscrição: ${error.message}. Por favor, tente novamente.`);
                }
            }
        });
    }
});