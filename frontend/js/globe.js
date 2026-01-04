averagePrices = {};
let averagePricesLoaded = false; // ✅ Track if data is ready
let selectedPoint = null;
let exchangeRatesLoaded = false;
let latestVisiblePoint = null;   // 🆕 Add this


// ✅ Load average prices
fetch("/average-prices")
  .then(res => res.json())
  .then(data => {
    averagePrices = data;
    averagePricesLoaded = true;
    console.log("✅ Loaded average prices:", averagePrices);
  })
  .catch(err => console.error("❌ Failed to load average prices:", err));

console.log("Globe.gl loaded ✅");

fetch("/exchange-last-updated")
  .then(res => res.json())
  .then(data => {
    const rawTs = data.timestamp;
    if (rawTs) {
      const date = new Date(rawTs);
      const formatted = date.toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
      document.getElementById('last-update-label').textContent = `${formatted}`;
    } else {
      document.getElementById('last-update-label').textContent = `Unknown`;
    }
  })
  .catch(err => {
    console.error("❌ Failed to load last update time:", err);
    document.getElementById('last-update-label').textContent = `Last update: error`;
  });



const container = document.getElementById('globe-container');
const cityDisplay = document.getElementById('city-name-display');


// Initialize the globe
const myGlobe = Globe()
  .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
  .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
  .pointAltitude(0.02)
  .pointRadius(0.2)
  .pointColor(() => 'orange')
  .pointLat('lat')
  .pointLng('lng')
  .pointsData([])  // Set empty initially
  .width(container.offsetWidth)
  .height(container.offsetHeight);

myGlobe(container);

// White background
const canvas = container.querySelector("canvas");
if (canvas) {
  canvas.style.backgroundColor = "#ffffff";
}

let safeData = [];  // 🔥 Move this outside

// Load cities
fetch('/static/js/cities.json')  // ✅ Adjust path if needed
  .then(res => res.json())
  .then(data => {
    console.log('✅ Loaded city data:', data);

    // ✅ Wrap all data inside label to keep metadata safe
    safeData = data.map(city => ({
      lat: city.lat,
      lng: city.lng,
      label: JSON.stringify({
        city: city.city,
        country: city.country,
        country_name: city.country_name,
        bestSeason: city.bestSeason
      })
    }));

    // ✅ Load to globe
    myGlobe.pointsData(safeData);


   myGlobe.onPointClick(point => {
  if (point) {
    selectedPoint = point;
    renderCityInfo(point);
  }
})

});

function renderCityInfo(point) {
  if (!point || !point.label) return;

  const meta = JSON.parse(point.label); // extract city data
  latestVisiblePoint = point;

  const target = document.getElementById("city-name-display");

  renderSharedCityHTML(meta, target, averagePrices, exchangeRates, selectedCurrency);
}



let exchangeRates = { EUR: 1.0 }; // Default
let selectedCurrency = 'EUR';

fetch('/exchange-rates')
  .then(res => res.json())
  .then(data =>{
    exchangeRates = data.rates;
    exchangeRates["EUR"] = 1.0;  // make sure EUR is included
    console.log("✅ Exchange rates loaded:", exchangeRates);
    exchangeRatesLoaded = true;

    const pointToUpdate = selectedPoint || latestVisiblePoint;
      if (pointToUpdate) {
        renderCityInfo(pointToUpdate);
      }

  })
  .catch(err => {
    console.error("❌ Failed to load exchange rates:", err);
  });

document.getElementById('currency-select').addEventListener('change', (e) => {
  selectedCurrency = e.target.value;
  console.log("💱 Currency changed to:", selectedCurrency);

  const pointToUpdate = selectedPoint || latestVisiblePoint;
  if (pointToUpdate) {
    renderCityInfo(pointToUpdate);
  }
});