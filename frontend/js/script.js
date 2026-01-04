// Hide the bottom fade when the user reaches the end of the scrollbox
document.addEventListener("DOMContentLoaded", () => {
  const scrollboxes = document.querySelectorAll(".hero-text .scrollbox");
  scrollboxes.forEach(box => {
    const toggleFade = () => {
      const atEnd = Math.ceil(box.scrollTop + box.clientHeight) >= box.scrollHeight;
      box.classList.toggle("at-end", atEnd);
    };
    box.addEventListener("scroll", toggleFade);
    // Run once after open (in case content fits)
    toggleFade();
  });

  // If <details> opens later, run once more to set initial fade
  document.querySelectorAll(".hero-text .readmore").forEach(d => {
    d.addEventListener("toggle", () => {
      const box = d.querySelector(".scrollbox");
      if (d.open && box) {
        // Wait a tick so layout is updated
        setTimeout(() => {
          const atEnd = Math.ceil(box.scrollTop + box.clientHeight) >= box.scrollHeight;
          box.classList.toggle("at-end", atEnd);
        }, 50);
      }
    });
  });
});


// --- Slideshow (single, clean version) ---
document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".hero-image.slideshow");
  if (!container) return;

  const imgA = container.querySelector(".slide.current");
  const imgB = container.querySelector(".slide.next");
  const btnPrev = container.querySelector(".slide-nav.prev");
  const btnNext = container.querySelector(".slide-nav.next-btn");
  const dotsContainer = container.querySelector(".slide-dots");
  const captionName = container.querySelector(".city-name");
  const captionNickname = container.querySelector(".city-nickname");

  const photos = [
    { src: "/static/logo+img/florence.jpg", name: "Florence", nickname: "'The City of Lilies'" },
    { src: "/static/logo+img/toronto.jpg",  name: "Toronto",  nickname: "'The 6ix'" },
    { src: "/static/logo+img/nashville.jpg",name: "Nashville",nickname: "'The Music City'" },
    { src: "/static/logo+img/tokio.jpg",    name: "Tokyo",    nickname: "'The Eastern Capital'" },
    { src: "/static/logo+img/athens.jpg",   name: "Athens",   nickname: "'The Glorious City'" },
    { src: "/static/logo+img/la.jpg",       name: "Los Angeles", nickname: "'City of Angels'" },
    { src: "/static/logo+img/rome.jpg",     name: "Rome",     nickname: "'The Eternal City'" },
    { src: "/static/logo+img/rio.jpg",      name: "Rio de Janeiro", nickname: "'The Marvelous City'" },
    { src: "/static/logo+img/chicago.jpg",  name: "Chicago",  nickname: "'The Windy City'" },
    { src: "/static/logo+img/paris.jpg",    name: "Paris",    nickname: "'The City of Love'" }
  ];

  // Preload
  photos.forEach(p => { const i = new Image(); i.src = p.src; });

  // Build dots
  dotsContainer.innerHTML = "";
  photos.forEach((_, i) => {
    const dot = document.createElement("div");
    dot.className = "slide-dot" + (i === 0 ? " active" : "");
    dot.addEventListener("click", () => { clearInterval(timer); goTo(i); });
    dotsContainer.appendChild(dot);
  });
  const dots = Array.from(dotsContainer.querySelectorAll(".slide-dot"));

  let index = 0;

  const setCaption = (i) => {
    captionName.textContent = photos[i].name || "";
    captionNickname.textContent = photos[i].nickname || "";
  };

  // Initial state
  imgA.src = photos[index].src;
  imgA.alt = photos[index].name;
  setCaption(index);

  const switchTo = (nextIndex) => {
    const front = container.querySelector(".slide.current");
    const back  = container.querySelector(".slide.next");

    back.src = photos[nextIndex].src;
    back.alt = photos[nextIndex].name;

    // Cross-fade
    front.classList.remove("current");
    front.classList.add("next");
    back.classList.remove("next");
    back.classList.add("current");

    index = nextIndex;
    setCaption(index);
    dots.forEach((d, i) => d.classList.toggle("active", i === index));
  };

  const next = () => switchTo((index + 1) % photos.length);
  const prev = () => switchTo((index - 1 + photos.length) % photos.length);
  const goTo = (i) => switchTo(i);

  let timer = setInterval(next, 3000);

  btnNext.addEventListener("click", () => { clearInterval(timer); next(); });
  btnPrev.addEventListener("click", () => { clearInterval(timer); prev(); });

  container.addEventListener("mouseenter", () => clearInterval(timer));
  container.addEventListener("mouseleave", () => { timer = setInterval(next, 3000); });
});


