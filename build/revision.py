# Interview revision content (patterns, cheat sheet, concept Q&A, checklist, traps)

SECTIONS = [
  dict(key="select", name="Select", blurb="Row filters, NULL logic and string length."),
  dict(key="joins", name="Basic Joins", blurb="INNER vs LEFT, anti-joins, self joins, the CROSS JOIN grid."),
  dict(key="agg", name="Basic Aggregate Functions", blurb="AVG, conditional aggregation, rates and percentages."),
  dict(key="sortgroup", name="Sorting and Grouping", blurb="GROUP BY, HAVING, COUNT(DISTINCT), NULL-on-empty."),
  dict(key="advjoin", name="Advanced Select and Joins", blurb="CASE, LAG/LEAD, running totals, forcing categories."),
  dict(key="subq", name="Subqueries", blurb="NOT IN, scalar subqueries, UNION ALL, window frames, DENSE_RANK."),
  dict(key="string", name="Advanced String Functions / Regex / Clause", blurb="String builders, LIKE vs REGEXP, DELETE, GROUP_CONCAT."),
]

PATTERNS = [
  dict(name="Row filter with nullable columns", when="Keep rows by conditions where a column can be NULL.",
       code="""WHERE col <> 2 OR col IS NULL      -- NULL <> 2 is UNKNOWN
WHERE IFNULL(col, 0) <> 2
WHERE NOT (col <=> 2)              -- null-safe equality""",
       ids=[1757, 584, 595, 620, 577]),
  dict(name="Anti-join: A without a match in B", when="\"Customers who never…\", \"visits without transactions\", \"manager left\".",
       code="""SELECT a.*
FROM A a
LEFT JOIN B b ON b.a_id = a.id
WHERE b.id IS NULL;
-- or: WHERE NOT EXISTS (SELECT 1 FROM B b WHERE b.a_id = a.id)""",
       ids=[1581, 1978, 1378]),
  dict(name="Self join: compare rows of one table", when="Yesterday vs today, start vs end, manager vs report, later duplicate vs earlier.",
       code="""SELECT ...
FROM T a
JOIN T b
  ON b.manager_id = a.id                       -- hierarchy
  -- ON DATEDIFF(a.day, b.day) = 1             -- previous day
  -- ON a.k = b.k AND a.type='start' AND b.type='end'""",
       ids=[197, 1661, 570, 1731, 196]),
  dict(name="Every combination, zeros included", when="\"For each student and each subject…\" — output must contain combos with no data.",
       code="""SELECT s.id, sub.name, COUNT(e.id) AS cnt
FROM Students s
CROSS JOIN Subjects sub
LEFT JOIN Exams e ON e.student_id = s.id AND e.subject = sub.name
GROUP BY s.id, sub.name;""",
       ids=[1280]),
  dict(name="Conditional aggregation and rates", when="Several metrics per group in one pass; \"rate\", \"percentage\", \"approved count\".",
       code="""SUM(state = 'approved')               -- count where true
SUM(IF(state = 'approved', amount, 0)) -- total where true
ROUND(AVG(rating < 3) * 100, 2)        -- percentage where true
ROUND(AVG(IF(action='confirmed',1,0)), 2)  -- rate, NULL-safe""",
       ids=[1934, 1211, 1193, 1174, 1633, 550]),
  dict(name="Filter groups with HAVING", when="Conditions on COUNT/SUM/AVG of a group.",
       code="""SELECT class
FROM Courses
GROUP BY class
HAVING COUNT(*) >= 5;""",
       ids=[570, 596, 1045, 619, 1327]),
  dict(name="First / latest row per group", when="\"First order\", \"first year\", \"price as of a date\".",
       code="""WHERE (g, d) IN (SELECT g, MIN(d) FROM T GROUP BY g)
-- window version:
ROW_NUMBER() OVER (PARTITION BY g ORDER BY d) = 1   -- exactly one row
RANK()       OVER (PARTITION BY g ORDER BY d) = 1   -- keep ties""",
       ids=[1070, 1174, 550, 1164]),
  dict(name="Top-N per group", when="\"Top 3 salaries per department\" — ties share a place.",
       code="""SELECT * FROM (
  SELECT e.*, DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk
  FROM Employee e
) t
WHERE rnk <= 3;""",
       ids=[185, 176]),
  dict(name="One row even when nothing matches", when="\"Return NULL if there is no such value.\"",
       code="""SELECT (SELECT ... ORDER BY x DESC LIMIT 1 OFFSET 1) AS answer;  -- scalar subquery → NULL
SELECT MAX(x) AS answer FROM (...) t;                            -- MAX of empty set → NULL""",
       ids=[176, 619]),
  dict(name="Relational division (\"has ALL of\")", when="\"Customers who bought every product\".",
       code="""SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);""",
       ids=[1045]),
  dict(name="Running and moving totals", when="\"Cumulative weight\", \"7-day moving average\".",
       code="""SUM(w) OVER (ORDER BY turn)                                   -- running total
SUM(a) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) -- last 7 rows
SUM(a) OVER (ORDER BY d RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW)""",
       ids=[1204, 1321]),
  dict(name="Neighbouring rows", when="\"Three in a row\", \"swap adjacent\", \"compared with previous\".",
       code="""LAG(col)  OVER (ORDER BY id)   -- previous row's value
LEAD(col) OVER (ORDER BY id)   -- next row's value
LAG(col, 2, 0) OVER (...)      -- two back, default 0""",
       ids=[180, 197, 626]),
  dict(name="Stack columns or force fixed rows: UNION ALL", when="Symmetric pairs (friends), fixed category lists, two answers in one column.",
       code="""SELECT requester_id AS id FROM R
UNION ALL
SELECT accepter_id FROM R;        -- unpivot both columns

SELECT 'Low' AS cat, SUM(x < 10) FROM T
UNION ALL SELECT 'High', SUM(x >= 10) FROM T;""",
       ids=[602, 1907, 1341, 595]),
  dict(name="Strings and regex", when="Clean, measure, match or aggregate text.",
       code="""CONCAT(UPPER(LEFT(s,1)), LOWER(SUBSTRING(s,2)))
CHAR_LENGTH(s)                            -- characters (LENGTH = bytes)
s LIKE 'X%' OR s LIKE '% X%'              -- word starts with X
REGEXP_LIKE(s, '^[a-z]+$', 'c')           -- case-sensitive regex
GROUP_CONCAT(DISTINCT x ORDER BY x SEPARATOR ',')""",
       ids=[1667, 1527, 1517, 1484, 1683]),
  dict(name="Date windows", when="Month filters, N-day periods, day-after checks.",
       code="""d >= '2020-02-01' AND d < '2020-03-01'     -- a month, half-open
d BETWEEN '2019-06-28' AND '2019-07-27'    -- 30 days ending 27 Jul
DATE_FORMAT(d, '%Y-%m')                    -- '2025-01'
DATE_ADD(d, INTERVAL 1 DAY), DATEDIFF(a, b) -- a - b in days""",
       ids=[1141, 1193, 1327, 1341, 197, 550]),
  dict(name="Delete duplicates, keep one", when="\"Keep the row with the smallest id per email\".",
       code="""DELETE p1
FROM Person p1
JOIN Person p2 ON p1.email = p2.email AND p1.id > p2.id;""",
       ids=[196]),
]

