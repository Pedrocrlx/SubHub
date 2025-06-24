// js/pie_chart.js

export function updatePieChart(subscriptions) {
    const categorySpending = calculateCategorySpending(subscriptions);
    const totalSpendingValue = Object.values(categorySpending).reduce((sum, value) => sum + value, 0);

    const pieCenterText = document.querySelector('.pie-center-text');
    const tooltipElement = document.querySelector('.pie-tooltip');
    const pieChartContainer = document.querySelector('.pie-chart-container');
    const pieChartSvg = document.querySelector('.pie-chart-svg');

    if (!pieCenterText || !tooltipElement || !pieChartContainer || !pieChartSvg) {
        console.error('Um ou mais elementos do gráfico de pizza não foram encontrados.');
        return;
    }

    pieChartSvg.innerHTML = ''; // Limpa o SVG anterior

    pieCenterText.innerHTML = `Total<br>${totalSpendingValue.toFixed(2)}€`;

    function toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    function getCoordinatesForPercent(percent) {
        const x = Math.cos(toRadians(percent * 360));
        const y = Math.sin(toRadians(percent * 360));
        return [x, y];
    }

    let currentPercentage = 0;

    for (const category in categorySpending) {
        const slicePercentage = categorySpending[category] / totalSpendingValue;

        const [startX, startY] = getCoordinatesForPercent(currentPercentage);
        currentPercentage += slicePercentage;
        const [endX, endY] = getCoordinatesForPercent(currentPercentage);

        const largeArcFlag = slicePercentage > 0.5 ? 1 : 0;

        const pathData = [
            `M 50 50`,
            `L ${50 + startX * 50} ${50 + startY * 50}`,
            `A 50 50 0 ${largeArcFlag} 1 ${50 + endX * 50} ${50 + endY * 50}`,
            `Z`
        ].join(' ');

        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathElement.setAttribute('d', pathData);
        pathElement.setAttribute('fill', getCategoryColor(category)); // Função para obter a cor da categoria
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

// Função auxiliar para calcular os gastos por categoria
function calculateCategorySpending(subscriptions) {
    const categorySpending = {};
    subscriptions.forEach(sub => {
        if (categorySpending[sub.category]) {
            categorySpending[sub.category] += sub.monthly_price;
        } else {
            categorySpending[sub.category] = sub.monthly_price;
        }
    });
    return categorySpending;
}

// Função auxiliar para obter a cor da categoria (adapte conforme necessário)
function getCategoryColor(category) {
    const colors = {
        Streaming: '#E50914',
        Music: '#1DB954',
        'YouTube Premium': '#FF0000',
        'Amazon Prime': '#00A8E1',
        'Microsoft 365': '#F25022',
        Gym: '#8A2BE2',
        'Cloud Storage': '#4CAF50',
        // Adicione mais categorias e cores aqui
    };
    return colors[category] || '#808080'; // Cor padrão se a categoria não for encontrada
}