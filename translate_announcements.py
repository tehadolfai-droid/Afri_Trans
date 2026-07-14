import sqlite3, os, time
from deep_translator import GoogleTranslator

DB = 'data.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

try:
    conn.execute('SELECT message_fr FROM announcements LIMIT 1')
except sqlite3.OperationalError:
    conn.execute("ALTER TABLE announcements ADD COLUMN message_fr TEXT DEFAULT ''")
    conn.commit()

rows = conn.execute("SELECT id, message, message_fr FROM announcements WHERE message_fr IS NULL OR message_fr = ''").fetchall()
print(f'{len(rows)} announcements to translate')

if rows:
    tr = GoogleTranslator(source='en', target='fr')
    done = 0
    for r in rows:
        try:
            fr_text = tr.translate(r['message'])
            conn.execute("UPDATE announcements SET message_fr = ? WHERE id = ?", (fr_text, r['id']))
            done += 1
            print(f'  {done}. id={r["id"]}: {r["message"][:40]}... -> {fr_text[:40]}...')
            time.sleep(0.5)
        except Exception as e:
            print(f'  Failed id={r["id"]}: {e}')
    conn.commit()
    print(f'Translated: {done}')
conn.close()
