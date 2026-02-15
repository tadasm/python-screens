# SQL Interview Rubric -- Data Engineering

**WHERE vs HAVING -- Screening + Practical Exercises**

## Overview

This rubric covers a structured SQL screening exercise in four stages. Start with the screening questions (Stages 1-2) for all candidates. Continue to Exercise 1 (junior level). If the candidate performs well, proceed to Exercise 2 (mid level). Each stage builds on the previous one.

**Interview Flow:**

- **Stage 1 -- Screening Question** (5 min): Verbal question about WHERE vs HAVING. 
- **Stage 2 -- Screening Question** (5 min): Verbal question about JOIN row expansion. 
- **Stage 3 -- Exercise 1: Junior** (10-15 min): Write a query using a single table. Candidate uses their own DB tool.
- **Stage 4 -- Exercise 2: Mid-Level** (15-20 min): Write a query using two tables with two-level aggregation.

---

## Stage 1 -- Screening Question (All Levels)

> **"Explain the difference between WHERE and HAVING clauses in SQL."**

### Expected Answers by Level

| Level | What to look for |
|-------|-----------------|
| **Junior** | Articulates the basic distinction: WHERE filters rows before grouping, HAVING filters groups after aggregation. Can give a simple example using COUNT or SUM. Imprecise wording is acceptable if the core concept is correct. |
| **Mid-Level** | Explains the logical query execution order (FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY). Explains why WHERE cannot reference aggregates. Mentions the performance implication: WHERE reduces the dataset before aggregation, making it more efficient than equivalent filtering in HAVING. |

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **Core concept** | Correctly distinguishes row-level vs group-level filtering. | Confuses the two or says they are interchangeable. |
| **Example quality** | Gives a concrete example without prompting. | Cannot produce an example when asked. |
| **Depth (mid+)** | Mentions execution order or performance implications. | Only gives textbook definition with no practical insight. |

---

## Stage 2 -- Screening Question: JOIN Row Expansion (All Levels)

> **"If you JOIN table A (1,000 rows) to table B (5,000 rows), can the result have more than 5,000 rows? When and why?"**

### Expected Answers by Level

| Level | What to look for |
|-------|-----------------|
| **Junior** | Says yes, it can. Explains that duplicate keys cause rows to multiply -- each matching pair produces a row. May use terms like "many-to-many" or "one-to-many" even if imprecisely. Imprecise wording is acceptable if they grasp that duplicates on the join key cause row expansion. |
| **Mid-Level** | Clearly distinguishes join types (INNER, LEFT, CROSS). Explains that a many-to-many relationship on the join key produces a Cartesian product *per key value*, so the result size is the sum of (count_A × count_B) for each key. May mention real-world consequences such as inflated aggregates or double-counting. May mention how to detect or prevent it (e.g. checking for duplicate keys before joining, using DISTINCT, or adding a grain constraint). |

### Example

**Table: `orders` (3 rows)**

| order_id | customer_id |
|----------|-------------|
| 1        | 10          |
| 2        | 10          |
| 3        | 10          |

**Table: `promos` (2 rows)**

| promo_id | customer_id | discount |
|----------|-------------|----------|
| 1        | 10          | 5%       |
| 2        | 10          | 10%      |

### DDL

```sql
CREATE TABLE orders_example (
    order_id    INT PRIMARY KEY,
    customer_id INT NOT NULL
);

CREATE TABLE promos (
    promo_id    INT PRIMARY KEY,
    customer_id INT NOT NULL,
    discount    VARCHAR(10) NOT NULL
);

INSERT INTO orders_example (order_id, customer_id) VALUES
(1, 10),
(2, 10),
(3, 10);

INSERT INTO promos (promo_id, customer_id, discount) VALUES
(1, 10, '5%'),
(2, 10, '10%');
```

### Sample Query

```sql
SELECT o.order_id, o.customer_id, p.promo_id, p.discount
FROM orders_example o
JOIN promos p ON o.customer_id = p.customer_id;
```

**Result: 6 rows** (exceeds both tables)

| order_id | customer_id | promo_id | discount |
|----------|-------------|----------|----------|
| 1        | 10          | 1        | 5%       |
| 1        | 10          | 2        | 10%      |
| 2        | 10          | 1        | 5%       |
| 2        | 10          | 2        | 10%      |
| 3        | 10          | 1        | 5%       |
| 3        | 10          | 2        | 10%      |

