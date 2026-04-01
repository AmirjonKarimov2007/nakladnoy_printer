// MANUAL order bo'lsa localStorage'dan olish
let order = window.ORDER_DATA;
const isManualOrder = window.IS_MANUAL_ORDER === true;
const urlParams = new URLSearchParams(window.location.search);
const orderId = urlParams.get("order_id") || "";

if (isManualOrder && !order) {
  try {
    const storageKey = `order_${orderId}`;
    const storedOrder = localStorage.getItem(storageKey);
    if (storedOrder) {
      order = JSON.parse(storedOrder);
      console.log("📦 MANUAL order localStorage'dan yuklandi:", order);
    } else {
      console.warn("❌ MANUAL order topilmadi:", storageKey);
    }
  } catch (e) {
    console.error("❌ MANUAL order o'qishda xatolik:", e);
  }
}

// MANUAL order ma'lumotlarini template'da ko'rsatish
if (isManualOrder && order) {
  // Hero ma'lumotlarini to'ldirish
  const dealIdDisplay = document.getElementById("dealIdDisplay");
  if (dealIdDisplay) dealIdDisplay.textContent = "#" + order.deal_id;

  const filialCodeDisplay = document.getElementById("filialCodeDisplay");
  if (filialCodeDisplay) filialCodeDisplay.textContent = order.filial_code;

  const dealTimeDisplay = document.getElementById("dealTimeDisplay");
  if (dealTimeDisplay) dealTimeDisplay.textContent = order.deal_time;

  // Mahsulotlarni dinamik render qilish
  const productList = document.getElementById("productList");
  if (productList && order.products) {
    productList.innerHTML = "";

    order.products.forEach(product => {
      const card = document.createElement("article");
      card.className = "product-card";
      card.dataset.index = product.index;
      card.dataset.id = product.product_id;
      card.dataset.barcode = product.barcode;
      card.dataset.name = product.name;
      card.dataset.qty = product.qty;
      card.dataset.boxQuant = product.box_quant || 0;
      card.dataset.price = product.price;
      card.dataset.total = product.total;

      card.innerHTML = `
        <div class="product-topline">
          <div class="line-left">
            <span class="badge">#${product.index}</span>
            <span class="barcode-badge">${product.barcode}</span>
          </div>
        </div>

        <div class="product-main">
          <div class="img-wrap" onclick="openLightbox(this)" role="button" tabindex="0" aria-label="${product.name} rasmini ko'rish">
            <img
              class="product-img"
              src="${product.image_url}"
              alt="${product.name}"
              loading="lazy"
              onerror="this.onerror=null;this.src='https://placehold.co/400x400/1a1a2e/a0a0b0?text=No+Image';"
            />
          </div>

          <div class="content-col">
            <div class="product-title">${product.name}</div>

            <div class="meta-grid">
              <div class="mini-box">
                <span>Soni</span>
                <b>${formatQty(product.qty, parseInt(product.box_quant) || 0)}</b>
              </div>
              <div class="mini-box">
                <span>Narxi</span>
                <b>${product.price}</b>
              </div>
              <div class="mini-box total">
                <span>Jami</span>
                <b>${product.total}</b>
              </div>
            </div>

            <div class="status-actions">
              <button class="status-btn success status-pick" data-status="picked" aria-label="Yig'ildi">
                ✅ Yig'ildi
              </button>
              <button class="status-btn danger status-not-found" data-status="not_found" aria-label="Topilmadi">
                ❌ Topilmadi
              </button>
              <button class="status-btn warn status-partial" data-status="partial" aria-label="Kam chiqdi">
                ⚠️ Kam
              </button>
              <button class="status-btn info status-replaced" data-status="replaced" aria-label="Almashtirildi">
                🔄 Alma
              </button>
            </div>

            <div class="status-line">
              <span class="status-label">Status:</span>
              <span class="status-value">Kutilmoqda</span>
            </div>
          </div>
        </div>
      `;

      productList.appendChild(card);
    });

    console.log("✅ MANUAL order mahsulotlari render qilindi:", order.products.length, "ta");
  }
}

