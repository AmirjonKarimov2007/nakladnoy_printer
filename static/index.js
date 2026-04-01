// =========================
// CACHE BUST & VERSION
// =========================
const CACHE_VERSION = "v2.3.1";
const CACHE_KEY = "picker_cache_version";

// Cache busting
const savedVersion = localStorage.getItem(CACHE_KEY);
if (savedVersion !== CACHE_VERSION) {
  console.log("🔄 Cache busting:", savedVersion, "->", CACHE_VERSION);
  localStorage.setItem(CACHE_KEY, CACHE_VERSION);
  // Force reload
  window.location.reload(true);
}

// =========================
// STATE & CONFIG
// =========================
let foundProducts = [];
let selectedProducts = [];
let excelProductsData = []; // Excel'dan olingan ma'lumotlar (kod, narx, jami)

console.log("✅", CACHE_VERSION, "- Index.js yuklanmoqda...");
console.log("📱 Browser:", navigator.userAgent);

// =========================
// DOM ELEMENTS
// =========================
const themeBtn = document.getElementById("themeBtn");
const excelInput = document.getElementById("excelInput");
const uploadBtn = document.getElementById("uploadBtn");
const statusCard = document.getElementById("statusCard");
const statusContent = document.getElementById("statusContent");
const statusTitle = document.getElementById("statusTitle");
const foundProductsCard = document.getElementById("foundProductsCard");
const foundProductsList = document.getElementById("foundProductsList");
const foundCount = document.getElementById("foundCount");
const continueBtn = document.getElementById("continueBtn");
const resetBtn = document.getElementById("resetBtn");

// DOM elements check
if (!themeBtn || !excelInput || !uploadBtn || !continueBtn) {
  console.error("❌ DOM elementlari topilmadi!");
  console.log("Topilmagan elementlar:", {
    themeBtn: !!themeBtn,
    excelInput: !!excelInput,
    uploadBtn: !!uploadBtn,
    continueBtn: !!continueBtn
  });
  alert("❌ Sahifa yuklanmadi. Yangilang (Ctrl+Shift+R).");
} else {
  console.log("✅ DOM elementlari topildi");
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
// EXCEL UPLOAD
// =========================
uploadBtn.addEventListener("click", () => {
  console.log("📤 Excel upload bosildi");
  excelInput.click();
});

excelInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) {
    console.log("⚠️ Fayl tanlanmadi");
    return;
  }

  console.log("📄 Fayl tanlandi:", {
    name: file.name,
    size: (file.size / 1024).toFixed(2) + " KB",
    type: file.type
  });

  showStatus("📖 Excel o'qilmoqda...", "loading");

  try {
    const excelData = await readExcelFile(file);
    console.log("📊 Excel data:", {
      sheetCount: excelData.length,
      rowSample: excelData.slice(0, 3)
    });

    const excelDataMap = extractExcelColumns(excelData);
    console.log("🔑 Topilgan ma'lumotlar:", {
      count: excelDataMap.length,
      samples: excelDataMap.slice(0, 3)
    });

    if (excelDataMap.length === 0) {
      showStatus("❌ Excel fayl bo'sh yoki B ustuni topilmadi", "error");
      return;
    }

    showStatus(`🔍 ${excelDataMap.length} ta kod topildi, qidirilmoqda...`, "loading");

    // products.json'dan ma'lumot olish
    const productsJsonData = await loadProductsJson();
    console.log("📦 Products JSON:", productsJsonData ? "mavjud" : "yo'q");

    if (!productsJsonData) {
      showStatus("❌ products.json topilmadi. Avval 'Mahsulotlarni yangilash' tugmasini bosing", "error");
      return;
    }

    // Kodlarni taqqoslash (Excel narx va jami bilan)
    const matchedProducts = matchCodes(excelDataMap, productsJsonData);
    console.log("✅ Mos kelgan mahsulotlar:", {
      count: matchedProducts.length,
      sample: matchedProducts.slice(0, 2)
    });

    if (matchedProducts.length === 0) {
      showStatus("❌ Hech qanday mos kelgan mahsulot topilmadi", "error");
      return;
    }

    foundProducts = matchedProducts;
    showStatus("✅ Mahsulotlar topildi! Order yaratilmoqda...", "loading");

    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(100);
    }

    // Avtomatik order yaratish va o'tish
    setTimeout(() => createOrderAndRedirect(), 500);

  } catch (error) {
    console.error("❌ Excel o'qishda xatolik:", error);
    showStatus("❌ Excel o'qishda xatolik: " + error.message, "error");
  }
});

