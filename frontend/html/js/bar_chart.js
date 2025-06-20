document.addEventListener('DOMContentLoaded', () => {
    // Dados de exemplo para as alturas das barras (de 0 a 1, relativo à altura máxima do gráfico)
    const barData = [0.25, 0.40, 0.55, 0.70, 0.85, 0.95]; // Representa 25%, 40% etc. da altura máxima

    const bars = document.querySelectorAll('.bar-chart .bar');
    const chartMaxHeight = 140; // A mesma altura definida no CSS para .bar-chart

    bars.forEach((bar, index) => {
        // Define a altura de cada barra com base nos dados
        bar.style.height = `${barData[index] * chartMaxHeight}px`;

        // Opcional: Se você quiser definir cores dinamicamente em vez de no CSS
        // const colors = ['#c0d1c0', '#a0c0a0', '#80ac80', '#609860', '#408440', '#207020'];
        // bar.style.backgroundColor = colors[index];
    });

    // Você também pode atualizar o valor de spending aqui se ele for dinâmico
    const totalSpendingElement = document.querySelector('.spending-value');
    totalSpendingElement.textContent = '155.00€';
});