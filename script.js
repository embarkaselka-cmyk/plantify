const defaultLogo =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect width='100%25' height='100%25' fill='%23111111'/%3E%3Ccircle cx='150' cy='150' r='130' fill='none' stroke='%23ff5a1f' stroke-width='10'/%3E%3Ctext x='50%25' y='47%25' fill='white' font-size='30' font-family='Arial' text-anchor='middle'%3EYoung%3C/text%3E%3Ctext x='50%25' y='60%25' fill='%23ff5a1f' font-size='30' font-family='Arial' text-anchor='middle'%3EJournalists%3C/text%3E%3C/svg%3E";

const arabicLogo =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect width='100%25' height='100%25' fill='%23ffffff'/%3E%3Ccircle cx='150' cy='150' r='140' fill='%2377addf'/%3E%3Ccircle cx='150' cy='150' r='110' fill='%230a0a0a' stroke='%23ffff00' stroke-width='14'/%3E%3Ctext x='50%25' y='22%25' fill='white' font-size='24' font-family='Cairo, Arial' text-anchor='middle'%3Eالصحفي الصغير%3C/text%3E%3Ctext x='50%25' y='84%25' fill='%23ffe351' font-size='21' font-family='Cairo, Arial' text-anchor='middle'%3EYoung Journalists Club%3C/text%3E%3C/svg%3E";

const form = document.getElementById("articleForm");
const articleQueueEl = document.getElementById("articleQueue");
const previewRoot = document.getElementById("previewRoot");
const generateArticleBtn = document.getElementById("generateArticleBtn");
const generateMagazineBtn = document.getElementById("generateMagazineBtn");
const exportPdfBtn = document.getElementById("exportPdfBtn");
const clubLogo = document.getElementById("clubLogo");
const statusMessage = document.getElementById("statusMessage");

let articles = [];
let imageCache = null;

clubLogo.src = arabicLogo || defaultLogo;
document.getElementById("year").textContent = new Date().getFullYear();

form.image.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) {
    imageCache = null;
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    imageCache = reader.result;
  };
  reader.readAsDataURL(file);
});

const persistedApiKey = localStorage.getItem("yjc_openai_api_key");
if (persistedApiKey) form.apiKey.value = persistedApiKey;

generateArticleBtn.addEventListener("click", async () => {
  generateArticleBtn.disabled = true;
  setStatus("Generating article...");

  try {
    const provider = form.aiProvider.value;
    const aiText =
      provider === "openai" ? await generateWithOpenAI() : generateSmartLocalArticle();

    form.content.value = aiText;
    setStatus(`Article generated via ${provider === "openai" ? "OpenAI API" : "Smart Local AI"}.`);
    flashButton(generateArticleBtn);
  } catch (error) {
    setStatus(`AI generation failed: ${error.message}`);
  } finally {
    generateArticleBtn.disabled = false;
  }
});

form.addEventListener("submit", (e) => {
  e.preventDefault();

  const article = {
    id: crypto.randomUUID(),
    title: form.title.value.trim(),
    author: form.author.value.trim(),
    category: form.category.value.trim(),
    content: form.content.value.trim(),
    location: form.location.value.trim(),
    date: form.date.value,
    image: imageCache,
  };

  if (!article.title || !article.author || !article.content) return;

  articles.unshift(article);
  renderQueue();
  form.reset();
  imageCache = null;
});

generateMagazineBtn.addEventListener("click", () => {
  if (!articles.length) {
    previewRoot.innerHTML = `<div class="placeholder"><h3>No articles yet</h3><p>Please add at least one article first.</p></div>`;
    return;
  }

  const main = articles[0];
  const featured = articles.slice(1, 4);

  previewRoot.innerHTML = `
    <article class="newspaper" contenteditable="true">
      <header class="news-header">
        <div>
          <h2>YJC MAGAZINE // NEXT EDITION</h2>
          <p style="color:#cfcfcf; font-size:.85rem;">Category Focus: ${escapeHtml(main.category)}</p>
        </div>
        <img src="${clubLogo.src}" alt="Club logo" style="width:56px;height:56px;border-radius:50%;"/>
      </header>

      <div class="breaking">⚡ BREAKING NEWS • LIVE FROM THE YOUNG JOURNALISTS CLUB</div>

      <div class="story-grid">
        <section class="main-story">
          <h2>${escapeHtml(main.title)}</h2>
          <div class="meta">
            <span>✍️ ${escapeHtml(main.author)}</span>
            <span>📍 ${escapeHtml(main.location)}</span>
            <span>🗓️ ${formatDate(main.date)}</span>
          </div>
          ${main.image ? `<img class="feature-image" src="${main.image}" alt="Article visual" />` : ""}
          <div class="story-content">${escapeHtml(main.content).replace(/\n/g, "<br>")}</div>
        </section>

        <aside class="sidebar">
          <h3>Featured Stories</h3>
          ${
            featured.length
              ? featured
                  .map(
                    (item, idx) => `
                <div class="side-card">
                  <small style="color:#ff9c77;">FEATURED #${idx + 1}</small>
                  <h4>${escapeHtml(item.title)}</h4>
                  <p style="color:#d0d0d0; font-size:.9rem; margin-top:.35rem;">
                    ${truncate(escapeHtml(item.content), 130)}
                  </p>
                </div>
              `,
                  )
                  .join("")
              : `<div class="side-card"><p>Add more articles to populate featured section.</p></div>`
          }
        </aside>
      </div>

      <footer class="page-no">Page 1 • Young Journalists Club Digital Press</footer>
    </article>
  `;

  flashButton(generateMagazineBtn);
});

