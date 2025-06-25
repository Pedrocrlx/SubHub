// js/next_payments.js

// Function to generate the next N monthly payment dates
function generateNextMonthlyPaymentDates(startDateStr, count = 12) {
    const startDate = new Date(startDateStr);

    // Validate startDate - crucial for preventing "Invalid Date" errors
    if (isNaN(startDate.getTime())) {
        console.error(`Invalid startDateStr for generateNextMonthlyPaymentDates: ${startDateStr}`);
        return [];
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize today to the start of the day

    const results = [];
    // Store original day of the month to handle month-end rollovers (e.g., Jan 31st -> Feb 28th/29th -> Mar 31st)
    const originalDay = startDate.getDate();

    let currentYear = startDate.getFullYear();
    let currentMonth = startDate.getMonth(); // 0-indexed month

    // Calculate the initial candidate payment date based on the start date
    let nextDate = new Date(currentYear, currentMonth, originalDay);
    nextDate.setHours(0, 0, 0, 0); // Normalize

    // Advance `nextDate` month by month until it is today or in the future
    // This loop finds the first upcoming payment date for a monthly subscription
    while (nextDate < today) {
        currentMonth++; // Move to the next month
        if (currentMonth > 11) { // If month overflows (e.g., December to January)
            currentMonth = 0;
            currentYear++;
        }
        // When setting a date, always consider the last day of the target month
        // This correctly handles cases like originalDay=31 in a 30-day month or Feb.
        const lastDayOfTargetMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const actualDay = Math.min(originalDay, lastDayOfTargetMonth); // Use original day or last day of month if original is too high

        nextDate = new Date(currentYear, currentMonth, actualDay);
        nextDate.setHours(0, 0, 0, 0); // Normalize
    }

    // Now, `nextDate` holds the *first* upcoming monthly payment date.
    // Generate `count` additional future payment dates from this point.
    for (let i = 0; i < count; i++) {
        results.push(new Date(nextDate)); // Push a copy of the date to results

        // Advance to the next month for the next iteration
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        // Recalculate `nextDate` considering month-end issues for the next iteration
        const lastDayOfTargetMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const actualDay = Math.min(originalDay, lastDayOfTargetMonth);
        nextDate = new Date(currentYear, currentMonth, actualDay);
        nextDate.setHours(0, 0, 0, 0); // Normalize
    }

    return results;
}

// Function to format the date in Portuguese
function formatDatePt(date) {
    // Current location is Pêra, Faro District, Portugal. Using pt-PT for locale.
    return date.toLocaleDateString("pt-PT", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}

// Function to get the service logo (no changes needed here)
export function getLogoForService(serviceName) {
    const logos = {
        "spotify": "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        "netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
        "amazon prime": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Amazon_Prime_Logo.svg",
        "chatgpt plus": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg",
        "youtube premium": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/YouTube_social_white_circle_%282017%29.svg/640px-YouTube_social_white_circle_%282017%29.svg.png",
        "disney+": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
        "hbo max": "https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg",
        "apple music": "https://upload.wikimedia.org/wikipedia/commons/d/df/Apple_Music_logo.svg",
        "crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Crunchyroll_Logo.svg",
        "microsoft 365": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_365_logo.svg",
        "adobe creative cloud": "https://upload.wikimedia.org/wikipedia/commons/2/23/Adobe_Creative_Cloud_Logo.svg",
        "google drive": "https://upload.wikimedia.org/wikipedia/commons/d/da/Google_Drive_logo.svg",
        "github copilot": "https://upload.wikimedia.org/wikipedia/commons/0/09/Github_logo.svg",
        "discord nitro": "https://cdn.iconscout.com/icon/free/png-512/free-discord-nitro-icon-download-in-svg-png-gif-file-formats--voice-premium-social-media-pack-user-interface-icons-6406718.png?f=webp&w=512",
        "another service": "https://upload.wikimedia.org/wikipedia/commons/5/55/Question_Mark.svg"
    };

    const key = serviceName.trim().toLowerCase();
    return logos[key] || "https://upload.wikimedia.org/wikipedia/commons/5/55/Question_Mark.svg";
}


export function updateNextPayments(subscriptions) {
    const subscriptionListElement = document.getElementById('subscription-list');
    if (!subscriptionListElement) {
        console.error("Element 'subscription-list' not found.");
        return;
    }

    if (!subscriptions || subscriptions.length === 0) {
        subscriptionListElement.innerHTML = '<p class="no-subscriptions">Nenhum pagamento futuro encontrado.</p>';
        return;
    }

    const allPayments = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize to the start of today for comparison

    subscriptions.forEach(sub => {
        const monthlyPrice = parseFloat(sub.monthly_price || 0);
        if (isNaN(monthlyPrice) || monthlyPrice <= 0) {
            console.warn(`Invalid or zero price for Next Payments: ${sub.service_name} (Price: ${sub.monthly_price}). Skipping.`);
            return; // Skip subscriptions with invalid or zero price
        }

        const startDateString = sub.starting_date;
        if (!startDateString) {
            console.warn(`Missing starting_date for Next Payments: ${sub.service_name}. Skipping.`);
            return;
        }

        // IMPORTANT: As discussed, we are explicitly treating ALL subscriptions as MONTHLY payments
        // This means the 'generateNextMonthlyPaymentDates' function will always provide monthly payment dates.
        const nextDates = generateNextMonthlyPaymentDates(startDateString, 12); // Get the next 12 upcoming monthly dates

        nextDates.forEach(date => {
            allPayments.push({
                service_name: sub.service_name,
                price: monthlyPrice, // Use the monthly price for all entries
                date: date,
                logo: getLogoForService(sub.service_name)
            });
        });
    });

    console.log("All generated future payments (before filtering/sorting):", allPayments);

    const upcoming = allPayments
        .filter(p => p.date >= today)
        .sort((a, b) => a.date.getTime() - b.date.getTime())
        .slice(0, 3);

    console.log("Next 3 Upcoming Payments (after filtering/sorting):", upcoming);

    subscriptionListElement.innerHTML = "";

    if (upcoming.length > 0) {
        upcoming.forEach(payment => {
            const item = document.createElement("div");
            item.className = "subscription";
            item.innerHTML = `
                <div class="subscription_div">
                    <img class="subscription_logo" src="${payment.logo}" alt="${payment.service_name}">
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
}