// =========================
// EXCEL FILE READING
// =========================
function readExcelFile(file) {
  console.log("📄 Excel fayl o'qilmoqda...");

  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        // Birinchi worksheet olish
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];

        console.log("📋 Worksheet:", firstSheetName);
        console.log("📊 Range:", worksheet["!ref"]);

        // JSON ga aylantirish
        const jsonData = XLSX.utils.sheet_to_json(worksheet, {
          header: 1,
          defval: null
        });

        console.log("📋 JSON data count:", jsonData.length, "qator");
        resolve(jsonData);
      } catch (error) {
        console.error("❌ Parse error:", error);
        reject(error);
      }
    };

    reader.onerror = (error) => {
      console.error("❌ FileReader error:", error);
      reject(new Error("Fayl o'qishda xatolik"));
    };

    reader.readAsArrayBuffer(file);
  });
}

// =========================
// EXTRACT COLUMNS B, F, H, I (B13 dan boshlab)
// =========================
function extractExcelColumns(jsonData) {
  console.log("📊 B, F, H, I ustunlar o'qilmoqda...");
  const data = [];

  // JSON array indexlari 0 dan boshlanadi, 13-qatordan boshlash (rowIndex >= 12)
  // B = index 1, F = index 5, H = index 7, I = index 8

  jsonData.forEach((row, rowIndex) => {
    // 13-qatordan boshlash (rowIndex >= 12)
    if (rowIndex >= 12) {
      const code = getCellValue(row, 'B');    // B ustun - Kod
      const qty = getCellValue(row, 'F');      // F ustun - Soni
      const price = getCellValue(row, 'H');    // H ustun - Narx
      const total = getCellValue(row, 'I');    // I ustun - Jami narx

      if (code && String(code).trim() !== "") {
        data.push({
          code: String(code).trim(),
          qty: qty ? parseFloat(qty) || 0 : 0,
          price: price ? parseFloat(price) || 0 : 0,
          total: total ? parseFloat(total) || 0 : 0
        });
      }
    }
  });

  console.log("✅ Topilgan ma'lumotlar:", data.length, "ta");
  return data;
}

function getCellValue(row, columnName) {
  // Avval column name bilan urinib ko'raylik
  if (row && row[columnName]) {
    return row[columnName];
  }

  // Agar row bo'lsa bo'lsa, array keys bilan urinib ko'raylik
  if (row && Array.isArray(row)) {
    const columnIndex = columnName.charCodeAt(0) - 'A'.charCodeAt(0);
    if (columnIndex < row.length) {
      return row[columnIndex];
    }
  }

  return null;
}

// =========================
// LOAD PRODUCTS.JSON
// =========================
async function loadProductsJson() {
  console.log("📦 products.json o'qilmoqda...");

  try {
    // Cache busting
    const response = await fetch('../static/products.json?v=' + Date.now());
    if (!response.ok) {
      throw new Error('products.json yuklanmadi');
    }

    // JSON parsing - text() + JSON.parse()
    const text = await response.text();
    console.log("📋 products.json text length:", text.length);

    const data = JSON.parse(text);
    console.log("✅ products.json yuklandi");
    return data;
  } catch (error) {
    console.error("❌ products.json yuklash xatoliki:", error);
    return null;
  }
}

