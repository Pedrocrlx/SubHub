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
        const bars = barChartContainer.querySelectorAll('.bar');
        const monthLabels = barChartContainer.querySelectorAll('.month-label'); // Select month labels
        bars.forEach(bar => {
            bar.style.height = '0px';
            bar.textContent = '';
        });
        monthLabels.forEach(label => { // Clear month labels too
            label.textContent = '';
        });
        const totalSpendingElement = document.querySelector('.spending-value');
        if (totalSpendingElement) totalSpendingElement.textContent = '0.00€';
        return;
    }

    const { monthlySpending, totalSpending, maxSpending } = calculateMonthlySpending(subscriptions);
    console.log("updateBarChart: Calculated barData - monthlySpending:", monthlySpending, "totalSpending:", totalSpending, "maxSpending:", maxSpending);

    const bars = barChartContainer.querySelectorAll('.bar');
    const monthLabels = barChartContainer.querySelectorAll('.month-label'); // Select month labels again
    const chartMaxHeight = 140;

    bars.forEach((bar, index) => {
        const barValue = monthlySpending[index] || 0;
        const heightPercentage = maxSpending > 0 ? (barValue / maxSpending) : 0;
        const barHeight = heightPercentage * chartMaxHeight;

        bar.style.height = `${barHeight}px`;
        bar.textContent = barValue.toFixed(2);
        bar.style.opacity = barValue > 0 ? '1' : '0.5';
        bar.title = `Spending: ${barValue.toFixed(2)}€`;

        // Update the month label for the current bar
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

// Helper function to calculate monthly spending
function calculateMonthlySpending(subscriptions) {
    // monthlySpending[0] = current month, monthlySpending[1] = last month, ..., monthlySpending[5] = 5 months ago
    const monthlySpending = new Array(6).fill(0);
    let totalCurrentMonthlySpending = 0; // For the total value in the top right corner

    // Get the current month and year to base calculations from
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

        // Iterate through the last 6 months (including current)
        for (let i = 0; i < 6; i++) {
            // Calculate the specific month and year for this bar
            let barMonth = currentMonth - i;
            let barYear = currentYear;

            if (barMonth < 0) { // If month goes into previous year
                barMonth += 12;
                barYear--;
            }

            // Get the last day of the month this bar represents
            const lastDayOfBarMonth = new Date(barYear, barMonth + 1, 0);
            lastDayOfBarMonth.setHours(23, 59, 59, 999); // Set to end of day for proper comparison

            // A subscription contributes to this month if its start_date is
            // on or before the last day of the bar's month.
            if (startDate <= lastDayOfBarMonth) {
                monthlySpending[i] += monthlyPrice;
            }
        }

        // Calculate the total for the *current* month (index 0 for the overview value)
        // This explicitly checks if the subscription was active on or before the end of the current month.
        const endOfCurrentMonth = new Date(currentYear, currentMonth + 1, 0);
        endOfCurrentMonth.setHours(23, 59, 59, 999);
        if (startDate <= endOfCurrentMonth) {
            totalCurrentMonthlySpending += monthlyPrice;
        }
    });

    // Find the maximum spending among the 6 months to scale the bars
    const maxSpending = Math.max(...monthlySpending);

    return {
        monthlySpending, // Array of spending for each of the last 6 months
        totalSpending: totalCurrentMonthlySpending, // Total for the *current* month
        maxSpending: maxSpending > 0 ? maxSpending : 1 // Prevents division by zero if all spending is 0
    };
}

// Helper to get month names for display
function getMonthName(offset) {
    const date = new Date();
    date.setMonth(date.getMonth() - offset);
    return date.toLocaleString('en-US', { month: 'short' }); // e.g., 'Jun', 'May', 'Apr'
}