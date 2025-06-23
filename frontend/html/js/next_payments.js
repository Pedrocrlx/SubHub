document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/auth/";
        return;
    }

    fetch("http://localhost:8000/subscriptions", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .then(subscriptions => {
        const allPayments = [];

        subscriptions.forEach(sub => {
            const nextDates = generateNextPaymentDates(sub.start_date, 12);
            nextDates.forEach(date => {
                allPayments.push({
                    service_name: sub.service_name,
                    price: sub.monthly_price,
                    date,
                    logo: getLogoForService(sub.service_name)
                });
            });
        });

        const upcoming = allPayments
            .filter(p => p.date >= new Date())
            .sort((a, b) => a.date - b.date)
            .slice(0, 3);

        const container = document.getElementById("subscription-list");
        container.innerHTML = "";

        upcoming.forEach(payment => {
            const item = document.createElement("div");
            item.className = "subscription";
            item.innerHTML = `
              <div style="display:flex; align-items:center;">
                <img src="${payment.logo}" alt="${payment.service_name}" style="width:40px; height:40px; margin-right:10px;">
                <div class="info">
                  <span>${payment.service_name}</span>
                  <span class="date">Pagamento: ${formatDatePt(payment.date)}</span>
                </div>
              </div>
              <div class="price">${payment.price.toFixed(2)}€</div>
            `;
            container.appendChild(item);
        });
    })
    .catch(err => {
        console.error("Erro ao buscar subscrições:", err);
        localStorage.clear();
        window.location.href = "/auth/";
    });
});

function generateNextPaymentDates(startDateStr, count = 12) {
    const startDate = new Date(startDateStr);
    const today = new Date();
    const results = [];

    let year = startDate.getFullYear();
    let month = startDate.getMonth();
    const day = startDate.getDate();
    let nextDate = new Date(year, month, day);

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

function getLogoForService(serviceName) {
    const logos = {
        "spotify": "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        "netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
        "amazon prime": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Amazon_Prime_Logo.svg",
        "chatgpt": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg",
        "youtube premium": "https://upload.wikimedia.org/wikipedia/commons/3/3f/YouTube_Premium_logo.svg",
        "disney plus": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
        "hbo max": "https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg",
        "apple music": "https://upload.wikimedia.org/wikipedia/commons/d/df/Apple_Music_logo.svg",
        "crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Crunchyroll_Logo.svg"
    };

    const key = serviceName.trim().toLowerCase();
    return logos[key] || "https://upload.wikimedia.org/wikipedia/commons/5/55/Question_Mark.svg";
}