// =========================
// MATCH CODES
// =========================
function matchCodes(excelData, productsJsonData) {
  console.log("🔍 Kodlarni taqqoshamoqda...");
  const matched = [];

  // products.json'dan inventory arrayni olish
  const productsArray = Array.isArray(productsJsonData) ? productsJsonData :
    (productsJsonData.inventory || productsJsonData.products || []);

  console.log("📦 Products array:", productsArray.length, "ta mahsulot");

  excelData.forEach((item, index) => {
    // Excel'dan kod, narx va jami
    const searchTerm = String(item.code).trim().toLowerCase();
    console.log(`🔍 ${index + 1}. Kod qidirilmoqda: "${searchTerm}"`);

    const found = productsArray.find(product => {
      const productCode = String(product.code || "").trim().toLowerCase();
      const productBarcode = String(product.barcodes || "").trim().toLowerCase();
      const productId = String(product.product_id || "").trim().toLowerCase();
      const isMatch = productCode === searchTerm ||
                       productBarcode === searchTerm ||
                       productId === searchTerm;

      if (isMatch) {
        console.log(`✅ ${index + 1}. MATCH: ${searchTerm} = ${product.name || product.short_name}`);
      }

      return isMatch;
    });

    if (found) {
      // Image URL yasash
      const imageUrl = `https://media.githubusercontent.com/media/AmirjonKarimov2007/rasmlar/main/${found.product_id}.jpg`;

      matched.push({
        ...found,
        image_url: imageUrl,
        excel_code: item.code,
        qty: item.qty,          // Excel'dan soni
        price: item.price,      // Excel'dan narx
        total: item.total        // Excel'dan jami narx
      });

      console.log(`✅ ${index + 1}. Kod "${item.code}" topildi:`, found.name || found.short_name, `Soni: ${item.qty}, Narx: ${item.price}, Jami: ${item.total}`);
    } else {
      console.log(`❌ ${index + 1}. Kod "${item.code}" topilmadi`);
    }
  });

  // Topilmagan kodlarni log qilish
  const matchedCodes = matched.map(p => p.excel_code);
  const unmatched = excelData.map(i => i.code).filter(code => !matchedCodes.includes(code));
  if (unmatched.length > 0) {
    console.log("❌ Topilmagan kodlar:", unmatched.length, "ta:", unmatched.slice(0, 5));
  }

  console.log("✅ Mos kelgan mahsulotlar:", matched.length, "ta");
  return matched;
}

// =========================
// SHOW FOUND PRODUCTS
// =========================
function showFoundProducts() {
  console.log("🛒 Mahsulotlar ko'rsatilmoqda...");

  foundCount.textContent = foundProducts.length;
  foundProductsList.innerHTML = "";
  foundProductsCard.style.display = "none"; // Kartochkani yashiramiz, chunki avtomatik o'tadi

  foundProducts.forEach((product, index) => {
    const productCard = document.createElement("article");
    productCard.className = "found-product-card";
    productCard.innerHTML = `
      <div class="found-product-main">
        <div class="found-product-image">
          <img
            src="${product.image_url}"
            alt="${product.name || product.short_name}"
            loading="lazy"
            onerror="this.onerror=null;this.src='https://placehold.co/100x100/1a1a2e/a0a0b0?text=No+Image';"
          />
        </div>
        <div class="found-product-info">
          <div class="found-product-title">${product.name || product.short_name}</div>
          <div class="found-product-details">
            <div class="found-product-detail">
              <span class="detail-label">Kod:</span>
              <span class="detail-value">${product.excel_code}</span>
            </div>
            <div class="found-product-detail">
              <span class="detail-label">Barcode:</span>
              <span class="detail-value">${product.barcodes || "—"}</span>
            </div>
            <div class="found-product-detail">
              <span class="detail-label">Son:</span>
              <span class="detail-value">${product.box_quant || "—"}</span>
            </div>
          </div>
          <div class="found-product-match">
            <span class="match-badge">✅ Mos keladi</span>
          </div>
        </div>
      </div>
    `;

    foundProductsList.appendChild(productCard);
  });

  console.log("✅ Mahsulotlar ko'rsatildi:", foundProducts.length, "ta");
}

// =========================
// STATUS DISPLAY
// =========================
function showStatus(message, type) {
  console.log(`📊 Status [${type}]:`, message);
  statusCard.style.display = "block";
  statusTitle.textContent = "📊 Status";

  if (type === "loading") {
    statusContent.innerHTML = `
      <div class="status-message loading">${message}</div>
      <div class="loading-spinner"></div>
    `;
  } else if (type === "success") {
    statusContent.innerHTML = `
      <div class="status-message success">${message}</div>
    `;
  } else if (type === "error") {
    statusContent.innerHTML = `
      <div class="status-message error">${message}</div>
    `;
  }
}

