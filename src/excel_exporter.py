"""Excel exporter for Facebook Comments."""

from __future__ import annotations

import io
import logging

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import CommentData, EXCEL_HEADERS

log = logging.getLogger(__name__)

HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="1877F2", end_color="1877F2", fill_type="solid")
HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)
HEADER_BORDER = Border(
    bottom=Side(style="thin", color="000000"),
    right=Side(style="thin", color="CCCCCC"),
)
DATA_ALIGNMENT = Alignment(vertical="top", wrap_text=True)

class ExcelExporter:
    """Exports comments to an Excel workbook."""

    def __init__(self):
        self._workbook = Workbook()
        self._sheet = self._workbook.active
        self._sheet.title = "Comments"
        self._current_row = 1
        self._total_rows = 0
        self._init_sheet()

    def _init_sheet(self) -> None:
        for col_idx, header in enumerate(EXCEL_HEADERS, 1):
            cell = self._sheet.cell(row=1, column=col_idx, value=header)
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = HEADER_ALIGNMENT
            cell.border = HEADER_BORDER

        column_widths = {
            1: 18,  # Comment ID
            2: 18,  # Post ID
            3: 20,  # Author Name
            4: 40,  # Author URL
            5: 60,  # Text
            6: 12,  # Reaction Count
            7: 10,  # Is Reply
            8: 18,  # Parent ID
            9: 20,  # Scraped At
        }
        for col, width in column_widths.items():
            self._sheet.column_dimensions[get_column_letter(col)].width = width

        self._sheet.freeze_panes = "A2"

    def add_comment(self, comment: CommentData) -> None:
        self._current_row += 1
        self._total_rows += 1
        
        row_data = comment.to_excel_row()
        for col_idx, value in enumerate(row_data, 1):
            cell = self._sheet.cell(row=self._current_row, column=col_idx, value=value)
            cell.alignment = DATA_ALIGNMENT
            
            if col_idx == 4 and value: # Author URL
                try:
                    cell.hyperlink = value
                    cell.font = Font(color="1155CC", underline="single")
                except:
                    pass

    def save_to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        self._workbook.save(buffer)
        buffer.seek(0)
        return buffer.read()

    def get_stats(self) -> dict:
        return {
            "total_rows": self._total_rows
        }
