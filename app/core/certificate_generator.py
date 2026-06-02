from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_certificate_pdf(name: str, course_title: str, issued_at_str: str, certificate_id: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Simple certificate layout
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "Certificate of Completion")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 150, f"This certifies that")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 190, name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 230, f"has successfully completed the course")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 260, course_title)

    c.setFont("Helvetica", 12)
    c.drawString(72, 72, f"Issued: {issued_at_str}")
    c.drawRightString(width - 72, 72, f"Certificate ID: {certificate_id}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
