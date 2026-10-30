from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import xlsxwriter


def generate_excel_report(rows: list[dict]) -> bytes:
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Cafeteria Report")

    headers = ["Date", "Description", "Amount", "Balance"]
    worksheet.write_row(0, 0, headers)

    for index, row in enumerate(rows, start=1):
        worksheet.write(index, 0, row.get("date", ""))
        worksheet.write(index, 1, row.get("description", ""))
        worksheet.write(index, 2, str(row.get("amount", 0)))
        worksheet.write(index, 3, str(row.get("balance", 0)))

    worksheet.autofilter(0, 0, len(rows), 3)
    workbook.close()
    return output.getvalue()


def generate_pdf_report(rows: list[dict]) -> bytes:
    output = BytesIO()
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Cafeteria Financial Report", styles["Title"]))
    story.append(Spacer(1, 18))

    table_data = [["Date", "Description", "Amount", "Balance"]]
    for row in rows:
        table_data.append([
            row.get("date", ""),
            row.get("description", ""),
            str(row.get("amount", 0)),
            str(row.get("balance", 0)),
        ])

    table = Table(table_data)
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6feb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ])
    )
    story.append(table)

    doc = SimpleDocTemplate(output, pagesize=letter)
    doc.build(story)
    return output.getvalue()
