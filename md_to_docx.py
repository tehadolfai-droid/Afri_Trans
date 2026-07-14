import re
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# -- Page setup
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)

# -- Helper: set cell shading
def set_cell_shading(cell, color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    tcPr.append(shading)

# -- Helper: add a code-style paragraph (Consolas, light grey bg)
def add_code_block(text):
    for line in text.strip().split('\n'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(1)
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        # light grey shading via paragraph shd
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), 'F2F2F2')
        shd.set(qn('w:val'), 'clear')
        pPr.append(shd)

# -- Helper: add a table from parsed rows
def add_table(headers, rows):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'
    # header row
    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(10)
        set_cell_shading(cell, 'D9E2F3')
    # data rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = tbl.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            # handle bold markdown within cell
            parts = re.split(r'(\*\*.*?\*\*)', val)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = cell.paragraphs[0].add_run(part[2:-2])
                    run.bold = True
                else:
                    cell.paragraphs[0].add_run(part)
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(10)
    doc.add_paragraph()  # spacing after table

# -- Parse the markdown content
with open('INTERNSHIP_REPORT.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

code_buffer = None
in_table = False
table_lines = []
list_counter = None  # for ordered lists

i = 0
while i < len(lines):
    line = lines[i].rstrip('\n')
    raw = lines[i].rstrip('\n')

    # --- flush code block
    if code_buffer is not None:
        if line.startswith('```'):
            add_code_block(code_buffer)
            code_buffer = None
            doc.add_paragraph()
            i += 1
            continue
        else:
            code_buffer += line + '\n'
            i += 1
            continue

    if line.startswith('```'):
        code_buffer = ''
        i += 1
        continue

    # --- in_table accumulation
    if in_table:
        if line.startswith('|') and line != '|---|':
            table_lines.append(line)
            i += 1
            continue
        else:
            # flush table
            if len(table_lines) >= 2:
                header = [c.strip() for c in table_lines[0].strip('|').split('|')]
                rows = []
                for tl in table_lines[1:]:
                    cells = [c.strip() for c in tl.strip('|').split('|')]
                    rows.append(cells)
                add_table(header, rows)
            in_table = False
            table_lines = []
            # fall through to process current line normally
            continue

    # --- detect table start
    if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|---'):
        # check it's not a code inline
        in_table = True
        table_lines = [line]
        i += 1
        continue

    # --- horizontal rule
    if re.match(r'^---+\s*$', line):
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '999999')
        pBdr.append(bottom)
        pPr.append(pBdr)
        i += 1
        continue

    # --- empty line
    if not line.strip():
        # reset list counter on blank line
        list_counter = None
        i += 1
        continue

    # --- reset list numbering after heading
    h_match = re.match(r'^(#{1,3})\s+(.+)$', line)
    if h_match:
        level = len(h_match.group(1))
        text = h_match.group(2)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        h = doc.add_heading(text, level=level if level <= 3 else 3)
        # reset list numbering
        p_reset = doc.add_paragraph()
        pPr = p_reset._p.get_or_add_pPr()
        numPr = OxmlElement('w:numPr')
        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), '0')
        numPr.append(numId)
        pPr.append(numPr)
        p_reset.paragraph_format.space_before = Pt(0)
        p_reset.paragraph_format.space_after = Pt(0)
        p_reset.paragraph_format.line_spacing = Pt(1)
        run_reset = p_reset.add_run('')
        run_reset.font.size = Pt(1)
        run_reset.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        i += 1
        continue

    # --- ordered list
    ol_match = re.match(r'^(\d+)\.\s+(.+)$', line)
    if ol_match:
        num = ol_match.group(1)
        text = ol_match.group(2)
        p = doc.add_paragraph(style='List Number')
        p.clear()
        run = p.add_run(text)
        run.font.size = Pt(11)
        # handle inline bold
        p.clear()
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                r = p.add_run(part[2:-2])
                r.bold = True
                r.font.size = Pt(11)
            else:
                r = p.add_run(part)
                r.font.size = Pt(11)
        i += 1
        continue

    # --- unordered list
    ul_match = re.match(r'^[-*]\s+(.+)$', line)
    if ul_match:
        text = ul_match.group(1)
        # check if it has bold header then colon then description
        p = doc.add_paragraph(style='List Bullet')
        p.clear()
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                r = p.add_run(part[2:-2])
                r.bold = True
                r.font.size = Pt(11)
            else:
                r = p.add_run(part)
                r.font.size = Pt(11)
        i += 1
        continue

    # --- regular paragraph
    text = line
    # inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    p = doc.add_paragraph()
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = p.add_run(part[2:-2])
            r.bold = True
        else:
            p.add_run(part)

    i += 1

# -- Save
doc.save('INTERNSHIP_REPORT.docx')
print("Done: INTERNSHIP_REPORT.docx created")
