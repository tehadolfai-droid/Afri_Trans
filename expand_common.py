"""Generate a professional internship report with chapters, sub-chapters, TOC, and page numbers."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import zipfile, os, shutil, copy

SRC = 'AFRI_Trans_reports.docx'
DST = 'AFRI_Trans_Report_2026.docx'
TMP = os.environ['TEMP'] + r'\report_build'

# ── 0. Extract images from source ──
if os.path.exists(TMP): shutil.rmtree(TMP)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)

IMG_DIR = os.path.join(TMP, 'word/media')

# ── 1. Create document ──
doc = Document()
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(4)
style.paragraph_format.line_spacing = 1.15

# Heading styles
for lvl, sz, clr in [(1, 18, '1a3c6e'), (2, 14, '2d5f8a'), (3, 12, '3a7bb5')]:
    s = doc.styles[f'Heading {lvl}']
    s.font.name = 'Calibri'
    s.font.size = Pt(sz)
    s.font.bold = True
    s.font.color.rgb = RGBColor(*bytes.fromhex(clr))
    s.paragraph_format.space_before = Pt(12 if lvl > 1 else 18)
    s.paragraph_format.space_after = Pt(6)

def add_heading(text, level=1):
    return doc.add_heading(text, level=level)

def add_para(text, bold=False, italic=False, size=11, color=None, align=None, space_after=4):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color: run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 0.63)
    return p

def add_img(img_name, width=Inches(5.5), caption=''):
    """Insert image from extracted media folder."""
    path = os.path.join