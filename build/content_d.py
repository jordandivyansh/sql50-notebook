# SQL 50 content — Advanced String Functions / Regex / Clause (problems 44–50)

PROBLEMS_D = [
dict(
  n=44, id=1667, slug="fix-names-in-a-table", title="Fix Names in a Table",
  sec="string", diff="Easy", concepts=["CONCAT", "UPPER/LOWER", "LEFT", "SUBSTRING"],
  pattern="Rebuild a string from transformed pieces",
  prompt="Fix every name so only the first character is uppercase and the rest are lowercase. Order by user_id.",
  returns="user_id, name (ordered)",
  setup="""
CREATE TABLE Users (user_id INT PRIMARY KEY, name VARCHAR(40));
INSERT INTO Users VALUES (1,'aNANYA'),(2,'vIKAS'),(3,'PRIYA'),(4,'z');
""",
  solution="""
SELECT user_id,
       CONCAT(UPPER(LEFT(name, 1)), LOWER(SUBSTRING(name, 2))) AS name
FROM Users
ORDER BY user_id;
""",
  alts=[("SUBSTR everywhere", """
SELECT user_id,
       CONCAT(UPPER(SUBSTR(name, 1, 1)), LOWER(SUBSTR(name, 2))) AS name
FROM Users
ORDER BY user_id;
""", "`SUBSTR` = `SUBSTRING`; `SUBSTRING(s, pos)` without a length returns the rest of the string.")],
  approach=["Split the name: first character + the rest.", "UPPER the first, LOWER the rest, CONCAT them back."],
  steps=[
    dict(t="Break apart, transform, rebuild", sql="""
SELECT user_id, name, LEFT(name, 1) AS first_char, SUBSTRING(name, 2) AS rest,
       CONCAT(UPPER(LEFT(name, 1)), LOWER(SUBSTRING(name, 2))) AS `+fixed`
FROM Users ORDER BY user_id""",
      note="For a one-letter name, SUBSTRING(name, 2) is just '' — no special case needed."),
  ],
  remember=[
    "MySQL strings are **1-indexed**: `SUBSTRING(s, 1, 1)` is the first character.",
    "`CONCAT()` returns NULL if any argument is NULL; `CONCAT_WS(sep, …)` skips NULLs.",
  ],
  pitfalls=["`SUBSTRING(name, 0, 1)` returns an empty string in MySQL (position 0)."],
  recall="CONCAT(UPPER(LEFT(name,1)), LOWER(SUBSTRING(name,2))) ORDER BY user_id.",
  ordered=True,
),
dict(
  n=45, id=1527, slug="patients-with-a-condition", title="Patients With a Condition",
  sec="string", diff="Easy", concepts=["LIKE", "REGEXP", "Word boundary"],
  pattern="Match a code at the start of a word in a space-separated list",
  prompt="`conditions` holds zero or more space-separated codes. Type I Diabetes codes always **start with** `DIAB1`. Return patients who have such a code.",
  returns="patient_id, patient_name, conditions (any order)",
  setup="""
CREATE TABLE Patients (patient_id INT PRIMARY KEY, patient_name VARCHAR(30), conditions VARCHAR(100));
INSERT INTO Patients VALUES
(1,'Anand','FEVR COUGH'),(2,'Bindu',''),(3,'Charu','DIAB100 MYOP'),(4,'Darsh','ACNE DIAB102'),
(5,'Ekta','DIAB201'),(6,'Faiz','SADIAB100'),(7,'Gauri','DIAB1');
""",
  solution="""
SELECT patient_id, patient_name, conditions
FROM Patients
WHERE conditions LIKE 'DIAB1%'
   OR conditions LIKE '% DIAB1%';
""",
  alts=[("REGEXP", """
SELECT patient_id, patient_name, conditions
FROM Patients
WHERE conditions REGEXP '(^| )DIAB1';
""", "Start of string OR a space, then DIAB1. `'\\\\bDIAB1'` (word boundary) also works in MySQL 8.")],
  approach=[
    "The code must start a word: either at the very start of the string, or right after a space.",
    "Two LIKE patterns: `'DIAB1%'` (first code) and `'% DIAB1%'` (any later code).",
  ],
  steps=[
    dict(t="Naive vs correct patterns", sql="""
SELECT patient_id, patient_name, conditions,
       conditions LIKE '%DIAB1%' AS `+LIKE '%DIAB1%' (naive)`,
       conditions LIKE 'DIAB1%' AS `+starts with`,
       conditions LIKE '% DIAB1%' AS `+after a space`,
       (conditions LIKE 'DIAB1%' OR conditions LIKE '% DIAB1%') AS _keep
FROM Patients ORDER BY patient_id""",
      note="Faiz's 'SADIAB100' contains DIAB1 in the middle of a word — the naive pattern wrongly matches it."),
  ],
  remember=[
    "LIKE wildcards: `%` = any sequence (incl. empty), `_` = exactly one character.",
    "\"Word starts with X\" in a space-separated list: `LIKE 'X%' OR LIKE '% X%'`.",
  ],
  pitfalls=["`LIKE '%DIAB1%'` matches codes like SADIAB100 — LeetCode tests this."],
  recall="LIKE 'DIAB1%' OR LIKE '% DIAB1%'.",
),
dict(
  n=46, id=196, slug="delete-duplicate-emails", title="Delete Duplicate Emails",
  sec="string", diff="Easy", concepts=["DELETE + JOIN", "Self join", "Error 1093"],
  pattern="Delete every duplicate except the smallest id",
  prompt="Write a **DELETE** statement that removes duplicate emails from `Person`, keeping only the row with the smallest id for each email. (LeetCode checks the table afterwards.)",
  returns="the Person table after the delete",
  setup="""
CREATE TABLE Person (id INT PRIMARY KEY, email VARCHAR(255));
INSERT INTO Person VALUES (1,'ravi@mail.com'),(2,'sana@mail.com'),(3,'ravi@mail.com'),(4,'tom@mail.com'),(5,'sana@mail.com'),(6,'ravi@mail.com');
""",
  solution="""
DELETE p1
FROM Person p1
JOIN Person p2
  ON p1.email = p2.email
 AND p1.id > p2.id;
""",
  post="SELECT * FROM Person ORDER BY id",
  alts=[
    ("NOT IN with a derived-table wrapper", """
DELETE FROM Person
WHERE id NOT IN (
  SELECT id FROM (
    SELECT MIN(id) AS id FROM Person GROUP BY email
  ) AS keep_ids
);
""", "The extra derived table is required: MySQL won't let you DELETE from a table and select from it in a direct subquery (error 1093)."),
    ("ROW_NUMBER", """
DELETE FROM Person
WHERE id IN (
  SELECT id FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
    FROM Person
  ) t
  WHERE rn > 1
);
""", "Number each email's rows by id; delete everything after the first."),
  ],
  approach=[
    "A row should go if another row has the **same email and a smaller id**.",
    "Self join expresses exactly that: `p1.email = p2.email AND p1.id > p2.id` → p1 is a later duplicate.",
    "MySQL's multi-table DELETE: `DELETE p1 FROM … JOIN …` deletes only from p1.",
  ],
  steps=[
    dict(t="Which rows have a smaller-id twin?", sql="""
SELECT p1.id AS `p1.id (to delete)`, p1.email, p2.id AS `p2.id (smaller twin)`
FROM Person p1 JOIN Person p2 ON p1.email = p2.email AND p1.id > p2.id
ORDER BY p1.id, p2.id""",
      note="Row 6 matches two smaller twins (1 and 3) — it is still deleted only once."),
    dict(t="Before → after, grouped by email", sql="""
SELECT email AS _grp, id, email,
       id = (SELECT MIN(id) FROM Person x WHERE x.email = p.email) AS _keep
FROM Person p ORDER BY email, id""",
      note="In each email group only the smallest id survives."),
  ],
  remember=[
    "MySQL DELETE with join: `DELETE alias FROM t alias JOIN …` — name the table(s) to delete from after DELETE.",
    "Error 1093 (\"can't specify target table for update in FROM clause\"): wrap the subquery in another derived table.",
    "To just *find* duplicates: `SELECT email FROM Person GROUP BY email HAVING COUNT(*) > 1`.",
  ],
  pitfalls=["Using `>=` or `<>` in the join deletes every copy, including the one to keep."],
  recall="DELETE p1 FROM Person p1 JOIN Person p2 ON same email AND p1.id > p2.id.",
),
dict(
  n=47, id=176, slug="second-highest-salary", title="Second Highest Salary",
  sec="string", diff="Medium", concepts=["LIMIT OFFSET", "DISTINCT", "Scalar subquery", "NULL on empty"],
  pattern="Nth distinct value — and NULL when it doesn't exist",
  prompt="Return the second highest **distinct** salary from `Employee`, or NULL if there isn't one.",
  returns="SecondHighestSalary (one row, possibly NULL)",
  setup="""
CREATE TABLE Employee (id INT PRIMARY KEY, salary INT);
INSERT INTO Employee VALUES (1,70000),(2,90000),(3,90000),(4,50000);
""",
  solution="""
SELECT (
  SELECT DISTINCT salary
  FROM Employee
  ORDER BY salary DESC
  LIMIT 1 OFFSET 1
) AS SecondHighestSalary;
""",
  alts=[
    ("MAX below the MAX", """
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);
""", "MAX over an empty set is NULL — the NULL case comes for free."),
    ("DENSE_RANK", """
SELECT MAX(salary) AS SecondHighestSalary
FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
  FROM Employee
) t
WHERE rnk = 2;
""", "Generalises to the Nth highest; the outer MAX guarantees one row (NULL if none)."),
  ],
  approach=[
    "Distinct salaries sorted descending; skip one, take one → `DISTINCT … ORDER BY … LIMIT 1 OFFSET 1`.",
    "If there's no second salary, that query returns **no rows** — but we need one NULL row.",
    "Wrap it as a scalar subquery: an empty scalar subquery evaluates to NULL.",
  ],
  steps=[
    dict(t="Rank the salaries", sql="""
SELECT id, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC, id) AS `+position`,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS `+dense_rank`,
       DENSE_RANK() OVER (ORDER BY salary DESC) = 2 AS _keep
FROM Employee ORDER BY salary DESC, id""",
      note="90000 appears twice. By position, row 2 is still 90000 — by distinct rank, #2 is 70000."),
    dict(t="Trap: OFFSET without DISTINCT", sql="""
SELECT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1""",
      note="Returns 90000 — the duplicate top salary. DISTINCT is essential."),
  ],
  remember=[
    "`LIMIT n OFFSET m` = skip m rows, take n (also written `LIMIT m, n`).",
    "Scalar subquery with no row → NULL. Plain query with no row → empty result.",
    "Nth highest (LC 177): `LIMIT 1 OFFSET N-1` (compute N-1 into a variable first inside a function).",
  ],
  pitfalls=["Forgetting DISTINCT.", "Returning an empty result instead of NULL when there's only one salary."],
  recall="SELECT (SELECT DISTINCT salary ORDER BY salary DESC LIMIT 1 OFFSET 1).",
),
dict(
  n=48, id=1484, slug="group-sold-products-by-the-date", title="Group Sold Products By The Date",
  sec="string", diff="Easy", concepts=["GROUP_CONCAT", "COUNT(DISTINCT)", "ORDER BY"],
  pattern="Aggregate strings into a list per group",
  prompt="For each sell_date, report the number of **different** products sold and their names sorted alphabetically, joined by commas. Order by sell_date.",
  returns="sell_date, num_sold, products (ordered)",
  setup="""
CREATE TABLE Activities (sell_date DATE, product VARCHAR(20));
INSERT INTO Activities VALUES
('2024-05-30','Pen'),('2024-06-01','Notebook'),('2024-06-02','Mask'),('2024-05-30','Bat'),
('2024-06-01','Atlas'),('2024-06-02','Mask'),('2024-05-30','Tiffin'),('2024-05-30','Bat');
""",
  solution="""
SELECT sell_date,
       COUNT(DISTINCT product) AS num_sold,
       GROUP_CONCAT(DISTINCT product ORDER BY product SEPARATOR ',') AS products
FROM Activities
GROUP BY sell_date
ORDER BY sell_date;
""",
  alts=[],
  approach=[
    "One row per date → GROUP BY sell_date.",
    "Duplicates exist → DISTINCT in both the count and the list.",
    "`GROUP_CONCAT(DISTINCT x ORDER BY x SEPARATOR ',')` builds the sorted list.",
  ],
  steps=[
    dict(t="Rows per date", sql="""
SELECT sell_date AS _grp, sell_date, product FROM Activities ORDER BY sell_date, product""",
      note="30 May sold Bat twice → counted and listed once."),
  ],
  remember=[
    "`GROUP_CONCAT(DISTINCT col ORDER BY col SEPARATOR ',')` — default separator is ','.",
    "Result is cut at `group_concat_max_len` (1024 bytes by default).",
    "PostgreSQL / SQL Server equivalent: `STRING_AGG(col, ',')`.",
  ],
  pitfalls=["Forgetting DISTINCT inside GROUP_CONCAT lists duplicates."],
  recall="GROUP BY date; COUNT(DISTINCT product); GROUP_CONCAT(DISTINCT product ORDER BY product).",
  ordered=True,
),
dict(
  n=49, id=1327, slug="list-the-products-ordered-in-a-period", title="List the Products Ordered in a Period",
  sec="string", diff="Easy", concepts=["JOIN", "Date range", "HAVING SUM"],
  pattern="Filter a month, aggregate, then filter groups",
  prompt="Return the names of products with **at least 100** units ordered in **February 2020**, and that amount.",
  returns="product_name, unit (any order)",
  setup="""
CREATE TABLE Products (product_id INT PRIMARY KEY, product_name VARCHAR(40), product_category VARCHAR(40));
CREATE TABLE Orders (product_id INT, order_date DATE, unit INT);
INSERT INTO Products VALUES (1,'Laptop','Computer'),(2,'Kurta','Clothing'),(3,'Mixer','Kitchen'),(4,'Kindle','Book');
INSERT INTO Orders VALUES
(1,'2020-02-05',60),(1,'2020-02-10',70),(2,'2020-01-18',30),(2,'2020-02-11',80),(2,'2020-02-29',20),
(3,'2020-02-17',50),(3,'2020-03-01',90),(4,'2020-02-09',100),(4,'2020-01-31',50);
""",
  solution="""
SELECT p.product_name, SUM(o.unit) AS unit
FROM Orders o
JOIN Products p ON p.product_id = o.product_id
WHERE o.order_date >= '2020-02-01'
  AND o.order_date <  '2020-03-01'
GROUP BY p.product_id, p.product_name
HAVING SUM(o.unit) >= 100;
""",
  alts=[("DATE_FORMAT filter", """
SELECT p.product_name, SUM(o.unit) AS unit
FROM Orders o
JOIN Products p USING (product_id)
WHERE DATE_FORMAT(o.order_date, '%Y-%m') = '2020-02'
GROUP BY p.product_id, p.product_name
HAVING unit >= 100;
""", "Readable, but wrapping the column in a function prevents index use. MySQL lets HAVING use the alias.")],
  approach=["Row filter: February 2020 (WHERE).", "Group per product and SUM units.", "Group filter: total ≥ 100 (HAVING)."],
  steps=[
    dict(t="Keep February 2020 orders", sql="""
SELECT o.product_id AS _grp, p.product_name, o.order_date, o.unit,
       (o.order_date >= '2020-02-01' AND o.order_date < '2020-03-01') AS _keep
FROM Orders o JOIN Products p ON p.product_id = o.product_id
ORDER BY o.product_id, o.order_date""",
      note="29 Feb is in (2020 is a leap year); 1 Mar and January orders are out."),
    dict(t="Sum per product, keep totals ≥ 100", sql="""
SELECT p.product_name, SUM(o.unit) AS `+feb_units`, SUM(o.unit) >= 100 AS _keep
FROM Orders o JOIN Products p ON p.product_id = o.product_id
WHERE o.order_date >= '2020-02-01' AND o.order_date < '2020-03-01'
GROUP BY p.product_id, p.product_name ORDER BY p.product_id""",
      note="Kurta hits exactly 100 — included (at least)."),
  ],
  remember=[
    "Half-open ranges `>= start AND < next_start` are the safest date filters (no end-of-month or time-of-day bugs).",
    "WHERE filters rows before grouping; HAVING filters the sums after.",
  ],
  pitfalls=["Ending the range at '2020-02-28'.", "Putting `SUM(unit) >= 100` in WHERE (invalid)."],
  recall="WHERE Feb-2020 range, GROUP BY product, HAVING SUM(unit) >= 100.",
),
dict(
  n=50, id=1517, slug="find-users-with-valid-e-mails", title="Find Users With Valid E-Mails",
  sec="string", diff="Easy", concepts=["REGEXP_LIKE", "Anchors", "Case sensitivity"],
  pattern="Validate a whole string with an anchored regex",
  prompt="A valid email has a prefix that **starts with a letter** and contains only letters, digits, `_`, `.` or `-`, followed by exactly the domain `@leetcode.com`. Return users with valid emails.",
  returns="user_id, name, mail (any order)",
  setup="""
CREATE TABLE Users (user_id INT PRIMARY KEY, name VARCHAR(30), mail VARCHAR(50));
INSERT INTO Users VALUES
(1,'Aarav','aarav.k@leetcode.com'),(2,'Bhumi','bhumi-99@leetcode.com'),(3,'Chris','_chris@leetcode.com'),
(4,'Diya','diya@leetcode.co'),(5,'Eva','eva#1@leetcode.com'),(6,'Farid','Farid_X@leetcode.com'),
(7,'Gina','gina@LEETCODE.COM'),(8,'Hrithik','hrithik@leetcodeXcom'),(9,'Ishan','9ishan@leetcode.com');
""",
  solution="""
SELECT *
FROM Users
WHERE REGEXP_LIKE(mail, '^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$', 'c');
""",
  alts=[("Case-sensitive collation", """
SELECT *
FROM Users
WHERE mail COLLATE utf8mb4_bin REGEXP '^[A-Za-z][A-Za-z0-9_.-]*@leetcode\\\\.com$';
""", "A `_bin` collation makes REGEXP case-sensitive. Inside a MySQL string, a literal dot is written `\\\\.` (or `[.]`). Older answers use `REGEXP BINARY`, which throws error 3995 on MySQL 8 with utf8mb4 columns.")],
  approach=[
    "Anchor the whole string: `^ … $`.",
    "First char a letter `[A-Za-z]`, then any of `[A-Za-z0-9_.-]*`, then the literal `@leetcode.com`.",
    "Escape the dot (or use `[.]`) and make the match case-sensitive.",
  ],
  steps=[
    dict(t="Why both escaping and case-sensitivity matter", sql="""
SELECT user_id, mail,
       mail REGEXP '^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$' AS `+default (case-insensitive)`,
       REGEXP_LIKE(mail, '^[A-Za-z][A-Za-z0-9_.-]*@leetcode.com$', 'c') AS `+unescaped dot`,
       REGEXP_LIKE(mail, '^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$', 'c') AS _keep
FROM Users ORDER BY user_id""",
      note="Gina's '@LEETCODE.COM' passes a default REGEXP (MySQL's default collation is case-insensitive). Hrithik's 'leetcodeXcom' passes when the dot is unescaped (. = any char)."),
  ],
  remember=[
    "MySQL `REGEXP` follows the column collation — usually **case-insensitive**. Use `REGEXP_LIKE(s, pat, 'c')` or `BINARY` for exact case.",
    "Inside a MySQL string literal, regex backslashes are doubled: `'\\\\.'`. `[.]` sidesteps the escaping.",
    "In a character class, put `-` last (or first) so it's literal.",
  ],
  pitfalls=["Unanchored pattern matches emails with junk before/after.", "Unescaped `.` matches any character."],
  recall="REGEXP_LIKE(mail, '^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$', 'c').",
),
]