if (order) {
  // =========================
  // DOM
  // =========================
  const searchInput = document.getElementById("searchInput");
  const resetAllBtn = document.getElementById("resetAllBtn");
  const themeBtn = document.getElementById("themeBtn");

  const productCards = [...document.querySelectorAll(".product-card")];

  // =========================
  // STATE
  // =========================
  const STORAGE_KEY = `spiska_promax_${order.deal_id}`;

  const statusMap = {
    pending: "Kutilmoqda",
    picked: "Yig'ildi",
    not_found: "Topilmadi",
    partial: "Kam chiqdi",
    replaced: "Almashtirildi",
  };

  // =========================
  // HELPERS
  // =========================
  function formatNumber(n) {
    return Number(n || 0).toLocaleString("uz-UZ");
  }

  function formatMoney(n) {
    return `${formatNumber(n)} so'm`;
  }

  function formatQty(qty, boxQuant) {
    if (!boxQuant || boxQuant === 0) {
      return `${formatNumber(qty)} dona`;
    }
    const karobka = Math.floor(qty / boxQuant);
    const qolgan = qty % boxQuant;
    if (qolgan > 0) {
      return `${formatNumber(karobka)} karobka ${formatNumber(qolgan)} dona`;
    } else {
      return `${formatNumber(karobka)} karobka`;
    }
  }

  function getStorage() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
      return {};
    }
  }

  function setStorage(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function getCardKey(card) {
    return card.dataset.barcode || card.dataset.id || card.dataset.index;
  }

  function getCardState(card) {
    const storage = getStorage();
    const key = getCardKey(card);
    return storage[key] || { status: "pending", worker: "" };
  }

  function saveCardState(card, state) {
    const storage = getStorage();
    const key = getCardKey(card);
    storage[key] = state;
    setStorage(storage);
  }

  function isCompletedStatus(status) {
    return ["picked", "not_found", "partial", "replaced"].includes(status);
  }

  // =========================
  // THEME
  // =========================
  const savedTheme = localStorage.getItem("picker_theme");
  if (savedTheme === "light") {
    document.body.classList.add("light");
    themeBtn.textContent = "☀️";
  } else {
    themeBtn.textContent = "🌙";
  }

  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    localStorage.setItem("picker_theme", isLight ? "light" : "dark");
    themeBtn.textContent = isLight ? "☀️" : "🌙";

    // Meta theme color yangilash
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute("content", isLight ? "#f8fafc" : "#0a0a14");
    }
  });

  // =========================
  // CARD STATE APPLY
  // =========================
  function applyStateToCard(card, state) {
    card.classList.remove("status-picked", "status-not_found", "status-partial", "status-replaced");

    if (state.status && state.status !== "pending") {
      card.classList.add(`status-${state.status}`);
    }

    const statusValue = card.querySelector(".status-value");
    if (statusValue) statusValue.textContent = statusMap[state.status] || "Kutilmoqda";
  }

  function loadSavedStates() {
    productCards.forEach(card => {
      const state = getCardState(card);
      applyStateToCard(card, state);
    });
  }

  // =========================
  // SET STATUS
  // =========================
  function setCardStatus(card, status) {
    const newState = { status, worker: "" };

    saveCardState(card, newState);
    applyStateToCard(card, newState);
    applyFilters();
    updateAnalytics();

    // Haptic feedback (agar qo'llab bo'lsa)
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }
  }

  function bindStatusButtons() {
    productCards.forEach(card => {
      const buttons = card.querySelectorAll(".status-btn");
      buttons.forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const status = btn.dataset.status;
          setCardStatus(card, status);
        });
      });
    });
  }

  // =========================
  // FILTERS
  // =========================
  function applyFilters() {
    const q = (searchInput.value || "").trim().toLowerCase();

    productCards.forEach(card => {
      const name = (card.dataset.name || "").toLowerCase();
      const barcode = (card.dataset.barcode || "").toLowerCase();

      const matchesSearch = !q || name.includes(q) || barcode.includes(q);
      card.style.display = matchesSearch ? "" : "none";
    });
  }

  let searchTimeout;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      applyFilters();
      updateAnalytics();
    }, 150);
  });

  // =========================
  // CSV EXPORT
  // =========================
  function exportCSV() {
    const rows = [];
    rows.push([
      "Index",
      "Barcode",
      "Mahsulot",
      "Soni",
      "Narxi",
      "Jami",
      "Status"
    ]);

    productCards.forEach(card => {
      const state = getCardState(card);

      // Karobka formatlash
      let qtyDisplay = card.dataset.qty || "";
      const boxQuant = card.dataset.boxQuant || "0";
      if (boxQuant && boxQuant !== "0") {
        const qty = parseFloat(card.dataset.qty) || 0;
        const bq = parseFloat(boxQuant);
        const karobka = Math.floor(qty / bq);
        const qolgan = qty % bq;
        if (qolgan > 0) {
          qtyDisplay = `${karobka} karobka ${qolgan} dona`;
        } else {
          qtyDisplay = `${karobka} karobka`;
        }
      }

      rows.push([
        card.dataset.index || "",
        card.dataset.barcode || "",
        card.dataset.name || "",
        qtyDisplay,
        card.dataset.price || "",
        card.dataset.total || "",
        statusMap[state.status] || "Kutilmoqda"
      ]);
    });

    const csvContent = rows
      .map(row => row.map(value => `"${String(value).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `spiska_${order.deal_id}_report.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  }

  // =========================
  // PRINT / PDF
  // =========================
  function printReport() {
    const reportRows = productCards.map(card => {
      const state = getCardState(card);
      return `
        <tr>
          <td>${card.dataset.index || ""}</td>
          <td>${card.dataset.barcode || ""}</td>
          <td>${card.dataset.name || ""}</td>
          <td>${card.dataset.qty || ""}</td>
          <td>${card.dataset.price || ""}</td>
          <td>${card.dataset.total || ""}</td>
          <td>${statusMap[state.status] || "Kutilmoqda"}</td>
        </tr>
      `;
    }).join("");

    const html = `
      <html>
      <head>
        <title>Spiska Report #${order.deal_id}</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 40px;
            color: #111;
            background: #fff;
          }
          h1 {
            margin-bottom: 10px;
            font-size: 24px;
            font-weight: 800;
            color: #1a1a1a;
          }
          .meta {
            margin-bottom: 20px;
            color: #444;
            font-size: 14px;
            line-height: 1.6;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 20px;
          }
          th, td {
            border: 1px solid #e5e7eb;
            padding: 12px 8px;
            text-align: left;
          }
          th {
            background: #f9fafb;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
          tr:nth-child(even) {
            background: #f9fafb;
          }
          @media print {
            body {
              padding: 20px;
            }
            .no-print {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        <h1>📦 Spiska Report #${order.deal_id}</h1>
        <div class="meta">
          <strong>Filial:</strong> ${order.filial_code} <br/>
          <strong>Sana:</strong> ${order.deal_time} <br/>
          <strong>Jami qator:</strong> ${order.items_count} <br/>
          <strong>Jami dona:</strong> ${formatNumber(order.total_qty)} <br/>
          <strong>Umumiy summa:</strong> ${formatMoney(order.total_amount)}
        </div>

        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Barcode</th>
              <th>Mahsulot</th>
              <th>Soni</th>
              <th>Narxi</th>
              <th>Jami</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${reportRows}
          </tbody>
        </table>
      </body>
      </html>
    `;

    const w = window.open("", "_blank");
    w.document.write(html);
    w.document.close();
    w.focus();
    w.print();
  }

  // =========================
  // UPDATE PRODUCTS (Vaqt cheklovi: 00:00 - 09:00 orasida ishlash)
  // =========================
  function isUpdateTimeAllowed() {
    const now = new Date();
    const hour = now.getHours();
    // Faqat tundan 00:00 dan ertalab 09:00 gacha ishlash
    return hour >= 0 && hour < 9;
  }

  function updateProducts() {
    // Vaqt tekshirish
    if (!isUpdateTimeAllowed()) {
      alert("⏰ Mahsulotlarni yangilash faqat tundan 00:00 dan ertalab 09:00 gacha mumkin!");
      return;
    }

    fetch("/api/update-products")
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          alert("✅ " + data.message);
          // Sahifani yangilash
          setTimeout(() => {
            location.reload();
          }, 1000);
        } else {
          alert("❌ " + data.message);
        }
      })
      .catch(error => {
        console.error("Xatolik:", error);
        alert("❌ Xatolik yuz berdi. Internetni tekshiring.");
      });
  }

  // =========================
  // RESET ALL
  // =========================
  resetAllBtn.addEventListener("click", () => {
    if (!confirm("Barcha mahsulotlar statusini tozalashni xohlaysizmi?")) return;

    productCards.forEach(card => {
      const resetState = { status: "pending", worker: "" };
      saveCardState(card, resetState);
      applyStateToCard(card, resetState);
    });
    updateAnalytics();

    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate([50, 100, 50]);
    }
  });

  // =========================
  // ANALYTICS
  // =========================
  function updateAnalytics() {
    let picked = 0;
    let notFound = 0;
    let partial = 0;
    let replaced = 0;

    productCards.forEach(card => {
      const state = getCardState(card);

      if (state.status === "picked") picked++;
      if (state.status === "not_found") notFound++;
      if (state.status === "partial") partial++;
      if (state.status === "replaced") replaced++;
    });

    const totalRows = productCards.length;
    const completed = picked + notFound + partial + replaced;
    const remaining = totalRows - completed;
    const percent = totalRows ? Math.round((completed / totalRows) * 100) : 0;

    document.getElementById("statRows").textContent = totalRows;
    document.getElementById("statQty").textContent = formatNumber(order.total_qty);
    document.getElementById("statAmount").textContent = formatMoney(order.total_amount);
    document.getElementById("statCompleted").textContent = `${percent}%`;

    document.getElementById("pickedRows").textContent = `${completed} / ${totalRows}`;
    document.getElementById("remainingRows").textContent = remaining;
    document.getElementById("notFoundCount").textContent = notFound;
    document.getElementById("partialCount").textContent = partial;

    document.getElementById("progressText").textContent = `${percent}%`;
    document.getElementById("progressFill").style.width = `${percent}%`;

    // Progress colorni yangilash
    const progressFill = document.getElementById("progressFill");
    if (percent === 100) {
      progressFill.style.background = "var(--gradient-success)";
    } else if (percent >= 75) {
      progressFill.style.background = "var(--gradient-info)";
    } else if (percent >= 50) {
      progressFill.style.background = "var(--gradient-warning)";
    } else {
      progressFill.style.background = "var(--gradient-primary)";
    }
  }

  // =========================
  // LIGHTBOX
  // =========================
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightboxImg");
  const lightboxTitle = document.getElementById("lightboxTitle");
  const lightboxBarcode = document.getElementById("lightboxBarcode");
  const lightboxPrev = document.getElementById("lightboxPrev");
  const lightboxNext = document.getElementById("lightboxNext");

  let currentCardIndex = -1;

  function openLightbox(imgWrap) {
    const card = imgWrap.closest(".product-card");
    const img = imgWrap.querySelector(".product-img");
    const name = card.dataset.name || "Mahsulot";
    const barcode = card.dataset.barcode || "—";

    // Hozirgi kartani indeksini topish
    currentCardIndex = productCards.findIndex(c => c === card);

    updateLightboxContent(img, name, barcode);
    updateNavigationButtons();
    lightbox.classList.add("active");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    // Rasmni yuklash animatsiyasi
    lightboxImg.style.opacity = "0";
    setTimeout(() => {
      lightboxImg.style.opacity = "1";
    }, 50);
  }

  function updateLightboxContent(img, name, barcode) {
    lightboxImg.src = img.src;
    lightboxImg.alt = name;
    lightboxTitle.textContent = name;
    lightboxBarcode.textContent = `Barcode: ${barcode}`;

    // Tugmalarni yangilash
    updateNavigationButtons();
  }

  function updateNavigationButtons() {
    // Birinchi kartada bo'lsa, prev tugmasi yashirish
    if (lightboxPrev) {
      lightboxPrev.style.display = currentCardIndex === 0 ? "none" : "flex";
    }

    // Oxirgi kartada bo'lsa, next tugmasi yashirish
    if (lightboxNext) {
      lightboxNext.style.display = currentCardIndex === productCards.length - 1 ? "none" : "flex";
    }
  }

  function navigateLightbox(e, direction) {
    if (e) e.stopPropagation();

    // Yangi indeksni hisoblash
    currentCardIndex += direction;

    // Cheklovlar
    if (currentCardIndex < 0) {
      currentCardIndex = 0; // Birinchi kartada qolish
      return;
    }

    if (currentCardIndex >= productCards.length) {
      currentCardIndex = productCards.length - 1; // Oxirgi kartada qolish
      return;
    }

    const nextCard = productCards[currentCardIndex];
    const img = nextCard.querySelector(".product-img");
    const name = nextCard.dataset.name || "Mahsulot";
    const barcode = nextCard.dataset.barcode || "—";

    // Rasmni almashtirish animatsiyasi
    lightboxImg.style.opacity = "0";
    setTimeout(() => {
      updateLightboxContent(img, name, barcode);
      lightboxImg.style.opacity = "1";
    }, 150);
  }

  function closeLightbox(e) {
    if (e) e.stopPropagation();
    lightbox.classList.remove("active");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    currentCardIndex = -1;
  }

  // Tugmalar uchun event listenerlar
  if (lightboxPrev) {
    lightboxPrev.addEventListener("click", (e) => navigateLightbox(e, -1));
  }

  if (lightboxNext) {
    lightboxNext.addEventListener("click", (e) => navigateLightbox(e, 1));
  }

  // Klaviatura navigatsiyasi
  document.addEventListener("keydown", (e) => {
    if (!lightbox.classList.contains("active")) return;

    if (e.key === "Escape") {
      closeLightbox();
    } else if (e.key === "ArrowLeft") {
      navigateLightbox(null, -1);
    } else if (e.key === "ArrowRight") {
      navigateLightbox(null, 1);
    }
  });

  lightbox.querySelector(".lightbox-content").addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // =========================
  // SWIPE NAVIGATSIIYASI (MOBILE)
  // =========================
  let touchStartX = 0;
  let touchEndX = 0;

  lightbox.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightbox.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        // Chapga surish - keyingi rasm
        navigateLightbox(null, 1);
      } else {
        // O'ngga surish - oldingi rasm
        navigateLightbox(null, -1);
      }
    }
  }

  // =========================
  // IMAGE LAZY LOADING
  // =========================
  function initLazyLoading() {
    const images = document.querySelectorAll(".product-img[data-src]");
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute("data-src");
          observer.unobserve(img);
        }
      });
    });

    images.forEach(img => {
      imageObserver.observe(img);
    });
  }

  // =========================
  // INIT
  // =========================
  // MANUAL order bo'lsa, productCardsni yangilash
  if (isManualOrder) {
    productCards.length = 0;
    const cards = document.querySelectorAll(".product-card");
    productCards.push(...cards);
    console.log("📦 ProductCards yangilandi:", productCards.length, "ta");
  }

  loadSavedStates();
  bindStatusButtons();
  applyFilters();
  updateAnalytics();
  initLazyLoading();

  // Page load animatsiyasi
  document.body.style.opacity = "0";
  setTimeout(() => {
    document.body.style.transition = "opacity 0.5s ease";
    document.body.style.opacity = "1";
  }, 100);

  // Product countni yangilash
  const productCountEl = document.getElementById("productCount");
  if (productCountEl) {
    productCountEl.textContent = `(${productCards.length} ta)`;
  }

  // Service Worker uchun support (agar kerak bo'lsa)
  if ('serviceWorker' in navigator) {
    // Offline support qo'shish mumkin
    console.log('Service Worker supported');
  }
}
