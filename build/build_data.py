"""Create one scratch database per problem (lc<id>), run every setup, step, solution and alternative against MySQL 8, and write data.json.
Fails loudly if an alternative disagrees with the main solution."""
import json, os, re, sys, decimal, datetime
from pathlib import Path
import pymysql

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from content_a import PROBLEMS_A
from content_b import PROBLEMS_B
from content_c import PROBLEMS_C
from content_d import PROBLEMS_D

PROBLEMS = PROBLEMS_A + PROBLEMS_B + PROBLEMS_C + PROBLEMS_D

# Connection settings: override with env vars, e.g. MYSQL_HOST=127.0.0.1 MYSQL_PASSWORD=secret
_kw = dict(user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''),
           charset='utf8mb4', autocommit=True)
if os.getenv('MYSQL_HOST'):
    _kw.update(host=os.environ['MYSQL_HOST'], port=int(os.getenv('MYSQL_PORT', '3306')))
else:
    _kw.update(unix_socket=os.getenv('MYSQL_SOCKET', '/var/run/mysqld/mysqld.sock'))
conn = pymysql.connect(**_kw)
cur = conn.cursor()


def split_sql(script):
    """Split on semicolons that are outside quotes."""
    out, buf, q = [], [], None
    for ch in script:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
        elif ch in ("'", '"', '`'):
            q = ch; buf.append(ch)
        elif ch == ';':
            s = ''.join(buf).strip()
            if s: out.append(s)
            buf = []
        else:
            buf.append(ch)
    s = ''.join(buf).strip()
    if s: out.append(s)
    return out


def conv(v):
    if v is None: return None
    if isinstance(v, decimal.Decimal): return str(v)
    if isinstance(v, datetime.datetime): return v.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(v, datetime.date): return v.isoformat()
    if isinstance(v, (bytes, bytearray)): return v.decode('utf8', 'replace')
    if isinstance(v, float):
        r = round(v, 6)
        return int(r) if r == int(r) else r
    return v


def query(sql):
    cur.execute(sql)
    if cur.description is None:
        return None
    cols = [d[0] for d in cur.description]
    rows = [[conv(v) for v in r] for r in cur.fetchall()]
    return {"cols": cols, "rows": rows}


def fresh(p):
    db = f"lc{p['id']}"
    cur.execute(f"DROP DATABASE IF EXISTS {db}")
    cur.execute(f"CREATE DATABASE {db}")
    cur.execute(f"USE {db}")
    for st in split_sql(p['setup']):
        cur.execute(st)


def run_solution(p, sql):
    fresh(p)
    res = None
    for st in split_sql(sql):
        r = query(st)
        if r is not None:
            res = r
    if p.get('post'):
        res = query(p['post'])
    return res


def norm(res, ordered):
    rows = [tuple('NULL' if v is None else str(v) for v in r) for r in res['rows']]
    return rows if ordered else sorted(rows)


problems_out, failures = [], []
for p in PROBLEMS:
    fresh(p)
    table_names = re.findall(r'CREATE TABLE\s+(\w+)', p['setup'])
    inputs = [dict(name=t, **query(f"SELECT * FROM {t}")) for t in table_names]
    # column types for the schema panel
    schema = []
    for t in table_names:
        cur.execute(f"SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_KEY FROM information_schema.COLUMNS "
                    f"WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION", (t,))
        schema.append(dict(name=t, cols=[[c, ty, k] for c, ty, k in cur.fetchall()]))
    steps = []
    for s in p['steps']:
        try:
            r = query(s['sql'])
        except Exception as e:
            failures.append(f"{p['id']} step '{s['t']}': {e}")
            r = {"cols": ["error"], "rows": [[str(e)]]}
        steps.append(dict(t=s['t'], note=s.get('note', ''), sql=s['sql'].strip(), **r))
    try:
        output = run_solution(p, p['solution'])
    except Exception as e:
        failures.append(f"{p['id']} MAIN: {e}")
        output = {"cols": ["error"], "rows": [[str(e)]]}
    ordered = p.get('ordered', False)
    alts = []
    for label, sql, note in p['alts']:
        try:
            r = run_solution(p, sql)
            ok = norm(r, ordered) == norm(output, ordered)
            if not ok:
                failures.append(f"{p['id']} ALT '{label}' differs:\n   main={output['rows']}\n   alt ={r['rows']}")
        except Exception as e:
            failures.append(f"{p['id']} ALT '{label}': {e}")
            ok = False
        alts.append(dict(label=label, sql=sql.strip(), note=note, verified=ok))
    out = {k: v for k, v in p.items() if k not in ('steps', 'alts', 'setup', 'solution')}
    out.update(setup=p['setup'].strip(), solution=p['solution'].strip(), steps=steps,
               alts=alts, inputs=inputs, schema=schema, output=output, ordered=ordered)
    problems_out.append(out)
    print(f"#{p['n']:>2} {p['id']:>4} {p['title'][:48]:<48} → {len(output['rows'])} row(s): {output['rows'][:4]}")

assert len(problems_out) == 50, len(problems_out)
assert [p['n'] for p in problems_out] == list(range(1, 51))
(HERE / 'data.json').write_text(json.dumps(problems_out, ensure_ascii=False), encoding='utf-8')
print("\nFAILURES:" if failures else "\nAll alternatives match their main solution; no step errors.")
for f in failures:
    print(" -", f)
