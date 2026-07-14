from docx import Document
import sys

doc = Document(r"C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\AFRI_Trans_Report_2026.docx")

# Find sections by heading text
sections = {
    "7.9": [],
    "8.3": [],
    "9.7": []
}
current_section = None
collecting = False

for p in doc.paragraphs:
    text = p.text.strip()
    style = p.style.name if p.style else ""

    # Detect section headings
    if "7.9" in text and ("Heading" in style or text.startswith("7.9")):
        current_section = "7.9"
        collecting = True
        sections["7.9"].append(("heading", text, style))
        continue
    elif "8.3" in text and ("Heading" in style or text.startswith("8.3")):
        current_section = "8.3"
        collecting = True
        sections["8.3"].append(("heading", text, style))
        continue
    elif "9.7" in text and ("Heading" in style or text.startswith("9.7")):
        current_section = "9.7"
        collecting = True
        sections["9.7"].append(("heading", text, style))
        continue

    # Check if we hit next section
    if collecting and current_section:
        # Stop if we hit another numbered heading
        for num in ["7.9", "7.10", "7.11", "8.3", "8.4", "9.7", "9.8", "9.9"]:
            if text.startswith(num + " ") or text.startswith(num + "."):
                if num != current_section:
                    collecting = False
                    current_section = None
                    break
        if collecting:
            sections[current_section].append(("body", text, style))

for sec_id, items in sections.items():
    print(f"\n{'='*60}")
    print(f"SECTION {sec_id}")
    print(f"{'='*60}")
    if not items:
        print("  (not found)")
    for typ, text, style in items:
        prefix = f"[{style}]" if typ == "heading" else "   "
        print(f"  {prefix} {text[:200]}")
