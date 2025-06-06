document.addEventListener("DOMContentLoaded", function () {
    // Function to load the menu and set up event listeners
    loadMenu();
    LoadFooter();
    const SignUp = document.getElementById("SignUp");
    const SignIn = document.getElementById("SignIn");

    SignUp.addEventListener('click', () => {
        window.location.href = "http://127.0.0.1:5500/frontend/auth.html?signup=true";
    });

    SignIn.addEventListener('click', () => {
        window.location.href = "http://127.0.0.1:5500/frontend/auth.html";
    });
});

// Function to load the custom menu component
// This function defines a custom HTML element for the menu and appends it to the document
// It also adds active classes to the menu items based on the current page
function loadMenu() {
    class CustomMenu extends HTMLElement {
        connectedCallback() {
            this.innerHTML = `
                <nav>
        <div id="nav-container" class="nav-container">
            <div id="links">
                <div id="logoContainer">
                    <p>
                        <span class="logo-sub">Sub</span><span class="logo-hub">Hub</span>
                    </p>
                </div>
                <a href="index.html" id="home-button" class="label button-terciary">home</a>
                <a id="language-button" class="label button-terciary">LANGUAGE</a>
                <a href="LearnMore.html" id="learnmore-button" class="label button-terciary">learn more</a>

            </div>
            <div>
                <button id="SignIn" class="button-secondary secondary-neutral">Sign In</button>
                <button id="SignUp" class="button-primary primary-neutral">Get started</button>
            </div>
        </div>
        </nav>
            `;
        }
    }
    customElements.define('custom-menu', CustomMenu);
    const homeButton = document.getElementById('home-button');
    const LearnMoreButton = document.getElementById('learnmore-button');
    const currentPath = window.location.pathname.split('/').pop();
    if (currentPath === 'index.html') {
        homeButton.classList.add('active');
    }
    if (currentPath === 'LearnMore.html') {
        LearnMoreButton.classList.add('active');
    }
}

function getYear() {
    const year = new Date().getFullYear();
    const yearElement = document.getElementById('year');
    if (yearElement) {
        yearElement.textContent = year;
    }
    return year;
}

LoadFooter = () => {
    class CustomFooter extends HTMLElement {
        connectedCallback() {
            this.innerHTML = `
<footer>
    <div class="footer-container">
        <div class="footer-content">
            <div class="footer-logo">
                <p>
                    <span class="logo-sub">Sub</span><span class="logo-hub">Hub</span>
                </p>
            </div>
            <div class="footer-links">
                <div class="underline">
                    <a href="index.html" class="label button-terciary">FULL FAQ</a>
                </div>
                <div class="underline">
                    <a href="index.html" class="label button-terciary">HELP CENTER</a>
                </div>
            </div>
            <div class="footer-links">
                <div class="underline">
                    <a href="index.html" class="label button-terciary">Account</a><br>
                </div>
                <div class="underline">
                    <a href="index.html" class="label button-terciary">JOBS</a>
                </div>
            </div>
            <div class="footer-links">
                <div class="underline">
                    <a href="index.html" class="label button-terciary">PRIVACY</a><br>
                </div>
                <div class="underline">
                    <a href="index.html" class="label button-terciary">CONTACT US</a>
                </div>
            </div>
            <div class="footer-line">

            </div>
            <div class="footer-rights">
                <p>&copy; ` + getYear() + ` SubHub. All rights reserved.</p>
            </div>
        </div>
    </div>
    
</footer>
            `;
        }
    }
    customElements.define('custom-footer', CustomFooter);
}
