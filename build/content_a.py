# SQL 50 content — Select + Basic Joins (problems 1–14)
# Sample data is original (not LeetCode's examples); problem statements are paraphrased.

PROBLEMS_A = [
# ───────────────────────────── SELECT ─────────────────────────────
dict(
  n=1, id=1757, slug="recyclable-and-low-fat-products", title="Recyclable and Low Fat Products",
  sec="select", diff="Easy", concepts=["WHERE", "AND"],
  pattern="Plain row filter on two flag columns",
  prompt="A `Products` table stores two Y/N flags per product: `low_fats` and `recyclable`. List the ids of products where **both** flags are `'Y'`.",
  returns="product_id (any order)",
  setup="""
CREATE TABLE Products (product_id INT PRIMARY KEY, low_fats ENUM('Y','N'), recyclable ENUM('Y','N'));
INSERT INTO Products VALUES (0,'Y','N'),(1,'Y','Y'),(2,'N','Y'),(3,'Y','Y'),(4,'N','N');
""",
  solution="""
SELECT product_id
FROM Products
WHERE low_fats = 'Y'
  AND recyclable = 'Y';
""",
  alts=[("Tuple comparison", """
SELECT product_id
FROM Products
WHERE (low_fats, recyclable) = ('Y', 'Y');
""", "MySQL supports row constructors — handy when matching several columns at once.")],
  approach=[
    "Output grain: one row per product, only the id column.",
    "Both conditions must hold at the same time → combine with `AND`.",
    "No joins, no grouping — a single `WHERE` does it.",
  ],
  steps=[
    dict(t="Test every row against both flags", sql="""
SELECT product_id, low_fats, recyclable,
       low_fats = 'Y' AS `+low_fats='Y'`,
       recyclable = 'Y' AS `+recyclable='Y'`,
       (low_fats = 'Y' AND recyclable = 'Y') AS _keep
FROM Products ORDER BY product_id""",
      note="`WHERE` keeps a row only when the whole condition is TRUE. Rows 1 and 3 pass both tests."),
  ],
  remember=[
    "ENUM values compare like strings — always quote them: `'Y'`.",
    "`AND` binds tighter than `OR`. When you mix them, add parentheses.",
  ],
  pitfalls=["Writing `low_fats = Y` (unquoted) makes MySQL look for a column named Y."],
  recall="WHERE low_fats='Y' AND recyclable='Y'.",
),
dict(
  n=2, id=584, slug="find-customer-referee", title="Find Customer Referee",
  sec="select", diff="Easy", concepts=["WHERE", "NULL", "IS NULL"],
  pattern="Negative filter on a nullable column",
  prompt="Each customer may have been referred by another customer (`referee_id`, can be NULL). Return the names of customers who were **not** referred by the customer with id = 2 — this includes customers referred by nobody.",
  returns="name (any order)",
  setup="""
CREATE TABLE Customer (id INT PRIMARY KEY, name VARCHAR(25), referee_id INT);
INSERT INTO Customer VALUES (1,'Will',NULL),(2,'Jane',NULL),(3,'Alex',2),(4,'Bill',NULL),(5,'Zack',1),(6,'Mark',2);
""",
  solution="""
SELECT name
FROM Customer
WHERE referee_id <> 2
   OR referee_id IS NULL;
""",
  alts=[
    ("IFNULL to a sentinel", """
SELECT name
FROM Customer
WHERE IFNULL(referee_id, 0) <> 2;
""", "Replace NULL with a value that can never be 2."),
    ("Null-safe equality <=>", """
SELECT name
FROM Customer
WHERE NOT (referee_id <=> 2);
""", "`<=>` returns 1/0 and never NULL, so NOT works as expected."),
  ],
  approach=[
    "\"Not referred by 2\" sounds like `referee_id <> 2` — but NULL referees must be included too.",
    "Any comparison with NULL (`NULL <> 2`) is UNKNOWN, and `WHERE` drops UNKNOWN rows.",
    "So add the NULL case explicitly with `OR referee_id IS NULL`.",
  ],
  steps=[
    dict(t="Naive filter: referee_id <> 2", sql="""
SELECT id, name, referee_id,
       referee_id <> 2 AS `+referee_id <> 2`,
       (referee_id <> 2) IS TRUE AS _keep
FROM Customer ORDER BY id""",
      note="The comparison is NULL for Will, Jane and Bill, so `WHERE` silently drops them. Only Zack survives — wrong."),
    dict(t="Fix: OR referee_id IS NULL", sql="""
SELECT id, name, referee_id,
       referee_id IS NULL AS `+is_null`,
       (referee_id <> 2 OR referee_id IS NULL) AS _keep
FROM Customer ORDER BY id""",
      note="Now the NULL rows are TRUE too. Only Alex and Mark (referred by 2) are excluded."),
  ],
  remember=[
    "SQL uses three-valued logic: TRUE, FALSE, UNKNOWN. `WHERE` keeps TRUE only.",
    "`= NULL` / `<> NULL` never match anything — use `IS NULL` / `IS NOT NULL`.",
    "`<=>` is MySQL's null-safe equal: `NULL <=> NULL` is 1.",
  ],
  pitfalls=["`WHERE referee_id != 2` alone fails the test case with NULL referees — the classic first trap of SQL 50."],
  recall="<> 2 OR IS NULL — NULL comparisons are UNKNOWN.",
),
dict(
  n=3, id=595, slug="big-countries", title="Big Countries",
  sec="select", diff="Easy", concepts=["WHERE", "OR", "UNION"],
  pattern="Filter with OR across two columns",
  prompt="A country is **big** if its area is at least 3,000,000 km² **or** its population is at least 25,000,000. Report name, population and area of big countries.",
  returns="name, population, area (any order)",
  setup="""
CREATE TABLE World (name VARCHAR(255), continent VARCHAR(255), area INT, population INT, gdp BIGINT);
INSERT INTO World VALUES
('India','Asia',3287263,1428600000,3550000000000),
('Nepal','Asia',147516,30900000,40000000000),
('Bhutan','Asia',38394,780000,3000000000),
('Australia','Oceania',7692024,26000000,1700000000000),
('Sri Lanka','Asia',65610,22000000,84000000000),
('Mongolia','Asia',1564116,3400000,20000000000);
""",
  solution="""
SELECT name, population, area
FROM World
WHERE area >= 3000000
   OR population >= 25000000;
""",
  alts=[("UNION of two filters", """
SELECT name, population, area FROM World WHERE area >= 3000000
UNION
SELECT name, population, area FROM World WHERE population >= 25000000;
""", "UNION (not UNION ALL) removes countries that satisfy both conditions, like India and Australia. This form lets MySQL use a separate index for each condition.")],
  approach=[
    "Either condition is enough → `OR`.",
    "\"At least\" means `>=` (inclusive).",
    "Select only the three requested columns.",
  ],
  steps=[
    dict(t="Evaluate both conditions per country", sql="""
SELECT name, area, population,
       area >= 3000000 AS `+big_area`,
       population >= 25000000 AS `+big_population`,
       (area >= 3000000 OR population >= 25000000) AS _keep
FROM World ORDER BY name""",
      note="India and Australia pass both; Nepal passes on population only. One TRUE is enough for OR."),
  ],
  remember=[
    "\"At least\" → `>=`; \"more than\" → `>`. Read boundaries carefully.",
    "Interview talking point: `OR` on two different columns can stop MySQL from using one index; rewriting as `UNION` lets each branch use its own index.",
  ],
  pitfalls=["Using `UNION ALL` in the alternative duplicates countries that match both conditions."],
  recall="area >= 3M OR population >= 25M (or UNION of the two).",
),
dict(
  n=4, id=1148, slug="article-views-i", title="Article Views I",
  sec="select", diff="Easy", concepts=["DISTINCT", "ORDER BY", "Alias"],
  pattern="Filter where two columns are equal, then de-duplicate",
  prompt="The `Views` log (it can contain duplicate rows) records who viewed which article. Find every author who viewed **at least one of their own** articles. Return their ids sorted ascending, as column `id`.",
  returns="id (sorted ascending)",
  setup="""
CREATE TABLE Views (article_id INT, author_id INT, viewer_id INT, view_date DATE);
INSERT INTO Views VALUES
(1,3,5,'2024-01-01'),(1,3,3,'2024-01-02'),(2,7,7,'2024-01-01'),(2,7,7,'2024-01-03'),
(4,7,1,'2024-01-04'),(3,4,4,'2024-01-05'),(3,4,4,'2024-01-05'),(5,9,2,'2024-01-06');
""",
  solution="""
SELECT DISTINCT author_id AS id
FROM Views
WHERE author_id = viewer_id
ORDER BY id;
""",
  alts=[("GROUP BY instead of DISTINCT", """
SELECT author_id AS id
FROM Views
WHERE author_id = viewer_id
GROUP BY author_id
ORDER BY id;
""", "Same result; GROUP BY also de-duplicates.")],
  approach=[
    "\"Viewed own article\" → the row's `author_id` equals its `viewer_id`.",
    "An author can do that many times (and the log has duplicates) → `DISTINCT`.",
    "Rename to `id` and sort ascending as asked.",
  ],
  steps=[
    dict(t="Keep self-views only", sql="""
SELECT article_id, author_id, viewer_id, view_date,
       author_id = viewer_id AS _keep
FROM Views ORDER BY article_id, view_date""",
      note="Five rows are self-views, but they belong to only three authors."),
    dict(t="Collapse each author to one row", sql="""
SELECT author_id AS _grp, author_id, viewer_id, article_id, view_date
FROM Views WHERE author_id = viewer_id ORDER BY author_id, view_date""",
      note="Each colour band is one author. `DISTINCT author_id` turns every band into a single row."),
  ],
  remember=[
    "`DISTINCT` applies to the whole selected row, not one column.",
    "MySQL lets you use a SELECT alias (`id`) in `ORDER BY`, but not in `WHERE`.",
  ],
  pitfalls=["Forgetting `ORDER BY id` — this problem checks the order."],
  recall="DISTINCT author_id WHERE author_id = viewer_id ORDER BY id.",
  ordered=True,
),
dict(
  n=5, id=1683, slug="invalid-tweets", title="Invalid Tweets",
  sec="select", diff="Easy", concepts=["CHAR_LENGTH", "String functions"],
  pattern="Filter on string length",
  prompt="A tweet is **invalid** if its content has more than 15 characters. Return the ids of invalid tweets.",
  returns="tweet_id (any order)",
  setup="""
CREATE TABLE Tweets (tweet_id INT PRIMARY KEY, content VARCHAR(50));
INSERT INTO Tweets VALUES (1,'Let us Code'),(2,'More than fifteen chars here!'),(3,'नमस्ते दुनिया'),(4,'SQL rocks!!!!!!');
""",
  solution="""
SELECT tweet_id
FROM Tweets
WHERE CHAR_LENGTH(content) > 15;
""",
  alts=[],
  approach=[
    "\"Number of characters\" → `CHAR_LENGTH()`.",
    "\"More than 15\" is strict → `> 15`.",
  ],
  steps=[
    dict(t="Characters vs bytes", sql="""
SELECT tweet_id, content,
       CHAR_LENGTH(content) AS `+CHAR_LENGTH`,
       LENGTH(content) AS `+LENGTH (bytes)`,
       CHAR_LENGTH(content) > 15 AS _keep
FROM Tweets ORDER BY tweet_id""",
      note="The Hindi tweet is 13 characters but 37 bytes in UTF-8. `LENGTH() > 15` would wrongly mark it invalid. Tweet 4 is exactly 15 → still valid."),
  ],
  remember=[
    "`CHAR_LENGTH()` counts characters; `LENGTH()` counts **bytes**. They differ for any non-ASCII text.",
    "LeetCode data is ASCII, so both pass there — but say CHAR_LENGTH in interviews.",
  ],
  pitfalls=["Using `>= 15` — a 15-character tweet is valid."],
  recall="CHAR_LENGTH(content) > 15 (not LENGTH → bytes).",
),

# ───────────────────────────── BASIC JOINS ─────────────────────────────
dict(
  n=6, id=1378, slug="replace-employee-id-with-the-unique-identifier", title="Replace Employee ID With The Unique Identifier",
  sec="joins", diff="Easy", concepts=["LEFT JOIN"],
  pattern="Keep every row of the main table → LEFT JOIN",
  prompt="`Employees` has id and name; `EmployeeUNI` maps some employee ids to a `unique_id`. Show each employee's unique id (NULL if they have none) next to their name.",
  returns="unique_id, name (any order)",
  setup="""
CREATE TABLE Employees (id INT PRIMARY KEY, name VARCHAR(20));
CREATE TABLE EmployeeUNI (id INT, unique_id INT, PRIMARY KEY (id, unique_id));
INSERT INTO Employees VALUES (1,'Aarav'),(7,'Bina'),(11,'Chetan'),(90,'Divya'),(3,'Esha');
INSERT INTO EmployeeUNI VALUES (3,1),(11,2),(90,3);
""",
  solution="""
SELECT u.unique_id, e.name
FROM Employees e
LEFT JOIN EmployeeUNI u
       ON e.id = u.id;
""",
  alts=[("RIGHT JOIN (tables swapped)", """
SELECT u.unique_id, e.name
FROM EmployeeUNI u
RIGHT JOIN Employees e ON e.id = u.id;
""", "Equivalent; most people standardise on LEFT JOIN for readability.")],
  approach=[
    "Every employee must appear, even without a match → the employee table is the \"preserved\" side.",
    "Put it on the left of a `LEFT JOIN`; unmatched rows get NULL for `unique_id`.",
  ],
  steps=[
    dict(t="LEFT JOIN keeps all employees", sql="""
SELECT e.id AS `e.id`, e.name, u.id AS `u.id`, u.unique_id
FROM Employees e LEFT JOIN EmployeeUNI u ON e.id = u.id
ORDER BY e.id""",
      note="Aarav and Bina have no partner row, so the `u.*` columns are NULL. An INNER JOIN would drop them."),
  ],
  remember=[
    "\"Show X even if it has no Y\" → `X LEFT JOIN Y`.",
    "Unmatched right-side columns become NULL.",
  ],
  pitfalls=["Using plain `JOIN` (INNER) loses employees without a unique id."],
  recall="Employees LEFT JOIN EmployeeUNI.",
),
dict(
  n=7, id=1068, slug="product-sales-analysis-i", title="Product Sales Analysis I",
  sec="joins", diff="Easy", concepts=["INNER JOIN", "USING"],
  pattern="Look up a name for each fact row → INNER JOIN",
  prompt="For every sale in `Sales`, report the product's name (from `Product`), the year and the price.",
  returns="product_name, year, price (any order)",
  setup="""
CREATE TABLE Sales (sale_id INT, product_id INT, year INT, quantity INT, price INT, PRIMARY KEY (sale_id, year));
CREATE TABLE Product (product_id INT PRIMARY KEY, product_name VARCHAR(10));
INSERT INTO Product VALUES (10,'Redmi'),(20,'iPhone'),(30,'Pixel');
INSERT INTO Sales VALUES (1,10,2021,10,12000),(2,10,2022,12,11000),(3,20,2022,5,70000),(4,20,2023,7,72000);
""",
  solution="""
SELECT p.product_name, s.year, s.price
FROM Sales s
JOIN Product p
  ON s.product_id = p.product_id;
""",
  alts=[("USING shorthand", """
SELECT p.product_name, s.year, s.price
FROM Sales s
JOIN Product p USING (product_id);
""", "`USING(col)` works when the join column has the same name in both tables.")],
  approach=[
    "Output grain: one row per sale.",
    "Each sale has exactly one product → INNER JOIN to fetch the name.",
  ],
  steps=[
    dict(t="Match each sale to its product", sql="""
SELECT s.sale_id, s.product_id, p.product_name, s.year, s.price
FROM Sales s JOIN Product p ON s.product_id = p.product_id
ORDER BY s.sale_id""",
      note="Pixel has no sales, so it never appears — fine, the question is about sales."),
  ],
  remember=["`JOIN` = `INNER JOIN`: keeps only matched pairs.", "Alias tables (`s`, `p`) and prefix columns to avoid ambiguity errors."],
  pitfalls=[],
  recall="Sales JOIN Product on product_id.",
),
dict(
  n=8, id=1581, slug="customer-who-visited-but-did-not-make-any-transactions", title="Customer Who Visited but Did Not Make Any Transactions",
  sec="joins", diff="Easy", concepts=["LEFT JOIN", "IS NULL", "Anti-join", "GROUP BY"],
  pattern="Anti-join: rows in A with no match in B",
  prompt="`Visits` lists mall visits; `Transactions` lists purchases made during a visit. For each customer, count the visits in which they bought **nothing**.",
  returns="customer_id, count_no_trans (any order)",
  setup="""
CREATE TABLE Visits (visit_id INT PRIMARY KEY, customer_id INT);
CREATE TABLE Transactions (transaction_id INT PRIMARY KEY, visit_id INT, amount INT);
INSERT INTO Visits VALUES (1,101),(2,102),(3,101),(4,103),(5,104),(6,103),(7,103),(8,105);
INSERT INTO Transactions VALUES (11,1,500),(12,1,250),(13,4,900),(14,8,120);
""",
  solution="""
SELECT v.customer_id,
       COUNT(*) AS count_no_trans
FROM Visits v
LEFT JOIN Transactions t
       ON v.visit_id = t.visit_id
WHERE t.transaction_id IS NULL
GROUP BY v.customer_id;
""",
  alts=[
    ("NOT IN", """
SELECT customer_id, COUNT(*) AS count_no_trans
FROM Visits
WHERE visit_id NOT IN (SELECT visit_id FROM Transactions)
GROUP BY customer_id;
""", "Safe here because Transactions.visit_id is never NULL. If the subquery could return NULL, NOT IN returns no rows at all."),
    ("NOT EXISTS", """
SELECT v.customer_id, COUNT(*) AS count_no_trans
FROM Visits v
WHERE NOT EXISTS (SELECT 1 FROM Transactions t WHERE t.visit_id = v.visit_id)
GROUP BY v.customer_id;
""", "NULL-safe and usually optimised to the same anti-join plan."),
  ],
  approach=[
    "\"Visits without transactions\" = rows in Visits that have no partner in Transactions → anti-join.",
    "LEFT JOIN, then keep rows where the right side is NULL.",
    "Count those per customer.",
  ],
  steps=[
    dict(t="LEFT JOIN visits to transactions", sql="""
SELECT v.visit_id, v.customer_id, t.transaction_id, t.amount
FROM Visits v LEFT JOIN Transactions t ON v.visit_id = t.visit_id
ORDER BY v.visit_id, t.transaction_id""",
      note="Visit 1 had two purchases so it appears twice. Visits with no purchase have NULL on the right."),
    dict(t="WHERE t.transaction_id IS NULL", sql="""
SELECT v.visit_id, v.customer_id, t.transaction_id,
       t.transaction_id IS NULL AS _keep
FROM Visits v LEFT JOIN Transactions t ON v.visit_id = t.visit_id
ORDER BY v.visit_id, t.transaction_id""",
      note="Only the NULL rows survive — these are the empty-handed visits."),
    dict(t="GROUP BY customer_id", sql="""
SELECT v.customer_id AS _grp, v.customer_id, v.visit_id
FROM Visits v LEFT JOIN Transactions t ON v.visit_id = t.visit_id
WHERE t.transaction_id IS NULL
ORDER BY v.customer_id, v.visit_id""",
      note="Customer 103 has two such visits; everyone else has one. Customer 105 never appears."),
  ],
  remember=[
    "Anti-join template: `A LEFT JOIN B ON … WHERE B.pk IS NULL`.",
    "Test a column of B that can't be NULL in a real match (its primary key).",
    "`NOT EXISTS` is the NULL-safe alternative to `NOT IN`.",
  ],
  pitfalls=["Putting `t.transaction_id IS NULL` in the `ON` clause instead of `WHERE` keeps every visit."],
  recall="LEFT JOIN Transactions WHERE t.transaction_id IS NULL, GROUP BY customer.",
),
dict(
  n=9, id=197, slug="rising-temperature", title="Rising Temperature",
  sec="joins", diff="Easy", concepts=["Self join", "DATEDIFF", "LAG"],
  pattern="Compare a row with the previous calendar day",
  prompt="`Weather` has one temperature per date. Return the ids of dates whose temperature is higher than on the **previous day** (yesterday).",
  returns="id (any order)",
  setup="""
CREATE TABLE Weather (id INT PRIMARY KEY, recordDate DATE, temperature INT);
INSERT INTO Weather VALUES
(1,'2024-01-03',20),(2,'2024-01-01',10),(3,'2024-01-02',25),
(4,'2024-01-04',30),(5,'2024-01-06',35),(6,'2024-01-07',38);
""",
  solution="""
SELECT today.id
FROM Weather today
JOIN Weather yesterday
  ON DATEDIFF(today.recordDate, yesterday.recordDate) = 1
WHERE today.temperature > yesterday.temperature;
""",
  alts=[
    ("DATE_SUB in the join", """
SELECT w1.id
FROM Weather w1
JOIN Weather w2
  ON w2.recordDate = DATE_SUB(w1.recordDate, INTERVAL 1 DAY)
WHERE w1.temperature > w2.temperature;
""", "Same logic; keeps the date column bare on one side, which is index-friendly."),
    ("LAG with a date check", """
SELECT id
FROM (
  SELECT id, recordDate, temperature,
         LAG(recordDate)  OVER (ORDER BY recordDate) AS prev_date,
         LAG(temperature) OVER (ORDER BY recordDate) AS prev_temp
  FROM Weather
) t
WHERE DATEDIFF(recordDate, prev_date) = 1
  AND temperature > prev_temp;
""", "LAG gives the previous *row*; you still must check that row is exactly one day earlier."),
  ],
  approach=[
    "Each row must be compared with another row of the same table → self join.",
    "Pair condition: the other row's date is exactly one day earlier → `DATEDIFF(a, b) = 1`.",
    "Then keep pairs where today is warmer.",
  ],
  steps=[
    dict(t="Pair each day with yesterday (LEFT JOIN to see misses)", sql="""
SELECT today.id, today.recordDate AS today_date, today.temperature AS today_temp,
       y.recordDate AS yesterday_date, y.temperature AS yesterday_temp,
       IFNULL(today.temperature > y.temperature, 0) AS _keep
FROM Weather today
LEFT JOIN Weather y ON DATEDIFF(today.recordDate, y.recordDate) = 1
ORDER BY today.recordDate""",
      note="Jan 6 is warmer than the previous row (Jan 4) but Jan 5 is missing, so it has no 'yesterday' and is excluded. The inner JOIN in the solution simply drops such rows."),
  ],
  remember=[
    "Never use `id + 1` for \"previous day\" — ids are not in date order here.",
    "`DATEDIFF(a, b)` returns a − b in days.",
    "`LAG()` returns the previous row, not the previous date — check the gap.",
  ],
  pitfalls=["Joining on `w1.id = w2.id + 1` fails when ids are shuffled or dates have gaps."],
  recall="Self join ON DATEDIFF(today, yesterday) = 1 AND warmer.",
),
dict(
  n=10, id=1661, slug="average-time-of-process-per-machine", title="Average Time of Process per Machine",
  sec="joins", diff="Easy", concepts=["Self join", "AVG", "ROUND"],
  pattern="Pair 'start' and 'end' rows of the same entity",
  prompt="`Activity` logs a `start` row and an `end` row (with a timestamp) for every process on every machine. For each machine, compute the average time a process takes (end − start), rounded to 3 decimals.",
  returns="machine_id, processing_time (any order)",
  setup="""
CREATE TABLE Activity (machine_id INT, process_id INT, activity_type ENUM('start','end'), timestamp DECIMAL(8,3));
INSERT INTO Activity VALUES
(0,0,'start',0.500),(0,0,'end',1.200),(0,1,'start',2.000),(0,1,'end',2.900),
(1,0,'start',0.250),(1,0,'end',1.000),(1,1,'start',3.100),(1,1,'end',3.600),
(2,0,'start',1.000),(2,0,'end',2.333);
""",
  solution="""
SELECT s.machine_id,
       ROUND(AVG(e.timestamp - s.timestamp), 3) AS processing_time
FROM Activity s
JOIN Activity e
  ON  s.machine_id   = e.machine_id
  AND s.process_id   = e.process_id
  AND s.activity_type = 'start'
  AND e.activity_type = 'end'
GROUP BY s.machine_id;
""",
  alts=[("Conditional aggregation (no join)", """
SELECT machine_id,
       ROUND(SUM(CASE WHEN activity_type = 'end' THEN timestamp ELSE -timestamp END)
             / COUNT(DISTINCT process_id), 3) AS processing_time
FROM Activity
GROUP BY machine_id;
""", "Sum of ends minus sum of starts = total duration; divide by number of processes.")],
  approach=[
    "A duration needs two rows (start, end) side by side → self join on (machine_id, process_id).",
    "Fix the roles in the join: left copy = start row, right copy = end row.",
    "Average the differences per machine and round to 3.",
  ],
  steps=[
    dict(t="Line up start and end rows", sql="""
SELECT s.machine_id AS _grp, s.machine_id, s.process_id,
       s.timestamp AS start_ts, e.timestamp AS end_ts,
       e.timestamp - s.timestamp AS `+duration`
FROM Activity s JOIN Activity e
  ON s.machine_id = e.machine_id AND s.process_id = e.process_id
 AND s.activity_type = 'start' AND e.activity_type = 'end'
ORDER BY s.machine_id, s.process_id""",
      note="One row per process. Machine 0: (0.7 + 0.9) / 2 = 0.800."),
  ],
  remember=[
    "Self join = put two rows of the same entity on one line.",
    "Put the role filters (`'start'` / `'end'`) in the join so each pair appears once.",
    "`ROUND(x, 3)` — LeetCode checks the rounding.",
  ],
  pitfalls=["Without the activity_type filters you get 4 pairs per process (start-start, start-end, …)."],
  recall="Self join start↔end on machine+process; ROUND(AVG(end-start),3).",
),
dict(
  n=11, id=577, slug="employee-bonus", title="Employee Bonus",
  sec="joins", diff="Easy", concepts=["LEFT JOIN", "NULL"],
  pattern="LEFT JOIN + filter that must also keep NULLs",
  prompt="Report the name and bonus of every employee whose bonus is **less than 1000** — employees with no bonus row count too (show NULL).",
  returns="name, bonus (any order)",
  setup="""
CREATE TABLE Employee (empId INT PRIMARY KEY, name VARCHAR(255), supervisor INT, salary INT);
CREATE TABLE Bonus (empId INT PRIMARY KEY, bonus INT);
INSERT INTO Employee VALUES (3,'Riya',NULL,4000),(1,'Kabir',3,1000),(2,'Meera',1,2000),(4,'Tanvi',3,4000),(5,'Om',3,3000);
INSERT INTO Bonus VALUES (2,500),(4,2000),(5,1000);
""",
  solution="""
SELECT e.name, b.bonus
FROM Employee e
LEFT JOIN Bonus b
       ON e.empId = b.empId
WHERE b.bonus < 1000
   OR b.bonus IS NULL;
""",
  alts=[("IFNULL", """
SELECT e.name, b.bonus
FROM Employee e
LEFT JOIN Bonus b ON e.empId = b.empId
WHERE IFNULL(b.bonus, 0) < 1000;
""", "Treat a missing bonus as 0 for the comparison only; the output still shows NULL.")],
  approach=[
    "Employees without a bonus row must appear → `LEFT JOIN Bonus`.",
    "Filter `bonus < 1000`, remembering NULL < 1000 is UNKNOWN → add `OR b.bonus IS NULL`.",
  ],
  steps=[
    dict(t="LEFT JOIN, then test bonus < 1000", sql="""
SELECT e.empId, e.name, b.bonus,
       b.bonus < 1000 AS `+bonus < 1000`,
       (b.bonus < 1000 OR b.bonus IS NULL) AS _keep
FROM Employee e LEFT JOIN Bonus b ON e.empId = b.empId
ORDER BY e.empId""",
      note="Kabir and Riya have NULL bonus: the plain comparison is NULL, so they need the `IS NULL` branch. Om's 1000 is not < 1000."),
  ],
  remember=["Same NULL trap as #2, now after a LEFT JOIN.", "Filters on the right table in `WHERE` can silently turn a LEFT JOIN into an INNER JOIN — unless you allow NULL."],
  pitfalls=["`WHERE b.bonus < 1000` alone drops every employee without a bonus."],
  recall="LEFT JOIN Bonus WHERE bonus < 1000 OR bonus IS NULL.",
),
dict(
  n=12, id=1280, slug="students-and-examinations", title="Students and Examinations",
  sec="joins", diff="Easy", concepts=["CROSS JOIN", "LEFT JOIN", "COUNT(col)"],
  pattern="Every combination → CROSS JOIN skeleton + LEFT JOIN facts",
  prompt="For **every** student and **every** subject, count how many times the student sat that exam (0 if never). `Examinations` may contain duplicates. Order by student_id, then subject_name.",
  returns="student_id, student_name, subject_name, attended_exams (ordered)",
  setup="""
CREATE TABLE Students (student_id INT PRIMARY KEY, student_name VARCHAR(20));
CREATE TABLE Subjects (subject_name VARCHAR(20) PRIMARY KEY);
CREATE TABLE Examinations (student_id INT, subject_name VARCHAR(20));
INSERT INTO Students VALUES (1,'Anil'),(2,'Bela'),(13,'Chirag');
INSERT INTO Subjects VALUES ('Math'),('Physics'),('Programming');
INSERT INTO Examinations VALUES
(1,'Math'),(1,'Physics'),(1,'Programming'),(2,'Programming'),(1,'Physics'),(1,'Math'),
(13,'Math'),(13,'Programming'),(13,'Physics'),(2,'Math'),(1,'Math');
""",
  solution="""
SELECT s.student_id, s.student_name, sub.subject_name,
       COUNT(e.subject_name) AS attended_exams
FROM Students s
CROSS JOIN Subjects sub
LEFT JOIN Examinations e
       ON e.student_id = s.student_id
      AND e.subject_name = sub.subject_name
GROUP BY s.student_id, s.student_name, sub.subject_name
ORDER BY s.student_id, sub.subject_name;
""",
  alts=[("Pre-aggregate, then join", """
SELECT s.student_id, s.student_name, sub.subject_name,
       IFNULL(c.cnt, 0) AS attended_exams
FROM Students s
CROSS JOIN Subjects sub
LEFT JOIN (
  SELECT student_id, subject_name, COUNT(*) AS cnt
  FROM Examinations
  GROUP BY student_id, subject_name
) c ON c.student_id = s.student_id AND c.subject_name = sub.subject_name
ORDER BY s.student_id, sub.subject_name;
""", "Counting first keeps the join small on big tables.")],
  approach=[
    "Output must include combinations that never happened (0) → build the full grid first: Students × Subjects = CROSS JOIN.",
    "Attach real exam rows with LEFT JOIN on both keys.",
    "Count a column from the exam table so missing rows count as 0.",
  ],
  steps=[
    dict(t="CROSS JOIN: the full student × subject grid", sql="""
SELECT s.student_id, s.student_name, sub.subject_name
FROM Students s CROSS JOIN Subjects sub
ORDER BY s.student_id, sub.subject_name""",
      note="3 students × 3 subjects = 9 rows. This is the shape of the final answer."),
    dict(t="LEFT JOIN exam rows onto the grid", sql="""
SELECT CONCAT(s.student_id, sub.subject_name) AS _grp,
       s.student_id, s.student_name, sub.subject_name, e.subject_name AS `e.subject_name`
FROM Students s CROSS JOIN Subjects sub
LEFT JOIN Examinations e ON e.student_id = s.student_id AND e.subject_name = sub.subject_name
ORDER BY s.student_id, sub.subject_name""",
      note="Anil's Math repeats 3 times (duplicates multiply rows). Bela–Physics has no exam → one row with NULL."),
    dict(t="COUNT(e.subject_name) per cell", sql="""
SELECT s.student_id, sub.subject_name,
       COUNT(*) AS `+COUNT(*) (wrong)`,
       COUNT(e.subject_name) AS `+COUNT(e.col) (right)`
FROM Students s CROSS JOIN Subjects sub
LEFT JOIN Examinations e ON e.student_id = s.student_id AND e.subject_name = sub.subject_name
GROUP BY s.student_id, sub.subject_name
ORDER BY s.student_id, sub.subject_name""",
      note="COUNT(*) counts the NULL placeholder row as 1. COUNT(column) skips NULLs → 0 for Bela–Physics."),
  ],
  remember=[
    "\"For every A and every B\" → `A CROSS JOIN B` builds the grid.",
    "`COUNT(*)` counts rows; `COUNT(col)` counts non-NULL values. After a LEFT JOIN, count a right-side column.",
    "With `ONLY_FULL_GROUP_BY`, list every non-aggregated SELECT column in GROUP BY.",
  ],
  pitfalls=["Starting from Examinations misses students who sat no exam (Bela–Physics, …)."],
  recall="Students CROSS JOIN Subjects LEFT JOIN Exams; COUNT(e.subject_name).",
  ordered=True,
),
dict(
  n=13, id=570, slug="managers-with-at-least-5-direct-reports", title="Managers with at Least 5 Direct Reports",
  sec="joins", diff="Medium", concepts=["Self join", "GROUP BY", "HAVING"],
  pattern="Self join manager ↔ reports, then filter groups",
  prompt="In `Employee`, `managerId` points to another row's `id`. Return the names of managers who have **at least five** direct reports.",
  returns="name (any order)",
  setup="""
CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(255), department VARCHAR(255), managerId INT);
INSERT INTO Employee VALUES
(101,'Sanjay','A',NULL),(102,'Dev','A',101),(103,'Isha','A',101),(104,'Amit','A',101),
(105,'Anya','A',101),(106,'Ron','B',101),(107,'Tara','B',106),(108,'Neel','B',106),
(109,'Pia','B',106),(110,'Zoya','B',106);
""",
  solution="""
SELECT m.name
FROM Employee m
JOIN Employee e
  ON e.managerId = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) >= 5;
""",
  alts=[("Subquery on managerId", """
SELECT name
FROM Employee
WHERE id IN (
  SELECT managerId
  FROM Employee
  GROUP BY managerId
  HAVING COUNT(*) >= 5
);
""", "Count reports per managerId first, then look up the names.")],
  approach=[
    "Reports and managers live in the same table → self join `e.managerId = m.id`.",
    "One row per (manager, report) pair → GROUP BY manager and count.",
    "Filter groups with `HAVING COUNT(*) >= 5`.",
  ],
  steps=[
    dict(t="Self join: manager next to each report", sql="""
SELECT m.id AS _grp, m.id AS manager_id, m.name AS manager, e.id AS report_id, e.name AS report
FROM Employee m JOIN Employee e ON e.managerId = m.id
ORDER BY m.id, e.id""",
      note="Sanjay has 5 report rows, Ron has 4."),
    dict(t="GROUP BY manager, HAVING COUNT(*) >= 5", sql="""
SELECT m.id, m.name, COUNT(*) AS `+reports`, COUNT(*) >= 5 AS _keep
FROM Employee m JOIN Employee e ON e.managerId = m.id
GROUP BY m.id, m.name ORDER BY m.id""",
      note="`HAVING` filters after grouping — `WHERE` can't see COUNT(*)."),
  ],
  remember=[
    "`WHERE` filters rows before grouping; `HAVING` filters groups after.",
    "Group by the manager's **id**, not just name — two managers can share a name.",
  ],
  pitfalls=["`GROUP BY m.name` alone would merge two different managers who happen to share a name."],
  recall="Self join e.managerId = m.id, GROUP BY m.id HAVING COUNT(*) >= 5.",
),
dict(
  n=14, id=1934, slug="confirmation-rate", title="Confirmation Rate",
  sec="joins", diff="Medium", concepts=["LEFT JOIN", "AVG(condition)", "IF", "ROUND"],
  pattern="Rate = AVG of a 0/1 flag; LEFT JOIN so zero-activity users stay",
  prompt="Users sign up (`Signups`) and later request confirmation messages (`Confirmations`, action is `confirmed` or `timeout`). A user's confirmation rate = confirmed messages ÷ all requested messages, or 0 if they requested none. Round to 2 decimals.",
  returns="user_id, confirmation_rate (any order)",
  setup="""
CREATE TABLE Signups (user_id INT PRIMARY KEY, time_stamp DATETIME);
CREATE TABLE Confirmations (user_id INT, time_stamp DATETIME, action ENUM('confirmed','timeout'), PRIMARY KEY (user_id, time_stamp));
INSERT INTO Signups VALUES (3,'2024-03-21 10:16:13'),(7,'2024-01-04 13:57:59'),(2,'2024-07-29 23:09:44'),(6,'2024-12-09 10:39:37');
INSERT INTO Confirmations VALUES
(3,'2024-01-06 03:30:46','timeout'),(3,'2024-07-14 14:00:00','timeout'),
(7,'2024-06-12 11:57:29','confirmed'),(7,'2024-06-13 12:58:28','confirmed'),(7,'2024-06-14 13:59:27','confirmed'),
(2,'2024-01-22 00:00:00','confirmed'),(2,'2024-02-28 23:59:59','timeout');
""",
  solution="""
SELECT s.user_id,
       ROUND(AVG(IF(c.action = 'confirmed', 1, 0)), 2) AS confirmation_rate
FROM Signups s
LEFT JOIN Confirmations c
       ON s.user_id = c.user_id
GROUP BY s.user_id;
""",
  alts=[("SUM / COUNT with IFNULL", """
SELECT s.user_id,
       ROUND(IFNULL(SUM(c.action = 'confirmed') / COUNT(c.action), 0), 2) AS confirmation_rate
FROM Signups s
LEFT JOIN Confirmations c ON s.user_id = c.user_id
GROUP BY s.user_id;
""", "For user 6, SUM/COUNT is NULL/0 = NULL → IFNULL turns it into 0.")],
  approach=[
    "Every signed-up user must appear (even with no requests) → `Signups LEFT JOIN Confirmations`.",
    "Turn each row into a 1 (confirmed) or 0 (anything else, including NULL).",
    "The average of a 0/1 column is exactly the rate. Round to 2.",
  ],
  steps=[
    dict(t="LEFT JOIN and flag confirmed rows", sql="""
SELECT s.user_id AS _grp, s.user_id, c.time_stamp, c.action,
       IF(c.action = 'confirmed', 1, 0) AS `+is_confirmed`
FROM Signups s LEFT JOIN Confirmations c ON s.user_id = c.user_id
ORDER BY s.user_id, c.time_stamp""",
      note="User 6 never requested a message: one row with NULL action → flag 0. AVG over that single 0 = 0.00 ✓."),
  ],
  remember=[
    "**AVG(condition)** = fraction of rows where the condition is true. Multiply by 100 for a percentage.",
    "`IF(cond, 1, 0)` maps NULL to 0 (because `NULL = 'confirmed'` is not TRUE).",
    "`SUM(cond)` counts TRUE rows (MySQL treats TRUE as 1).",
  ],
  pitfalls=["Using `AVG(c.action = 'confirmed')` directly gives NULL for users with no requests — AVG ignores NULL."],
  recall="Signups LEFT JOIN Confirmations; ROUND(AVG(IF(action='confirmed',1,0)),2).",
),
]
