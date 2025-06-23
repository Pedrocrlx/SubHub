import { endpoints } from './endpoints.js';
import { closeModal, openModal, loadSubscriptions } from '/js/dashboard.js'; // Importa as funções

document.addEventListener('DOMContentLoaded', () => {
    const editSubscriptionModal = document.getElementById('editSubscriptionModal');
    const editSubscriptionForm = document.getElementById('editSubscriptionForm');
    const editSubscriptionIdInput = document.getElementById('editSubscriptionId');

    const editServiceSelect = document.getElementById('editService');
    const editCategorySelect = document.getElementById('editCategory');
    const editStatusSelect = document.getElementById('editStatus');
    const editRenovationDayInput = document.getElementById('editRenovationDay');
    const editRenovationTypeSelect = document.getElementById('editRenovationType');
    const editRateInput = document.getElementById('editRate');
    const unsubscribeNote = editSubscriptionModal.querySelector('.unsubscribe-note');

    async function loadDropdownOptions(selectElement, apiUrl, valueKey, textKey, selectedValue = null) {
        try {
            // Adicionando o token para chamadas autenticadas
            const token = localStorage.getItem("access_token");
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await fetch(apiUrl, { headers });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            selectElement.innerHTML = '';
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item[valueKey];
                option.textContent = item[textKey];
                if (selectedValue !== null && String(item[valueKey]) === String(selectedValue)) {
                    option.selected = true;
                }
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error(`Error loading ${selectElement.id} options from ${apiUrl}:`, error);
        }
    }

    // Função global para abrir o modal de edição e preencher os campos
    window.openEditSubscriptionModal = async (subscriptionData) => {
        editSubscriptionIdInput.value = subscriptionData.id;
        editRenovationDayInput.value = subscriptionData.renovationDay || '';
        editRateInput.value = subscriptionData.rate || '';

        // Carregar e selecionar os dropdowns. Adapte endpoints e chaves conforme sua API.
        await loadDropdownOptions(editServiceSelect, endpoints.analytics.categories, 'name', 'name', subscriptionData.service);
        await loadDropdownOptions(editCategorySelect, endpoints.analytics.categories, 'name', 'name', subscriptionData.category);
        await loadDropdownOptions(editStatusSelect, 'http://localhost:8000/api/statuses', 'id', 'name', subscriptionData.status);
        await loadDropdownOptions(editRenovationTypeSelect, 'http://localhost:8000/api/renovation_types', 'id', 'type', subscriptionData.renovationType);

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

            const subscriptionId = editSubscriptionIdInput.value;
            const formData = new FormData(editSubscriptionForm);
            const data = Object.fromEntries(formData.entries());

            data.renovation = `${data.renovationDay} / ${data.renovationType}`;
            delete data.renovationDay;
            delete data.renovationType;

            data.price = parseFloat(data.rate);
            delete data.rate;

            console.log('Updating subscription data:', data);

            try {
                // Sua endpoint de edição deve aceitar o ID na URL ou no corpo
                // Se a sua API espera o nome do serviço para PUT/PATCH, ajuste aqui
                // Assumindo que a rota de update é a mesma de 'add' mas com o ID no final para PUT
                const response = await fetch(`${endpoints.subscriptions.add}/${subscriptionId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                }

                const result = await response.json();
                console.log('Subscription Updated:', result);
                alert('Subscrição atualizada com sucesso!');
                closeModal('editSubscriptionModal');
                await loadSubscriptions(); // Recarregar a lista de subscrições
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

            const subscriptionId = editSubscriptionIdInput.value;
            const serviceName = editServiceSelect.value; // Pega o nome do serviço selecionado

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
                    await loadSubscriptions(); // Recarregar a lista de subscrições
                } catch (error) {
                    console.error('Error deleting subscription:', error);
                    alert(`Erro ao cancelar subscrição: ${error.message}. Por favor, tente novamente.`);
                }
            }
        });
    }
});