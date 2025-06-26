// js/dashboard.js

import { endpoints } from './endpoints.js';
import { openModal, closeModal } from './utils.js';
import { updateBarChart } from './bar_chart.js';
import { updatePieChart } from './pie_chart.js';
import { updateNextPayments, getLogoForService } from './next_payments.js'; 
import { resetNewSubscriptionForm } from './new_subscription_modal.js';
import { requireAuth } from './user_authentication.js';

export async function loadSubscriptions() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("Access token not found. Redirecting to login.");
        window.location.href = "/auth/";
        return;
    }

    const subscriptionsTableBody = document.getElementById('subscriptionsTableBody');
    if (!subscriptionsTableBody) {
        console.error("Element 'subscriptionsTableBody' not found.");
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
        console.log("Subscriptions loaded:", subscriptions);

        subscriptionsTableBody.innerHTML = '';
        if (subscriptions && subscriptions.length > 0) {
            subscriptions.forEach(sub => {
                const row = document.createElement('tr');
                row.dataset.serviceName = sub.service_name;
                row.dataset.monthlyPrice = sub.monthly_price;
                row.dataset.startingDate = sub.starting_date;
                row.dataset.category = sub.category;
                row.dataset.renovationType = sub.renovation_type || 'Monthly';

                const logoUrl = getLogoForService(sub.service_name); // Get the logo URL

                row.innerHTML = `
                    <td>
                        <div style="display:flex; align-items:center;">
                            <img src="${logoUrl}" alt="${sub.service_name}" style="width:30px; height:30px; margin-right:10px; border-radius: 5px;">
                            ${sub.service_name}
                        </div>
                    </td>
                    <td>${sub.starting_date}</td>
                    <td>${(parseFloat(sub.monthly_price || 0)).toFixed(2)}€</td>
                    <td>${sub.category}</td>
                    <td>
                        <button class="action-btn edit-btn" aria-label="Edit Subscription"><i class='bx bxs-pencil'></i></button>
                        <button class="action-btn delete-btn" aria-label="Delete Subscription"><i class='bx bxs-trash'></i></button>
                    </td>
                `;
                subscriptionsTableBody.appendChild(row);
            });
        } else {
            subscriptionsTableBody.innerHTML = '<tr><td colspan="5">No subscriptions found.</td></tr>';
        }

        updateDashboardCharts(subscriptions);

    } catch (error) {
        console.error('Error loading subscriptions:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error!',
            text: `Error loading subscriptions: ${error.message}. Please try again.`,
            confirmButtonText: 'OK'
        });
    }
}

// Function to update all dashboard components
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

    // --- Logic for the "Add Subscription" button ---
    const addSubscriptionBtn = document.getElementById('addSubscriptionBtn');
    if (addSubscriptionBtn) {
        addSubscriptionBtn.addEventListener('click', () => {
            resetNewSubscriptionForm();
            openModal('newSubscriptionModal');
        });
    }

    // --- Logic to close modals ---
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

    // Call loadSubscriptions to load initial data
    await loadSubscriptions();

    // --- Event delegation for Edit/Delete buttons in the table ---
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
                renovation_type: row.dataset.renovationType
            };
            if (typeof window.openEditSubscriptionModal === 'function') {
                window.openEditSubscriptionModal(subscriptionData);
            } else {
                console.error("openEditSubscriptionModal is not defined or not a function.");
            }
        } else if (e.target.closest('.delete-btn')) {

            const result = await Swal.fire({
                title: 'Are you sure?',
                text: `Do you really want to delete the subscription "${serviceName}"?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Yes, delete it!',
                cancelButtonText: 'Cancel',
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
                            title: 'Authentication Error',
                            text: 'Access token not found. Please log in again.',
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
                        title: 'Deleted!',
                        text: `Subscription "${serviceName}" deleted successfully.`,
                        icon: 'success',
                        confirmButtonText: 'OK',
                        customClass: { confirmButton: 'button-primary' },
                        buttonsStyling: false
                    });
                    await loadSubscriptions();
                } catch (error) {
                    console.error('Error deleting subscription:', error);
                    Swal.fire({
                        title: 'Error!',
                        text: `Error deleting subscription: ${error.message}. Please try again.`,
                        icon: 'error',
                        confirmButtonText: 'OK',
                        customClass: { confirmButton: 'button-primary' },
                        buttonsStyling: false
                    });
                }
            } else {
                console.log('Deletion cancelled by the user.');
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