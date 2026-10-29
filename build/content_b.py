# SQL 50 content — Basic Aggregate Functions + Sorting and Grouping (problems 15–29)

PROBLEMS_B = [
# ───────────────────────────── BASIC AGGREGATE FUNCTIONS ─────────────────────────────
dict(
  n=15, id=620, slug="not-boring-movies", title="Not Boring Movies",
  sec="agg", diff="Easy", concepts=["WHERE", "MOD", "ORDER BY DESC"],
  pattern="Filter + sort",
  prompt="From `Cinema`, list movies with an **odd** id whose description is not `'boring'`, sorted by rating from highest to lowest.",
  returns="id, movie, description, rating (rating descending)",
  setup="""
CREATE TABLE Cinema (id INT PRIMARY KEY, movie VARCHAR(255), description VARCHAR(255), rating DECIMAL(2,1));
INSERT INTO Cinema VALUES
(1,'Lagaan','epic sports drama',8.1),(2,'Swades','slow burn',8.2),(3,'Race 3','boring',1.9),
(4,'Dangal','biopic',8.3),(5,'Andhadhun','thriller',8.2),(6,'Queen','feel good',8.1),(7,'Tumbbad','horror',8.4);
""",
  solution="""
SELECT *
FROM Cinema
WHERE id % 2 = 1
  AND description <> 'boring'
ORDER BY rating DESC;
""",
  alts=[("MOD()", """
SELECT *
FROM Cinema
WHERE MOD(id, 2) = 1 AND description != 'boring'
ORDER BY rating DESC;
""", "`MOD(a,b)`, `a % b` and `a MOD b` are identical in MySQL.")],
  approach=["Two row conditions → `WHERE … AND …`.", "Odd id → `id % 2 = 1`.", "Sort by rating descending."],
  steps=[
    dict(t="Check both conditions", sql="""
SELECT id, movie, description, rating,
       id % 2 = 1 AS `+odd_id`, description <> 'boring' AS `+not_boring`,
       (id % 2 = 1 AND description <> 'boring') AS _keep
FROM Cinema ORDER BY id""",
      note="Race 3 has an odd id but is boring; even ids are out regardless."),
  ],
  remember=["`<>` and `!=` are the same.", "`ORDER BY col DESC` — default direction is ASC."],
  pitfalls=["Forgetting `DESC` — this problem checks the order."],
  recall="id % 2 = 1 AND description <> 'boring' ORDER BY rating DESC.",
  ordered=True,
),
dict(
  n=16, id=1251, slug="average-selling-price", title="Average Selling Price",
  sec="agg", diff="Easy", concepts=["LEFT JOIN", "BETWEEN", "Weighted average", "IFNULL"],
  pattern="Range join (date BETWEEN start AND end) + weighted average",
  prompt="`Prices` gives a product's price for date ranges; `UnitsSold` records units sold on a date. For every product, compute the average selling price = total revenue ÷ total units, rounded to 2. Products with no sales get 0.",
  returns="product_id, average_price (any order)",
  setup="""
CREATE TABLE Prices (product_id INT, start_date DATE, end_date DATE, price INT, PRIMARY KEY (product_id, start_date, end_date));
CREATE TABLE UnitsSold (product_id INT, purchase_date DATE, units INT);
INSERT INTO Prices VALUES
(1,'2024-02-17','2024-02-28',5),(1,'2024-03-01','2024-03-22',20),
(2,'2024-02-01','2024-02-20',15),(2,'2024-02-21','2024-03-31',30),
(3,'2024-02-21','2024-03-31',30);
INSERT INTO UnitsSold VALUES (1,'2024-02-25',100),(1,'2024-03-01',15),(2,'2024-02-10',200),(2,'2024-03-22',30);
""",
  solution="""
SELECT p.product_id,
       ROUND(IFNULL(SUM(p.price * u.units) / SUM(u.units), 0), 2) AS average_price
FROM Prices p
LEFT JOIN UnitsSold u
       ON p.product_id = u.product_id
      AND u.purchase_date BETWEEN p.start_date AND p.end_date
GROUP BY p.product_id;
""",
  alts=[],
  approach=[
    "A sale belongs to the price row whose range contains its date → join on product **and** `purchase_date BETWEEN start_date AND end_date`.",
    "Average selling price is weighted by units: Σ(price×units) ÷ Σ(units) — not AVG(price).",
    "Products with no sales must stay → LEFT JOIN from Prices, and IFNULL the NULL result to 0.",
  ],
  steps=[
    dict(t="Range join each sale to its price period", sql="""
SELECT p.product_id AS _grp, p.product_id, p.start_date, p.end_date, p.price,
       u.purchase_date, u.units, p.price * u.units AS `+revenue`
FROM Prices p LEFT JOIN UnitsSold u
  ON p.product_id = u.product_id AND u.purchase_date BETWEEN p.start_date AND p.end_date
ORDER BY p.product_id, p.start_date""",
      note="Product 1: (500 + 300) / 115 = 6.96. Product 3 never sold → NULLs → IFNULL gives 0."),
  ],
  remember=[
    "Weighted average = `SUM(value * weight) / SUM(weight)`.",
    "With a LEFT JOIN, put conditions on the right table in `ON`, not `WHERE` — otherwise unmatched rows are filtered out.",
    "`BETWEEN a AND b` is inclusive on both ends.",
  ],
  pitfalls=["`AVG(price)` ignores how many units were sold at each price.", "Putting the date condition in WHERE drops product 3."],
  recall="Prices LEFT JOIN UnitsSold ON id AND date BETWEEN; ROUND(IFNULL(SUM(p*u)/SUM(u),0),2).",
),
dict(
  n=17, id=1075, slug="project-employees-i", title="Project Employees I",
  sec="agg", diff="Easy", concepts=["JOIN", "AVG", "ROUND"],
  pattern="Join then average per group",
  prompt="For each project, report the average years of experience of its employees, rounded to 2.",
  returns="project_id, average_years (any order)",
  setup="""
CREATE TABLE Project (project_id INT, employee_id INT, PRIMARY KEY (project_id, employee_id));
CREATE TABLE Employee (employee_id INT PRIMARY KEY, name VARCHAR(10), experience_years INT NOT NULL);
INSERT INTO Project VALUES (1,1),(1,2),(1,3),(2,1),(2,4);
INSERT INTO Employee VALUES (1,'Kiran',3),(2,'Asha',2),(3,'Vikram',1),(4,'Leela',2);
""",
  solution="""
SELECT p.project_id,
       ROUND(AVG(e.experience_years), 2) AS average_years
FROM Project p
JOIN Employee e
  ON p.employee_id = e.employee_id
GROUP BY p.project_id;
""",
  alts=[],
  approach=["Experience lives in Employee, project membership in Project → JOIN.", "GROUP BY project, AVG, ROUND 2."],
  steps=[
    dict(t="Join and group by project", sql="""
SELECT p.project_id AS _grp, p.project_id, e.name, e.experience_years
FROM Project p JOIN Employee e ON p.employee_id = e.employee_id
ORDER BY p.project_id, e.employee_id""",
      note="Project 1: (3+2+1)/3 = 2.00; Project 2: (3+2)/2 = 2.50."),
  ],
  remember=["`ROUND(AVG(x), 2)` — the most common output format in SQL 50."],
  pitfalls=[],
  recall="JOIN, GROUP BY project_id, ROUND(AVG(experience_years),2).",
),
dict(
  n=18, id=1633, slug="percentage-of-users-attended-a-contest", title="Percentage of Users Attended a Contest",
  sec="agg", diff="Easy", concepts=["Scalar subquery", "COUNT", "ORDER BY multi"],
  pattern="Group count ÷ global count (scalar subquery)",
  prompt="For each contest, compute the percentage of **all users** who registered, rounded to 2. Sort by percentage descending, ties by contest_id ascending.",
  returns="contest_id, percentage (ordered)",
  setup="""
CREATE TABLE Users (user_id INT PRIMARY KEY, user_name VARCHAR(20));
CREATE TABLE Register (contest_id INT, user_id INT, PRIMARY KEY (contest_id, user_id));
INSERT INTO Users VALUES (1,'Ravi'),(2,'Sita'),(3,'Gopal'),(4,'Nisha');
INSERT INTO Register VALUES
(101,1),(101,2),(101,3),(101,4),(102,1),(102,3),(103,2),(104,1),(104,2),(104,4),(105,3),(105,4);
""",
  solution="""
SELECT contest_id,
       ROUND(COUNT(user_id) * 100 / (SELECT COUNT(*) FROM Users), 2) AS percentage
FROM Register
GROUP BY contest_id
ORDER BY percentage DESC, contest_id;
""",
  alts=[("CROSS JOIN the total", """
SELECT r.contest_id,
       ROUND(COUNT(r.user_id) * 100 / t.total, 2) AS percentage
FROM Register r
CROSS JOIN (SELECT COUNT(*) AS total FROM Users) t
GROUP BY r.contest_id, t.total
ORDER BY percentage DESC, r.contest_id;
""", "Same idea with the total as a one-row derived table.")],
  approach=[
    "Numerator: registrations per contest (GROUP BY contest_id).",
    "Denominator: total users — one number for the whole table → scalar subquery.",
    "Two-key sort: percentage DESC, then contest_id ASC.",
  ],
  steps=[
    dict(t="Denominator: total users", sql="SELECT COUNT(*) AS total_users FROM Users",
      note="A scalar subquery returns exactly one value and can be used anywhere an expression fits."),
    dict(t="Numerator: registrations per contest", sql="""
SELECT contest_id AS _grp, contest_id, user_id FROM Register ORDER BY contest_id, user_id""",
      note="Contest 102 and 105 both have 2 of 4 users → 50.00 tie, broken by contest_id."),
  ],
  remember=[
    "MySQL `/` always returns a decimal (5/2 = 2.5000). Use `DIV` for integer division.",
    "Multi-key `ORDER BY`: each key gets its own ASC/DESC.",
  ],
  pitfalls=["Dividing by registered users instead of all users."],
  recall="COUNT per contest * 100 / (SELECT COUNT(*) FROM Users); ORDER BY pct DESC, id.",
  ordered=True,
),
dict(
  n=19, id=1211, slug="queries-quality-and-percentage", title="Queries Quality and Percentage",
  sec="agg", diff="Easy", concepts=["AVG", "AVG(condition)", "ROUND"],
  pattern="Two aggregates per group, one of them a percentage of a condition",
  prompt="For each query_name: **quality** = average of rating ÷ position; **poor_query_percentage** = % of results with rating < 3. Round both to 2.",
  returns="query_name, quality, poor_query_percentage (any order)",
  setup="""
CREATE TABLE Queries (query_name VARCHAR(30), result VARCHAR(50), position INT, rating INT);
INSERT INTO Queries VALUES
('Mango','Alphonso',1,5),('Mango','Kesar',2,4),('Mango','Mango Shake',50,1),
('Tea','Assam',1,4),('Tea','Darjeeling',4,2),('Tea','Tea Kettle',20,1),
(NULL,'orphan row',3,2);
""",
  solution="""
SELECT query_name,
       ROUND(AVG(rating / position), 2) AS quality,
       ROUND(AVG(rating < 3) * 100, 2) AS poor_query_percentage
FROM Queries
WHERE query_name IS NOT NULL
GROUP BY query_name;
""",
  alts=[("SUM(CASE) / COUNT", """
SELECT query_name,
       ROUND(SUM(rating / position) / COUNT(*), 2) AS quality,
       ROUND(SUM(CASE WHEN rating < 3 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) AS poor_query_percentage
FROM Queries
WHERE query_name IS NOT NULL
GROUP BY query_name;
""", "Spelled out; works in every SQL dialect.")],
  approach=[
    "Per-row ratio first (`rating / position`), then average it.",
    "Poor percentage = AVG of the 0/1 flag `rating < 3`, × 100.",
    "LeetCode added a test with NULL query_name rows; they must not appear → filter them.",
  ],
  steps=[
    dict(t="Per-row ratio and poor flag", sql="""
SELECT query_name AS _grp, query_name, result, position, rating,
       rating / position AS `+rating/position`, rating < 3 AS `+is_poor`,
       query_name IS NOT NULL AS _keep
FROM Queries ORDER BY query_name, position""",
      note="Mango: (5 + 2 + 0.02) / 3 = 2.34, poor = 1/3 = 33.33%. The NULL-named row is excluded."),
  ],
  remember=["`AVG(cond) * 100` = percentage of rows meeting cond.", "Round each output column separately."],
  pitfalls=["Rounding the ratio per row before averaging changes the result — average first, round last."],
  recall="ROUND(AVG(rating/position),2), ROUND(AVG(rating<3)*100,2); drop NULL names.",
),
dict(
  n=20, id=1193, slug="monthly-transactions-i", title="Monthly Transactions I",
  sec="agg", diff="Medium", concepts=["DATE_FORMAT", "SUM(condition)", "SUM(IF)", "GROUP BY 2 cols"],
  pattern="Conditional aggregation per (month, country)",
  prompt="For each month and country, report: number of transactions, number approved, total amount, and total approved amount.",
  returns="month, country, trans_count, approved_count, trans_total_amount, approved_total_amount (any order)",
  setup="""
CREATE TABLE Transactions (id INT PRIMARY KEY, country VARCHAR(4), state ENUM('approved','declined'), amount INT, trans_date DATE);
INSERT INTO Transactions VALUES
(121,'IN','approved',1000,'2024-12-18'),(122,'IN','declined',2000,'2024-12-19'),
(123,'US','approved',2000,'2025-01-01'),(124,'IN','approved',2000,'2025-01-07'),
(125,'IN','declined',500,'2025-01-15'),(126,NULL,'approved',700,'2025-01-20');
""",
  solution="""
SELECT DATE_FORMAT(trans_date, '%Y-%m') AS month,
       country,
       COUNT(*)                              AS trans_count,
       SUM(state = 'approved')               AS approved_count,
       SUM(amount)                           AS trans_total_amount,
       SUM(IF(state = 'approved', amount, 0)) AS approved_total_amount
FROM Transactions
GROUP BY month, country;
""",
  alts=[("CASE + LEFT()", """
SELECT LEFT(trans_date, 7) AS month, country,
       COUNT(*) AS trans_count,
       SUM(CASE WHEN state = 'approved' THEN 1 ELSE 0 END) AS approved_count,
       SUM(amount) AS trans_total_amount,
       SUM(CASE WHEN state = 'approved' THEN amount ELSE 0 END) AS approved_total_amount
FROM Transactions
GROUP BY LEFT(trans_date, 7), country;
""", "`LEFT(date, 7)` works because MySQL casts the date to 'YYYY-MM-DD' text.")],
  approach=[
    "Group key = (month string, country).",
    "Totals use COUNT/SUM; \"approved only\" totals use a condition inside the aggregate.",
    "Count approved: `SUM(state='approved')`. Approved amount: `SUM(IF(approved, amount, 0))`.",
  ],
  steps=[
    dict(t="Derive month and approved-only values per row", sql="""
SELECT CONCAT(DATE_FORMAT(trans_date,'%Y-%m'), IFNULL(country,'-')) AS _grp,
       id, DATE_FORMAT(trans_date, '%Y-%m') AS `+month`, country, state, amount,
       state = 'approved' AS `+is_approved`,
       IF(state = 'approved', amount, 0) AS `+approved_amount`
FROM Transactions ORDER BY `+month`, country""",
      note="Each colour is one (month, country) group. The NULL country forms its own group — GROUP BY treats NULLs as equal."),
  ],
  remember=[
    "Conditional aggregation: put the condition **inside** SUM/COUNT so one pass gives several metrics.",
    "`DATE_FORMAT(d, '%Y-%m')` → '2025-01'. (`%m` month, `%i` minutes!)",
    "MySQL allows SELECT aliases in GROUP BY (`GROUP BY month`).",
  ],
  pitfalls=["Filtering `WHERE state='approved'` kills the overall counts.", "Using `%M` gives the month *name*."],
  recall="GROUP BY DATE_FORMAT(d,'%Y-%m'), country; SUM(state='approved'), SUM(IF(approved,amount,0)).",
),
dict(
  n=21, id=1174, slug="immediate-food-delivery-ii", title="Immediate Food Delivery II",
  sec="agg", diff="Medium", concepts=["Tuple IN", "MIN per group", "AVG(condition)", "ROW_NUMBER"],
  pattern="First row per group, then a percentage",
  prompt="An order is **immediate** if the preferred delivery date equals the order date. Each customer's **first order** is the one with the earliest order_date. What percentage of first orders were immediate? Round to 2.",
  returns="immediate_percentage (single value)",
  setup="""
CREATE TABLE Delivery (delivery_id INT PRIMARY KEY, customer_id INT, order_date DATE, customer_pref_delivery_date DATE);
INSERT INTO Delivery VALUES
(1,11,'2024-08-01','2024-08-03'),(2,12,'2024-08-02','2024-08-02'),(3,11,'2024-08-11','2024-08-11'),
(4,13,'2024-08-24','2024-08-24'),(5,13,'2024-08-21','2024-08-22'),(6,12,'2024-08-11','2024-08-13'),
(7,14,'2024-08-09','2024-08-09');
""",
  solution="""
SELECT ROUND(AVG(order_date = customer_pref_delivery_date) * 100, 2) AS immediate_percentage
FROM Delivery
WHERE (customer_id, order_date) IN (
  SELECT customer_id, MIN(order_date)
  FROM Delivery
  GROUP BY customer_id
);
""",
  alts=[("ROW_NUMBER", """
SELECT ROUND(AVG(order_date = customer_pref_delivery_date) * 100, 2) AS immediate_percentage
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn
  FROM Delivery
) t
WHERE rn = 1;
""", "Window version — scales to \"first N per group\".")],
  approach=[
    "Restrict to each customer's first order: find (customer, MIN(order_date)) and keep rows matching that pair.",
    "On those rows, the percentage of immediate orders = AVG(order_date = pref_date) × 100.",
  ],
  steps=[
    dict(t="Mark each customer's first order", sql="""
SELECT customer_id AS _grp, delivery_id, customer_id, order_date, customer_pref_delivery_date,
       order_date = customer_pref_delivery_date AS `+immediate`,
       (customer_id, order_date) IN (SELECT customer_id, MIN(order_date) FROM Delivery GROUP BY customer_id) AS _keep
FROM Delivery ORDER BY customer_id, order_date""",
      note="Customer 11's *second* order is immediate but doesn't count. First orders: 11 ✗, 12 ✓, 13 ✗, 14 ✓ → 50.00."),
  ],
  remember=[
    "\"First/latest row per group\" → `(group, date) IN (SELECT group, MIN/MAX(date) … GROUP BY group)`.",
    "`ROW_NUMBER() OVER (PARTITION BY g ORDER BY d)` and keep `rn = 1` is the window equivalent.",
  ],
  pitfalls=["Averaging over all orders, not just first orders."],
  recall="Filter (customer, MIN(order_date)) IN …, then ROUND(AVG(order=pref)*100,2).",
),
dict(
  n=22, id=550, slug="game-play-analysis-iv", title="Game Play Analysis IV",
  sec="agg", diff="Medium", concepts=["MIN per group", "DATE_ADD", "Ratio"],
  pattern="Compare each player's activity to their first login",
  prompt="Report the fraction of players who logged in again on the day **right after** their first login, rounded to 2.",
  returns="fraction (single value)",
  setup="""
CREATE TABLE Activity (player_id INT, device_id INT, event_date DATE, games_played INT, PRIMARY KEY (player_id, event_date));
INSERT INTO Activity VALUES
(1,2,'2024-03-01',5),(1,2,'2024-03-02',6),(2,3,'2024-06-25',1),(3,1,'2024-03-02',0),(3,4,'2024-07-03',5),
(4,1,'2024-05-10',2),(4,1,'2024-05-11',3),(4,1,'2024-05-12',1),
(5,1,'2024-01-01',1),(5,1,'2024-01-05',1),(5,1,'2024-01-06',1);
""",
  solution="""
SELECT ROUND(
         COUNT(a.player_id) / (SELECT COUNT(DISTINCT player_id) FROM Activity),
         2) AS fraction
FROM Activity a
JOIN (
  SELECT player_id, MIN(event_date) AS first_login
  FROM Activity
  GROUP BY player_id
) f
  ON a.player_id = f.player_id
 AND a.event_date = DATE_ADD(f.first_login, INTERVAL 1 DAY);
""",
  alts=[("Tuple IN", """
SELECT ROUND(COUNT(*) / (SELECT COUNT(DISTINCT player_id) FROM Activity), 2) AS fraction
FROM Activity
WHERE (player_id, DATE_SUB(event_date, INTERVAL 1 DAY)) IN (
  SELECT player_id, MIN(event_date) FROM Activity GROUP BY player_id
);
""", "A row qualifies if (player, the day before it) is that player's first login.")],
  approach=[
    "Step 1: first login per player (GROUP BY + MIN).",
    "Step 2: does the same player have a row on first_login + 1 day? Join on that exact date.",
    "Fraction = matching players ÷ all distinct players.",
  ],
  steps=[
    dict(t="First login per player", sql="""
SELECT player_id, MIN(event_date) AS first_login,
       DATE_ADD(MIN(event_date), INTERVAL 1 DAY) AS `+day_after`
FROM Activity GROUP BY player_id ORDER BY player_id""",
      note="We only care about the day after the *first* login."),
    dict(t="Find a login exactly on day_after", sql="""
SELECT a.player_id AS _grp, a.player_id, a.event_date, f.first_login,
       a.event_date = DATE_ADD(f.first_login, INTERVAL 1 DAY) AS _keep
FROM Activity a
JOIN (SELECT player_id, MIN(event_date) AS first_login FROM Activity GROUP BY player_id) f USING (player_id)
ORDER BY a.player_id, a.event_date""",
      note="Players 1 and 4 qualify. Player 5 has consecutive days later, but not after the first login. 2 / 5 = 0.40."),
  ],
  remember=[
    "`DATE_ADD(d, INTERVAL 1 DAY)` / `DATE_SUB(d, INTERVAL 1 DAY)`.",
    "Denominator is `COUNT(DISTINCT player_id)`, not row count.",
  ],
  pitfalls=["Checking *any* two consecutive days instead of first-login + 1."],
  recall="first_login = MIN per player; count rows on first_login+1; ÷ COUNT(DISTINCT player).",
),

# ───────────────────────────── SORTING AND GROUPING ─────────────────────────────
dict(
  n=23, id=2356, slug="number-of-unique-subjects-taught-by-each-teacher", title="Number of Unique Subjects Taught by Each Teacher",
  sec="sortgroup", diff="Easy", concepts=["COUNT(DISTINCT)", "GROUP BY"],
  pattern="Distinct count per group",
  prompt="A teacher can teach the same subject in several departments. For each teacher, count the number of **unique** subjects they teach.",
  returns="teacher_id, cnt (any order)",
  setup="""
CREATE TABLE Teacher (teacher_id INT, subject_id INT, dept_id INT, PRIMARY KEY (subject_id, dept_id));
INSERT INTO Teacher VALUES (1,10,1),(1,10,2),(1,11,1),(2,10,3),(2,12,3),(2,13,3),(3,11,4);
""",
  solution="""
SELECT teacher_id,
       COUNT(DISTINCT subject_id) AS cnt
FROM Teacher
GROUP BY teacher_id;
""",
  alts=[],
  approach=["One row per teacher → GROUP BY teacher_id.", "Same subject in two departments counts once → COUNT(DISTINCT subject_id)."],
  steps=[
    dict(t="Group rows by teacher", sql="""
SELECT teacher_id AS _grp, teacher_id, subject_id, dept_id FROM Teacher ORDER BY teacher_id, subject_id""",
      note="Teacher 1 teaches subject 10 in two departments → 3 rows but 2 unique subjects."),
  ],
  remember=["`COUNT(DISTINCT col)` ignores duplicates and NULLs."],
  pitfalls=["`COUNT(*)` gives 3 for teacher 1."],
  recall="GROUP BY teacher_id, COUNT(DISTINCT subject_id).",
),
dict(
  n=24, id=1141, slug="user-activity-for-the-past-30-days-i", title="User Activity for the Past 30 Days I",
  sec="sortgroup", diff="Easy", concepts=["Date range", "BETWEEN", "COUNT(DISTINCT)"],
  pattern="Date window + distinct count per day",
  prompt="Find the daily active user count for the 30-day period ending **2019-07-27 inclusive**. A user is active on a day if they have at least one activity that day. Skip days with no activity.",
  returns="day, active_users (any order)",
  setup="""
CREATE TABLE Activity (user_id INT, session_id INT, activity_date DATE,
  activity_type ENUM('open_session','end_session','scroll_down','send_message'));
INSERT INTO Activity VALUES
(1,1,'2019-07-20','open_session'),(1,1,'2019-07-20','scroll_down'),
(2,4,'2019-07-20','open_session'),(2,4,'2019-07-21','send_message'),
(3,2,'2019-07-21','open_session'),(3,2,'2019-07-21','end_session'),
(4,3,'2019-06-27','open_session'),(5,5,'2019-06-28','open_session'),(6,6,'2019-07-28','open_session');
""",
  solution="""
SELECT activity_date AS day,
       COUNT(DISTINCT user_id) AS active_users
FROM Activity
WHERE activity_date BETWEEN '2019-06-28' AND '2019-07-27'
GROUP BY activity_date;
""",
  alts=[("DATEDIFF window", """
SELECT activity_date AS day, COUNT(DISTINCT user_id) AS active_users
FROM Activity
WHERE DATEDIFF('2019-07-27', activity_date) BETWEEN 0 AND 29
GROUP BY activity_date;
""", "0..29 days before the end date = 30 days. Not index-friendly (function on the column).")],
  approach=[
    "30 days ending on the 27th inclusive → start = 27 Jul − 29 days = **28 Jun**.",
    "Filter that window, group by date, count distinct users (a user has many activities per day).",
  ],
  steps=[
    dict(t="Keep only the 30-day window", sql="""
SELECT user_id, activity_date, activity_type,
       DATEDIFF('2019-07-27', activity_date) AS `+days_before_end`,
       activity_date BETWEEN '2019-06-28' AND '2019-07-27' AS _keep
FROM Activity ORDER BY activity_date, user_id""",
      note="27 Jun is 30 days before → outside (31st day). 28 Jul is after the end → outside."),
    dict(t="Count distinct users per day", sql="""
SELECT activity_date AS _grp, activity_date, user_id, activity_type
FROM Activity WHERE activity_date BETWEEN '2019-06-28' AND '2019-07-27'
ORDER BY activity_date, user_id""",
      note="20 Jul has 3 rows but only 2 distinct users."),
  ],
  remember=[
    "\"N days ending on D inclusive\" → `BETWEEN D − (N−1) AND D`.",
    "Data can contain dates **after** the end date — bound both sides.",
  ],
  pitfalls=["Starting at '2019-06-27' gives a 31-day window.", "`COUNT(user_id)` counts activities, not users."],
  recall="BETWEEN '2019-06-28' AND '2019-07-27', GROUP BY date, COUNT(DISTINCT user_id).",
),
dict(
  n=25, id=1070, slug="product-sales-analysis-iii", title="Product Sales Analysis III",
  sec="sortgroup", diff="Medium", concepts=["Tuple IN", "MIN per group", "RANK"],
  pattern="All rows belonging to the first year of each group",
  prompt="For every product, return **all** sales from the first year that product was sold: product_id, first_year, quantity and price.",
  returns="product_id, first_year, quantity, price (any order)",
  setup="""
CREATE TABLE Sales (sale_id INT, product_id INT, year INT, quantity INT, price INT, PRIMARY KEY (sale_id, year));
INSERT INTO Sales VALUES (1,10,2020,10,500),(2,10,2021,12,550),(3,20,2021,5,900),(4,20,2021,8,950),(5,20,2022,3,1000),(6,30,2023,4,300);
""",
  solution="""
SELECT product_id, year AS first_year, quantity, price
FROM Sales
WHERE (product_id, year) IN (
  SELECT product_id, MIN(year)
  FROM Sales
  GROUP BY product_id
);
""",
  alts=[("RANK window", """
SELECT product_id, year AS first_year, quantity, price
FROM (
  SELECT *, RANK() OVER (PARTITION BY product_id ORDER BY year) AS rnk
  FROM Sales
) t
WHERE rnk = 1;
""", "RANK keeps ties (several sales in the first year). ROW_NUMBER would keep only one.")],
  approach=[
    "First year per product = MIN(year) grouped by product.",
    "A product may have several sales in that year → keep every row whose (product, year) matches.",
  ],
  steps=[
    dict(t="Keep rows from each product's first year", sql="""
SELECT product_id AS _grp, sale_id, product_id, year, quantity, price,
       (product_id, year) IN (SELECT product_id, MIN(year) FROM Sales GROUP BY product_id) AS _keep
FROM Sales ORDER BY product_id, year, sale_id""",
      note="Product 20 had two sales in 2021 — both are returned."),
  ],
  remember=[
    "`GROUP BY product_id` with `MIN(year), quantity` is **invalid** under ONLY_FULL_GROUP_BY (quantity isn't from the min row anyway).",
    "Ties in \"first\" → `RANK()`/`DENSE_RANK()`, not `ROW_NUMBER()`.",
  ],
  pitfalls=["`SELECT product_id, MIN(year), quantity … GROUP BY product_id` returns an arbitrary quantity (or errors)."],
  recall="(product_id, year) IN (SELECT product_id, MIN(year) … GROUP BY product_id).",
),
dict(
  n=26, id=596, slug="classes-more-than-5-students", title="Classes More Than 5 Students",
  sec="sortgroup", diff="Easy", concepts=["GROUP BY", "HAVING"],
  pattern="Filter groups by size",
  prompt="Find every class that has **at least five** students.",
  returns="class (any order)",
  setup="""
CREATE TABLE Courses (student VARCHAR(255), class VARCHAR(255), PRIMARY KEY (student, class));
INSERT INTO Courses VALUES
('Aman','Math'),('Bhavna','Math'),('Chirag','Math'),('Deepa','Math'),('Esha','Math'),
('Farhan','Hindi'),('Gauri','Hindi'),('Harsh','Hindi'),('Ira','Hindi'),('Jai','Chess');
""",
  solution="""
SELECT class
FROM Courses
GROUP BY class
HAVING COUNT(student) >= 5;
""",
  alts=[("Subquery", """
SELECT class
FROM (SELECT class, COUNT(*) AS n FROM Courses GROUP BY class) t
WHERE n >= 5;
""", "Equivalent: aggregate first, filter the derived table with WHERE.")],
  approach=["Group by class, count students, keep groups with count ≥ 5 using HAVING."],
  steps=[
    dict(t="Count per class and filter groups", sql="""
SELECT class, COUNT(student) AS `+students`, COUNT(student) >= 5 AS _keep
FROM Courses GROUP BY class ORDER BY class""",
      note="Despite the title, the condition is \"at least 5\" (≥)."),
  ],
  remember=["Aggregate conditions go in `HAVING`.", "(student, class) is the PK, so no duplicate enrolments — otherwise use COUNT(DISTINCT student)."],
  pitfalls=["Title says \"more than 5\" but the statement says at least 5 → use `>=`."],
  recall="GROUP BY class HAVING COUNT(student) >= 5.",
),
dict(
  n=27, id=1729, slug="find-followers-count", title="Find Followers Count",
  sec="sortgroup", diff="Easy", concepts=["GROUP BY", "COUNT", "ORDER BY"],
  pattern="Count per key, sorted",
  prompt="For each user, return the number of followers, sorted by user_id ascending.",
  returns="user_id, followers_count (ordered)",
  setup="""
CREATE TABLE Followers (user_id INT, follower_id INT, PRIMARY KEY (user_id, follower_id));
INSERT INTO Followers VALUES (3,1),(1,3),(2,1),(2,3),(2,4),(4,2);
""",
  solution="""
SELECT user_id,
       COUNT(follower_id) AS followers_count
FROM Followers
GROUP BY user_id
ORDER BY user_id;
""",
  alts=[],
  approach=["GROUP BY user, COUNT followers, ORDER BY user_id."],
  steps=[
    dict(t="Group by user", sql="""
SELECT user_id AS _grp, user_id, follower_id FROM Followers ORDER BY user_id, follower_id""",
      note="User 2 has three followers."),
  ],
  remember=["Output order is checked here — add ORDER BY."],
  pitfalls=[],
  recall="GROUP BY user_id, COUNT(follower_id), ORDER BY user_id.",
  ordered=True,
),
dict(
  n=28, id=619, slug="biggest-single-number", title="Biggest Single Number",
  sec="sortgroup", diff="Easy", concepts=["HAVING", "MAX", "NULL on empty"],
  pattern="Aggregate over a filtered set — returns NULL when empty",
  prompt="A **single number** appears exactly once in `MyNumbers`. Return the largest single number, or NULL if there is none.",
  returns="num (one row, possibly NULL)",
  setup="""
CREATE TABLE MyNumbers (num INT);
INSERT INTO MyNumbers VALUES (9),(9),(7),(2),(7),(4),(1),(5),(4);
""",
  solution="""
SELECT MAX(num) AS num
FROM (
  SELECT num
  FROM MyNumbers
  GROUP BY num
  HAVING COUNT(*) = 1
) singles;
""",
  alts=[("Scalar subquery wrapper", """
SELECT (
  SELECT num
  FROM MyNumbers
  GROUP BY num
  HAVING COUNT(*) = 1
  ORDER BY num DESC
  LIMIT 1
) AS num;
""", "A scalar subquery that finds no row yields NULL — the outer SELECT still returns one row.")],
  approach=[
    "Find numbers appearing once: GROUP BY num HAVING COUNT(*) = 1.",
    "Take the max. If there are no singles, the answer must be a single NULL row.",
    "`MAX()` over zero rows returns NULL automatically — that's the trick.",
  ],
  steps=[
    dict(t="Frequency of each number", sql="""
SELECT num, COUNT(*) AS `+freq`, COUNT(*) = 1 AS _keep
FROM MyNumbers GROUP BY num ORDER BY num DESC""",
      note="Singles: 5, 2, 1 → MAX = 5. If all numbers repeated, MAX over nothing = NULL."),
  ],
  remember=[
    "Aggregates (MAX, SUM…) without GROUP BY always return **one** row — NULL if the input is empty.",
    "`ORDER BY … LIMIT 1` on an empty set returns **zero** rows — fails the \"return null\" case unless wrapped.",
  ],
  pitfalls=["`SELECT num … HAVING COUNT(*)=1 ORDER BY num DESC LIMIT 1` alone returns nothing instead of NULL."],
  recall="MAX(num) over (GROUP BY num HAVING COUNT(*)=1) — MAX of empty = NULL.",
),
dict(
  n=29, id=1045, slug="customers-who-bought-all-products", title="Customers Who Bought All Products",
  sec="sortgroup", diff="Medium", concepts=["COUNT(DISTINCT)", "HAVING", "Relational division"],
  pattern="\"Has ALL of X\" → distinct count equals total count",
  prompt="`Customer` (may contain duplicates) lists which product_keys each customer bought. Return the ids of customers who bought **every** product in `Product`.",
  returns="customer_id (any order)",
  setup="""
CREATE TABLE Customer (customer_id INT NOT NULL, product_key INT);
CREATE TABLE Product (product_key INT PRIMARY KEY);
INSERT INTO Product VALUES (10),(20),(30);
INSERT INTO Customer VALUES
(1,10),(1,20),(1,30),(2,10),(2,10),(2,20),(3,30),(3,20),(3,10),(3,10),(4,10),(4,20),(4,20);
""",
  solution="""
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);
""",
  alts=[("Double NOT EXISTS", """
SELECT DISTINCT c.customer_id
FROM Customer c
WHERE NOT EXISTS (
  SELECT 1 FROM Product p
  WHERE NOT EXISTS (
    SELECT 1 FROM Customer c2
    WHERE c2.customer_id = c.customer_id AND c2.product_key = p.product_key
  )
);
""", "\"There is no product this customer didn't buy.\" Classic textbook relational division.")],
  approach=[
    "\"Bought all products\" = the number of different products they bought equals the number of products.",
    "Duplicates exist → COUNT(DISTINCT product_key).",
    "Compare against `(SELECT COUNT(*) FROM Product)` in HAVING.",
  ],
  steps=[
    dict(t="Distinct products per customer vs total", sql="""
SELECT customer_id, COUNT(*) AS `+rows`, COUNT(DISTINCT product_key) AS `+distinct_products`,
       (SELECT COUNT(*) FROM Product) AS total_products,
       COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product) AS _keep
FROM Customer GROUP BY customer_id ORDER BY customer_id""",
      note="Customers 2 and 4 have 3 rows but only 2 distinct products — COUNT(*) would wrongly include them."),
  ],
  remember=["Relational division (\"for all\") ≈ `COUNT(DISTINCT x) = (SELECT COUNT(*) FROM X)`."],
  pitfalls=["`COUNT(product_key)` counts duplicates."],
  recall="GROUP BY customer HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product).",
),
]
