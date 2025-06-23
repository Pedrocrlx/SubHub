import { endpoints } from './endpoints.js';
import { closeModal, openModal, loadSubscriptions } from './dashboard.js'; // Importa as funções
import { getToken } from './user_authentication.js';

document.addEventListener('DOMContentLoaded', () => {
    const newSubscriptionModal = document.getElementById('newSubscriptionModal');
    const newSubscriptionForm = document.getElementById('newSubscriptionForm');

    const newServiceSelect = document.getElementById('newService');
    const newCategorySelect = document.getElementById('newCategory');
    const newStatusSelect = document.getElementById('newStatus');
    const newRenovationTypeSelect = document.getElementById('newRenovationType');

    async function loadDropdownOptions(selectElement, apiUrl, valueKey, textKey, selectedValue = null) {
        try {
            // Adicionando o token para chamadas autenticadas
            const token = getToken();
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await fetch(apiUrl, { headers });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            selectElement.innerHTML = `<option value="">Select ${textKey}</option>`;
            console.log(data);
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

    if (newSubscriptionModal) {
        newSubscriptionModal.addEventListener('transitionend', () => {
            if (newSubscriptionModal.classList.contains('active')) {
                // Adapte estas endpoints e chaves conforme sua API
                // Assumindo que endpoints.analytics.categories pode retornar tanto serviços quanto categorias
                // Se você tiver endpoints separadas para cada, use-as aqui.
                loadDropdownOptions(newServiceSelect, endpoints.analytics.categories, 'name', 'name'); // Ex: 'name' para ambos
                loadDropdownOptions(newCategorySelect, endpoints.analytics.categories, 'name', 'name'); // Ex: 'name' para ambos
                loadDropdownOptions(newStatusSelect, 'http://localhost:8000/api/statuses', 'id', 'name'); // Substitua pela sua endpoint real se tiver
                loadDropdownOptions(newRenovationTypeSelect, 'http://localhost:8000/api/renovation_types', 'id', 'type'); // Substitua pela sua endpoint real se tiver
            }
        });
    }

    if (newSubscriptionForm) {
        newSubscriptionForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const token = localStorage.getItem("access_token");
            if (!token) {
                alert("Você não está autenticado.");
                window.location.href = "/auth/";
                return;
            }

            const formData = new FormData(newSubscriptionForm);
            const data = Object.fromEntries(formData.entries());

            // Adapte conforme sua API espera o campo 'renovation' e 'price'
            data.renovation = `${data.renovationDay} / ${data.renovationType}`;
            delete data.renovationDay;
            delete data.renovationType;

            data.price = parseFloat(data.rate);
            delete data.rate;

            console.log('Sending new subscription data:', data);

            try {
                const response = await fetch(endpoints.subscriptions.add, {
                    method: 'POST',
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
                console.log('New Subscription Added:', result);
                alert('Subscrição adicionada com sucesso!');
                closeModal('newSubscriptionModal');
                newSubscriptionForm.reset();
                // Recarregar a lista de subscrições na tabela principal
                await loadSubscriptions(); // Chama a função exportada do dashboard.js
            } catch (error) {
                console.error('Error adding new subscription:', error);
                alert(`Erro ao adicionar subscrição: ${error.message}. Por favor, tente novamente.`);
            }
        });
    }
});