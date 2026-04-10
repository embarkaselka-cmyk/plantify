# Smart Newspaper Generator - Young Journalists Club

تطبيق مكتبي احترافي لإنشاء صحيفة/مجلة رقمية عربية بتصميم شبيه بالصحف الواقعية، مع دعم RTL وتوليد مقالات ونظام حفظ مشاريع وتصدير PDF.

## Structure

- `main.py`
- `ui/main_window.py`
- `logic/models.py`
- `logic/storage.py`
- `logic/ai_generator.py`
- `templates/newspaper_template.py`
- `exporter/pdf_exporter.py`
- `assets/`
- `data/`

## Features

- واجهة حديثة Light/Dark
- هوية بصرية قابلة للتخصيص (Primary/Secondary)
- دعم لوجو النادي (زر اختيار صورة)
- إدخال بيانات المقال كاملة
- توليد/تحسين المقال بالعربية (OpenAI Placeholder)
- عدة مقالات في نفس العدد
- سحب وإفلات الصور (Drag & Drop)
- شارة Breaking News اختيارية
- معاينة داخل التطبيق قبل التصدير
- تصدير PDF عالي الجودة
- حفظ/تحميل المشاريع JSON

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build Windows EXE

### Option 1 (with spec)
```bash
pyinstaller SmartNewspaperGenerator.spec
```

### Option 2 (one command)
```bash
pyinstaller --noconfirm --windowed --name SmartNewspaperGenerator \
  --add-data "assets;assets" --add-data "templates;templates" --add-data "data;data" main.py
```

> ملف التنفيذ النهائي يظهر في `dist/SmartNewspaperGenerator/`.

## OpenAI Integration Placeholder

عدّل الملف `logic/ai_generator.py` لإضافة استدعاء OpenAI API الحقيقي عند توفر المفتاح.

## Logo Note

تم إضافة `assets/club_logo_placeholder.svg` بشكل افتراضي. لاستعمال شعار النادي المرفق منكم بدقة، ضع ملف الشعار بصيغة PNG في:

`assets/club_logo.png`

ثم اختره من زر **اختيار لوجو النادي** داخل التطبيق.

## Example Usage

1. أدخل عنوان المقال واسم الكاتب والمحتوى.
2. اضغط **Generate Article** لتحسين الصياغة.
3. أضف صوراً بالسحب والإفلات.
4. اضغط **إضافة المقال إلى العدد**.
5. كرر لإضافة أكثر من مقال.
6. اضغط **Generate Newspaper** للمعاينة.
7. اضغط **Export PDF** للحصول على العدد النهائي.
