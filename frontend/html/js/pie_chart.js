document.addEventListener('DOMContentLoaded', () => {
    const pieData = [
        { name: 'Netflix', value: 17.99, color: '#E50914' },
        { name: 'Spotify', value: 10.99, color: '#1DB954' },
        { name: 'YouTube Premium', value: 12.99, color: '#FF0000' },
        { name: 'Amazon Prime', value: 5.99, color: '#00A8E1' },
        { name: 'Microsoft 365', value: 7.00, color: '#F25022' },
        { name: 'Gym Membership', value: 35.00, color: '#8A2BE2' },
        { name: 'Cloud Storage', value: 2.99, color: '#4CAF50' }
    ];

    const cores = {
  netflix: '#E50914',
  spotify: '#1DB954',
  youtube: '#FF0000',
  amazon: '#00A8E1',
  microsoft: '#F25022',
  gym: '#8A2BE2',
  cloud: '#4CAF50'
};
    
    const totalSpendingValue = pieData.reduce((sum, item) => sum + item.value, 0);

    const pieCenterText = document.querySelector('.pie-center-text');
    const tooltipElement = document.querySelector('.pie-tooltip');
    const pieChartContainer = document.querySelector('.pie-chart-container');
    const pieChartSvg = document.querySelector('.pie-chart-svg'); // Variável correta para o SVG

    // --- Início da Verificação de Elementos ---
    // Adicionei essas verificações para ajudar na depuração.
    // Se algum destes for null, o erro será exibido no console.
    if (!pieCenterText) { console.error('Element .pie-center-text not found!'); return; }
    if (!tooltipElement) { console.error('Element .pie-tooltip not found!'); return; }
    if (!pieChartContainer) { console.error('Element .pie-chart-container not found!'); return; }
    if (!pieChartSvg) { console.error('Element .pie-chart-svg not found! Cannot draw pie chart.'); return; }
    // --- Fim da Verificação de Elementos ---


    // Atualiza o valor total no HTML
    pieCenterText.innerHTML = `Total<br>${totalSpendingValue.toFixed(2)}€`;

    // Função para converter graus em radianos
    function toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    // Função para obter coordenadas de um ponto em um círculo
    function getCoordinatesForPercent(percent) {
        const x = Math.cos(toRadians(percent * 360));
        const y = Math.sin(toRadians(percent * 360));
        return [x, y];
    }

    let currentPercentage = 0; // Porcentagem acumulada

    pieData.forEach((item, index) => {
        const slicePercentage = item.value / totalSpendingValue;

        const [startX, startY] = getCoordinatesForPercent(currentPercentage);
        currentPercentage += slicePercentage;
        const [endX, endY] = getCoordinatesForPercent(currentPercentage);

        // Define se o arco é grande (maior que 180 graus)
        const largeArcFlag = slicePercentage > 0.5 ? 1 : 0;

        // O comando 'd' (data) para o path SVG
        // M = MoveTo (centro do círculo - 50,50 no viewBox de 100x100)
        // L = LineTo (início do arco)
        // A = Arc (raio X, raio Y, x-axis-rotation, large-arc-flag, sweep-flag, endX, endY)
        // Z = ClosePath (volta ao centro)
        // Multiplicamos por 50 e somamos 50 para converter de coord. unitárias (-1 a 1) para o viewBox (0 a 100)
        const pathData = [
            `M 50 50`, // Move para o centro do SVG (50,50 do viewBox)
            `L ${50 + startX * 50} ${50 + startY * 50}`, // Vai para o início do arco (raio 50)
            `A 50 50 0 ${largeArcFlag} 1 ${50 + endX * 50} ${50 + endY * 50}`, // Desenha o arco
            `Z` // Fecha o path de volta ao centro
        ].join(' ');

        // Cria o elemento path SVG
        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathElement.setAttribute('d', pathData);
        pathElement.setAttribute('fill', item.color);
        pathElement.classList.add('pie-slice-path'); // Adiciona classe para estilização CSS

        // Adiciona dados ao elemento path para o tooltip
        pathElement.dataset.name = item.name;
        pathElement.dataset.value = item.value.toFixed(2);
        pathElement.dataset.percentage = (slicePercentage * 100).toFixed(0);

        // Adiciona event listeners para o hover
        pathElement.addEventListener('mouseenter', (e) => {
            const name = e.target.dataset.name;
            const value = e.target.dataset.value;
            const percentage = e.target.dataset.percentage;

            tooltipElement.innerHTML = `<strong>${name}</strong><br>${value}€ (${percentage}%)`;
            tooltipElement.classList.add('active');

            // Posiciona o tooltip relativo ao container do gráfico
            const containerRect = pieChartContainer.getBoundingClientRect();
            // e.clientX e e.clientY são as coordenadas do mouse na viewport.
            // Precisamos subtrair a posição do container para obter uma posição relativa.
            tooltipElement.style.left = `${e.clientX - containerRect.left + 15}px`;
            tooltipElement.style.top = `${e.clientY - containerRect.top + 15}px`;
        });

        pathElement.addEventListener('mouseleave', () => {
            tooltipElement.classList.remove('active');
        });

        // Adiciona a fatia SVG ao elemento SVG principal
        pieChartSvg.appendChild(pathElement);
    });
});
