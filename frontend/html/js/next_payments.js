
const subscriptions = [
    {
        service_name: "spotify",
        price: 4.99,
        start_date: "2024-03-30",
        logo: "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
    },
    {
        service_name: "amazon prime",
        price: 100.00,
        start_date: "2025-05-30",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Amazon_Prime_Logo.svg/640px-Amazon_Prime_Logo.svg.png"
    },
    {
        service_name: "ChatGPT",
        price: 100.00,
        start_date: "2025-05-30",
        logo: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/ChatGPT-Logo.svg/640px-ChatGPT-Logo.svg.png"
    }
];

function generateNextPaymentDates(startDateStr, count = 12) {
    const startDate = new Date(startDateStr);
    const today = new Date();
    const results = [];

    let year = startDate.getFullYear();
    let month = startDate.getMonth();
    const day = startDate.getDate();
    let nextDate = new Date(year, month, day);

    // Avança até a próxima futura
    while (nextDate <= today) {
        month++;
        if (month > 11) {
            month = 0;
            year++;
        }
        const lastDay = new Date(year, month + 1, 0).getDate();
        const correctDay = Math.min(day, lastDay);
        nextDate = new Date(year, month, correctDay);
    }

    // Agora gera os próximos N
    for (let i = 0; i < count; i++) {
        const paymentDate = new Date(nextDate);
        results.push(paymentDate);

        nextDate.setMonth(nextDate.getMonth() + 1);
        const lastDay = new Date(nextDate.getFullYear(), nextDate.getMonth() + 1, 0).getDate();
        const correctDay = Math.min(day, lastDay);
        nextDate.setDate(correctDay);
    }

    return results;
}

function formatDatePt(date) {
    return date.toLocaleDateString("pt-PT", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}

// Cria uma lista com todas as próximas datas de cobrança de todos os serviços
const allPayments = [];

subscriptions.forEach(sub => {
    const nextDates = generateNextPaymentDates(sub.start_date, 12); // próximos 12 meses
    nextDates.forEach(date => {
        allPayments.push({
            service_name: sub.service_name,
            price: sub.price,
            date,
            logo: sub.logo
        });
    });
});

// Ordena por data e pega as 3 mais próximas
const upcoming = allPayments
    .filter(p => p.date >= new Date())
    .sort((a, b) => a.date - b.date)
    .slice(0, 3);

const container = document.getElementById("subscription-list");

upcoming.forEach(payment => {
    const item = document.createElement("div");
    item.className = "subscription";
    item.innerHTML = `
      <div style="display:flex; align-items:center;">
        <img src="${payment.logo}" alt="${payment.service_name}">
        <div class="info">
          <span>${payment.service_name}</span>
          <span class="date">Pagamento: ${formatDatePt(payment.date)}</span>
        </div>
      </div>
      <div class="price">${payment.price.toFixed(2)}€</div>
    `;
    container.appendChild(item);
});