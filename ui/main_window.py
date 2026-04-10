from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QTextDocument
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from exporter.pdf_exporter import export_html_to_pdf
from logic.ai_generator import enhance_article_text
from logic.models import Article, Project
from logic.storage import ProjectStorage
from templates.newspaper_template import render_html


class ImageListWidget(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)

    def dragEnterEvent(self, event):  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):  # type: ignore[override]
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                self.addItem(local)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.storage = ProjectStorage()
        self.project = Project(articles=[])
        self.current_html = ""

        self.setWindowTitle("Smart Newspaper Generator - Young Journalists Club")
        self.resize(1500, 900)
        self._build_ui()
        self.apply_theme("light")

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top_bar = QHBoxLayout()
        self.newspaper_name = QLineEdit("نادي الصحفي الصغير")
        self.issue_title = QLineEdit("العدد الأسبوعي")
        self.template_box = QComboBox()
        self.template_box.addItems(["classic", "modern", "bold"])
        self.theme_box = QComboBox()
        self.theme_box.addItems(["light", "dark"])
        self.theme_box.currentTextChanged.connect(self.apply_theme)

        self.primary_btn = QPushButton("Primary Color")
        self.secondary_btn = QPushButton("Secondary Color")
        self.logo_btn = QPushButton("اختيار لوجو النادي")
        self.primary_btn.clicked.connect(lambda: self.pick_color("primary"))
        self.secondary_btn.clicked.connect(lambda: self.pick_color("secondary"))
        self.logo_btn.clicked.connect(self.pick_logo)

        top_bar.addWidget(QLabel("اسم الصحيفة"))
        top_bar.addWidget(self.newspaper_name)
        top_bar.addWidget(QLabel("عنوان العدد"))
        top_bar.addWidget(self.issue_title)
        top_bar.addWidget(QLabel("القالب"))
        top_bar.addWidget(self.template_box)
        top_bar.addWidget(self.theme_box)
        top_bar.addWidget(self.primary_btn)
        top_bar.addWidget(self.secondary_btn)
        top_bar.addWidget(self.logo_btn)
        layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        form_group = QGroupBox("بيانات المقال")
        form = QFormLayout(form_group)
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(["سياسة", "رياضة", "ثقافة", "تعليم", "تقنية", "مجتمع"])
        self.location_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(date.today())
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("اكتب محتوى المقال هنا...")
        self.breaking_box = QCheckBox("Breaking News")

        form.addRow("عنوان المقال", self.title_input)
        form.addRow("اسم الكاتب", self.author_input)
        form.addRow("التصنيف", self.category_input)
        form.addRow("المكان", self.location_input)
        form.addRow("التاريخ", self.date_input)
        form.addRow("المحتوى", self.content_input)
        form.addRow("", self.breaking_box)

        left_layout.addWidget(form_group)

        img_group = QGroupBox("صور المقال (Drag & Drop)")
        img_layout = QVBoxLayout(img_group)
        self.images_list = ImageListWidget()
        add_image_btn = QPushButton("إضافة صور")
        clear_images_btn = QPushButton("مسح الصور")
        add_image_btn.clicked.connect(self.add_images)
        clear_images_btn.clicked.connect(self.images_list.clear)
        img_layout.addWidget(self.images_list)
        img_layout.addWidget(add_image_btn)
        img_layout.addWidget(clear_images_btn)
        left_layout.addWidget(img_group)

        buttons = QHBoxLayout()
        gen_article_btn = QPushButton("Generate Article")
        add_article_btn = QPushButton("إضافة المقال إلى العدد")
        gen_news_btn = QPushButton("Generate Newspaper")
        save_btn = QPushButton("Save Project")
        load_btn = QPushButton("Load Project")
        export_btn = QPushButton("Export PDF")

        gen_article_btn.clicked.connect(self.generate_article)
        add_article_btn.clicked.connect(self.add_article)
        gen_news_btn.clicked.connect(self.generate_newspaper)
        save_btn.clicked.connect(self.save_project)
        load_btn.clicked.connect(self.load_project)
        export_btn.clicked.connect(self.export_pdf)

        for b in [gen_article_btn, add_article_btn, gen_news_btn, save_btn, load_btn, export_btn]:
            buttons.addWidget(b)
        left_layout.addLayout(buttons)

        self.articles_list = QListWidget()
        left_layout.addWidget(QLabel("مقالات العدد"))
        left_layout.addWidget(self.articles_list)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("معاينة المجلة / الصحيفة"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        right_layout.addWidget(self.preview)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 800])

    def apply_theme(self, mode: str) -> None:
        if mode == "dark":
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#121212"))
            palette.setColor(QPalette.WindowText, QColor("#eeeeee"))
            palette.setColor(QPalette.Base, QColor("#1f1f1f"))
            palette.setColor(QPalette.Text, QColor("#f2f2f2"))
            self.setPalette(palette)
        else:
            self.setPalette(self.style().standardPalette())

    def pick_color(self, target: str) -> None:
        color = QColorDialog.getColor()
        if not color.isValid():
            return
        if target == "primary":
            self.project.primary_color = color.name()
        else:
            self.project.secondary_color = color.name()

    def pick_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg *.svg)")
        if path:
            self.project.logo_path = path

    def add_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.webp)")
        for f in files:
            self.images_list.addItem(f)

    def generate_article(self) -> None:
        improved = enhance_article_text(
            self.title_input.text(),
            self.category_input.currentText(),
            self.content_input.toPlainText(),
            self.author_input.text(),
            self.location_input.text(),
        )
        self.content_input.setPlainText(improved)

    def _collect_form_article(self) -> Article:
        return Article(
            title=self.title_input.text().strip(),
            author=self.author_input.text().strip(),
            category=self.category_input.currentText(),
            content=self.content_input.toPlainText().strip(),
            location=self.location_input.text().strip(),
            date_text=self.date_input.date().toString("yyyy-MM-dd"),
            images=[self.images_list.item(i).text() for i in range(self.images_list.count())],
            is_breaking=self.breaking_box.isChecked(),
        )

    def add_article(self) -> None:
        article = self._collect_form_article()
        if not article.title or not article.content:
            QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال عنوان ومحتوى المقال.")
            return
        self.project.articles.append(article)
        self.articles_list.addItem(QListWidgetItem(f"{article.title} | {article.author}"))
        self.content_input.clear()
        self.images_list.clear()

    def generate_newspaper(self) -> None:
        self.project.newspaper_name = self.newspaper_name.text().strip() or self.project.newspaper_name
        self.project.issue_title = self.issue_title.text().strip() or self.project.issue_title
        self.project.template_name = self.template_box.currentText()
        self.current_html = render_html(self.project)
        self.preview.setHtml(self.current_html)

    def save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "data/newspaper_project.json", "JSON (*.json)")
        if not path:
            return
        self.project.newspaper_name = self.newspaper_name.text().strip() or self.project.newspaper_name
        self.project.issue_title = self.issue_title.text().strip() or self.project.issue_title
        self.project.template_name = self.template_box.currentText()
        saved = self.storage.save(self.project, path)
        QMessageBox.information(self, "Saved", f"تم حفظ المشروع:\n{saved}")

    def load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "data", "JSON (*.json)")
        if not path:
            return
        try:
            self.project = self.storage.load(path)
            self.newspaper_name.setText(self.project.newspaper_name)
            self.issue_title.setText(self.project.issue_title)
            self.template_box.setCurrentText(self.project.template_name)
            self.articles_list.clear()
            for article in self.project.articles:
                self.articles_list.addItem(f"{article.title} | {article.author}")
            self.generate_newspaper()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"تعذر تحميل المشروع:\n{exc}")

    def export_pdf(self) -> None:
        if not self.current_html:
            self.generate_newspaper()
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "newspaper_issue.pdf", "PDF (*.pdf)")
        if not path:
            return
        try:
            export_html_to_pdf(self.current_html, path)
            QMessageBox.information(self, "Done", f"تم التصدير إلى:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", str(exc))
