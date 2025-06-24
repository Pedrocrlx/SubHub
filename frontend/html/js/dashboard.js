
import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { updateBarChart } from './bar_chart.js';
import { updatePieChart } from './pie_chart.js';
import { updateNextPayments } from './next_payments.js';
import { resetNewSubscriptionForm } from './new_subscription_modal.js'; // NOVO: Importa a função de reset
import { requireAuth } from './user_authentication.js';

// Exporta loadSubscriptions para que outros módulos possam usá-la
export async function loadSubscriptions() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("Token de acesso não encontrado. Redirecionando para login.");
        window.location.href = "/auth/";
        return;
    }

    const subscriptionsTableBody = document.getElementById('subscriptionsTableBody');
    if (!subscriptionsTableBody) {
        console.error("Elemento 'subscriptionsTableBody' não encontrado.");
        return;
    }

    try {
        const response = await fetch(endpoints.subscriptions.list, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = "/auth/";
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const subscriptions = await response.json();
        console.log("Subscrições carregadas:", subscriptions);

        subscriptionsTableBody.innerHTML = '';
        if (subscriptions && subscriptions.length > 0) {
            subscriptions.forEach(sub => {
                const row = document.createElement('tr');
                row.dataset.serviceName = sub.service_name;
                row.dataset.monthlyPrice = sub.monthly_price;
                row.dataset.startingDate = sub.starting_date;
                row.dataset.category = sub.category;
                row.dataset.renovationType = sub.renovation_type || 'Monthly'; // Incluído renovation_type

                row.innerHTML = `
                    <td>${sub.service_name}</td>
                    <td>${sub.starting_date}</td>
                    <td>${(parseFloat(sub.monthly_price || 0)).toFixed(2)}€</td>
                    <td>${sub.category}</td>
                    <td>
                        <button class="action-btn edit-btn"><i class='bx bxs-pencil'></i></button>
                        <button class="action-btn delete-btn"><i class='bx bxs-trash'></i></button>
                    </td>
                `;
                subscriptionsTableBody.appendChild(row);
            });
        } else {
            subscriptionsTableBody.innerHTML = '<tr><td colspan="5">Nenhuma subscrição encontrada.</td></tr>';
        }

        updateDashboardCharts(subscriptions);

    } catch (error) {
        console.error('Erro ao carregar subscrições:', error);
        alert('Erro ao carregar subscrições. Por favor, tente novamente.');
    }
}

// Função para atualizar todos os componentes do dashboard
function updateDashboardCharts(subscriptions) {
    updateBarChart(subscriptions);
    updatePieChart(subscriptions);
    updateNextPayments(subscriptions);
}

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/auth/";
        return;
    }

    const userName = localStorage.getItem("user_name");
    const userDisplay = document.getElementById("user-info");
    if (userDisplay && userName) {
        userDisplay.textContent = `Welcome, ${userName}!`;
    }

    // --- Lógica para o botão "Add Subscription" ---
    const addSubscriptionBtn = document.getElementById('addSubscriptionBtn');
    if (addSubscriptionBtn) {
        addSubscriptionBtn.addEventListener('click', () => {
            resetNewSubscriptionForm(); // NOVO: Chama a função de reset antes de abrir
            openModal('newSubscriptionModal');
        });
    }

    // --- Lógica para fechar as modais ---
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay.id);
            }
        });
    });

    document.querySelectorAll('.close-modal-btn').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modalId = e.target.closest('.modal-overlay').id;
            closeModal(modalId);
        });
    });

    // Chama loadSubscriptions para carregar os dados iniciais
    await loadSubscriptions();

    // --- Delegação de eventos para botões de Edit/Delete na tabela ---
    const subscriptionsTableBody = document.getElementById('subscriptionsTableBody');
    subscriptionsTableBody.addEventListener('click', async (e) => {
        const row = e.target.closest('tr');
        if (!row) return;

        const serviceName = row.dataset.serviceName;

        if (e.target.closest('.edit-btn')) {
            const subscriptionData = {
                service_name: row.dataset.serviceName,
                monthly_price: parseFloat(row.dataset.monthlyPrice),
                starting_date: row.dataset.startingDate,
                category: row.dataset.category,
                renovation_type: row.dataset.renovationType // Passa o tipo de renovação
            };
            if (typeof window.openEditSubscriptionModal === 'function') {
                window.openEditSubscriptionModal(subscriptionData);
            } else {
                console.error("openEditSubscriptionModal não está definida ou não é uma função.");
            }
        } else if (e.target.closest('.delete-btn')) {

            const result = await Swal.fire({
                title: 'Tem certeza?',
                text: `Deseja realmente deletar a subscrição "${serviceName}"?`,
                icon: 'warning',
                showCancelButton: true, 
                confirmButtonText: 'Sim, deletar!',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
                customClass: {
                    confirmButton: 'button-primary danger-button', 
                    cancelButton: 'button-secondary'
                },
                buttonsStyling: false 
            });

            if (result.isConfirmed) { 
                try {
                    const token = localStorage.getItem("access_token"); 
                    if (!token) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro de Autenticação',
                            text: 'Token de acesso não encontrado. Por favor, faça login novamente.',
                            confirmButtonText: 'OK',
                            customClass: { confirmButton: 'button-primary' },
                            buttonsStyling: false
                        }).then(() => {
                            localStorage.clear();
                            window.location.href = "/auth/";
                        });
                        return;
                    }

                    const response = await fetch(endpoints.subscriptions.delete(serviceName), {
                        method: 'DELETE',
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || response.statusText}`);
                    }

                    Swal.fire({
                        title: 'Deletado!',
                        text: `Subscrição "${serviceName}" deletada com sucesso.`,
                        icon: 'success',
                        confirmButtonText: 'OK',
                        customClass: { confirmButton: 'button-primary' },
                        buttonsStyling: false
                    });
                    await loadSubscriptions(); 
                } catch (error) {
                    console.error('Error deleting subscription:', error);
                    Swal.fire({
                        title: 'Erro!',
                        text: `Erro ao deletar subscrição: ${error.message}. Por favor, tente novamente.`,
                        icon: 'error',
                        confirmButtonText: 'OK',
                        customClass: { confirmButton: 'button-primary' },
                        buttonsStyling: false
                    });
                }
            } else {
                console.log('Deleção cancelada pelo utilizador.');
            }
        }
    });

    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            fetch(endpoints.auth.logout, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
                .finally(() => {
                    localStorage.clear();
                    window.location.href = "/auth/";
                });
        });
    }
});