// js/next_payments.js

// Função para gerar as próximas N datas de pagamento mensais
function generateNextMonthlyPaymentDates(startDateStr, count = 12) {
    const startDate = new Date(startDateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normaliza para o início do dia

    const results = [];

    let year = startDate.getFullYear();
    let month = startDate.getMonth();
    const day = startDate.getDate();

    let nextDate = new Date(year, month, day);
    nextDate.setHours(0, 0, 0, 0); // Normaliza para o início do dia

    // Encontra a primeira data de pagamento que é hoje ou no futuro
    // Se a data de início for, por exemplo, 15 de Junho e hoje for 24 de Junho, o próximo pagamento é 15 de Julho.
    // Se a data de início for 25 de Junho e hoje for 24 de Junho, o próximo pagamento é 25 de Junho.
    while (nextDate < today) {
        month++;
        if (month > 11) {
            month = 0;
            year++;
        }
        const lastDay = new Date(year, month + 1, 0).getDate();
        const correctDay = Math.min(day, lastDay);
        nextDate = new Date(year, month, correctDay);
        nextDate.setHours(0, 0, 0, 0); // Normaliza para o início do dia
    }

    // Adiciona as próximas 'count' datas futuras
    for (let i = 0; i < count; i++) {
        const paymentDate = new Date(nextDate);
        results.push(paymentDate);

        nextDate.setMonth(nextDate.getMonth() + 1);
        // Ajusta o dia se o mês seguinte tiver menos dias
        const lastDay = new Date(nextDate.getFullYear(), nextDate.getMonth() + 1, 0).getDate();
        const correctDay = Math.min(day, lastDay);
        nextDate.setDate(correctDay);
        nextDate.setHours(0, 0, 0, 0); // Normaliza para o início do dia
    }

    return results;
}

// Função para formatar a data em português
function formatDatePt(date) {
    return date.toLocaleDateString("pt-PT", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}

// Função para obter o logotipo do serviço
function getLogoForService(serviceName) {
    const logos = {
        "spotify": "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        "netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
        "amazon prime": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Amazon_Prime_Logo.svg",
        "chatgpt plus": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", // Ajuste para "ChatGPT Plus"
        "youtube premium": "https://upload.wikimedia.org/wikipedia/commons/3/3f/YouTube_Premium_logo.svg",
        "disney+": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg", // Ajuste para "Disney+"
        "hbo max": "https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg",
        "apple music": "https://upload.wikimedia.org/wikipedia/commons/d/df/Apple_Music_logo.svg",
        "crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Crunchyroll_Logo.svg",
        "microsoft 365": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_365_logo.svg", // Exemplo
        "adobe creative cloud": "https://upload.wikimedia.org/wikipedia/commons/2/23/Adobe_Creative_Cloud_Logo.svg", // Exemplo
        "google drive": "https://upload.wikimedia.org/wikipedia/commons/d/da/Google_Drive_logo.svg", // Exemplo
        "github copilot": "https://upload.wikimedia.org/wikipedia/commons/0/09/Github_logo.svg", // Exemplo, pode precisar de um logo Copilot específico
        "another service": "https://upload.wikimedia.org/wikipedia/commons/5/55/Question_Mark.svg" // Fallback para "Another Service"
    };

    const key = serviceName.trim().toLowerCase();
    return logos[key] || "https://upload.wikimedia.org/wikipedia/commons/5/55/Question_Mark.svg";
}


export function updateNextPayments(subscriptions) {
    const subscriptionListElement = document.getElementById('subscription-list');
    if (!subscriptionListElement) {
        console.error("Elemento 'subscription-list' não encontrado.");
        return;
    }

    if (!subscriptions || subscriptions.length === 0) {
        subscriptionListElement.innerHTML = '<p class="no-subscriptions">Nenhum pagamento futuro encontrado.</p>';
        return;
    }

    const allPayments = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normaliza para o início do dia

    subscriptions.forEach(sub => {
        const monthlyPrice = parseFloat(sub.monthly_price || 0);
        if (isNaN(monthlyPrice) || monthlyPrice <= 0) {
            console.warn(`Subscrição inválida (preço) para Next Payments: ${sub.service_name}`);
            return;
        }

        // Usamos 'starting_date' conforme o que foi definido para as modais e API
        // Se a sua API retorna 'start_date', mude aqui para 'sub.start_date'
        const startDateString = sub.starting_date;
        if (!startDateString) {
             console.warn(`Subscrição inválida (data de início) para Next Payments: ${sub.service_name}`);
             return;
        }


        // IMPORTANT: Esta lógica assume que todas as subscrições são mensais
        // Se tiver "renovation_type" na API, esta parte precisa ser ajustada:
        // const renovationType = sub.renovation_type || 'Monthly'; // Assumindo 'Monthly' se não vier da API
        // if (renovationType === 'Monthly') {
        //     const nextDates = generateNextMonthlyPaymentDates(startDateString, 12);
        //     nextDates.forEach(date => {
        //         allPayments.push({
        //             service_name: sub.service_name,
        //             price: monthlyPrice,
        //             date: date,
        //             logo: getLogoForService(sub.service_name)
        //         });
        //     });
        // } else if (renovationType === 'Annually') {
        //     // Lógica para pagamentos anuais
        //     // ...
        // }


        // Usando a sua função generateNextPaymentDates que gera 12 meses futuros
        const nextDates = generateNextMonthlyPaymentDates(startDateString, 12);
        nextDates.forEach(date => {
            allPayments.push({
                service_name: sub.service_name,
                price: monthlyPrice,
                date: date,
                logo: getLogoForService(sub.service_name)
            });
        });
    });

    const upcoming = allPayments
        .filter(p => p.date >= today) // Filtra apenas datas futuras ou hoje
        .sort((a, b) => a.date.getTime() - b.date.getTime()) // Ordena cronologicamente
        .slice(0, 3); // Pega os próximos 3

    subscriptionListElement.innerHTML = ""; // Limpa o conteúdo existente

    if (upcoming.length > 0) {
        upcoming.forEach(payment => {
            const item = document.createElement("div");
            item.className = "subscription"; // Usando a sua classe
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
            subscriptionListElement.appendChild(item);
        });
    } else {
        subscriptionListElement.innerHTML = '<p class="no-subscriptions">Nenhum pagamento futuro encontrado.</p>';
    }
    console.log("Next 3 Upcoming Payments:", upcoming); // Debugging
}