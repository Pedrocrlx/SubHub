// js/pie_chart.js

// Global variables for color management (will be reset/re-initialized carefully)
const colorPalette = [
    '#FF6384', // Red-pink
    '#36A2EB', // Blue
    '#FFCE56', // Yellow
    '#4BC0C0', // Teal
    '#9966FF', // Purple
    '#FF9F40', // Orange
    '#A7D9A4', // Light Green
    '#B0BEC5', // Grey-Blue
    '#7F8C8D', // Dark Grey
    '#2ECC71', // Emerald Green
    '#E74C3C', // Alizarin Red
    '#3498DB', // Peter River Blue
    '#F1C40F', // Sunflower Yellow
    '#1ABC9C', // Turquoise
    '#8E44AD', // Amethyst Purple
    '#D35400'  // Pumpkin Orange
];
// This map will store category -> assigned color for the *current* rendering cycle
let currentRenderingCategoryColors = {};


export function updatePieChart(subscriptions) {
    const categorySpending = calculateCategorySpending(subscriptions);
    const totalSpendingValue = Object.values(categorySpending).reduce((sum, value) => sum + value, 0);

    const pieCenterText = document.querySelector('.pie-center-text');
    const tooltipElement = document.querySelector('.pie-tooltip');
    const pieChartContainer = document.querySelector('.pie-chart-container');
    const pieChartSvg = document.querySelector('.pie-chart-svg');

    if (!pieCenterText || !tooltipElement || !pieChartContainer || !pieChartSvg) {
        console.error('One or more pie chart elements not found.');
        return;
    }

    pieChartSvg.innerHTML = ''; // Clear previous SVG content

    // Reset color assignments for this rendering cycle
    currentRenderingCategoryColors = {};
    let paletteIndex = 0; // Reset index for palette use

    // Handle case where there are no subscriptions or total spending is zero
    if (totalSpendingValue === 0) {
        pieCenterText.innerHTML = `Total<br>0.00€`;
        const noDataText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        noDataText.setAttribute('x', '50');
        noDataText.setAttribute('y', '50');
        noDataText.setAttribute('text-anchor', 'middle');
        noDataText.setAttribute('dominant-baseline', 'middle');
        noDataText.setAttribute('font-size', '8px');
        noDataText.setAttribute('fill', '#999');
        noDataText.textContent = 'No data';
        pieChartSvg.appendChild(noDataText);

        const fullCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        fullCircle.setAttribute('cx', '50');
        fullCircle.setAttribute('cy', '50');
        fullCircle.setAttribute('r', '50');
        fullCircle.setAttribute('fill', '#e0e0e0');
        pieChartSvg.appendChild(fullCircle);
        return;
    }

    pieCenterText.innerHTML = `Total<br>${totalSpendingValue.toFixed(2)}€`;

    function toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    function getCoordinatesForPercent(percent) {
        const x = Math.cos(toRadians(percent * 360 - 90));
        const y = Math.sin(toRadians(percent * 360 - 90));
        return [x, y];
    }

    let currentPercentage = 0;
    const categories = Object.keys(categorySpending);

    // Assign colors for the *current* set of categories
    categories.forEach(category => {
        // Use a specific color if defined, otherwise cycle through the palette
        const specificColor = getSpecificCategoryColor(category);
        if (specificColor) {
            currentRenderingCategoryColors[category] = specificColor;
        } else {
            // Assign from palette, cycling if needed
            currentRenderingCategoryColors[category] = colorPalette[paletteIndex % colorPalette.length];
            paletteIndex++; // Move to the next color in the palette
        }
    });


    for (const category of categories) {
        const slicePercentage = categorySpending[category] / totalSpendingValue;

        if (slicePercentage < 0.005 && categories.length > 1) {
            console.warn(`Skipping very small slice for category: ${category} (${(slicePercentage * 100).toFixed(2)}%)`);
            currentPercentage += slicePercentage;
            continue;
        }

        const [startX, startY] = getCoordinatesForPercent(currentPercentage);
        currentPercentage += slicePercentage;
        const [endX, endY] = getCoordinatesForPercent(currentPercentage);

        const largeArcFlag = slicePercentage > 0.5 ? 1 : 0;

        let pathData;
        if (slicePercentage === 1 && categories.length === 1) {
            pathData = `M 50 50 L 50 0 A 50 50 0 1 1 49.99 0 Z`;
        } else {
            pathData = [
                `M 50 50`,
                `L ${50 + startX * 50} ${50 + startY * 50}`,
                `A 50 50 0 ${largeArcFlag} 1 ${50 + endX * 50} ${50 + endY * 50}`,
                `Z`
            ].join(' ');
        }

        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        // Use the color assigned for the current rendering cycle
        pathElement.setAttribute('fill', currentRenderingCategoryColors[category]);
        pathElement.setAttribute('d', pathData);
        pathElement.classList.add('pie-slice-path');

        pathElement.dataset.name = category;
        pathElement.dataset.value = categorySpending[category].toFixed(2);
        pathElement.dataset.percentage = (slicePercentage * 100).toFixed(0);

        pathElement.addEventListener('mouseenter', (e) => {
            const name = e.target.dataset.name;
            const value = e.target.dataset.value;
            const percentage = e.target.dataset.percentage;

            tooltipElement.innerHTML = `<strong>${name}</strong><br>${value}€ (${percentage}%)`;
            tooltipElement.classList.add('active');

            const containerRect = pieChartContainer.getBoundingClientRect();
            tooltipElement.style.left = `${e.clientX - containerRect.left + 15}px`;
            tooltipElement.style.top = `${e.clientY - containerRect.top + 15}px`;
        });

        pathElement.addEventListener('mouseleave', () => {
            tooltipElement.classList.remove('active');
        });

        pieChartSvg.appendChild(pathElement);
    }
}

// Helper function to calculate spending by category
function calculateCategorySpending(subscriptions) {
    const categorySpending = {};
    subscriptions.forEach(sub => {
        const price = parseFloat(sub.monthly_price);
        if (isNaN(price)) {
            console.warn(`Invalid monthly_price for subscription: ${sub.service_name}`);
            return;
        }

        if (categorySpending[sub.category]) {
            categorySpending[sub.category] += price;
        } else {
            categorySpending[sub.category] = price;
        }
    });
    return categorySpending;
}

// Function for specific, hardcoded category colors (if any)
function getSpecificCategoryColor(category) {
    const specificColors = {
        'Netflix': '#E50914',
        'Spotify': '#1DB954',
        'YouTube Premium': '#FF0000',
        'Amazon Prime': '#00A8E1',
        'Microsoft 365': '#F25022',
        'Entertainment': '#FF5733', // Example: a specific color for 'Entertainment'
        'Music': '#33FF57',         // Example: a specific color for 'Music'
        'Productivity': '#3357FF',
        'Gaming': '#FF33A0',
        'Cloud Storage': '#A033FF',
        'Development': '#33FFF2',
        'Education': '#F2FF33',
        'Health': '#FF3333',
        // Add more specific categories and colors here if they *must* have a fixed color
    };
    return specificColors[category]; // Returns undefined if not found
}