import { endpoints } from './endpoints.js'; // Importa suas endpoints
import { getToken } from './user_authentication.js';


// Funções para abrir/fechar modais, exportadas para uso em outros módulos se necessário
export function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

export function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        // Opcional: resetar o formulário da modal ao fechar
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

export async function loadSubscriptions() {
    const token = getToken();
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
        console.log("Subscrições:", subscriptions);

        subscriptionsTableBody.innerHTML = '';
        if (subscriptions && subscriptions.length > 0) {
            subscriptions.forEach(sub => {
                const row = document.createElement('tr');
                row.dataset.id = sub._id || sub.id;
                row.dataset.service = sub.service || sub.name;
                row.dataset.category = sub.category || 'N/A';
                row.dataset.status = sub.status || 'Active';
                row.dataset.renovationDay = sub.renovation_day || 'N/A';
                row.dataset.renovationType = sub.renovation_type || 'N/A';
                row.dataset.price = sub.price || sub.rate || 0;

                const renovationDisplayDate = sub.renovation_date ? new Date(sub.renovation_date).toLocaleDateString('pt-PT') : 'N/A';


                row.innerHTML = `
                        <td>${sub.service || sub.name}</td>
                        <td>${renovationDisplayDate}</td>
                        <td>${(parseFloat(sub.price || sub.rate || 0)).toFixed(2)}€</td>
                        <td>${sub.status || 'Active'}</td>
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

    } catch (error) {
        console.error('Erro ao carregar subscrições:', error);
        alert('Erro ao carregar subscrições. Por favor, tente novamente.');
    }
};

document.addEventListener("DOMContentLoaded", async () => { // Adicionado 'async' aqui
   const token = getToken();

    // Obter info do utilizador (nome/email)
    const userName = localStorage.getItem("user_name");
    const userEmail = localStorage.getItem("user_email");

    // Atualizar DOM com o nome
    const userDisplay = document.getElementById("user-info");
    if (userDisplay && userName) {
        userDisplay.textContent = `Welcome, ${userName}!`;
    }

    // --- Lógica para o botão "Add Subscription" ---
    const addSubscriptionBtn = document.getElementById('addSubscriptionBtn');
    if (addSubscriptionBtn) {
        addSubscriptionBtn.addEventListener('click', () => {
            openModal('newSubscriptionModal');
        });
    }

    // --- Lógica para fechar as modais clicando no 'X' ou fora delas ---
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


    const subscriptionsTableBody = document.getElementById('subscriptionsTableBody');

    await loadSubscriptions();

    subscriptionsTableBody.addEventListener('click', async (e) => {
        const row = e.target.closest('tr');
        if (!row) return;

        const subscriptionId = row.dataset.id;
        const serviceName = row.dataset.service;

        if (e.target.closest('.edit-btn')) {
            const subscriptionData = {
                id: subscriptionId,
                service: row.dataset.service,
                category: row.dataset.category,
                status: row.dataset.status,
                renovationDay: row.dataset.renovationDay,
                renovationType: row.dataset.renovationType,
                rate: parseFloat(row.dataset.price)
            };
            if (window.openEditSubscriptionModal) {
                window.openEditSubscriptionModal(subscriptionData);
            } else {
                console.error("openEditSubscriptionModal not found!");
            }
        } else if (e.target.closest('.delete-btn')) {
            if (confirm(`Tem certeza que deseja deletar a subscrição ${serviceName}?`)) {
                try {
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

                    alert(`Subscrição ${serviceName} deletada com sucesso!`);
                    await loadSubscriptions();
                } catch (error) {
                    console.error('Error deleting subscription:', error);
                    alert(`Erro ao deletar subscrição: ${error.message}. Por favor, tente novamente.`);
                }
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
    const totalSpendingOverview = document.querySelector('.spending-value');
    if (totalSpendingOverview) {
        totalSpendingOverview.textContent = '0.00€';
    }
});