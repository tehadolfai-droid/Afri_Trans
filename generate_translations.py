import json
from pathlib import Path
from deep_translator import GoogleTranslator

TR_DIR = Path('translations')

LANGUAGE_MAP = {
    'fr': 'french',
    'ar': 'arabic',
    'pt': 'portuguese',
    'es': 'spanish',
    'sw': 'swahili',
    'am': 'amharic',
    'so': 'somali',
    'ti': 'tigrinya',
    'af': 'afrikaans',
    'zu': 'zulu',
}

with open(TR_DIR / 'en.json', encoding='utf-8') as f:
    en = json.load(f)

print(f'en.json: {len(en)} keys (master)')
print()

for lang_code, lang_name in sorted(LANGUAGE_MAP.items()):
    path = TR_DIR / f'{lang_code}.json'
    if path.exists():
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    missing = [k for k in en if k not in data]
    
    if missing:
        print(f'{lang_code}.json ({lang_name}): {len(missing)} missing keys, translating...')
        try:
            translator = GoogleTranslator(source='en', target=lang_code)
            for k in missing:
                translated = translator.translate(k)
                data[k] = translated
        except Exception as e:
            print(f'  Translation failed: {e}')
            print(f'  Falling back to English for {len(missing)} keys')
            for k in missing:
                data[k] = en[k]
    else:
        print(f'{lang_code}.json ({lang_name}): all keys present')

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print()
print('Done! All translations synced.')