function hideStatus() {
  statusCard.style.display = "none";
  console.log("🚫 Status yashirildi");
}

// =========================
// CREATE ORDER AND REDIRECT
// =========================
function createOrderAndRedirect() {
  console.log("➡️ Order avtomatik yaratilmoqda...");

  if (foundProducts.length === 0) {
    alert("❌ Avval Excel yuklang va mahsulotlar topilishi kerak");
    return;
  }

  try {
    const dealId = "MANUAL_" + Date.now();
    const order = {
      deal_id: dealId,
      filial_code: "5012602",
      deal_time: new Date().toLocaleString('uz-UZ'),
      items_count: foundProducts.length,
      total_qty: foundProducts.reduce((sum, p) => sum + (parseFloat(p.qty) || 0), 0),
      total_amount: foundProducts.reduce((sum, p) => sum + (parseFloat(p.total) || 0), 0),
      products: foundProducts.map((p, index) => ({
        index: index + 1,
        product_id: p.product_id,
        barcode: p.barcodes || p.code,
        name: p.name || p.short_name,
        qty: parseFloat(p.qty) || 0,       // Excel'dan soni
        price: parseFloat(p.price) || 0,    // Excel'dan narx
        total: parseFloat(p.total) || 0,    // Excel'dan jami narx
        image_url: p.image_url
      }))
    };

    console.log("📝 Order data:", order);

    // localStorage'ga saqlash
    localStorage.setItem(`order_${dealId}`, JSON.stringify(order));
    console.log("✅ Order localStorage'ga saqlandi");

    // Order pagega o'tish
    console.log("➡️ Order pagega o'tilmoqda...");
    window.location.href = `/?order_id=${dealId}`;

  } catch (error) {
    console.error("❌ Order yaratish xatoliki:", error);
    showStatus("❌ Order yaratishda xatolik: " + error.message, "error");
  }
}

// =========================
// CONTINUE TO ORDER (ESKI - ENDI AUTO)
// =========================
continueBtn.addEventListener("click", () => {
  console.log("➡️ Davom etish bosildi");
  createOrderAndRedirect();
});

// =========================
// NORMALIZE ORDER DATA
// =========================
function normalizeOrderData(products) {
  return {
    items_count: products.length,
    total_qty: products.reduce((sum, p) => sum + (parseInt(p.box_quant) || 0), 0),
    total_amount: products.reduce((sum, p) => sum + (parseFloat(p.price) || 0) * (parseInt(p.box_quant) || 0), 0)
  };
}

// =========================
// RESET
// =========================
resetBtn.addEventListener("click", () => {
  console.log("🔄 Qayta boshlash bosildi");

  if (!confirm("Barchani qayta boshlaysizmi?")) return;

  // Inputni tozalash
  excelInput.value = "";

  // Mahsulotlarni tozalash
  foundProducts = [];
  foundProductsCard.style.display = "none";
  foundProductsList.innerHTML = "";
  hideStatus();

  // Haptic feedback
  if (navigator.vibrate) {
    navigator.vibrate([50, 100, 50]);
  }

  console.log("✅ Qayta boshlandi");
});

// =========================
// DRAG & DROP
// =========================
const fileUploadWrapper = document.querySelector(".file-upload-wrapper");

fileUploadWrapper.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileUploadWrapper.classList.add("drag-over");
});

fileUploadWrapper.addEventListener("dragleave", () => {
  fileUploadWrapper.classList.remove("drag-over");
});

fileUploadWrapper.addEventListener("drop", (e) => {
  e.preventDefault();
  console.log("📤 Fayl tashlandi");
  fileUploadWrapper.classList.remove("drag-over");

  const file = e.dataTransfer.files[0];
  if (file) {
    console.log("📄 Tashlangan fayl:", file.name);

    // Input file ni o'zgartirish
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    excelInput.files = dataTransfer.files;

    // Change event trigger qilish
    const event = new Event("change");
    excelInput.dispatchEvent(event);
  }
});

// =========================
// PAGE LOAD
// =========================
console.log("⚡ Index.js to'liq yuklandi v" + CACHE_VERSION);
