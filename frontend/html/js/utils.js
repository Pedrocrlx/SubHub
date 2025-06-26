
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
