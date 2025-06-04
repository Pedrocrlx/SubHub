document.addEventListener("DOMContentLoaded", function () {
    // Function to load the menu and set up event listeners
    loadMenu();
    LoadFooter();
});

// Function to load the custom menu component
// This function defines a custom HTML element for the menu and appends it to the document
// It also adds active classes to the menu items based on the current page
function loadMenu() {
    class CustomMenu extends HTMLElement {
        connectedCallback() {
            this.innerHTML = `
                <nav>
        <div id="links">
            <div id="logoContainer">
                <p>
                    <span class="logo-sub">Sub</span><span class="logo-hub">Hub</span>
                </p>
            </div>
            <a href="index.html" id="home-button" class="label">home</a>
            <a  id="language-button"class="label">LANGUAGE</a>
            <a href="LearnMore.html" id="learnmore-button" class="label">learn more</a>

        </div>
        <div>
            <button id="SignIn" class="button-secondary secondary-neutral">Sign In</button>
            <button id="SignUp" class="button-primary primary-neutral">Get started</button>
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

            `;
        }
    }
    customElements.define('custom-footer', CustomFooter);
}
