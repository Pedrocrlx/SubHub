// js/new_subscription_modal.js

import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { loadSubscriptions } from './dashboard.js';

// Variáveis globais dentro deste módulo para acesso pela função de reset
let newServiceSelect;
let newCategorySelect;
let newRenovationTypeSelect;
let newStartingDateInput;
let newFlatpickrInstance;
let newSubscriptionForm;

// Dados fixos para os dropdowns (decididos no frontend)
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

// NOVO: Função exportada para resetar e inicializar os campos do formulário
export function resetNewSubscriptionForm() {
    if (newSubscriptionForm) {
        newSubscriptionForm.reset(); // Reseta todos os campos do formulário HTML
    }
    // Repopula os dropdowns com as opções padrão
    populateDropdown(newServiceSelect, services, 'Select Service Name');
    populateDropdown(newCategorySelect, categories, 'Select Category');
    populateDropdown(newRenovationTypeSelect, renovationTypes, 'Select Type');
    // Limpa a data selecionada no Flatpickr
    if (newFlatpickrInstance) {
        newFlatpickrInstance.clear();
    }
    console.log("Formulário de Nova Subscrição resetado.");
}


document.addEventListener('DOMContentLoaded', () => {
    const newSubscriptionModal = document.getElementById('newSubscriptionModal');
    newSubscriptionForm = document.getElementById('newSubscriptionForm'); // Atribui à variável global

    newServiceSelect = document.getElementById('newService'); // Atribui às variáveis globais
    newCategorySelect = document.getElementById('newCategory');
    newRenovationTypeSelect = document.getElementById('newRenovationType');
    newStartingDateInput = document.getElementById('newStartingDate');

    if (newStartingDateInput) {
        newFlatpickrInstance = flatpickr(newStartingDateInput, {
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "F j, Y",
            appendTo: newSubscriptionModal, // Anexa ao modal
            // Remover onOpen e onClose se não precisar de manipulação de estilo
            onOpen: (selectedDates, dateStr, instance) => {
                // newStartingDateInput.style.pointerEvents = 'auto'; // Removido: Pode causar problemas
            },
            onClose: (selectedDates, dateStr, instance) => {
                // newStartingDateInput.style.pointerEvents = 'none'; // Removido: Pode causar problemas
            }
        });
    }

    if (newSubscriptionForm) {
        newSubscriptionForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const token = localStorage.getItem("access_token");
            if (!token) {
                // SUBSTITUÍDO: alert("Você não está autenticado.")
                Swal.fire({
                    icon: 'error',
                    title: 'Erro de Autenticação',
                    text: 'Token de acesso não encontrado. Por favor, faça login novamente.',
                    confirmButtonText: 'OK',
                    customClass: { confirmButton: 'button-primary' },
                    buttonsStyling: false
                }).then(() => {
                    window.location.href = "/auth/"; // Redireciona após o usuário clicar OK
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
                renovation_type: data.renovation_type
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
                    const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido' })); // Captura erro se JSON falhar
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                }

                const result = await response.json();
                console.log('New Subscription Added:', result);

                // SUBSTITUÍDO: alert('Subscrição adicionada com sucesso!')
                Swal.fire({
                    title: 'Sucesso!',
                    text: 'Subscrição adicionada com sucesso!',
                    icon: 'success',
                    confirmButtonText: 'OK',
                    customClass: { confirmButton: 'button-primary' },
                    buttonsStyling: false
                }).then(() => {
                    closeModal('newSubscriptionModal');
                    loadSubscriptions(); // Recarrega a tabela e dashboards
                });

            } catch (error) {
                console.error('Error adding new subscription:', error);
                // SUBSTITUÍDO: alert(`Erro ao adicionar subscrição: ${error.message}. Por favor, tente novamente.`)
                Swal.fire({
                    title: 'Error!',
                    text: `Error please make sure to fill all the filds, and try again later.`,
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