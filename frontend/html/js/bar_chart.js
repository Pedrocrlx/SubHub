// js/bar_chart.js

export function updateBarChart(subscriptions) {
    console.log("updateBarChart: Subscriptions received:", subscriptions);

    const barChartContainer = document.querySelector('.bar-chart');
    if (!barChartContainer) {
        console.error("updateBarChart: Bar chart container '.bar-chart' not found.");
        return;
    }

    if (!subscriptions || subscriptions.length === 0) {
        console.warn("updateBarChart: No subscriptions to display. Bar chart will be empty.");
        const monthLabels = barChartContainer.querySelectorAll('.month-label'); 
        const bars = barChartContainer.querySelectorAll('.bar');
        monthLabels.forEach(label => { 
            label.textContent = '';
        });
        bars.forEach(bar => {
            bar.style.height = '0px';
            bar.textContent = '';
        });
        const totalSpendingElement = document.querySelector('.spending-value');
        if (totalSpendingElement) totalSpendingElement.textContent = '0.00€';
        return;
    }

    const { monthlySpending, totalSpending, maxSpending } = calculateMonthlySpending(subscriptions);
    console.log("updateBarChart: Calculated barData - monthlySpending:", monthlySpending, "totalSpending:", totalSpending, "maxSpending:", maxSpending);

    const bars = barChartContainer.querySelectorAll('.bar');
    const monthLabels = barChartContainer.querySelectorAll('.month-label'); 
    const barLabels = barChartContainer.querySelectorAll('.bar-label');
    const chartMaxHeight = 140;

    bars.forEach((bar, index) => {
        const barValue = monthlySpending[index] || 0;
        const heightPercentage = maxSpending > 0 ? (barValue / maxSpending) : 0;
        const barHeight = heightPercentage * chartMaxHeight;
        bar.style.height = `${barHeight}px`;
        bar.style.opacity = barValue > 0 ? '1' : '0.5';
        bar.title = `Spending: ${barValue.toFixed(2)}€`;
        if (barLabels[index]) {
            barLabels[index].textContent = `${barValue.toFixed(2)}€`;
        }        
        if (monthLabels[index]) {
            monthLabels[index].textContent = getMonthName(index);
        }

        console.log(`Bar ${index} (${getMonthName(index)}): value=${barValue.toFixed(2)}€, height=${barHeight.toFixed(2)}px`);
    });

    const totalSpendingElement = document.querySelector('.spending-value');
    if (totalSpendingElement) {
        totalSpendingElement.textContent = `${totalSpending.toFixed(2)}€`;
    }
}

function calculateMonthlySpending(subscriptions) {
    const monthlySpending = new Array(6).fill(0);
    let totalCurrentMonthlySpending = 0; 

    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();

    subscriptions.forEach(sub => {
        const monthlyPrice = parseFloat(sub.monthly_price || 0);
        if (isNaN(monthlyPrice) || monthlyPrice <= 0) {
            console.warn(`Invalid or zero monthly_price for bar chart calculation for ${sub.service_name}: ${sub.monthly_price}`);
            return;
        }

        const startDate = new Date(sub.starting_date);
        startDate.setHours(0, 0, 0, 0); // Normalize startDate to the start of its day

        if (isNaN(startDate.getTime())) {
            console.error(`Invalid starting_date for subscription ${sub.service_name}: ${sub.starting_date}. Skipping.`);
            return;
        }

        for (let i = 0; i < 6; i++) {
            let barMonth = currentMonth - i;
            let barYear = currentYear;

            if (barMonth < 0) {
                barMonth += 12;
                barYear--;
            }
            const lastDayOfBarMonth = new Date(barYear, barMonth + 1, 0);
            lastDayOfBarMonth.setHours(23, 59, 59, 999);

            if (startDate <= lastDayOfBarMonth) {
                monthlySpending[i] += monthlyPrice;
            }
        }

        const endOfCurrentMonth = new Date(currentYear, currentMonth + 1, 0);
        endOfCurrentMonth.setHours(23, 59, 59, 999);
        if (startDate <= endOfCurrentMonth) {
            totalCurrentMonthlySpending += monthlyPrice;
        }
    });

    const maxSpending = Math.max(...monthlySpending);

    return {
        monthlySpending,
        totalSpending: totalCurrentMonthlySpending,
        maxSpending: maxSpending > 0 ? maxSpending : 1 
    };
}

// Helper to get month names for display
function getMonthName(offset) {
    const date = new Date();
    date.setMonth(date.getMonth() - offset);
    return date.toLocaleString('en-US', { month: 'short' });
}