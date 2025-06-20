
document.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');
    const closeBtn = document.querySelector('.close-sidebar-btn');
    const main = document.querySelector('main');

    function showSidebar() {
        sidebar.classList.add('active');
        main.classList.add('sidebar-visible');

        const overlay = document.createElement('div');
        overlay.classList.add('sidebar-overlay');
        document.body.appendChild(overlay);
        overlay.addEventListener('click', hideSidebar);
    }

    function hideSidebar() {
        sidebar.classList.remove('active');
        main.classList.remove('sidebar-visible');

        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) overlay.remove();
    }

    hamburgerBtn.addEventListener('click', showSidebar);
    closeBtn.addEventListener('click', hideSidebar);
});
