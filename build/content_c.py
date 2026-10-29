# SQL 50 content — Advanced Select and Joins + Subqueries (problems 30–43)

PROBLEMS_C = [
# ───────────────────────────── ADVANCED SELECT AND JOINS ─────────────────────────────
dict(
  n=30, id=1731, slug="the-number-of-employees-which-report-to-each-employee", title="The Number of Employees Which Report to Each Employee",
  sec="advjoin", diff="Easy", concepts=["Self join", "COUNT", "ROUND(AVG)"],
  pattern="Self join manager ↔ reports, aggregate per manager",
  prompt="A manager is anyone with at least one direct report (`reports_to` points to them). For each manager, return id, name, number of direct reports, and the reports' average age rounded to the nearest integer. Sort by employee_id.",
  returns="employee_id, name, reports_count, average_age (ordered)",
  setup="""
CREATE TABLE Employees (employee_id INT PRIMARY KEY, name VARCHAR(20), reports_to INT, age INT);
INSERT INTO Employees VALUES
(1,'Manish',NULL,45),(2,'Nidhi',1,38),(3,'Omkar',1,35),(4,'Pooja',NULL,40),
(5,'Qadir',4,29),(6,'Rhea',4,30),(7,'Sahil',4,30),(8,'Tina',2,25);
""",
  solution="""
SELECT m.employee_id, m.name,
       COUNT(e.employee_id) AS reports_count,
       ROUND(AVG(e.age))    AS average_age
FROM Employees m
JOIN Employees e
  ON e.reports_to = m.employee_id
GROUP BY m.employee_id, m.name
ORDER BY m.employee_id;
""",
  alts=[],
  approach=[
    "Managers and reports are rows of the same table → self join `e.reports_to = m.employee_id`.",
    "INNER JOIN automatically drops people with no reports (they aren't managers).",
    "Per manager: COUNT reports, ROUND(AVG(age)) with no decimals.",
  ],
  steps=[
    dict(t="Each manager with their direct reports", sql="""
SELECT m.employee_id AS _grp, m.employee_id, m.name AS manager, e.name AS report, e.age
FROM Employees m JOIN Employees e ON e.reports_to = m.employee_id
ORDER BY m.employee_id, e.employee_id""",
      note="Manish: (38 + 35) / 2 = 36.5 → rounds to 37. Nidhi manages Tina, so she is a manager too."),
  ],
  remember=[
    "`ROUND(x)` with no second argument → nearest integer.",
    "MySQL rounds exact decimals half away from zero (36.5 → 37). AVG of INTs is an exact DECIMAL, so this is reliable.",
  ],
  pitfalls=["Using `CEIL`/`FLOOR` instead of ROUND."],
  recall="Self join e.reports_to = m.id; COUNT, ROUND(AVG(e.age)); ORDER BY id.",
  ordered=True,
),
dict(
  n=31, id=1789, slug="primary-department-for-each-employee", title="Primary Department for Each Employee",
  sec="advjoin", diff="Easy", concepts=["OR + subquery", "UNION", "COUNT() OVER"],
  pattern="Two rules for choosing a row → OR (or UNION)",
  prompt="Employees with several departments mark one as primary (`primary_flag = 'Y'`). Employees with only one department have flag `'N'` on it. Report each employee's primary department.",
  returns="employee_id, department_id (any order)",
  setup="""
CREATE TABLE Employee (employee_id INT, department_id INT, primary_flag ENUM('Y','N'), PRIMARY KEY (employee_id, department_id));
INSERT INTO Employee VALUES (1,10,'N'),(2,10,'Y'),(2,20,'N'),(3,30,'N'),(4,20,'N'),(4,30,'N'),(4,40,'Y'),(5,50,'N');
""",
  solution="""
SELECT employee_id, department_id
FROM Employee
WHERE primary_flag = 'Y'
   OR employee_id IN (
        SELECT employee_id
        FROM Employee
        GROUP BY employee_id
        HAVING COUNT(*) = 1
      );
""",
  alts=[
    ("UNION", """
SELECT employee_id, department_id FROM Employee WHERE primary_flag = 'Y'
UNION
SELECT employee_id, MIN(department_id) FROM Employee GROUP BY employee_id HAVING COUNT(*) = 1;
""", "One branch per rule. MIN() just satisfies ONLY_FULL_GROUP_BY — the group has one row."),
    ("Window count", """
SELECT employee_id, department_id
FROM (
  SELECT *, COUNT(*) OVER (PARTITION BY employee_id) AS cnt
  FROM Employee
) t
WHERE primary_flag = 'Y' OR cnt = 1;
""", "Attach the per-employee count to every row without collapsing them."),
  ],
  approach=[
    "Rule A: the row flagged 'Y'.",
    "Rule B: the employee has exactly one department (that row, whatever its flag).",
    "Either rule → `OR`, with rule B as an IN-subquery on employees having COUNT(*) = 1.",
  ],
  steps=[
    dict(t="Department count per employee + the two rules", sql="""
SELECT employee_id AS _grp, employee_id, department_id, primary_flag,
       COUNT(*) OVER (PARTITION BY employee_id) AS `+dept_count`,
       (primary_flag = 'Y' OR COUNT(*) OVER (PARTITION BY employee_id) = 1) AS _keep
FROM Employee ORDER BY employee_id, department_id""",
      note="Employees 1, 3, 5 have a single department (flag 'N') → kept by rule B."),
  ],
  remember=["`COUNT(*) OVER (PARTITION BY x)` = group size on every row, without GROUP BY collapsing rows."],
  pitfalls=["Selecting only `primary_flag = 'Y'` misses single-department employees."],
  recall="flag='Y' OR employee_id IN (GROUP BY id HAVING COUNT(*)=1).",
),
dict(
  n=32, id=610, slug="triangle-judgement", title="Triangle Judgement",
  sec="advjoin", diff="Easy", concepts=["CASE WHEN", "IF"],
  pattern="Derived label column with CASE",
  prompt="For each row of three segment lengths x, y, z, report whether they can form a triangle ('Yes' / 'No').",
  returns="x, y, z, triangle (any order)",
  setup="""
CREATE TABLE Triangle (x INT, y INT, z INT, PRIMARY KEY (x, y, z));
INSERT INTO Triangle VALUES (13,15,30),(10,20,15),(3,4,5),(1,2,3);
""",
  solution="""
SELECT x, y, z,
       CASE WHEN x + y > z AND x + z > y AND y + z > x
            THEN 'Yes' ELSE 'No'
       END AS triangle
FROM Triangle;
""",
  alts=[("IF()", """
SELECT x, y, z,
       IF(x + y > z AND x + z > y AND y + z > x, 'Yes', 'No') AS triangle
FROM Triangle;
""", "MySQL's `IF(cond, a, b)` is a compact two-branch CASE.")],
  approach=["Triangle inequality: every pair of sides must sum to **more than** the third.", "Return a label → CASE WHEN … THEN 'Yes' ELSE 'No'."],
  steps=[
    dict(t="Check all three inequalities", sql="""
SELECT x, y, z, x + y > z AS `+x+y>z`, x + z > y AS `+x+z>y`, y + z > x AS `+y+z>x`,
       IF(x + y > z AND x + z > y AND y + z > x, 'Yes', 'No') AS `+triangle`
FROM Triangle ORDER BY x""",
      note="1, 2, 3 is degenerate: 1 + 2 = 3, not greater → No."),
  ],
  remember=["Strict `>` — equal sums make a flat line, not a triangle.", "CASE is evaluated top-down; first TRUE branch wins."],
  pitfalls=["Using `>=`."],
  recall="CASE WHEN x+y>z AND x+z>y AND y+z>x THEN 'Yes' ELSE 'No'.",
),
dict(
  n=33, id=180, slug="consecutive-numbers", title="Consecutive Numbers",
  sec="advjoin", diff="Medium", concepts=["LAG", "LEAD", "Self join", "DISTINCT"],
  pattern="Compare a row with its neighbours → LAG/LEAD",
  prompt="Find all numbers that appear at least **three times in a row** (by id order) in `Logs`.",
  returns="ConsecutiveNums (any order)",
  setup="""
CREATE TABLE Logs (id INT PRIMARY KEY, num VARCHAR(10));
INSERT INTO Logs VALUES
(1,'7'),(2,'7'),(3,'3'),(4,'3'),(5,'3'),(6,'7'),(7,'3'),(8,'3'),(9,'3'),(10,'3'),(11,'7'),(12,'7'),(13,'7');
""",
  solution="""
SELECT DISTINCT num AS ConsecutiveNums
FROM (
  SELECT num,
         LAG(num)  OVER (ORDER BY id) AS prev_num,
         LEAD(num) OVER (ORDER BY id) AS next_num
  FROM Logs
) t
WHERE num = prev_num
  AND num = next_num;
""",
  alts=[("Triple self join", """
SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num
  AND l2.num = l3.num;
""", "Classic answer; relies on ids being gap-free. The LAG/LEAD version only needs them to be ordered.")],
  approach=[
    "\"Three in a row\" = a row equal to both its previous and next row.",
    "LAG/LEAD fetch neighbour values in id order.",
    "A long streak produces several matches → DISTINCT.",
  ],
  steps=[
    dict(t="Fetch each row's neighbours", sql="""
SELECT id, num, LAG(num) OVER (ORDER BY id) AS `+prev_num`, LEAD(num) OVER (ORDER BY id) AS `+next_num`,
       IFNULL(num = LAG(num) OVER (ORDER BY id) AND num = LEAD(num) OVER (ORDER BY id), 0) AS _keep
FROM Logs ORDER BY id""",
      note="The streak of four 3s (ids 7–10) matches twice (ids 8 and 9) → DISTINCT collapses them. The 7s at ids 1–2 are only a pair."),
  ],
  remember=[
    "`LAG(col, n, default)` / `LEAD(col, n, default)` look n rows back / ahead within the window order.",
    "For \"at least K in a row\" with big K, use the gaps-and-islands trick: `id - ROW_NUMBER() OVER (PARTITION BY num ORDER BY id)` is constant within a streak.",
  ],
  pitfalls=["Forgetting DISTINCT — streaks longer than 3 return duplicates.", "Self join on `id + 1` breaks if ids have gaps."],
  recall="num = LAG(num) AND num = LEAD(num) over id order; DISTINCT.",
),
dict(
  n=34, id=1164, slug="product-price-at-a-given-date", title="Product Price at a Given Date",
  sec="advjoin", diff="Medium", concepts=["MAX per group", "LEFT JOIN", "IFNULL", "UNION"],
  pattern="Latest change on/before a date, with a default",
  prompt="`Products` logs price changes (product_id, new_price, change_date). Every product starts at price 10. Find every product's price on **2019-08-16**.",
  returns="product_id, price (any order)",
  setup="""
CREATE TABLE Products (product_id INT, new_price INT, change_date DATE, PRIMARY KEY (product_id, change_date));
INSERT INTO Products VALUES
(1,25,'2019-08-10'),(1,40,'2019-08-16'),(1,45,'2019-08-20'),
(2,60,'2019-08-12'),(2,70,'2019-08-14'),(3,15,'2019-08-17'),(4,12,'2019-08-01');
""",
  solution="""
SELECT p.product_id,
       IFNULL(lp.new_price, 10) AS price
FROM (SELECT DISTINCT product_id FROM Products) p
LEFT JOIN (
  SELECT product_id, new_price
  FROM Products
  WHERE (product_id, change_date) IN (
    SELECT product_id, MAX(change_date)
    FROM Products
    WHERE change_date <= '2019-08-16'
    GROUP BY product_id
  )
) lp ON p.product_id = lp.product_id;
""",
  alts=[
    ("UNION of two cases", """
SELECT product_id, 10 AS price
FROM Products
GROUP BY product_id
HAVING MIN(change_date) > '2019-08-16'
UNION ALL
SELECT product_id, new_price
FROM Products
WHERE (product_id, change_date) IN (
  SELECT product_id, MAX(change_date)
  FROM Products WHERE change_date <= '2019-08-16'
  GROUP BY product_id
);
""", "Case 1: first change is after the date → still 10. Case 2: price of the latest change on/before the date."),
    ("ROW_NUMBER", """
SELECT p.product_id, IFNULL(t.new_price, 10) AS price
FROM (SELECT DISTINCT product_id FROM Products) p
LEFT JOIN (
  SELECT product_id, new_price,
         ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY change_date DESC) AS rn
  FROM Products
  WHERE change_date <= '2019-08-16'
) t ON t.product_id = p.product_id AND t.rn = 1;
""", "Latest qualifying change = rank 1 when ordered by date descending."),
  ],
  approach=[
    "The price on a date = the price from the **latest change on or before** that date.",
    "Products whose first change is after the date never changed yet → default 10.",
    "So: list all products, LEFT JOIN their latest qualifying price, IFNULL to 10.",
  ],
  steps=[
    dict(t="Changes on or before 2019-08-16", sql="""
SELECT product_id AS _grp, product_id, new_price, change_date,
       change_date <= '2019-08-16' AS _keep
FROM Products ORDER BY product_id, change_date""",
      note="The change dated exactly 2019-08-16 counts (≤). Product 3's only change is later."),
    dict(t="Latest qualifying change per product", sql="""
SELECT product_id, MAX(change_date) AS last_change
FROM Products WHERE change_date <= '2019-08-16'
GROUP BY product_id ORDER BY product_id""",
      note="Product 3 is missing here — that's why the final step needs a LEFT JOIN from all products."),
    dict(t="LEFT JOIN from all products, default 10", sql="""
SELECT p.product_id, lp.new_price AS `lp.new_price`, IFNULL(lp.new_price, 10) AS `+price`
FROM (SELECT DISTINCT product_id FROM Products) p
LEFT JOIN (SELECT product_id, new_price FROM Products
           WHERE (product_id, change_date) IN (SELECT product_id, MAX(change_date) FROM Products
                                               WHERE change_date <= '2019-08-16' GROUP BY product_id)) lp
  ON p.product_id = lp.product_id
ORDER BY p.product_id""",
      note="NULL → 10 for product 3."),
  ],
  remember=[
    "\"Value as of date D\" = latest record with date ≤ D.",
    "A default for missing matches = LEFT JOIN + IFNULL/COALESCE.",
  ],
  pitfalls=["Using `<` instead of `<=` (changes on the day itself apply).", "Inner join loses products with no change before the date."],
  recall="All products LEFT JOIN (latest change ≤ date via MAX); IFNULL(price, 10).",
),
dict(
  n=35, id=1204, slug="last-person-to-fit-in-the-bus", title="Last Person to Fit in the Bus",
  sec="advjoin", diff="Medium", concepts=["Running total", "SUM() OVER", "Self join"],
  pattern="Running total, then the last row under a limit",
  prompt="People board a bus in `turn` order. The bus holds at most 1000 kg. Return the name of the last person who can board without exceeding the limit (the first person always fits).",
  returns="person_name (single value)",
  setup="""
CREATE TABLE Queue (person_id INT PRIMARY KEY, person_name VARCHAR(30), weight INT, turn INT);
INSERT INTO Queue VALUES (1,'Arjun',300,3),(2,'Bhim',400,1),(3,'Karna',150,4),(4,'Nakul',200,2),(5,'Sahdev',120,5),(6,'Yudhi',90,6);
""",
  solution="""
SELECT person_name
FROM (
  SELECT person_name, turn,
         SUM(weight) OVER (ORDER BY turn) AS total_weight
  FROM Queue
) t
WHERE total_weight <= 1000
ORDER BY turn DESC
LIMIT 1;
""",
  alts=[("Self join running total", """
SELECT q1.person_name
FROM Queue q1
JOIN Queue q2 ON q2.turn <= q1.turn
GROUP BY q1.turn, q1.person_name
HAVING SUM(q2.weight) <= 1000
ORDER BY q1.turn DESC
LIMIT 1;
""", "Pre-window-function way: sum everyone at or before my turn.")],
  approach=[
    "Weight on the bus after person k boards = sum of weights of turns 1..k → running total.",
    "Keep rows where the running total ≤ 1000; the answer is the one with the highest turn.",
  ],
  steps=[
    dict(t="Running total in boarding order", sql="""
SELECT turn, person_name, weight,
       SUM(weight) OVER (ORDER BY turn) AS `+running_total`,
       SUM(weight) OVER (ORDER BY turn) <= 1000 AS _keep
FROM Queue ORDER BY turn""",
      note="Karna pushes the total to 1050, so Arjun (900) is the last to board. Yudhi is light, but boarding stops in order."),
  ],
  remember=[
    "`SUM(x) OVER (ORDER BY k)` = running total.",
    "Default frame with ORDER BY is `RANGE UNBOUNDED PRECEDING` — rows with equal `k` are summed together. Use `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` if `k` can tie.",
  ],
  pitfalls=["Ordering by person_id instead of turn."],
  recall="SUM(weight) OVER (ORDER BY turn) ≤ 1000, ORDER BY turn DESC LIMIT 1.",
),
dict(
  n=36, id=1907, slug="count-salary-categories", title="Count Salary Categories",
  sec="advjoin", diff="Medium", concepts=["UNION ALL", "SUM(condition)", "CASE"],
  pattern="Fixed list of categories that must all appear (even with 0)",
  prompt="Count accounts per salary category: 'Low Salary' (< 20000), 'Average Salary' (20000–50000 inclusive), 'High Salary' (> 50000). All three categories must be returned, with 0 if empty.",
  returns="category, accounts_count (any order)",
  setup="""
CREATE TABLE Accounts (account_id INT PRIMARY KEY, income INT);
INSERT INTO Accounts VALUES (1,20000),(2,50000),(3,50001),(4,72000),(5,120000);
""",
  solution="""
SELECT 'Low Salary' AS category,
       SUM(income < 20000) AS accounts_count
FROM Accounts
UNION ALL
SELECT 'Average Salary',
       SUM(income BETWEEN 20000 AND 50000)
FROM Accounts
UNION ALL
SELECT 'High Salary',
       SUM(income > 50000)
FROM Accounts;
""",
  alts=[("Category table LEFT JOIN", """
SELECT c.category, COUNT(a.account_id) AS accounts_count
FROM (
  SELECT 'Low Salary' AS category
  UNION ALL SELECT 'Average Salary'
  UNION ALL SELECT 'High Salary'
) c
LEFT JOIN Accounts a
  ON c.category = CASE WHEN a.income < 20000 THEN 'Low Salary'
                       WHEN a.income <= 50000 THEN 'Average Salary'
                       ELSE 'High Salary' END
GROUP BY c.category;
""", "Build the list of categories first, then LEFT JOIN and count — empty categories get 0.")],
  approach=[
    "A plain `GROUP BY category` can't produce a category with zero rows.",
    "So write one SELECT per category, each returning exactly one row with SUM(condition), and stack them with UNION ALL.",
  ],
  steps=[
    dict(t="Label every account", sql="""
SELECT account_id, income,
       CASE WHEN income < 20000 THEN 'Low Salary'
            WHEN income <= 50000 THEN 'Average Salary'
            ELSE 'High Salary' END AS `+category`
FROM Accounts ORDER BY income""",
      note="20000 and 50000 are both 'Average' (inclusive boundaries)."),
    dict(t="Trap: GROUP BY drops empty categories", sql="""
SELECT CASE WHEN income < 20000 THEN 'Low Salary'
            WHEN income <= 50000 THEN 'Average Salary'
            ELSE 'High Salary' END AS category,
       COUNT(*) AS accounts_count
FROM Accounts GROUP BY category ORDER BY category""",
      note="No 'Low Salary' row at all — GROUP BY only creates groups that have data. Hence UNION ALL."),
  ],
  remember=[
    "To force rows for categories with no data: one SELECT per category + UNION ALL, or a category list LEFT JOIN data.",
    "Aggregate without GROUP BY → exactly one row, even if 0 rows match.",
    "On a completely empty table `SUM()` gives NULL — wrap with IFNULL(…, 0) if that can happen.",
  ],
  pitfalls=["GROUP BY CASE … returns only categories that have accounts."],
  recall="Three SELECTs with SUM(condition) stacked by UNION ALL.",
),

# ───────────────────────────── SUBQUERIES ─────────────────────────────
dict(
  n=37, id=1978, slug="employees-whose-manager-left-the-company", title="Employees Whose Manager Left the Company",
  sec="subq", diff="Easy", concepts=["NOT IN", "Subquery", "NULL"],
  pattern="Reference to a row that no longer exists → NOT IN",
  prompt="Find employees earning **less than 30000** whose manager has left the company (their `manager_id` is set, but no employee has that id anymore). Sort by employee_id.",
  returns="employee_id (ordered)",
  setup="""
CREATE TABLE Employees (employee_id INT PRIMARY KEY, name VARCHAR(20), manager_id INT, salary INT);
INSERT INTO Employees VALUES
(1,'Ishaan',NULL,90000),(2,'Jaya',1,25000),(3,'Kunal',7,28000),(4,'Lata',8,45000),
(5,'Mohan',NULL,15000),(6,'Naina',9,29999),(10,'Ojas',2,31000);
""",
  solution="""
SELECT employee_id
FROM Employees
WHERE salary < 30000
  AND manager_id NOT IN (SELECT employee_id FROM Employees)
ORDER BY employee_id;
""",
  alts=[("Self LEFT JOIN anti-join", """
SELECT e.employee_id
FROM Employees e
LEFT JOIN Employees m ON e.manager_id = m.employee_id
WHERE e.salary < 30000
  AND e.manager_id IS NOT NULL
  AND m.employee_id IS NULL
ORDER BY e.employee_id;
""", "Must explicitly exclude NULL manager_id here — the LEFT JOIN would treat them as 'missing manager'.")],
  approach=[
    "\"Manager left\" = manager_id points to an id not present in the table → `NOT IN (SELECT employee_id …)`.",
    "Employees with NULL manager_id never had a manager — `NULL NOT IN (…)` is UNKNOWN, so they drop out automatically.",
  ],
  steps=[
    dict(t="Evaluate both conditions", sql="""
SELECT employee_id, name, manager_id, salary,
       salary < 30000 AS `+salary < 30000`,
       manager_id NOT IN (SELECT employee_id FROM Employees) AS `+manager_left`,
       (salary < 30000 AND manager_id NOT IN (SELECT employee_id FROM Employees)) IS TRUE AS _keep
FROM Employees ORDER BY employee_id""",
      note="Managers 7, 8, 9 don't exist. Mohan's NULL manager gives NULL, not TRUE → excluded."),
  ],
  remember=[
    "`x NOT IN (subquery)`: if the subquery returns **any NULL**, the result is never TRUE → zero rows. Safe here because employee_id is a primary key.",
    "Prefer `NOT EXISTS` when the subquery column is nullable.",
  ],
  pitfalls=["Forgetting ORDER BY employee_id."],
  recall="salary < 30000 AND manager_id NOT IN (SELECT employee_id …) ORDER BY id.",
  ordered=True,
),
dict(
  n=38, id=626, slug="exchange-seats", title="Exchange Seats",
  sec="subq", diff="Medium", concepts=["CASE", "Scalar subquery", "LEAD/LAG"],
  pattern="Swap adjacent rows by rewriting ids",
  prompt="Swap the seats of every two consecutive students (1↔2, 3↔4, …). If the count is odd, the last student stays. Return the result ordered by id.",
  returns="id, student (ordered by id)",
  setup="""
CREATE TABLE Seat (id INT PRIMARY KEY, student VARCHAR(255));
INSERT INTO Seat VALUES (1,'Aditi'),(2,'Bhanu'),(3,'Chhavi'),(4,'Dhruv'),(5,'Eklavya');
""",
  solution="""
SELECT CASE
         WHEN id % 2 = 1 AND id = (SELECT MAX(id) FROM Seat) THEN id
         WHEN id % 2 = 1 THEN id + 1
         ELSE id - 1
       END AS id,
       student
FROM Seat
ORDER BY id;
""",
  alts=[
    ("LEAD / LAG", """
SELECT id,
       CASE WHEN id % 2 = 1 THEN COALESCE(LEAD(student) OVER (ORDER BY id), student)
            ELSE LAG(student) OVER (ORDER BY id)
       END AS student
FROM Seat
ORDER BY id;
""", "Keep ids, move names instead: odd seats take the next name (or keep their own if last)."),
    ("XOR trick", """
SELECT s1.id, COALESCE(s2.student, s1.student) AS student
FROM Seat s1
LEFT JOIN Seat s2 ON ((s1.id + 1) ^ 1) - 1 = s2.id
ORDER BY s1.id;
""", "`((id+1) ^ 1) - 1` maps 1↔2, 3↔4… Neat but needs explaining in an interview."),
  ],
  approach=[
    "Instead of moving names, rewrite the ids: odd → id+1, even → id−1.",
    "Exception: the last odd id (no partner) keeps its id → compare with `(SELECT MAX(id) FROM Seat)`.",
    "Sort by the new id.",
  ],
  steps=[
    dict(t="Compute each student's new id", sql="""
SELECT id, student, id % 2 = 1 AS `+is_odd`, (SELECT MAX(id) FROM Seat) AS max_id,
       CASE WHEN id % 2 = 1 AND id = (SELECT MAX(id) FROM Seat) THEN id
            WHEN id % 2 = 1 THEN id + 1 ELSE id - 1 END AS `+new_id`
FROM Seat ORDER BY id""",
      note="Eklavya (5) is odd and last → stays at 5. ORDER BY then uses the new id alias."),
  ],
  remember=[
    "`ORDER BY id` here sorts by the **output alias** `id` (the new id) — MySQL resolves ORDER BY names against SELECT aliases first.",
    "CASE branches are checked in order — put the special case first.",
  ],
  pitfalls=["Checking `id = MAX(id)` without a subquery is an aggregate error."],
  recall="CASE: odd & last → id; odd → id+1; even → id−1; ORDER BY id.",
  ordered=True,
),
dict(
  n=39, id=1341, slug="movie-rating", title="Movie Rating",
  sec="subq", diff="Medium", concepts=["UNION ALL", "ORDER BY + LIMIT", "Date range"],
  pattern="Two independent top-1 queries stacked",
  prompt="Return two values in one column `results`: (1) the name of the user who rated the most movies (ties → alphabetically smaller name); (2) the title of the movie with the highest average rating in **February 2020** (ties → alphabetically smaller title).",
  returns="results (two rows)",
  setup="""
CREATE TABLE Movies (movie_id INT PRIMARY KEY, title VARCHAR(30));
CREATE TABLE Users (user_id INT PRIMARY KEY, name VARCHAR(30));
CREATE TABLE MovieRating (movie_id INT, user_id INT, rating INT, created_at DATE, PRIMARY KEY (movie_id, user_id));
INSERT INTO Movies VALUES (1,'Sholay'),(2,'Rang De Basanti'),(3,'Gully Boy'),(4,'Rohan');
INSERT INTO Users VALUES (1,'Rohan'),(2,'Meghna'),(3,'Aditya'),(4,'Farah');
INSERT INTO MovieRating VALUES
(1,1,5,'2020-02-11'),(1,2,4,'2020-02-12'),(1,3,3,'2020-01-20'),(2,1,4,'2020-02-17'),
(2,2,5,'2020-03-01'),(3,1,3,'2020-02-22'),(4,3,5,'2020-02-05'),(4,4,4,'2020-02-29');
""",
  solution="""
(SELECT u.name AS results
 FROM MovieRating r
 JOIN Users u ON u.user_id = r.user_id
 GROUP BY u.user_id, u.name
 ORDER BY COUNT(*) DESC, u.name
 LIMIT 1)
UNION ALL
(SELECT m.title
 FROM MovieRating r
 JOIN Movies m ON m.movie_id = r.movie_id
 WHERE r.created_at >= '2020-02-01' AND r.created_at < '2020-03-01'
 GROUP BY m.movie_id, m.title
 ORDER BY AVG(r.rating) DESC, m.title
 LIMIT 1);
""",
  alts=[],
  approach=[
    "Two unrelated questions → two queries, each `ORDER BY metric DESC, name ASC LIMIT 1`.",
    "Stack them into one column with UNION **ALL** — the user name and movie title can be identical.",
    "Wrap each part in parentheses so its ORDER BY/LIMIT applies to that part only.",
  ],
  steps=[
    dict(t="Ratings per user", sql="""
SELECT u.name, COUNT(*) AS `+ratings`
FROM MovieRating r JOIN Users u ON u.user_id = r.user_id
GROUP BY u.user_id, u.name ORDER BY COUNT(*) DESC, u.name""",
      note="Rohan rated 3 movies → result 1 = Rohan."),
    dict(t="Average rating per movie in Feb 2020", sql="""
SELECT m.title, AVG(r.rating) AS `+feb_avg`, COUNT(*) AS feb_ratings
FROM MovieRating r JOIN Movies m ON m.movie_id = r.movie_id
WHERE r.created_at >= '2020-02-01' AND r.created_at < '2020-03-01'
GROUP BY m.movie_id, m.title ORDER BY AVG(r.rating) DESC, m.title""",
      note="Sholay and Rohan tie at 4.5 → alphabetical tie-break picks 'Rohan'. The 1 Mar and 20 Jan ratings are excluded; 29 Feb counts."),
    dict(t="Trap: UNION removes the duplicate", sql="""
(SELECT u.name AS results FROM MovieRating r JOIN Users u ON u.user_id = r.user_id
 GROUP BY u.user_id, u.name ORDER BY COUNT(*) DESC, u.name LIMIT 1)
UNION
(SELECT m.title FROM MovieRating r JOIN Movies m ON m.movie_id = r.movie_id
 WHERE r.created_at >= '2020-02-01' AND r.created_at < '2020-03-01'
 GROUP BY m.movie_id, m.title ORDER BY AVG(r.rating) DESC, m.title LIMIT 1)""",
      note="Both answers are 'Rohan', so plain UNION returns one row. Expected output has two — LeetCode includes a test like this."),
  ],
  remember=[
    "`UNION` de-duplicates; `UNION ALL` keeps everything (and is faster).",
    "ORDER BY / LIMIT inside a UNION part needs parentheses around that part.",
    "Month filter: `>= '2020-02-01' AND < '2020-03-01'` — handles leap years and is index-friendly.",
  ],
  pitfalls=["UNION instead of UNION ALL.", "`BETWEEN '2020-02-01' AND '2020-02-28'` misses 29 Feb 2020."],
  recall="(top user by COUNT, name LIMIT 1) UNION ALL (top Feb-2020 movie by AVG, title LIMIT 1).",
),
dict(
  n=40, id=1321, slug="restaurant-growth", title="Restaurant Growth",
  sec="subq", diff="Medium", concepts=["Window frame", "ROWS BETWEEN", "CTE", "Moving average"],
  pattern="Moving sum/average over the last 7 days",
  prompt="`Customer` records payments per visit (several customers can visit on the same day; every day has at least one visit). For each day from the 7th day onward, report the total paid over that day and the 6 days before it, and the 7-day average rounded to 2.",
  returns="visited_on, amount, average_amount (ordered by visited_on)",
  setup="""
CREATE TABLE Customer (customer_id INT, name VARCHAR(20), visited_on DATE, amount INT, PRIMARY KEY (customer_id, visited_on));
INSERT INTO Customer VALUES
(1,'Asha','2024-01-01',100),(2,'Bala','2024-01-02',110),(3,'Chand','2024-01-03',120),(4,'Dia','2024-01-04',130),
(1,'Asha','2024-01-05',110),(5,'Eshan','2024-01-06',140),(6,'Fiza','2024-01-07',150),(7,'Gagan','2024-01-08',80),
(8,'Hema','2024-01-09',110),(1,'Asha','2024-01-10',130),(3,'Chand','2024-01-10',150);
""",
  solution="""
WITH daily AS (
  SELECT visited_on, SUM(amount) AS amount
  FROM Customer
  GROUP BY visited_on
),
windowed AS (
  SELECT visited_on,
         SUM(amount) OVER w AS amount,
         ROUND(AVG(amount) OVER w, 2) AS average_amount,
         ROW_NUMBER() OVER (ORDER BY visited_on) AS day_no
  FROM daily
  WINDOW w AS (ORDER BY visited_on ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
)
SELECT visited_on, amount, average_amount
FROM windowed
WHERE day_no >= 7
ORDER BY visited_on;
""",
  alts=[
    ("Self join on dates", """
SELECT d1.visited_on,
       SUM(d2.amount) AS amount,
       ROUND(SUM(d2.amount) / 7, 2) AS average_amount
FROM (SELECT visited_on, SUM(amount) AS amount FROM Customer GROUP BY visited_on) d1
JOIN (SELECT visited_on, SUM(amount) AS amount FROM Customer GROUP BY visited_on) d2
  ON DATEDIFF(d1.visited_on, d2.visited_on) BETWEEN 0 AND 6
GROUP BY d1.visited_on
HAVING COUNT(*) = 7
ORDER BY d1.visited_on;
""", "Each day joins to itself and the 6 previous days; HAVING COUNT = 7 drops the first 6 days."),
    ("RANGE frame with INTERVAL", """
SELECT visited_on, amount, average_amount
FROM (
  SELECT visited_on,
         SUM(amount) OVER (ORDER BY visited_on RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW) AS amount,
         ROUND(SUM(amount) OVER (ORDER BY visited_on RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW) / 7, 2) AS average_amount,
         MIN(visited_on) OVER () AS first_day
  FROM (SELECT visited_on, SUM(amount) AS amount FROM Customer GROUP BY visited_on) d
) t
WHERE visited_on >= first_day + INTERVAL 6 DAY
ORDER BY visited_on;
""", "A date-based frame stays correct even if some calendar days are missing."),
  ],
  approach=[
    "Several customers per day → first collapse to **one row per day** (SUM per date).",
    "Then a window frame of the current row + 6 preceding rows gives the 7-day sum and average.",
    "Skip the first 6 days (incomplete windows) using ROW_NUMBER ≥ 7.",
  ],
  steps=[
    dict(t="Collapse to one row per day", sql="""
SELECT visited_on, COUNT(*) AS visits, SUM(amount) AS `+day_total`
FROM Customer GROUP BY visited_on ORDER BY visited_on""",
      note="10 Jan had two customers → 280. Windowing the raw table would count 10 Jan twice as two 'days'."),
    dict(t="7-row frame: sum and average", sql="""
SELECT visited_on, day_total,
       SUM(day_total) OVER w AS `+7day_sum`, ROUND(AVG(day_total) OVER w, 2) AS `+7day_avg`,
       ROW_NUMBER() OVER (ORDER BY visited_on) >= 7 AS _keep
FROM (SELECT visited_on, SUM(amount) AS day_total FROM Customer GROUP BY visited_on) d
WINDOW w AS (ORDER BY visited_on ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
ORDER BY visited_on""",
      note="First 6 days have partial windows → dropped. 7 Jan: 860 / 7 = 122.86."),
  ],
  remember=[
    "Window frame syntax: `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` (row-count based).",
    "`RANGE BETWEEN INTERVAL 6 DAY PRECEDING AND CURRENT ROW` is value-based — robust to missing dates.",
    "Named windows: `WINDOW w AS (…)` avoids repeating the frame.",
  ],
  pitfalls=["Windowing before aggregating per day.", "Forgetting to drop the first 6 days."],
  recall="Daily SUM → SUM/AVG OVER (ROWS 6 PRECEDING) → keep day_no ≥ 7.",
  ordered=True,
),
dict(
  n=41, id=602, slug="friend-requests-ii-who-has-the-most-friends", title="Friend Requests II: Who Has the Most Friends",
  sec="subq", diff="Medium", concepts=["UNION ALL", "GROUP BY", "ORDER BY LIMIT"],
  pattern="Symmetric relation → stack both columns, then count",
  prompt="Each row of `RequestAccepted` makes requester and accepter friends. Find the person with the most friends and their friend count (tests guarantee a single winner).",
  returns="id, num (single row)",
  setup="""
CREATE TABLE RequestAccepted (requester_id INT, accepter_id INT, accept_date DATE, PRIMARY KEY (requester_id, accepter_id));
INSERT INTO RequestAccepted VALUES (10,20,'2024-05-01'),(10,30,'2024-05-02'),(20,30,'2024-05-03'),(30,40,'2024-05-04'),(50,30,'2024-05-05');
""",
  solution="""
SELECT id, COUNT(*) AS num
FROM (
  SELECT requester_id AS id FROM RequestAccepted
  UNION ALL
  SELECT accepter_id FROM RequestAccepted
) people
GROUP BY id
ORDER BY num DESC
LIMIT 1;
""",
  alts=[("Ties-safe (follow-up)", """
WITH counts AS (
  SELECT id, COUNT(*) AS num
  FROM (SELECT requester_id AS id FROM RequestAccepted
        UNION ALL
        SELECT accepter_id FROM RequestAccepted) p
  GROUP BY id
)
SELECT id, num
FROM counts
WHERE num = (SELECT MAX(num) FROM counts);
""", "Returns every person tied for the maximum.")],
  approach=[
    "Friendship is two-way: a person can appear in either column.",
    "Stack both columns into one list of ids with UNION ALL — each appearance = one friend.",
    "Count per id, take the top one.",
  ],
  steps=[
    dict(t="Unpivot: one row per (person, friend)", sql="""
SELECT requester_id AS _grp, requester_id AS id, accepter_id AS friend, 'requester' AS `+role` FROM RequestAccepted
UNION ALL
SELECT accepter_id, accepter_id, requester_id, 'accepter' FROM RequestAccepted
ORDER BY id, friend""",
      note="Person 30 appears 4 times — as accepter 3 times and as requester once."),
    dict(t="Count friends per person", sql="""
SELECT id, COUNT(*) AS num, COUNT(*) = MAX(COUNT(*)) OVER () AS _keep
FROM (SELECT requester_id AS id FROM RequestAccepted UNION ALL SELECT accepter_id FROM RequestAccepted) p
GROUP BY id ORDER BY num DESC, id""",
      note="30 has 4 friends — the winner."),
  ],
  remember=[
    "Symmetric relationships (friends, edges) → `UNION ALL` both directions before counting.",
    "With only the id column selected, plain `UNION` would collapse each person to one row → every count becomes 1.",
    "Follow-up for ties: compare with `MAX(num)` or use `RANK()`.",
  ],
  pitfalls=["Counting only requester_id."],
  recall="UNION ALL requester & accepter ids, GROUP BY id, ORDER BY count DESC LIMIT 1.",
),
dict(
  n=42, id=585, slug="investments-in-2016", title="Investments in 2016",
  sec="subq", diff="Medium", concepts=["IN + GROUP BY HAVING", "Tuple IN", "COUNT() OVER"],
  pattern="Two independent group-size conditions on the same rows",
  prompt="Sum `tiv_2016` for policyholders who (a) share their `tiv_2015` value with at least one other policyholder, and (b) have a unique location (no one else has the same (lat, lon)). Round to 2.",
  returns="tiv_2016 (single value)",
  setup="""
CREATE TABLE Insurance (pid INT PRIMARY KEY, tiv_2015 DECIMAL(10,2), tiv_2016 DECIMAL(10,2), lat DECIMAL(5,2), lon DECIMAL(5,2));
INSERT INTO Insurance VALUES
(1,15,10,28.61,77.20),(2,25,20,19.07,72.87),(3,15,30,19.07,72.87),
(4,15,45,12.97,77.59),(5,35,50,22.57,88.36),(6,25,15,13.08,80.27);
""",
  solution="""
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
        SELECT tiv_2015 FROM Insurance
        GROUP BY tiv_2015 HAVING COUNT(*) > 1)
  AND (lat, lon) IN (
        SELECT lat, lon FROM Insurance
        GROUP BY lat, lon HAVING COUNT(*) = 1);
""",
  alts=[("Window counts", """
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
  SELECT tiv_2016,
         COUNT(*) OVER (PARTITION BY tiv_2015) AS same_tiv,
         COUNT(*) OVER (PARTITION BY lat, lon) AS same_loc
  FROM Insurance
) t
WHERE same_tiv > 1 AND same_loc = 1;
""", "One pass: attach both group sizes to every row, then filter.")],
  approach=[
    "Condition (a): tiv_2015 belongs to a group of size > 1.",
    "Condition (b): (lat, lon) belongs to a group of size = 1.",
    "Each is a GROUP BY … HAVING subquery; combine with AND, then SUM.",
  ],
  steps=[
    dict(t="Group sizes for both conditions", sql="""
SELECT pid, tiv_2015, tiv_2016, lat, lon,
       COUNT(*) OVER (PARTITION BY tiv_2015) AS `+same_tiv_2015`,
       COUNT(*) OVER (PARTITION BY lat, lon) AS `+same_location`,
       (COUNT(*) OVER (PARTITION BY tiv_2015) > 1 AND COUNT(*) OVER (PARTITION BY lat, lon) = 1) AS _keep
FROM Insurance ORDER BY pid""",
      note="pid 3 shares tiv_2015 but also shares a location with pid 2 → out. pid 5 is unique on tiv_2015 → out. 10 + 45 + 15 = 70.00."),
  ],
  remember=[
    "Multi-column membership: `(a, b) IN (SELECT a, b …)`.",
    "`COUNT(*) OVER (PARTITION BY …)` = \"how many rows share this value\" on every row.",
  ],
  pitfalls=["Requiring (a) and (b) against different subsets — both are evaluated over the whole table."],
  recall="tiv_2015 IN (count>1) AND (lat,lon) IN (count=1); ROUND(SUM(tiv_2016),2).",
),
dict(
  n=43, id=185, slug="department-top-three-salaries", title="Department Top Three Salaries",
  sec="subq", diff="Hard", concepts=["DENSE_RANK", "PARTITION BY", "Correlated subquery"],
  pattern="Top-N per group with ties → DENSE_RANK",
  prompt="A high earner is an employee whose salary is among the **top three unique salaries** in their department. Return department name, employee name and salary of all high earners.",
  returns="Department, Employee, Salary (any order)",
  setup="""
CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(255), salary INT, departmentId INT);
CREATE TABLE Department (id INT PRIMARY KEY, name VARCHAR(255));
INSERT INTO Department VALUES (1,'Engineering'),(2,'Sales');
INSERT INTO Employee VALUES
(1,'Arjun',95000,1),(2,'Bhavya',88000,2),(3,'Chirag',61000,2),(4,'Dev',110000,1),(5,'Esha',72000,1),
(6,'Farhan',95000,1),(7,'Gita',80000,1),(8,'Hari',50000,2),(9,'Indu',45000,2);
""",
  solution="""
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM (
  SELECT name, salary, departmentId,
         DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS rnk
  FROM Employee
) e
JOIN Department d ON d.id = e.departmentId
WHERE e.rnk <= 3;
""",
  alts=[("Correlated subquery", """
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee e
JOIN Department d ON d.id = e.departmentId
WHERE (
  SELECT COUNT(DISTINCT e2.salary)
  FROM Employee e2
  WHERE e2.departmentId = e.departmentId
    AND e2.salary > e.salary
) < 3;
""", "\"Fewer than 3 distinct salaries are higher than mine\" ⇔ I'm in the top 3 unique salaries.")],
  approach=[
    "Top-N **per group** → window function with `PARTITION BY departmentId`.",
    "\"Top three unique salaries\" → ties share a rank and don't consume extra ranks → `DENSE_RANK`.",
    "Filter rank ≤ 3 in an outer query (window results can't be used in WHERE directly).",
  ],
  steps=[
    dict(t="ROW_NUMBER vs RANK vs DENSE_RANK per department", sql="""
SELECT e.departmentId AS _grp, d.name AS department, e.name, e.salary,
       ROW_NUMBER() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC, e.name) AS `+row_number`,
       RANK()       OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) AS `+rank`,
       DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) AS `+dense_rank`,
       DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) <= 3 AS _keep
FROM Employee e JOIN Department d ON d.id = e.departmentId
ORDER BY d.name, e.salary DESC, e.name""",
      note="Arjun and Farhan tie at 95000: RANK jumps 2→4 (so Gita would be cut), DENSE_RANK goes 2→3 (Gita kept). That's exactly why DENSE_RANK."),
  ],
  remember=[
    "ROW_NUMBER: 1,2,3,4 (no ties) · RANK: 1,2,2,4 (gaps) · DENSE_RANK: 1,2,2,3 (no gaps).",
    "\"Top N unique values\" → DENSE_RANK. \"Top N rows\" → ROW_NUMBER.",
    "Window functions are evaluated after WHERE → filter on them from an outer query or CTE.",
  ],
  pitfalls=["`LIMIT 3` can't work per department.", "RANK cuts people after a tie."],
  recall="DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) ≤ 3, join Department.",
),
]
