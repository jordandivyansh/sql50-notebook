"""Assemble ../index.html from template.html + data.json + revision.py (no database needed)."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from revision import REVISION

problems = json.loads((HERE / 'data.json').read_text(encoding='utf-8'))
ids = {p['id'] for p in problems}
for pt in REVISION['patterns']:
    for i in pt['ids']:
        assert i in ids, (pt['name'], i)

def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

tpl = (HERE / 'template.html').read_text(encoding='utf-8')
out = tpl.replace('__PROBLEMS__', js(problems)).replace('__REVISION__', js(REVISION))
(HERE.parent / 'index.html').write_text(out, encoding='utf-8')
print('wrote index.html,', len(out) // 1024, 'KB')