CHEATSHEET = [
  dict(group="NULL handling", rows=[
    ["col IS NULL / IS NOT NULL", "The only correct NULL test", "WHERE referee_id IS NULL"],
    ["IFNULL(a, b)", "b when a is NULL (2 args)", "IFNULL(bonus, 0)"],
    ["COALESCE(a, b, c…)", "First non-NULL argument", "COALESCE(nick, name, 'n/a')"],
    ["NULLIF(a, b)", "NULL when a = b — avoids divide-by-zero", "x / NULLIF(y, 0)"],
    ["a <=> b", "Null-safe equality: NULL <=> NULL is 1", "NOT (referee_id <=> 2)"],
  ]),
  dict(group="Conditionals", rows=[
    ["CASE WHEN … THEN … ELSE … END", "First TRUE branch wins", "CASE WHEN x<20000 THEN 'Low' … END"],
    ["IF(cond, a, b)", "MySQL two-way shortcut", "IF(state='approved', amount, 0)"],
    ["cond (bare)", "Comparisons return 1 / 0 / NULL", "SUM(rating < 3)"],
  ]),
  dict(group="Aggregates", rows=[
    ["COUNT(*) · COUNT(col)", "All rows · non-NULL values", "COUNT(e.subject_name)"],
    ["COUNT(DISTINCT col)", "Unique non-NULL values", "COUNT(DISTINCT user_id)"],
    ["SUM / AVG / MIN / MAX", "Ignore NULLs; empty input → NULL", "ROUND(AVG(x), 2)"],
    ["GROUP_CONCAT(…)", "Join strings per group", "GROUP_CONCAT(DISTINCT p ORDER BY p SEPARATOR ',')"],
  ]),
  dict(group="Window functions", rows=[
    ["ROW_NUMBER()", "1,2,3,4 — unique positions", "ROW_NUMBER() OVER (PARTITION BY g ORDER BY d)"],
    ["RANK()", "1,2,2,4 — ties share, gaps after", "RANK() OVER (ORDER BY score DESC)"],
    ["DENSE_RANK()", "1,2,2,3 — ties share, no gaps", "DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC)"],
    ["LAG / LEAD(col, n, default)", "Value n rows before / after", "LAG(temperature) OVER (ORDER BY recordDate)"],
    ["SUM(x) OVER (ORDER BY k)", "Running total", "SUM(weight) OVER (ORDER BY turn)"],
    ["ROWS BETWEEN n PRECEDING AND CURRENT ROW", "Moving window by row count", "AVG(a) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)"],
    ["COUNT(*) OVER (PARTITION BY g)", "Group size on every row", "COUNT(*) OVER (PARTITION BY lat, lon)"],
  ]),
  dict(group="Dates", rows=[
    ["DATEDIFF(a, b)", "a − b in days", "DATEDIFF('2019-07-27', d)"],
    ["TIMESTAMPDIFF(unit, a, b)", "b − a in unit (note the order flips)", "TIMESTAMPDIFF(MONTH, start, end)"],
    ["DATE_ADD / DATE_SUB(d, INTERVAL n unit)", "Shift a date", "DATE_ADD(first_login, INTERVAL 1 DAY)"],
    ["DATE_FORMAT(d, fmt)", "%Y year, %m month, %d day, %H hour, %i minute", "DATE_FORMAT(d, '%Y-%m')"],
    ["YEAR(d) · MONTH(d) · LAST_DAY(d)", "Parts and month end", "LAST_DAY('2020-02-10') = 2020-02-29"],
  ]),
  dict(group="Strings", rows=[
    ["CONCAT(a, b) · CONCAT_WS(sep, …)", "CONCAT is NULL if any arg is NULL; CONCAT_WS skips NULLs", "CONCAT(first, ' ', last)"],
    ["UPPER · LOWER · TRIM · REPLACE", "Case, whitespace, substitution", "REPLACE(phone, '-', '')"],
    ["LEFT(s, n) · RIGHT(s, n) · SUBSTRING(s, pos, len)", "1-indexed", "SUBSTRING(name, 2)"],
    ["CHAR_LENGTH(s) · LENGTH(s)", "Characters · bytes", "CHAR_LENGTH(content) > 15"],
    ["LOCATE(sub, s) · INSTR(s, sub)", "Position of substring (0 if absent)", "LOCATE('@', mail)"],
    ["LIKE: % any run, _ one char", "Case-insensitive under default collation", "LIKE '% DIAB1%'"],
    ["REGEXP_LIKE(s, pat, 'c')", "Regex; 'c' = case-sensitive", "REGEXP_LIKE(mail, '^[A-Za-z]', 'c')"],
  ]),
  dict(group="Numbers and paging", rows=[
    ["ROUND(x, d) · TRUNCATE(x, d)", "Round · cut off", "ROUND(0.625, 2) = 0.63"],
    ["a / b · a DIV b · a % b", "Decimal division · integer division · remainder", "7 DIV 2 = 3"],
    ["CEIL · FLOOR · ABS", "Integer bounds, absolute value", "CEIL(4.1) = 5"],
    ["CAST(x AS DECIMAL(10,2))", "Explicit type conversion", "CAST(price AS SIGNED)"],
    ["LIMIT n OFFSET m · LIMIT m, n", "Skip m, take n", "LIMIT 1 OFFSET 1"],
  ]),
]

