(function () {
  let allCities = [];
  let selectedCurrency = "EUR";
  let exchangeRatesLoaded = false;
  let averagePricesLoaded = false;

  let averagePrices = {};
  let exchangeRates = { EUR: 1.0 };

  // 🔁 Currency dropdown listener
  const currencyDropdown = document.getElementById("currency-select");
  if (currencyDropdown) {
    currencyDropdown.addEventListener("change", function (e) {
      selectedCurrency = e.target.value;
    });
  }

  // ✅ Helper to render info box after search
  function renderCityInfoSearch(city) {
    const displayTarget = document.getElementById("search-city-display");

    if (!averagePricesLoaded || !exchangeRatesLoaded) {
      console.log("⏳ Data not ready yet.");
      return;
    }

    renderSharedCityHTML(
      city,
      displayTarget,
      averagePrices,
      exchangeRates,
      selectedCurrency
    );
  }

  // 🔁 Fetch cities
  fetch("/static/js/cities.json")
    .then(res => {
      if (!res.ok) throw new Error("Failed to load cities.json");
      return res.json();
    })
    .then(data => {
      console.log("✅ Loaded cities:", data.length);
      allCities = data;
    })
    .catch(err => {
      console.error("❌ Error loading cities.json:", err);
    });

  // 🔁 Fetch average prices
  fetch("/average-prices")
    .then(res => res.json())
    .then(data => {
      averagePrices = data;
      averagePricesLoaded = true;
      console.log("✅ Loaded average prices");
    });

  // 🔁 Fetch exchange rates
  fetch("/exchange-rates")
    .then(res => res.json())
    .then(data => {
      exchangeRates = data.rates;
      exchangeRates["EUR"] = 1.0;
      exchangeRatesLoaded = true;
      console.log("✅ Loaded exchange rates");
    });

  // 🔎 Handle input search
  const input = document.getElementById("search-cities");
  const resultsBox = document.getElementById("search-results");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    resultsBox.innerHTML = "";

    if (query.length < 1) return;

    const matches = allCities.map(city => {
      const cityName = city.city.toLowerCase();
      const countryName = city.country_name.toLowerCase();

      let score = -1;
      if (cityName.startsWith(query)) score = 2;
      else if (cityName.includes(query)) score = 1;
      else if (countryName.startsWith(query)) score = 1;
      else if (countryName.includes(query)) score = 0;

      return { city, score };
    }).filter(result => result.score >= 0);

    matches.sort((a, b) => b.score - a.score);

    matches.slice(0, 3).forEach(result => {
      const city = result.city;
      const div = document.createElement("div");
      div.textContent = `${city.city}, ${city.country_name}`;

      div.addEventListener("click", () => {
        input.value = `${city.city}, ${city.country_name}`;
        resultsBox.innerHTML = "";
        renderCityInfoSearch(city);
      });

      resultsBox.appendChild(div);
    });
  });
})();
