function getCurrencySymbol(code) {
  const symbols = {
    EUR: '€', USD: '$', GBP: '£', JPY: '¥', AUD: 'A$',
    RON: 'lei', CAD: 'C$', CHF: 'CHF', CZK: 'Kč', MXN: 'MX$', HUF: 'Ft'
  };
  return symbols[code] || code + ' ';
}

function priceToStarRating(price) {
  if (!price) return 0;
  if (price < 20) return 1;
  if (price < 40) return 2;
  if (price < 60) return 3;
  if (price < 80) return 4;
  return 5;
}

function renderStars(starsCount) {
  let html = `<div class="price-stars">`;
  for (let i = 1; i <= 5; i++) {
    html += `<span class="star ${i <= starsCount ? 'filled' : ''}">★</span>`;
  }
  html += `</div>`;
  return html;
}


function renderSharedCityHTML(meta, target, averagePrices, exchangeRates, selectedCurrency) {
  const mapsUrl = `https://www.google.com/maps/place/${meta.city}`;
  const flagUrl = `https://flagcdn.com/48x36/${meta.country.toLowerCase()}.png`;
  const bestTime = meta.bestSeason || "N/A";
  const meanPrice = averagePrices[meta.city.toLowerCase()];

  let priceDisplay = '';
  let starHTML = '';

  if (exchangeRates && meanPrice !== undefined) {
    let rate = exchangeRates[selectedCurrency] || 1.0;
    const converted = meanPrice * rate;
    const symbol = getCurrencySymbol(selectedCurrency);
    priceDisplay = `${symbol}${converted.toFixed(2)}`;
    const stars = priceToStarRating(meanPrice);
    starHTML = renderStars(stars);
  } else {
    priceDisplay = `<span class="spinner inline"></span>`;
    starHTML = `<div class="price-stars"><span class="spinner"></span></div>`;
  }

  // ✅ Predict button as a <a> tag styled inline
  const predictUrl = `/predict.html?city=${encodeURIComponent(meta.city)}`;
  const predictButton = `
    <a href="${predictUrl}"
       style="background: linear-gradient(135deg, #f6c85f, #e4b745, #d1a02a);
              color: white;
              border: none;
              border-radius: 30px;
              padding: 12px 28px;
              font-weight: 600;
              font-size: 1.05rem;
              cursor: pointer;
              box-shadow: 0 4px 8px rgba(0,0,0,0.15);
              text-decoration: none;
              display: inline-block;
              margin-top: 16px;">
       Predict
    </a>
  `;

  // ✅ Build the city info box
  target.innerHTML = `
    <div class="city-info-header"><br>
      <img src="${flagUrl}" alt="${meta.country}" title="${meta.country_name}">
      <span style="font-size: 20px; font-weight: bold;">${meta.city}</span>
    </div>
    <div style="font-size: 16px;"><br><br>
      <strong>Best time to visit:</strong> ${bestTime}<br><br>
      <strong>Avg. Airbnb price:</strong> ${priceDisplay}<br>
      <strong>Expensiveness:</strong> ${starHTML}<br>
      <a href="${mapsUrl}" target="_blank"
         style="display:inline-block;margin-top:6px;color:#1a73e8;">
        📍View on Google Maps
      </a><br><br>
      ${predictButton}
    </div>
  `;
}
