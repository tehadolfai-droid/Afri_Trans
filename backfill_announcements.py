"""Back-fill translations for all existing announcements to all 11 languages."""
import sqlite3, time
from deep_translator import GoogleTranslator

DB = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\data.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Add new columns if they don't exist
for col in ('message_ar', 'message_pt', 'message_sw', 'message_am',
            'message_so', 'message_ti', 'message_es', 'message_af', 'message_zu'):
    try:
        conn.execute(f"ALTER TABLE announcements ADD COLUMN {col} TEXT DEFAULT ''")
        print(f'Added column {col}')
    except sqlite3.OperationalError:
        pass

LANG_TARGETS = {
    'ar': 'message_ar', 'pt': 'message_pt', 'sw': 'message_sw',
    'am': 'message_am', 'so': 'message_so', 'ti': 'message_ti',
    'es': 'message_es', 'af': 'message_af', 'zu': 'message_zu',
}

rows = conn.execute(
    "SELECT id, message FROM announcements"
).fetchall()
print(f'{len(rows)} announcements to process')

done = 0
for r in rows:
    for lang_code, col_name in LANG_TARGETS.items():
        existing = conn.execute(
            f"SELECT {col_name} FROM announcements WHERE id = ?", (r['id'],)
        ).fetchone()[0]
        if existing:
            continue
        try:
            tr = GoogleTranslator(source='en', target=lang_code)
            translated = tr.translate(r['message'])
            conn.execute(f"UPDATE announcements SET {col_name} = ? WHERE id = ?",
                         (translated, r['id']))
            done += 1
            print(f'  id={r["id"]} [{lang_code}]: {r["message"][:30]}... -> {translated[:30]}...')
            time.sleep(0.3)
        except Exception as e:
            print(f'  Failed id={r["id"]} [{lang_code}]: {e}')
            conn.execute(f"UPDATE announcements SET {col_name} = ? WHERE id = ?",
                         (r['message'], r['id']))

conn.commit()
print(f'\nDone! {done} translations added.')
conn.close()