Each of the 3 orders matches each of the 2 promos on `customer_id = 10`, producing 3 × 2 = 6 rows -- more than either input table.

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **Core concept** | Correctly identifies that duplicate join keys cause row multiplication. | Says the result is always capped at the size of the larger table, or says "no" outright. |
| **Example quality** | Can describe a scenario where this happens (e.g. "if a customer has multiple orders and multiple addresses"). | Cannot explain *when* it would happen. |
| **Depth (mid+)** | Mentions Cartesian product per key value, real-world consequences like inflated aggregates, or strategies to detect/prevent it. | Only gives a vague "yes, duplicates" with no practical insight. |

---

## Stage 3 -- Exercise 1: Junior Level

*Share the DDL statements below with the candidate. They should load the data into their database tool and write the query live.*

### Sample Table: `orders`

| order_id | customer_id | order_date | product_category | amount | status |
|----------|-------------|------------|------------------|--------|-----------|
| 1 | 101 | 2024-01-15 | Electronics | 250.00 | completed |
| 2 | 102 | 2024-01-20 | Electronics | 75.00 | completed |
| 3 | 101 | 2024-02-10 | Clothing | 120.00 | cancelled |
| 4 | 103 | 2024-02-14 | Electronics | 300.00 | completed |
| 5 | 102 | 2024-03-01 | Clothing | 85.00 | completed |
| 6 | 101 | 2024-03-05 | Electronics | 400.00 | completed |
| 7 | 103 | 2024-03-12 | Clothing | 60.00 | completed |
| 8 | 104 | 2024-03-15 | Electronics | 350.00 | completed |
| 9 | 102 | 2024-04-01 | Electronics | 500.00 | completed |
| 10 | 103 | 2024-04-10 | Clothing | 90.00 | cancelled |
| 11 | 102 | 2024-02-15 | Electronics | NULL | completed |

### DDL -- Share with Candidate

```sql
CREATE TABLE orders (
    order_id        INT PRIMARY KEY,
    customer_id     INT NOT NULL,
    order_date      DATE NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    amount          DECIMAL(10,2),
    status          VARCHAR(20) NOT NULL
);

INSERT INTO orders (order_id, customer_id, order_date, product_category, amount, status) VALUES
(1,  101, '2024-01-15', 'Electronics', 250.00, 'completed'),
(2,  102, '2024-01-20', 'Electronics',  75.00, 'completed'),
(3,  101, '2024-02-10', 'Clothing',    120.00, 'cancelled'),
(4,  103, '2024-02-14', 'Electronics', 300.00, 'completed'),
(5,  102, '2024-03-01', 'Clothing',     85.00, 'completed'),
(6,  101, '2024-03-05', 'Electronics', 400.00, 'completed'),
(7,  103, '2024-03-12', 'Clothing',     60.00, 'completed'),
(8,  104, '2024-03-15', 'Electronics', 350.00, 'completed'),
(9,  102, '2024-04-01', 'Electronics', 500.00, 'completed'),
(10, 103, '2024-04-10', 'Clothing',     90.00, 'cancelled'),
(11, 102, '2024-02-15', 'Electronics',   NULL, 'completed');
```

### Question

> **"Find all customers who have spent more than EUR500 in total on completed orders. Return the customer_id, the number of orders, and the total amount spent."**

### Expected Answer

Note that order 11 has a NULL amount. `SUM` ignores NULLs, so total_spent is unaffected -- but `COUNT(*)` includes the NULL row, inflating the order count for customer 102 (4 instead of 3). The candidate should handle this by filtering NULLs in WHERE or by using `COUNT(amount)` instead of `COUNT(*)`.

```sql
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent
FROM orders
WHERE status = 'completed'
  AND amount IS NOT NULL
GROUP BY customer_id
HAVING SUM(amount) > 500;
```

Using `COUNT(amount)` without the WHERE filter is equally correct:

```sql
SELECT
    customer_id,
    COUNT(amount) AS order_count,
    SUM(amount) AS total_spent
FROM orders
WHERE status = 'completed'
GROUP BY customer_id
HAVING SUM(amount) > 500;
```

A candidate may avoid HAVING entirely by wrapping the aggregation in a subquery and filtering in the outer WHERE. This is valid and produces the correct result. If they take this route, ask them to rewrite it using HAVING to confirm they understand the clause.

