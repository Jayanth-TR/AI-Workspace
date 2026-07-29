import os
from uuid import uuid4

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing, Rect, String, Line

from docx import Document

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from app.schemas.file import FileGenerateRequest
from app.services.llm_service import LLMService


llm_service = LLMService()


class FileService:

    def create_custom_diagram(self, content: str):
        # Scan content for potential block names
        import re
        blocks = []

        # Look for numbered items like "1. Perception Layer:" or "1. Input:"
        matches = re.findall(r'\d+\.\s*([^:\n\-\–\—]+)', content)
        for m in matches:
            name = m.strip()
            # Clean up names (remove bold formatting stars, etc.)
            name = name.replace("**", "").replace("*", "")
            if len(name) < 25 and name not in blocks:
                blocks.append(name)

        # Fallback to defaults if we didn't find clear block names
        if len(blocks) < 3:
            blocks = ["Perception Layer", "Cognitive Layer", "Execution Layer"]
        else:
            blocks = blocks[:3] # We only draw 3 boxes in this simple diagram template

        d = Drawing(400, 120)

        # Colors: Blue, Purple, Green
        colors = [
            ("#EBF5FF", "#2563EB", "#1E3A8A"), # Blue
            ("#F5F3FF", "#7C3AED", "#5B21B6"), # Purple
            ("#ECFDF5", "#10B981", "#065F46")  # Green
        ]

        # Draw the 3 boxes
        x_coords = [10, 150, 290]
        for i in range(3):
            bg, border, text_color = colors[i]
            x = x_coords[i]
            # Draw box
            d.add(Rect(x, 40, 100, 40, fillColor=HexColor(bg), strokeColor=HexColor(border), strokeWidth=1.5, rx=5, ry=5))

            # Draw text wrapping if it's too long
            label = blocks[i]
            if len(label) > 15:
                # Split into words
                words = label.split(" ")
                if len(words) >= 2:
                    w1 = " ".join(words[:len(words)//2])
                    w2 = " ".join(words[len(words)//2:])
                    d.add(String(x + 50, 64, w1, textAnchor="middle", fontSize=8, fillColor=HexColor(text_color), fontName="Helvetica-Bold"))
                    d.add(String(x + 50, 52, w2, textAnchor="middle", fontSize=8, fillColor=HexColor(text_color), fontName="Helvetica-Bold"))
                else:
                    d.add(String(x + 50, 58, label[:15], textAnchor="middle", fontSize=8, fillColor=HexColor(text_color), fontName="Helvetica-Bold"))
            else:
                d.add(String(x + 50, 58, label, textAnchor="middle", fontSize=9, fillColor=HexColor(text_color), fontName="Helvetica-Bold"))

            # Connectors
            if i < 2:
                next_x = x_coords[i+1]
                arrow_start = x + 100
                d.add(Line(arrow_start, 60, next_x, 60, strokeColor=HexColor(border), strokeWidth=1.5))
                # Arrowhead
                d.add(Line(next_x - 5, 56, next_x, 60, strokeColor=HexColor(border), strokeWidth=1.5))
                d.add(Line(next_x - 5, 64, next_x, 60, strokeColor=HexColor(border), strokeWidth=1.5))

        # Draw feedback loop line from Execution (Box 3) back to Cognitive (Box 2)
        d.add(Line(340, 40, 340, 15, strokeColor=HexColor("#10B981"), strokeWidth=1.2))
        d.add(Line(340, 15, 200, 15, strokeColor=HexColor("#6B7280"), strokeWidth=1.2, strokeDashArray=[2, 2]))
        d.add(Line(200, 15, 200, 40, strokeColor=HexColor("#6B7280"), strokeWidth=1.2, strokeDashArray=[2, 2]))
        # Arrowhead up
        d.add(Line(196, 35, 200, 40, strokeColor=HexColor("#6B7280"), strokeWidth=1.2))
        d.add(Line(204, 35, 200, 40, strokeColor=HexColor("#6B7280"), strokeWidth=1.2))

        # Label for Feedback
        d.add(String(270, 20, "Feedback / Learn Loop", textAnchor="middle", fontSize=7, fillColor=HexColor("#4B5563"), fontName="Helvetica-Oblique"))

        return d

    def process_prompt(
        self,
        prompt: str
    ):
        """
        Generates the required file from a prompt.
        This method is used by the chat service.
        """

        request = FileGenerateRequest(
            prompt=prompt,
            file_type=""
        )

        return self.generate_file(request)

    def generate_file(
        self,
        request: FileGenerateRequest
    ):

        # Create output folder
        os.makedirs(
            "generated_files",
            exist_ok=True
        )

        # Ask AI to determine the best file type
        file_type_data = llm_service.detect_file_type(request.prompt)
        file_type = file_type_data.get("file_type", "").strip().lower()

        # PDF
        if file_type == "pdf":

            content = llm_service.generate_document_content(
                request.prompt
            )

            return self.create_pdf(content)

        # WORD
        elif file_type == "docx":

            content = llm_service.generate_document_content(
                request.prompt
            )

            return self.create_word(content)

        # EXCEL
        elif file_type == "xlsx":

            data = llm_service.generate_excel_data(
                request.prompt
            )

            return self.create_excel(data)

        # Unsupported
        else:

            return {
                "message": "Unsupported file type",
                "detected_type": file_type
            }

    # ==========================================================
    # PDF
    # ==========================================================

    def build_reportlab_table(self, table_data):
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        # Calculate col widths
        col_count = len(table_data[0]) if table_data else 1
        col_width = 480 / col_count
        
        styles = getSampleStyleSheet()
        cell_style = ParagraphStyle(
            "TableCellStyle",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=HexColor("#1E293B")
        )
        cell_bold_style = ParagraphStyle(
            "TableCellBoldStyle",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=HexColor("#0F172A"),
            fontName="Helvetica-Bold"
        )
        
        flowable_data = []
        for r_idx, row in enumerate(table_data):
            flowable_row = []
            for col in row:
                style = cell_bold_style if r_idx == 0 else cell_style
                flowable_row.append(Paragraph(col.strip(), style))
            flowable_data.append(flowable_row)
            
        t = Table(flowable_data, colWidths=[col_width] * col_count)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#F1F5F9")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def build_word_table(self, document, table_data):
        if not table_data:
            return
        col_count = len(table_data[0])
        table = document.add_table(rows=len(table_data), cols=col_count)
        table.style = 'Light Shading Accent 1'
        for r_idx, row in enumerate(table_data):
            for c_idx, cell_value in enumerate(row):
                table.rows[r_idx].cells[c_idx].text = cell_value.strip()

    # ==========================================================
    # PDF
    # ==========================================================

    def create_pdf(
        self,
        content: str
    ):

        filename = f"{uuid4()}.pdf"

        file_path = os.path.join(
            "generated_files",
            filename
        )

        document = SimpleDocTemplate(
            file_path,
            leftMargin=50,
            rightMargin=50,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            textColor=HexColor("#1F4E79"),
            spaceAfter=25
        )

        heading_style = ParagraphStyle(
            "HeadingStyle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=HexColor("#1F4E79"),
            spaceBefore=15,
            spaceAfter=10
        )

        subheading_style = ParagraphStyle(
            "SubheadingStyle",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=HexColor("#2C5E8A"),
            spaceBefore=12,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["BodyText"],
            fontSize=11,
            leading=20,
            spaceAfter=10
        )

        bullet_style = ParagraphStyle(
            "BulletStyle",
            parent=styles["BodyText"],
            fontSize=11,
            leading=18,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        )

        story = []
        current_table_data = []

        for line in content.split("\n"):

            line = line.strip()

            if not line:
                if current_table_data:
                    story.append(self.build_reportlab_table(current_table_data))
                    story.append(Spacer(1, 10))
                    current_table_data = []
                continue

            if line.startswith("[TABLE_ROW]"):
                row_text = line[11:].strip()
                cells = [c.strip() for c in row_text.split("|")]
                current_table_data.append(cells)
                continue

            if current_table_data:
                story.append(self.build_reportlab_table(current_table_data))
                story.append(Spacer(1, 10))
                current_table_data = []

            # Custom structured tags
            if line.startswith("[TITLE]"):
                story.append(Paragraph(line[7:].strip(), title_style))
            elif line.startswith("[HEADING]"):
                story.append(Paragraph(line[9:].strip(), heading_style))
            elif line.startswith("[SUBHEADING]"):
                story.append(Paragraph(line[12:].strip(), subheading_style))
            elif line.startswith("[BULLET]"):
                story.append(Paragraph(f"• {line[8:].strip()}", bullet_style))
            elif line.startswith("[TEXT]"):
                story.append(Paragraph(line[6:].strip(), body_style))
            elif line == "[PAGE_BREAK]":
                story.append(PageBreak())

            # Fallbacks
            elif line.startswith("# "):
                story.append(Paragraph(line[2:].strip(), title_style))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:].strip(), heading_style))
            elif line.startswith("### "):
                story.append(Paragraph(line[4:].strip(), subheading_style))
            elif line.startswith("- "):
                story.append(Paragraph(f"• {line[2:].strip()}", bullet_style))
            elif line.startswith("* "):
                story.append(Paragraph(f"• {line[2:].strip()}", bullet_style))
            elif line == "---":
                story.append(PageBreak())

            # Normal Paragraph
            else:
                clean_line = line.replace("**", "").replace("*", "")

                if "[insert diagram" in clean_line.lower() or "[architecture diagram" in clean_line.lower():
                    story.append(Spacer(1, 10))
                    story.append(self.create_custom_diagram(content))
                    story.append(Spacer(1, 15))
                else:
                    story.append(Paragraph(clean_line, body_style))

            if line != "---" and line != "[PAGE_BREAK]":
                story.append(Spacer(1, 5))

        if current_table_data:
            story.append(self.build_reportlab_table(current_table_data))

        document.build(story)

        return {
            "filename": filename,
            "file_path": file_path
        }

    # ==========================================================
    # WORD
    # ==========================================================

    def create_word(
        self,
        content: str
    ):

        filename = f"{uuid4()}.docx"

        file_path = os.path.join(
            "generated_files",
            filename
        )

        document = Document()
        current_table_data = []

        for line in content.split("\n"):

            line = line.strip()

            if not line:
                if current_table_data:
                    self.build_word_table(document, current_table_data)
                    current_table_data = []
                continue

            if line.startswith("[TABLE_ROW]"):
                row_text = line[11:].strip()
                cells = [c.strip() for c in row_text.split("|")]
                current_table_data.append(cells)
                continue

            if current_table_data:
                self.build_word_table(document, current_table_data)
                current_table_data = []

            # Custom structured tags
            if line.startswith("[TITLE]"):
                document.add_heading(line[7:].strip(), level=0)
            elif line.startswith("[HEADING]"):
                document.add_heading(line[9:].strip(), level=1)
            elif line.startswith("[SUBHEADING]"):
                document.add_heading(line[12:].strip(), level=2)
            elif line.startswith("[BULLET]"):
                document.add_paragraph(line[8:].strip(), style="List Bullet")
            elif line.startswith("[TEXT]"):
                document.add_paragraph(line[6:].strip())
            elif line == "[PAGE_BREAK]":
                document.add_page_break()

            # Fallbacks
            elif line.startswith("# "):
                document.add_heading(line[2:], level=0)
            elif line.startswith("## "):
                document.add_heading(line[3:], level=1)
            elif line.startswith("### "):
                document.add_heading(line[4:], level=2)
            elif line.startswith("- "):
                document.add_paragraph(line[2:], style="List Bullet")
            elif line.startswith("* "):
                document.add_paragraph(line[2:], style="List Bullet")
            elif line == "---":
                document.add_page_break()

            else:
                clean_line = line.replace("**", "").replace("*", "")
                document.add_paragraph(clean_line)

        if current_table_data:
            self.build_word_table(document, current_table_data)

        document.save(file_path)

        return {
            "filename": filename,
            "file_path": file_path
        }

    # ==========================================================
    # EXCEL
    # ==========================================================

    def create_excel(
        self,
        data
    ):

        if not data:

            return {
                "message": "No data generated."
            }

        filename = f"{uuid4()}.xlsx"

        file_path = os.path.join(
            "generated_files",
            filename
        )

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Generated Data"

        # Headers
        headers = list(data[0].keys())

        sheet.append(headers)

        # Rows
        for row in data:

            sheet.append(
                list(row.values())
            )

        # Header Style
        for cell in sheet[1]:

            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

            cell.fill = PatternFill(
                fill_type="solid",
                start_color="4F81BD"
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        # Auto Width
        for column in sheet.columns:

            max_length = 0

            column_letter = get_column_letter(
                column[0].column
            )

            for cell in column:

                if cell.value:

                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            sheet.column_dimensions[
                column_letter
            ].width = max_length + 3

        workbook.save(file_path)

        return {
            "filename": filename,
            "file_path": file_path
        }

    # ==========================================================
    # SPECIALIZED WORKFLOW GENERATORS (Invoice, Expense, Proposal)
    # ==========================================================

    def generate_invoice_doc(self, prompt: str) -> dict:
        """Generates a professional itemized Invoice document in PDF format."""
        os.makedirs("generated_files", exist_ok=True)
        filename = f"Invoice_{uuid4().hex[:8]}.pdf"
        file_path = os.path.join("generated_files", filename)

        invoice_prompt = (
            f"User Invoice Request: {prompt}\n\n"
            f"Generate structured content for a professional Invoice including:\n"
            f"[TITLE] INVOICE\n"
            f"[HEADING] Invoice Details\n"
            f"[TEXT] Invoice Number: INV-2026-001 | Date: July 28, 2026 | Due Date: August 15, 2026\n"
            f"[HEADING] Bill To\n"
            f"[TEXT] Client: ACME Corporation | Contact: billing@acme.com\n"
            f"[HEADING] Services & Line Items\n"
            f"[TABLE]\n"
            f"Item Description | Quantity | Rate | Total\n"
            f"AI Platform Development & Setup | 1 | $3,500.00 | $3,500.00\n"
            f"Knowledge Base RAG Integration | 1 | $1,200.00 | $1,200.00\n"
            f"Automated Workflow Configuration | 2 | $400.00 | $800.00\n"
            f"[HEADING] Summary\n"
            f"[TEXT] Subtotal: $5,500.00\n"
            f"[TEXT] Tax (10%): $550.00\n"
            f"[TEXT] **TOTAL DUE: $6,050.00**\n"
        )
        content = llm_service.generate_document_content(invoice_prompt)
        pdf_res = self.create_pdf(content)
        pdf_res["filename"] = filename
        return pdf_res

    def generate_expense_sheet_doc(self, prompt: str) -> dict:
        """Generates an Expense Tracker spreadsheet in XLSX format."""
        os.makedirs("generated_files", exist_ok=True)

        expense_data = [
            {"Date": "2026-07-01", "Category": "Software & SaaS", "Description": "OpenAI API Usage", "Payment Method": "Corporate Card", "Amount ($)": 150.00},
            {"Date": "2026-07-05", "Category": "Cloud Infrastructure", "Description": "AWS Hosting & Vector DB", "Payment Method": "Corporate Card", "Amount ($)": 280.50},
            {"Date": "2026-07-12", "Category": "Office Supplies", "Description": "Hardware Accessories", "Payment Method": "Reimbursement", "Amount ($)": 85.20},
            {"Date": "2026-07-20", "Category": "Consulting & Services", "Description": "Security Audit", "Payment Method": "Wire Transfer", "Amount ($)": 1200.00},
            {"Date": "2026-07-25", "Category": "Travel & Meals", "Description": "Team Client Workshop", "Payment Method": "Corporate Card", "Amount ($)": 340.00},
        ]
        
        # Try to parse AI generated tabular data if available
        try:
            custom_data = llm_service.generate_excel_data(f"Generate expense sheet rows for: {prompt}")
            if custom_data and len(custom_data) > 0:
                expense_data = custom_data
        except Exception:
            pass

        filename = f"Expense_Sheet_{uuid4().hex[:8]}.xlsx"
        file_path = os.path.join("generated_files", filename)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Expense Report"

        # Headers
        headers = list(expense_data[0].keys())
        sheet.append(headers)

        for row in expense_data:
            sheet.append(list(row.values()))

        # Header Formatting
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(fill_type="solid", start_color="1E40AF")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Auto Column Widths
        for col in sheet.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = max(len(str(cell.value or '')) for cell in col)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        workbook.save(file_path)
        return {
            "filename": filename,
            "file_path": file_path
        }

    def generate_proposal_doc(self, prompt: str) -> dict:
        """Generates a Business Proposal document in PDF or DOCX format."""
        os.makedirs("generated_files", exist_ok=True)
        filename = f"Business_Proposal_{uuid4().hex[:8]}.pdf"

        proposal_prompt = (
            f"User Business Proposal Request: {prompt}\n\n"
            f"Generate a professional, compelling Business Proposal:\n"
            f"[TITLE] BUSINESS PROPOSAL\n"
            f"[HEADING] Executive Summary\n"
            f"[TEXT] This proposal outlines our end-to-end solution designed to accelerate business workflows, integrate multi-mode AI automation, and maximize operational efficiency.\n"
            f"[HEADING] Project Scope & Objectives\n"
            f"[BULLET] Implementation of AI Agent Router for automated workflow dispatch.\n"
            f"[BULLET] Integration of Knowledge Base RAG semantic search over corporate documents.\n"
            f"[BULLET] Automated document generation engine for invoices, expense reports, and proposals.\n"
            f"[HEADING] Deliverables & Timeline\n"
            f"[TEXT] Phase 1: Core Architecture & Setup (Weeks 1-2)\n"
            f"[TEXT] Phase 2: AI Agent & Custom Generators (Weeks 3-4)\n"
            f"[TEXT] Phase 3: Testing, Deployment & User Training (Week 5)\n"
            f"[HEADING] Pricing & Investment\n"
            f"[TEXT] Total Project Investment: $15,000 USD (Includes 12 months maintenance & support).\n"
        )
        content = llm_service.generate_document_content(proposal_prompt)
        pdf_res = self.create_pdf(content)
        pdf_res["filename"] = filename
        return pdf_res