document.addEventListener("DOMContentLoaded", () => {
  const bars = document.querySelectorAll(".city-bar");
  
  bars.forEach(bar => {
    const score = parseFloat(bar.dataset.score);
    const intensity = Math.max(0, Math.min(1, score / 10)); // 0 to 1
    // HSL: hue=30 (orange), saturation=100%, lightness changes
    const lightness = 80 - (intensity * 40); // from 80% (light) to 40% (dark)
    bar.style.backgroundColor = `hsl(30, 100%, ${lightness}%)`;
  });
});


document.querySelectorAll(".city-bar").forEach(bar => {
  const score = parseInt(bar.getAttribute("data-score"));
  
  // Width proportional to score (max 90%)
  bar.style.width = (score * 9) + "%";
  
  // Orange intensity based on score
  const base = 255 - (score * 10); // Lower score => lighter orange
  bar.style.backgroundColor = `rgb(255, ${180 + score*5}, ${base})`;
});


let averagePrices = {}

// Load prices once from backend
fetch("/average-prices")
  .then(res => res.json())
  .then(data => {
    averagePrices = data;
  });





document.addEventListener("DOMContentLoaded", () => {
  const launcher = document.getElementById("chat-launcher");
  const chatBox = document.getElementById("chat-box");
  const closeChat = document.getElementById("close-chat");
  const chatContent = document.getElementById("chat-content");

  launcher.addEventListener("click", () => {
    chatBox.classList.remove("hidden");
  });

  closeChat.addEventListener("click", () => {
    chatBox.classList.add("hidden");
  });

  // Handle chatbot button clicks
  chatContent.addEventListener("click", (e) => {
    if (e.target.tagName === "BUTTON" && e.target.dataset.choice) {
      const choice = e.target.dataset.choice;
      handleUserChoice(choice);
    }
  });

  function appendBotMessage(messageHTML) {
    const msg = document.createElement("div");
    msg.className = "message bot";
    msg.innerHTML = messageHTML;
    chatContent.appendChild(msg);
    chatContent.scrollTop = chatContent.scrollHeight;
  }

  function handleUserChoice(choice) {
    if (choice === "top3") {
      appendBotMessage(`
        Very nice! I’ll help you with that — just a few quick questions.<br><br>
        <strong>Which continent are you interested in?</strong>
        <div class="option-buttons">
          <button data-choice="Europe">Europe</button>
          <button data-choice="Asia">Asia</button>
          <button data-choice="Africa">Africa</button>
          <button data-choice="Americas">Americas</button>
          <button data-choice="Oceania">Oceania</button>
          <button data-choice="UnknownContinent">I don't know</button>
        </div>
      `);
    } else if (choice === "surprise") {
      appendBotMessage("No worries! I’ll surprise you soon 😄. Stay tuned!");
    } else if (["Europe", "Asia", "Africa", "Americas", "Oceania", "UnknownContinent"].includes(choice)) {
      appendBotMessage(`Great! You're interested in <strong>${choice}</strong>. Next question coming soon...`);
      // You can build step-by-step followups here
    }
  }
});


window.location.href = `/predict.html?city=florence`


  