CONCEPTS = [
  dict(q="WHERE vs HAVING?",
       a="`WHERE` filters individual rows **before** grouping and can't use aggregates. `HAVING` filters groups **after** GROUP BY and can use `COUNT()`, `SUM()` etc. Put plain row conditions in WHERE — it shrinks the data before the expensive grouping."),
  dict(q="ROW_NUMBER vs RANK vs DENSE_RANK?",
       a="For salaries 100, 90, 90, 80: ROW_NUMBER → 1, 2, 3, 4; RANK → 1, 2, 2, 4; DENSE_RANK → 1, 2, 2, 3. Use DENSE_RANK for \"top N distinct values\", ROW_NUMBER for \"exactly one row per group\"."),
  dict(q="Which joins exist, and how do you get a FULL OUTER JOIN in MySQL?",
       a="INNER (matches only), LEFT / RIGHT (keep all rows of one side, NULLs for the other), CROSS (every combination), self join (a table joined to itself). MySQL has no FULL OUTER JOIN: write `A LEFT JOIN B … UNION A RIGHT JOIN B …` (UNION removes the duplicated matched rows)."),
  dict(q="UNION vs UNION ALL?",
       a="UNION removes duplicate rows (extra sort/hash step); UNION ALL keeps every row and is faster. Default to UNION ALL unless you need de-duplication — it's also the correct choice when two answers can be equal (LC 1341) or when stacking ids to count (LC 602)."),
  dict(q="COUNT(*) vs COUNT(1) vs COUNT(col) vs COUNT(DISTINCT col)?",
       a="COUNT(*) and COUNT(1) both count rows (same performance in MySQL). COUNT(col) counts non-NULL values of col. COUNT(DISTINCT col) counts unique non-NULL values. After a LEFT JOIN, count a right-table column to get 0 for unmatched rows."),
  dict(q="How does NULL behave?",
       a="Any comparison with NULL is UNKNOWN (so `= NULL` never matches — use IS NULL). Aggregates skip NULLs; COUNT(*) does not. GROUP BY puts all NULLs in one group. In MySQL, NULLs sort **first** in ASC order. Arithmetic with NULL gives NULL."),
  dict(q="Why is NOT IN dangerous?",
       a="`x NOT IN (1, 2, NULL)` expands to `x<>1 AND x<>2 AND x<>NULL`; the last part is UNKNOWN, so the whole condition is never TRUE and the query returns nothing. If the subquery column can be NULL, use NOT EXISTS or a LEFT JOIN … IS NULL anti-join."),
  dict(q="IN vs EXISTS?",
       a="IN compares a value with a list/subquery result; EXISTS checks whether a correlated subquery returns any row and stops at the first match. Modern MySQL often rewrites both into semi-joins, so performance is similar; the real difference is NULL behaviour with the NOT forms."),
  dict(q="Correlated vs non-correlated subquery?",
       a="A non-correlated subquery runs on its own once (e.g. `SELECT MAX(salary) FROM Employee`). A correlated subquery references the outer row (`WHERE e2.dept = e.dept`) and logically runs once per outer row — fine on small data, but a window function or join is usually faster."),
  dict(q="CTE vs subquery vs temporary table?",
       a="A CTE (`WITH x AS (…)`) is a named subquery for one statement — more readable, can be referenced several times, and can be RECURSIVE (hierarchies, number series). A derived table is the inline form. A temporary table persists for the session and can be indexed — useful for heavy multi-step work."),
  dict(q="Window function vs GROUP BY?",
       a="GROUP BY collapses each group to one row. A window function computes over a group (PARTITION BY) but keeps every row, so you can show the row and its group's metric side by side (rank, running total, group size)."),
  dict(q="What is the logical order of execution — and why can't I use a SELECT alias in WHERE?",
       a="FROM/JOIN → WHERE → GROUP BY → HAVING → window functions → SELECT → DISTINCT → ORDER BY → LIMIT. Aliases are created in SELECT, after WHERE runs. MySQL does allow aliases in GROUP BY, HAVING and ORDER BY as an extension. Window results can only be filtered from an outer query."),
  dict(q="DELETE vs TRUNCATE vs DROP?",
       a="DELETE removes chosen rows (WHERE), is logged row by row, fires triggers and can be rolled back. TRUNCATE removes all rows fast, resets AUTO_INCREMENT, and is DDL (implicit commit in MySQL). DROP removes the table itself, structure included."),
  dict(q="Primary key vs unique key vs foreign key?",
       a="Primary key: unique, NOT NULL, one per table; in InnoDB it is the clustered index. Unique key: unique values but allows NULLs (multiple), many per table. Foreign key: references another table's key to enforce referential integrity (with ON DELETE/UPDATE actions)."),
  dict(q="Clustered vs secondary index (InnoDB)?",
       a="The clustered index is the table itself, stored in primary-key order. A secondary index stores the indexed columns plus the primary key; a lookup that needs other columns goes back to the clustered index. A covering index contains every column the query needs, so that second lookup is skipped."),
  dict(q="When will MySQL not use an index?",
       a="Function or arithmetic on the indexed column (`YEAR(d) = 2020`, `DATE_FORMAT(d…)`), leading wildcard (`LIKE '%x'`), implicit type conversion, not using the leftmost column of a composite index, OR across different columns, or when the optimizer estimates a full scan is cheaper (low selectivity). Rewrite as a range: `d >= '2020-01-01' AND d < '2021-01-01'`."),
  dict(q="Composite index — the leftmost-prefix rule?",
       a="An index on (a, b, c) can serve filters on a, on a+b, and on a+b+c, but not on b alone or c alone. Equality columns first, then the range column; a range on a column stops the use of later columns for seeking."),
  dict(q="How do you read EXPLAIN?",
       a="Check `type` (ALL = full table scan; ref/eq_ref/range are good), `key` (index actually used), `rows` (estimated rows examined) and `Extra` (\"Using filesort\" / \"Using temporary\" signal extra work; \"Using index\" means covering index). MySQL 8 also has EXPLAIN ANALYZE with real timings."),
  dict(q="Normalization in one breath?",
       a="1NF: atomic values, no repeating groups. 2NF: no non-key column depends on only part of a composite key. 3NF: no non-key column depends on another non-key column. Normalize to avoid update anomalies; denormalize deliberately for read-heavy reporting."),
  dict(q="ACID and isolation levels?",
       a="Atomicity, Consistency, Isolation, Durability. Isolation levels: READ UNCOMMITTED (dirty reads), READ COMMITTED, REPEATABLE READ (InnoDB default), SERIALIZABLE. Anomalies to name: dirty read, non-repeatable read, phantom read."),
  dict(q="CHAR vs VARCHAR, DECIMAL vs FLOAT?",
       a="CHAR(n) is fixed length (padded), good for fixed codes; VARCHAR(n) is variable length. DECIMAL is exact — use it for money; FLOAT/DOUBLE are approximate binary floats (0.1 + 0.2 ≠ 0.3)."),
  dict(q="How do you find and remove duplicates?",
       a="Find: `SELECT email, COUNT(*) FROM T GROUP BY email HAVING COUNT(*) > 1`. Remove keeping the smallest id: `DELETE t1 FROM T t1 JOIN T t2 ON t1.email = t2.email AND t1.id > t2.id`, or delete rows with `ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) > 1` via a derived table."),
  dict(q="Nth highest salary — three ways?",
       a="(1) `SELECT DISTINCT salary … ORDER BY salary DESC LIMIT 1 OFFSET N-1`, wrapped in a scalar subquery for NULL. (2) `DENSE_RANK() OVER (ORDER BY salary DESC) = N` with an outer MAX. (3) Correlated: salary where `COUNT(DISTINCT higher salaries) = N-1`."),
  dict(q="How do you pivot rows into columns?",
       a="Conditional aggregation: `SELECT id, SUM(CASE WHEN month='Jan' THEN revenue END) AS jan, SUM(CASE WHEN month='Feb' THEN revenue END) AS feb FROM T GROUP BY id`. MySQL has no PIVOT keyword. Unpivot with UNION ALL."),
  dict(q="What does ONLY_FULL_GROUP_BY do?",
       a="With it on (MySQL 8 default), every SELECT column must be aggregated or functionally dependent on the GROUP BY columns. It stops queries like `SELECT dept, name, MAX(salary) … GROUP BY dept` that would otherwise return an arbitrary name — not the one with the max salary."),
  dict(q="Default window frame gotcha?",
       a="With ORDER BY and no frame, the frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: rows with equal ORDER BY values are included together, and LAST_VALUE returns the current row's peer, not the partition's last. Specify `ROWS BETWEEN …` (or UNBOUNDED FOLLOWING for LAST_VALUE) explicitly."),
  dict(q="Integer division and rounding in MySQL?",
       a="In MySQL `/` returns a decimal (5/2 = 2.5000); use DIV for integer division. In PostgreSQL / SQL Server, int/int truncates — cast first. ROUND on exact DECIMAL values rounds half away from zero (2.5 → 3)."),
  dict(q="View vs materialized view?",
       a="A view is a stored query, re-run every time it is read. A materialized view stores the result and needs refreshing. MySQL has no native materialized views — use a summary table refreshed by events or ETL."),
]

