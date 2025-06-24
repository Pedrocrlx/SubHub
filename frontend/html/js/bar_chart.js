// js/bar_chart.js

export function updateBarChart(subscriptions) {
    console.log("updateBarChart: Subscriptions received:", subscriptions); // Debugging
    if (!subscriptions || subscriptions.length === 0) {
        console.warn("updateBarChart: No subscriptions to display. Bar chart will be empty.");
        const bars = document.querySelectorAll('.bar-chart .bar');
        bars.forEach(bar => bar.style.height = '0px'); // Clear bars
        const totalSpendingElement = document.querySelector('.spending-value');
        if (totalSpendingElement) totalSpendingElement.textContent = '0.00€';
        return;
    }

    const barData = calculateMonthlySpending(subscriptions);
    console.log("updateBarChart: Calculated barData:", barData); // Debugging

    const bars = document.querySelectorAll('.bar-chart .bar');
    const chartMaxHeight = 140; // A mesma altura definida no CSS para .bar-chart

    bars.forEach((bar, index) => {
        // Certifique-se de que o valor existe e não é NaN
        const barValue = barData.monthlySpending[index] || 0;
        const heightPercentage = barData.maxSpending > 0 ? (barValue / barData.maxSpending) : 0;
        bar.style.height = `${heightPercentage * chartMaxHeight}px`;
        // console.log(`Bar ${index}: value=${barValue}, height=${bar.style.height}`); // More debugging
    });

    // Atualiza o valor total de gastos
    const totalSpendingElement = document.querySelector('.spending-value');
    if (totalSpendingElement) {
        totalSpendingElement.textContent = `${barData.totalSpending.toFixed(2)}€`;
    }
}

// Função auxiliar para calcular os gastos mensais
function calculateMonthlySpending(subscriptions) {
    const monthlySpending = new Array(6).fill(0); // [Current Month, Last Month, ..., 5 Months Ago]
    let totalCurrentMonthlySpending = 0; // Para o valor total no canto superior direito
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize para o início do dia

    subscriptions.forEach(sub => {
        const monthlyPrice = parseFloat(sub.monthly_price || 0);
        if (isNaN(monthlyPrice)) {
            console.warn(`Invalid monthly_price for ${sub.service_name}: ${sub.monthly_price}`);
            return; // Pula subscrições com preço inválido
        }

        const startDate = new Date(sub.starting_date);
        startDate.setHours(0, 0, 0, 0);

        // Calcula o total de gastos recorrentes do mês atual para o elemento 'spending-value'
        // Assume que se a subscrição começou, ela contribui para o mês atual
        if (startDate <= today) {
            totalCurrentMonthlySpending += monthlyPrice;
        }

        // Calcula a contribuição para cada um dos últimos 6 meses para o gráfico de barras
        for (let i = 0; i < 6; i++) { // i = 0 para o mês atual, i = 1 para o mês passado, etc.
            // Cria uma data para o início do mês que estamos a calcular (ex: 1 de Junho para i=0, 1 de Maio para i=1)
            const monthBeingCalculated = new Date(today.getFullYear(), today.getMonth() - i, 1);
            monthBeingCalculated.setHours(0, 0, 0, 0);

            // Se a subscrição começou no mês que estamos a calcular ou antes
            if (startDate <= monthBeingCalculated) {
                monthlySpending[i] += monthlyPrice;
            }
        }
    });

    const maxSpending = Math.max(...monthlySpending);
    return {
        monthlySpending,
        totalSpending: totalCurrentMonthlySpending, // Este é o total para o mês atual
        maxSpending: maxSpending > 0 ? maxSpending : 1 // Evita divisão por zero se todos os gastos forem 0
    };
}