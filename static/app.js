const imageInput = document.getElementById("imageInput");
const notesInput = document.getElementById("notes");
const analyzeBtn = document.getElementById("analyzeBtn");
const preview = document.getElementById("preview");
const previewHint = document.getElementById("previewHint");
const results = document.getElementById("results");

imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    preview.src = reader.result;
    preview.hidden = false;
    previewHint.hidden = true;
  };
  reader.readAsDataURL(file);
});

analyzeBtn.addEventListener("click", async () => {
  const file = imageInput.files?.[0];
  if (!file) {
    results.innerHTML = '<p class="warning">يرجى اختيار صورة أولاً.</p>';
    return;
  }

  const bitmap = await createImageBitmap(file);
  const canvas = document.createElement("canvas");
  canvas.width = 180;
  canvas.height = 180;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
  let greenDominant = 0;
  let yellowish = 0;
  let brownish = 0;
  let brightSum = 0;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i] / 255;
    const g = data[i + 1] / 255;
    const b = data[i + 2] / 255;

    brightSum += (r + g + b) / 3;
    if (g > r && g > b) greenDominant += 1;
    if (r > 0.6 && g > 0.55 && b < 0.35) yellowish += 1;
    if (r > 0.35 && g > 0.2 && g < 0.45 && b < 0.25) brownish += 1;
  }

  const px = data.length / 4;
  const score = {
    green: greenDominant / px,
    yellow: yellowish / px,
    brown: brownish / px,
    brightness: brightSum / px,
  };

  const findings = [];

  if (score.brown > 0.12) {
    findings.push({
      title: "احتمال جفاف أو احتراق أطراف الأوراق",
      confidence: Math.min(95, Math.round(55 + score.brown * 160)),
      explanation: "تظهر نسب بنية أعلى من الطبيعي في الصورة.",
      actions: ["افحص رطوبة التربة قبل الري.", "قلل الشمس المباشرة وقت الظهيرة.", "ارفع الرطوبة حول النبات."],
    });
  }

  if (score.yellow > 0.16) {
    findings.push({
      title: "احتمال اصفرار بسبب ري زائد أو نقص تغذية",
      confidence: Math.min(92, Math.round(50 + score.yellow * 160)),
      explanation: "تم رصد مناطق صفراء واضحة في الأوراق.",
      actions: ["خفف الري وتأكد من التصريف.", "استخدم سماد متوازن بجرعة خفيفة.", "أزل الأوراق التالفة."],
    });
  }

  if (score.green < 0.22) {
    findings.push({
      title: "انخفاض الحيوية العامة",
      confidence: Math.round(50 + (0.22 - score.green) * 180),
      explanation: "المساحة الخضراء أقل من المتوقع وقد تعني إجهادًا عامًا.",
      actions: ["حسن الإضاءة غير المباشرة.", "افحص الجذور واحتمال تزاحمها.", "راجع وجود آفات أسفل الأوراق."],
    });
  }

  if (score.brightness < 0.25) {
    findings.push({
      title: "إضاءة ضعيفة",
      confidence: 70,
      explanation: "الصورة داكنة وربما بيئة النبات كذلك.",
      actions: ["وفر إضاءة أفضل 6-8 ساعات حسب النوع.", "نظف الأوراق من الغبار."],
    });
  }

  const notes = notesInput.value.trim();
  if (/(حشرات|سوس|من|عناكب|بقع)/.test(notes)) {
    findings.push({
      title: "احتمال وجود آفات",
      confidence: 65,
      explanation: "ملاحظاتك تتوافق مع أعراض آفات نباتية.",
      actions: ["اعزل النبتة مؤقتًا.", "اغسل الأوراق بماء فاتر.", "استخدم صابون زراعي أو زيت نيم."],
    });
  }

  if (!findings.length) {
    findings.push({
      title: "النبتة تبدو بصحة جيدة",
      confidence: 82,
      explanation: "لا توجد مؤشرات قوية لمشكلة واضحة في الصورة.",
      actions: ["استمر على جدول الري الحالي.", "لف الأصيص أسبوعيًا لتوزيع الضوء.", "استمر في المراقبة الدورية."],
    });
  }

  findings.sort((a, b) => b.confidence - a.confidence);

  results.innerHTML = findings
    .map(
      (f) => `
      <article class="finding">
        <h3>${f.title} (ثقة ${f.confidence}%)</h3>
        <p>${f.explanation}</p>
        <ul>${f.actions.map((a) => `<li>${a}</li>`).join("")}</ul>
      </article>
    `,
    )
    .join("");
});