FRAMEWORK = [
  dict(t="Pin the grain", d="Say out loud: \"one output row per ___\". Confirm the output columns, their names and whether order matters."),
  dict(t="Find tables and the preserved side", d="Which tables hold each column? Which entity must appear even without matches (LEFT JOIN from it)? Which keys join them?"),
  dict(t="List the edge cases", d="NULLs in filters and joins, duplicate rows, ties for first place, empty input (one NULL row or no rows?), inclusive/exclusive date boundaries."),
  dict(t="Build in logical order", d="FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY/LIMIT. Trace 3–4 sample rows through each stage before writing the next."),
  dict(t="Offer an alternative and talk performance", d="Mention the window-function vs self-join version, indexes on join and filter columns, and keeping predicates sargable (no functions on indexed columns)."),
]

TRAPS = [
  "`= NULL` never matches — use `IS NULL`; `NULL <> 2` drops the row (#2, #11).",
  "`NOT IN (subquery)` returns nothing if the subquery yields any NULL — prefer `NOT EXISTS` (#8, #37).",
  "A condition on the right table in `WHERE` turns a LEFT JOIN into an INNER JOIN — put it in `ON` (#16).",
  "After a LEFT JOIN, `COUNT(*)` counts the NULL placeholder row — count a right-table column (#12).",
  "`UNION` silently de-duplicates — use `UNION ALL` unless you want that (#39, #41).",
  "`RANK()` leaves gaps after ties — \"top N distinct\" means `DENSE_RANK()` (#43).",
  "`ORDER BY … LIMIT` on an empty set gives no row — wrap in a scalar subquery or aggregate to get NULL (#28, #47).",
  "`LENGTH()` counts bytes; `CHAR_LENGTH()` counts characters (#5).",
  "MySQL `REGEXP` and `LIKE` are case-insensitive by default; escape `.` in patterns (#50).",
  "\"30 days ending D inclusive\" starts at D − 29; February 2020 has 29 days — use half-open ranges (#24, #39, #49).",
  "Aggregate first, then window: moving averages need one row per day (#40).",
  "Window results can't be filtered in the same query's `WHERE` — use a subquery or CTE (#33, #43).",
  "`SELECT g, MIN(d), other_col … GROUP BY g` does not return other_col from the MIN row (#25).",
]

EXEC_ORDER = [
  ["FROM / JOIN", "Build the working set of rows"],
  ["WHERE", "Filter rows (no aggregates, no SELECT aliases)"],
  ["GROUP BY", "Collapse rows into groups"],
  ["HAVING", "Filter groups (aggregates allowed)"],
  ["Window functions", "OVER (…) computed on the grouped rows"],
  ["SELECT", "Compute output columns; aliases are born"],
  ["DISTINCT", "Remove duplicate output rows"],
  ["ORDER BY", "Sort (aliases allowed)"],
  ["LIMIT / OFFSET", "Cut the result"],
]

REVISION = dict(sections=SECTIONS, patterns=PATTERNS, cheatsheet=CHEATSHEET, concepts=CONCEPTS,
                framework=FRAMEWORK, traps=TRAPS, exec_order=EXEC_ORDER)
