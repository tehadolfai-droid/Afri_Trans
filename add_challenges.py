"""
Add missing challenge items to the Introduction section of AFRI_Trans_Report_2026.docx.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

doc = Document('AFRI_Trans_Report_2026.docx')
body = doc.element.body

def get_text(elem):
    return ''.join(t.text or '' for t in elem.iter(W + 't'))

def make_list_para(text, after_elem):
    """Create a 'List Number' paragraph and insert it after the given element."""
    # Find the List Number style ID
    list_id = None
    for s in doc.styles:
        if s.name == 'List Number':
            list_id = s.style_id
            break
    
    p = etree.SubElement(body, W + 'p')
    pPr = etree.SubElement(p, W + 'pPr')
    pStyle = etree.SubElement(pPr, W + 'pStyle')
    pStyle.set(W + 'val', list_id)
    
    spacing = etree.SubElement(pPr, W + 'spacing')
    spacing.set(W + 'after', '120')
    spacing.set(W + 'line', '276')
    spacing.set(W + 'lineRule', 'auto')
    
    r = etree.SubElement(p, W + 'r')
    rPr = etree.SubElement(r, W + 'rPr')
    rFonts = etree.SubElement(rPr, W + 'rFonts')
    rFonts.set(W + 'ascii', 'Calibri')
    rFonts.set(W + 'hAnsi', 'Calibri')
    sz = etree.SubElement(rPr, W + 'sz')
    sz.set(W + 'val', '22')  # 11pt
    
    t = etree.SubElement(r, W + 't')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    # Insert after the reference element
    after_elem.addnext(p)
    return p

# Find the "Security" bullet paragraph (last item in current challenge list)
# Then insert new challenge items after it
all_pe = list(body.iterchildren(W + 'p'))

security_idx = None
objectives_heading_idx = None

for i, pe in enumerate(all_pe):
    txt = get_text(pe).strip()
    sid = ''
    ppr = pe.find(W + 'pPr')
    if ppr is not None:
        ps = ppr.find(W + 'pStyle')
        if ps is not None:
            sid = ps.get(W + 'val', '')
    
    if sid == 'ListNumber' and 'Security:' in txt:
        security_idx = i
    if sid == 'Heading2' and '3. Objectives' in txt:
        objectives_heading_idx = i

print(f'Security bullet at index: {security_idx}')
print(f'Objectives heading at index: {objectives_heading_idx}')

if security_idx is not None:
    security_pe = all_pe[security_idx]
    
    new_challenges = [
        'No Commission Exemption: Agencies had no way to opt out of the 1% platform commission — all bookings were charged regardless of volume.',
        'No Real-Time Seat Updates: The seat map was static — if two passengers viewed the same trip simultaneously, neither would see the other\'s selection until a page refresh.',
        'No Departure Notifications: Passengers received no reminders before departure, leading to missed trips.',
        'Concurrency Bugs (TOCTOU): Agency registration checked name and email uniqueness then inserted in separate database connections — two simultaneous requests with the same name would both pass validation and create duplicate records. The booking reference counter had the same flaw.',
    ]
    
    for ch in reversed(new_challenges):
        make_list_para(ch, security_pe)
    
    print(f'Added {len(new_challenges)} challenge items after Security')

# Also update the Primary Objectives to include subscription and notification features
# Find the "Add subscription plans" partial bullet in primary objectives
for pe in all_pe:
    txt = get_text(pe).strip()
    if 'Add subscription plans' in txt:
        # This is a concatenated bullet from the original that got split across lines
        # Replace it by finding the bullet and fixing its text
        for r in pe.iter(W + 'r'):
            for t in r.iter(W + 't'):
                if 'Add subscription plans' in (t.text or ''):
                    t.text = 'Add subscription plans (monthly / 6-month / annual) so agencies can prepay to skip platform commission'
                    print('Updated subscription objective')
                    break
        break

# Also update "Harden concurrent access" in secondary objectives
for pe in all_pe:
    txt = get_text(pe).strip()
    if 'Harden concurrent access' in txt:
        for r in pe.iter(W + 'r'):
            for t in r.iter(W + 't'):
                if 'Harden concurrent' in (t.text or ''):
                    t.text = 'Harden concurrent access: atomic transactions for registration and booking, unique indexes for duplicate prevention'
                    print('Updated concurrency objective')
                    break
        break

# Add missing objectives
# Find the "Support agency management" bullet
for i, pe in enumerate(all_pe):
    txt = get_text(pe).strip()
    if 'Support agency management' in txt:
        # Add after it: subscription system, live seat map, notification scheduler
        new_secondary = [
            'Implement subscription system: monthly, 6-month, and annual plans that exempt agencies from platform commission',
            'Build live seat map with 30-second auto-refresh for real-time availability across concurrent users',
            'Add departure notification scheduler: WhatsApp Cloud API, USB GSM modem, Twilio, and console fallback — all dormant until configured',
        ]
        for ns in reversed(new_secondary):
            make_list_para(ns, pe)
        print(f'Added {len(new_secondary)} secondary objectives')
        break

import os
tmp = os.environ['TEMP'] + '/AFRI_Trans_Report_2026.docx'
doc.save(tmp)
# Copy over the original
import shutil
shutil.copy2(tmp, 'AFRI_Trans_Report_2026.docx')
os.remove(tmp)
print(f'\nSaved AFRI_Trans_Report_2026.docx (via temp)')
