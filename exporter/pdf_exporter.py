from __future__ import annotations

from PySide6.QtGui import QTextDocument, QPageLayout, QPageSize
from PySide6.QtPrintSupport import QPrinter


def export_html_to_pdf(html: str, output_path: str) -> None:
    document = QTextDocument()
    document.setHtml(html)

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(output_path)
    printer.setPageSize(QPageSize(QPageSize.A4))
    printer.setPageMargins((15, 18, 15, 18), QPageLayout.Millimeter)

    document.print(printer)
