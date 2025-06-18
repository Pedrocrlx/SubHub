document.addEventListener("DOMContentLoaded", function () {
    // Function to load the menu and set up event listeners
    loadMenu();
    LoadFooter();
});

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
                <a href="/home/" id="home-button" class="label button-terciary">home</a>
                <a id="language-button" class="label button-terciary">LANGUAGE</a>
                <a href="/learn_more/" id="learnmore-button" class="label button-terciary">learn more</a>

            </div>
            <div>
                <button id="SignIn" class="button-secondary secondary-neutral" onclick="signIn()">Sign In</button>
                <button id="SignUp" class="button-primary primary-neutral" onclick="signUp()">Get started</button>
            </div>
        </div>
        </nav>
            `;
        }
    }
    customElements.define('custom-menu', CustomMenu);
    const homeButton = document.getElementById('home-button');
    const LearnMoreButton = document.getElementById('learnmore-button');
    const currentPath = window.location.pathname.split('/');
    console.log("Current Path: " + currentPath[1]);
    if (currentPath[1] === 'home') {
        homeButton.classList.add('active');
    }
    if (currentPath[1] === 'learn_more') {
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

function LoadFooter() {
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

function signUp() {
    window.location.href = "/auth/?signup=true";
}
function signIn() {
    window.location.href = "/auth/";
}