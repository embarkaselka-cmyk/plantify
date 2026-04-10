# نادي الصحفي الصغير - Newspaper Generator

منصة متكاملة (Backend + Frontend) لإنشاء مقالات عربية بالذكاء الاصطناعي، تصميم جريدة تلقائيًا، وتصدير المجلات بصيغة PDF وPNG.

## ✅ المزايا الأساسية

- توليد مقالات عربية احترافية عبر الذكاء الاصطناعي.
- نظام أنماط AI:
  - **Online**: باستخدام OpenAI API.
  - **Offline**: باستخدام Ollama محليًا بدون إنترنت.
  - **Auto**: تبديل تلقائي بناءً على الاتصال.
- لوحة تحكم عربية RTL لإدارة المقالات.
- تخصيص الهوية البصرية (ألوان + شعار).
- معاينة مباشرة لتنسيق الصحيفة.
- تصدير PDF وPNG بجودة مناسبة للطباعة/المشاركة.

---

## 📁 هيكل المشروع

```text
project-root/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── ai/
│   │   │   ├── online_ai.py
│   │   │   ├── offline_ai.py
│   │   │   ├── ai_manager.py
│   │   ├── routers/
│   │   │   ├── articles.py
│   │   │   ├── magazines.py
│   │   │   ├── users.py
│   │   ├── utils/
│   │   │   ├── pdf_generator.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ArticleEditor.jsx
│   │   │   ├── MagazinePreview.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── ExportManager.jsx
│   │   ├── services/api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │
│   ├── public/index.html
│   ├── package.json
│   ├── vite.config.js
│
└── README.md
```

---

## ⚙️ الإعداد والتشغيل

## 1) Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # على ويندوز: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

سيفتح الخادم على:
- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

## 2) Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

واجهة التطبيق:
- `http://127.0.0.1:5173`

## 3) Offline AI (Ollama)

```bash
# ثبّت Ollama من الموقع الرسمي
ollama pull llama2
ollama serve
```

ثم تأكد أن `.env` في backend يحتوي:

```env
OPENAI_API_KEY=
AI_MODE=auto
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

## 🤖 كيف يعمل الذكاء الاصطناعي

- عند إنشاء مقال، الواجهة ترسل `mode`:
  - `online` أو `offline` أو `auto`.
- في `auto`:
  - إذا كان هناك إنترنت يتم استخدام OpenAI.
  - بدون إنترنت يتم التحويل تلقائيًا إلى Ollama.
- في حال فشل أي مزود، النظام يعيد نصًا احتياطيًا عربيًا للحفاظ على الاستمرارية.

---

## 🔌 أهم الـ API Endpoints

### المقالات
- `GET /articles` جلب المقالات.
- `POST /articles/generate` توليد مقال وحفظه.
- `PUT /articles/{id}` تعديل مقال.
- `DELETE /articles/{id}` حذف مقال.

### المجلات
- `GET /magazines` جلب المجلات.
- `POST /magazines` إنشاء نسخة مجلة.
- `POST /magazines/{id}/export/pdf` تصدير PDF.
- `POST /magazines/{id}/export/png` تصدير PNG.
- `GET /magazines/download?path=...` تنزيل ملف تصدير.

### المستخدمون
- `GET /users`
- `POST /users`

---

## 🧪 مثال استخدام سريع

1. افتح الواجهة.
2. أدخل:
   - اسم الكاتب
   - عنوان المقال
   - الموضوع
   - التصنيف
3. اختر وضع AI (تلقائي/أونلاين/أوفلاين).
4. اضغط **Generate Article**.
5. من لوحة التصدير:
   - **إنشاء نسخة جريدة**
   - ثم **Export PDF** أو **Export PNG**.

---

## 📝 ملاحظات إنتاجية

- SQLite تستخدم للتطوير السريع. يمكن لاحقًا التبديل إلى PostgreSQL.
- معالجة العربية في PDF أساسية؛ يمكن تحسين تشكيل النص عبر `arabic-reshaper` و`python-bidi`.
- يفضل حفظ الشعار في تخزين ملفات دائم في بيئات الإنتاج.