exportPdfBtn.addEventListener("click", async () => {
  const node = previewRoot.querySelector(".newspaper");
  if (!node) {
    setStatus("Please generate the magazine first.");
    return;
  }

  try {
    await ensurePdfLibrary();
    const opt = {
      margin: 0.3,
      filename: `young-journalists-magazine-${Date.now()}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
    };

    await html2pdf().from(node).set(opt).save();
    setStatus("PDF exported successfully.");
    flashButton(exportPdfBtn);
  } catch (error) {
    setStatus("PDF library blocked. Opening print dialog as fallback.");
    window.print();
  }
});

function renderQueue() {
  articleQueueEl.innerHTML = articles
    .map(
      (a, i) => `
      <li>
        <strong>${i + 1}. ${escapeHtml(a.title)}</strong>
        <p style="margin-top:.25rem; color:#ffb095; font-size:.84rem;">${escapeHtml(a.author)} • ${escapeHtml(
        a.category,
      )}</p>
      </li>
    `,
    )
    .join("");
}

function flashButton(btn) {
  btn.animate(
    [
      { transform: "translateY(0)", filter: "brightness(1)" },
      { transform: "translateY(-2px)", filter: "brightness(1.3)" },
      { transform: "translateY(0)", filter: "brightness(1)" },
    ],
    { duration: 350, easing: "ease-out" },
  );
}

function truncate(str, length) {
  return str.length > length ? `${str.slice(0, length)}…` : str;
}

function formatDate(dateValue) {
  if (!dateValue) return "N/A";
  const d = new Date(dateValue);
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.innerText = value || "";
  return div.innerHTML;
}

function setStatus(message) {
  statusMessage.textContent = message;
}

function generateSmartLocalArticle() {
  const title = form.title.value.trim() || "Untitled Headline";
  const author = form.author.value.trim() || "Staff Reporter";
  const category = form.category.value.trim() || "General";
  const location = form.location.value.trim() || "Local Desk";
  const dateText = formatDate(form.date.value);
  const base = form.content.value.trim();

  const opener = `In ${location}, the Young Journalists Club investigated a developing ${category.toLowerCase()} story under the headline "${title}."`;
  const body = `Student reporters interviewed sources, verified details, and assembled a fact-checked narrative with clear context for readers. The team highlighted why this event matters now, who is affected, and what outcomes to watch next.`;
  const closer = `Filed by ${author} on ${dateText}, this report emphasizes ethical journalism, transparency, and community impact while inviting readers to engage with the next edition.`;
  const callout = `Breaking Insight: Youth-led media teams can turn curiosity into credible reporting when they combine field observation, interviews, and evidence-based writing.`;

  return [base, opener, body, closer, callout].filter(Boolean).join("\n\n");
}

async function generateWithOpenAI() {
  const apiKey = form.apiKey.value.trim();
  if (!apiKey) {
    throw new Error("No API key provided. Add a key or switch to Smart Local AI.");
  }
  localStorage.setItem("yjc_openai_api_key", apiKey);

  const prompt = {
    title: form.title.value.trim(),
    author: form.author.value.trim(),
    category: form.category.value.trim(),
    location: form.location.value.trim(),
    date: form.date.value || new Date().toISOString().slice(0, 10),
    content: form.content.value.trim(),
  };

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: form.aiModel.value.trim() || "gpt-4o-mini",
      temperature: 0.8,
      messages: [
        {
          role: "system",
          content:
            "You are a professional magazine editor. Generate a polished news article in 4-6 paragraphs with factual tone and engaging style.",
        },
        {
          role: "user",
          content: `Write an article with these fields: ${JSON.stringify(prompt)}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenAI API error (${response.status}): ${text.slice(0, 120)}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content?.trim() || generateSmartLocalArticle();
}

async function ensurePdfLibrary() {
  if (typeof html2pdf === "function") return;
  await loadScript("https://unpkg.com/html2pdf.js@0.10.1/dist/html2pdf.bundle.min.js");
  if (typeof html2pdf !== "function") {
    throw new Error("html2pdf unavailable");
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

(function particleBackground() {
  const canvas = document.getElementById("particle-canvas");
  const ctx = canvas.getContext("2d");
  const particles = [];
  const particleCount = 70;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function createParticle() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2 + 0.5,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      alpha: Math.random() * 0.6 + 0.2,
    };
  }

  function init() {
    resize();
    particles.length = 0;
    for (let i = 0; i < particleCount; i += 1) particles.push(createParticle());
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 90, 31, ${p.alpha})`;
      ctx.shadowBlur = 12;
      ctx.shadowColor = "#ff5a1f";
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", init);
  init();
  draw();
})();
