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

generateArticleBtn.addEventListener("click", () => {
  const moodLines = [
    "In a bold development, young reporters uncovered details that reshape the community narrative.",
    "Eyewitnesses describe the scene as energetic, hopeful, and full of possibility for local youth.",
    "Experts believe this momentum can inspire a new generation of ethical media creators.",
  ];

  const base = form.content.value.trim();
  const generated = `${base ? base + "\n\n" : ""}${moodLines.join(" ")}`;
  form.content.value = generated;
  flashButton(generateArticleBtn);
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
  if (!node) return;

  const opt = {
    margin: 0.3,
    filename: `young-journalists-magazine-${Date.now()}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
  };

  await html2pdf().from(node).set(opt).save();
  flashButton(exportPdfBtn);
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