```sql
SELECT *
FROM (
    SELECT
        customer_id,
        COUNT(amount) AS order_count,
        SUM(amount) AS total_spent
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
) sub
WHERE total_spent > 500;
```

### Expected Result

| customer_id | order_count | total_spent |
|-------------|-------------|-------------|
| 101 | 2 | 650.00 |
| 102 | 3 | 660.00 |

**Common mistake** -- if the candidate uses `COUNT(*)` without filtering NULLs, customer 102 shows `order_count = 4` instead of 3. The total_spent is still correct (660.00) because SUM ignores NULLs.

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **WHERE usage** | Filters `status = 'completed'` in WHERE (before aggregation). | Puts status filter in HAVING or filters after grouping. |
| **HAVING usage** | Uses `HAVING SUM(amount) > 500` for post-aggregation filter. If the candidate uses a subquery to avoid HAVING (see answer above), ask them to rewrite using HAVING. | Tries `WHERE SUM(amount) > 500` directly on the grouped query (syntax error), or cannot produce a HAVING version when asked. |
| **NULL handling** | Notices the NULL amount and handles it -- either filters `amount IS NOT NULL` in WHERE, or uses `COUNT(amount)` instead of `COUNT(*)`. Bonus: explains why SUM ignores NULLs but COUNT(*) does not. | Does not notice the NULL at all, even after seeing a suspicious order_count of 4 for customer 102. |
| **Correct result** | Returns customers 101 and 102 with correct counts and totals. | Includes cancelled orders in count/sum or wrong totals. |
| **Code clarity** | Clean formatting, meaningful aliases. | Messy or unreadable. Not a dealbreaker on its own. |

---

## Stage 4 -- Exercise 2: Mid-Level

*This exercise adds a second table and requires two-level aggregation. Only proceed here if the candidate passed Stage 3. Share the additional DDL with the candidate.*

### Additional Table: `customers`

| customer_id | customer_name | region |
|-------------|---------------|--------|
| 101 | Alice | North |
| 102 | Bob | South |
| 103 | Carol | North |
| 104 | Dave | South |

### DDL -- Share with Candidate

```sql
-- Add this to the existing database with the orders table

CREATE TABLE customers (
    customer_id   INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    region        VARCHAR(50) NOT NULL
);

INSERT INTO customers (customer_id, customer_name, region) VALUES
(101, 'Alice', 'North'),
(102, 'Bob',   'South'),
(103, 'Carol', 'North'),
(104, 'Dave',  'South');
```

### Question

> **"For each region, find customers who spent EUR300 or more on completed orders in Q1 2024 (January-March). Then, only show regions where at least 2 different customers met that threshold. Return the region, customer name, and their total spend."**

### Why This Is Mid-Level

The candidate must recognise this cannot be solved in a single GROUP BY. There are two filtering stages: first aggregate per customer per region to find who qualifies, then filter on how many customers per region met the threshold. This requires a CTE or subquery. The JOIN to the customers table adds a practical element that reflects real data modelling.

### Expected Answer

Any approach that produces correct results and demonstrates awareness of the two-pass requirement is acceptable. Below is one solution using a CTE with a subquery. Alternatives include window functions (e.g. `COUNT(*) OVER (PARTITION BY region)`), self-joins, or nested subqueries. Do not penalise a candidate for choosing a different approach.

**Approach A -- CTE + subquery:**

```sql
WITH customer_region_spend AS (
    SELECT
        c.region,
        c.customer_name,
        c.customer_id,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name, c.customer_id
    HAVING SUM(o.amount) >= 300
)
SELECT
    region,
    customer_name,
    total_spent
FROM customer_region_spend
WHERE region IN (
    SELECT region
    FROM customer_region_spend
    GROUP BY region
    HAVING COUNT(*) >= 2
)
ORDER BY region, total_spent DESC;
```

**Approach B -- Window function:**

```sql
WITH customer_region_spend AS (
    SELECT
        c.region,
        c.customer_name,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name
    HAVING SUM(o.amount) >= 300
),
with_count AS (
    SELECT
        region,
        customer_name,
        total_spent,
        COUNT(*) OVER (PARTITION BY region) AS customers_in_region
    FROM customer_region_spend
)
SELECT region, customer_name, total_spent
FROM with_count
WHERE customers_in_region >= 2
ORDER BY region, total_spent DESC;
```

**Approach C -- Two CTEs + JOIN:**

Materialises qualifying regions in a second CTE and JOINs back. Some candidates find this more readable than WHERE IN.

```sql
WITH customer_spend AS (
    SELECT
        c.region,
        c.customer_name,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name
    HAVING SUM(o.amount) >= 300
),
qualifying_regions AS (
    SELECT region
    FROM customer_spend
    GROUP BY region
    HAVING COUNT(*) >= 2
)
SELECT cs.region, cs.customer_name, cs.total_spent
FROM customer_spend cs
JOIN qualifying_regions qr ON cs.region = qr.region
ORDER BY cs.region, cs.total_spent DESC;
```

**Approach D -- Nested subqueries (no CTE):**

Valid but less readable because the inner query is repeated. If a candidate writes this, it works -- but it is a good prompt to ask whether they know of a way to avoid the duplication (leading to CTEs).

```sql
SELECT region, customer_name, total_spent
FROM (
    SELECT
        c.region,
        c.customer_name,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name
    HAVING SUM(o.amount) >= 300
) AS customer_spend
WHERE region IN (
    SELECT region
    FROM (
        SELECT
            c.region,
            c.customer_name,
            SUM(o.amount) AS total_spent
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'completed'
          AND o.order_date >= '2024-01-01'
          AND o.order_date < '2024-04-01'
        GROUP BY c.region, c.customer_name
        HAVING SUM(o.amount) >= 300
    ) AS qualified
    GROUP BY region
    HAVING COUNT(*) >= 2
)
ORDER BY region, total_spent DESC;
```

### Step-by-Step Walkthrough

**Step 1 -- Completed orders in Q1 2024 (after WHERE, before aggregation):**

| order_id | customer_id | region | amount |
|----------|-------------|--------|--------|
| 1 | 101 | North | 250.00 |
| 2 | 102 | South | 75.00 |
| 4 | 103 | North | 300.00 |
| 5 | 102 | South | 85.00 |
| 6 | 101 | North | 400.00 |
| 7 | 103 | North | 60.00 |
| 8 | 104 | South | 350.00 |
| 11 | 102 | South | NULL |

*Orders 3 and 10 excluded (cancelled). Order 9 excluded (April). Order 11 included (completed, Q1) but has NULL amount -- SUM ignores it, so Bob's total is unaffected.*

**Step 2 -- Aggregate per customer per region, keep >=EUR300:**

| region | customer_name | total_spent |
|--------|---------------|-------------|
| North | Alice | 650.00 |
| North | Carol | 360.00 |
| South | Dave | 350.00 |

*Bob: EUR75 + EUR85 = EUR160 (below threshold). Dave: EUR350 (meets threshold).*

**Step 3 -- Which regions have >=2 qualifying customers?**

- North has 2 qualifying customers (Alice and Carol) (yes)
- South has 1 qualifying customer (Dave) (no -- needs at least 2)

### Expected Result

| region | customer_name | total_spent |
|--------|---------------|-------------|
| North | Alice | 650.00 |
| North | Carol | 360.00 |

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **Recognises two-pass problem** | Uses CTE or subquery; explains why single GROUP BY won't work. | Tries to solve in one pass and gets stuck or produces wrong results. |
| **JOIN correctness** | Correctly joins orders to customers on customer_id. | Incorrect join condition or misses the join entirely. |
| **WHERE placement** | Status and date filters in WHERE (row-level, before aggregation). | Puts row-level filters in HAVING. |
| **HAVING at both levels** | HAVING for >=EUR300 per customer, HAVING for >=2 customers per region. | Misses one of the two aggregation levels. |
| **Date handling** | Correct date range. Preferred pattern is `>= '2024-01-01' AND < '2024-04-01'` (half-open interval) because it is safe for both DATE and TIMESTAMP columns. `BETWEEN '2024-01-01' AND '2024-03-31'` is acceptable since the column is DATE, but note BETWEEN would silently miss rows after midnight on March 31 if the column were TIMESTAMP. | Wrong date range (e.g. includes April or misses March). |
| **Code quality** | Uses CTE over nested subqueries (readability). Meaningful aliases. | Deeply nested subqueries that are hard to follow. Minor concern on its own. |
