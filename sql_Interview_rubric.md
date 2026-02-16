# SQL Interview Rubric -- Data Engineering

**WHERE vs HAVING -- Screening + Practical Exercises**

## Overview

This rubric covers a structured SQL screening exercise in four stages. Start with the screening questions (Stages 1-2) for all candidates. Continue to Exercise 1 (junior level). If the candidate performs well, proceed to Exercise 2 (mid level). Each stage builds on the previous one.

**Interview Flow:**

- **Stage 1 -- Screening Question** (5 min): Verbal question about WHERE vs HAVING. 
- **Stage 2 -- Screening Question** (5 min): Verbal question about JOIN row expansion. 
- **Stage 3 -- Exercise 1: Junior** (10-15 min): Write a query using a single table.
- **Stage 4 -- Exercise 2: Mid-Level** (15-20 min): Write a query using two tables with two-level aggregation.

---

## Stage 1 -- Screening Question (All Levels)

> **"Explain the difference between WHERE and HAVING clauses in SQL."**

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **Core concept** | Candidate says WHERE filters individual rows *before* grouping and HAVING filters groups *after* aggregation. They don't need to use these exact words -- any phrasing that shows they understand the timing difference is a pass. Imprecise wording is fine as long as the core idea is correct. | Candidate confuses the two, says they are interchangeable, or cannot explain which one runs first. |
| **Example** | Candidate gives a concrete example without being asked, e.g. "WHERE filters out cancelled orders, HAVING keeps only groups with COUNT > 5." The example doesn't need to be runnable SQL -- a clear verbal description is enough. | Candidate cannot produce any example, even when prompted with "Can you give me a quick example of when you'd use each one?" |
| **Execution order (mid+)** | Candidate explains the logical query execution order (FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY) and can explain *why* you can't put an aggregate like SUM() in a WHERE clause -- because WHERE runs before GROUP BY, so aggregates don't exist yet. Bonus: mentions that WHERE is more efficient because it reduces the dataset before the engine has to do the grouping work. | Candidate only recites "WHERE is for rows, HAVING is for groups" with no deeper reasoning. Acceptable for junior, but insufficient for mid-level -- a mid-level candidate should be able to explain the *why*, not just the *what*. |

### Interviewer Hints

Use these if the candidate gets stuck. Give the gentler hint first; only escalate if they're still struggling.

| Stuck on... | Hint 1 (gentle nudge) | Hint 2 (more direct) |
|---|---|---|
| **Can't articulate the difference at all** | "Think about *when* each clause runs during query execution. One runs early, one runs late -- does that help?" | "WHERE runs before the data is grouped. HAVING runs after. So which one can see aggregate results like SUM or COUNT?" |
| **Can't produce an example** | "Imagine a table of orders with a status column and an amount column. When would you use WHERE, and when would you need HAVING?" | "Say you want to exclude cancelled orders and only show customers whose total spend is over 1,000. Which filter goes where?" |
| **Knows the what but not the why (mid+)** | "What would happen if you tried to write `WHERE SUM(amount) > 1000`? Why wouldn't that work?" | "SQL processes the query in a specific logical order: FROM, then WHERE, then GROUP BY, then HAVING. Since WHERE runs before GROUP BY, the groups haven't been formed yet -- so aggregate functions like SUM don't exist at that point." |

---

## Stage 2 -- Screening Question: JOIN Row Expansion (All Levels)

> **"If you JOIN table A (1,000 rows) to table B (5,000 rows), can the result have more than 5,000 rows? When and why?"**

### Example

**Table: `orders_example` (3 rows)**

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
| **Core concept** | Candidate immediately says "yes" and explains that when multiple rows in table A match multiple rows in table B on the join key, every combination is produced. They might say "duplicates on the join key cause row multiplication" or use terms like "one-to-many" or "many-to-many" -- exact terminology doesn't matter as long as the mechanism is clear. | Candidate says "no, the result can't be larger than the bigger table" or says "it's always capped at 5,000." This is a fundamental misunderstanding of how JOINs work. |
| **Example** | Candidate describes a concrete scenario without being asked, e.g. "if a customer has 3 orders and 2 shipping addresses, joining on customer_id gives 6 rows for that customer." A verbal description is enough -- they don't need to write SQL. | Candidate cannot explain *when* row expansion would happen, even when prompted with "Can you describe a situation where this might occur?" |
| **Depth (mid+)** | Candidate explains the Cartesian product per key value, or mentions real-world consequences like inflated aggregates and double-counting revenue. Bonus: mentions strategies to prevent it -- checking for duplicate keys before joining, using DISTINCT, or verifying the grain of each table. | Candidate gives only a vague "yes, because of duplicates" with no practical insight into why it matters or how to detect it. Acceptable for junior, but insufficient for mid-level. |

### Interviewer Hints

Use these if the candidate gets stuck. Give the gentler hint first; only escalate if they're still struggling.

| Stuck on... | Hint 1 (gentle nudge) | Hint 2 (more direct) |
|---|---|---|
| **Says "no" or is unsure whether the result can exceed 5,000 rows** | "Think about what happens when a single row in table A matches more than one row in table B. How many output rows does that produce?" | "If customer 10 has 3 orders and 2 promos, the JOIN combines every order with every promo for that customer. That's 3 times 2 = 6 rows just for one customer. Scale that up and you can easily exceed both input tables." |
| **Says "yes" but can't explain when or why** | "Can you think of a real-world scenario where one entity has multiple related records in both tables? For example, a customer with multiple orders and multiple addresses." | "Row expansion happens when the join key is not unique on *either* side -- each matching pair produces a row. If customer 10 appears 3 times in A and 2 times in B, you get 3 x 2 = 6 rows for that customer alone." |
| **Understands the mechanism but can't explain consequences (mid+)** | "If this happened in a reporting query, and you ran `SUM(amount)` on the result -- what would go wrong?" | "When rows multiply, any aggregation on the joined result will double-count. For example, if an order appears twice because of two matching promos, that order's amount gets summed twice. This is how revenue numbers get silently inflated." |
| **Can't describe how to prevent it (mid+ bonus)** | "Before running a JOIN in production, what would you check about the join keys?" | "You can check for uniqueness on the join key with `SELECT customer_id, COUNT(*) FROM table GROUP BY customer_id HAVING COUNT(*) > 1`. If you find duplicates, you need to decide whether to deduplicate first or if the many-to-many result is intentional." |

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

Note that order 11 has a NULL amount. `SUM` ignores NULLs, so total_spent is unaffected -- but `COUNT(*)` includes the NULL row, giving customer 102 an order_count of 4 instead of 3. Both counts are defensible: order 11 *is* a completed order (count = 4), it just has no recorded amount (count = 3). The real test is whether the candidate **notices the NULL and can reason about it**, not which count they choose. If they use `COUNT(*)` and get 4, ask: "Order 11 has a NULL amount -- does that affect your results?" A candidate who can explain the SUM/COUNT difference on the spot passes.

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
| 102 | 3 or 4 | 660.00 |

Customer 102's order_count depends on how the candidate handles the NULL amount in order 11. Both `3` (excludes the NULL row) and `4` (counts all completed orders) are acceptable -- see NULL handling criterion below.

### Evaluation

| Criterion | Strong answer | Weak answer |
|-----------|---------------|-------------|
| **WHERE usage** | Candidate's query has `WHERE status = 'completed'` (or equivalent) so that cancelled orders are excluded *before* any grouping happens. This is the correct place for row-level filters -- it means the aggregation only sees the rows that matter. | Candidate puts the status filter inside HAVING (e.g. `HAVING status = 'completed'`) or tries to filter cancelled orders after the aggregation. Look for this in their query: if `status` appears after GROUP BY instead of before it, that's the problem. |
| **HAVING usage** | Candidate uses `HAVING SUM(amount) > 500` to keep only groups whose total exceeds 500. This is the correct clause for filtering on aggregated values. If the candidate instead wraps the query in a subquery and filters with `WHERE total_spent > 500` in the outer query, that's a valid alternative -- but ask them: "Can you rewrite this using HAVING?" They should be able to. | Candidate writes `WHERE SUM(amount) > 500` directly in the main query -- this will throw a syntax error because you can't use aggregate functions in WHERE. If they get this error and can't figure out why, or if they can't rewrite their subquery approach using HAVING when asked, that's a clear gap. |
| **NULL handling** | Row 11 has a NULL amount. The question says "number of orders" which is genuinely ambiguous -- order 11 *is* a completed order, it just has no recorded amount. A strong candidate **notices the NULL unprompted** and either: (1) filters it out (`AND amount IS NOT NULL` or `COUNT(amount)`), or (2) keeps it (`COUNT(*)`) and explains why. Either interpretation is correct. The key signal is awareness: can they explain that `SUM` skips NULLs but `COUNT(*)` doesn't? If customer 102 shows `order_count = 4` and the candidate proactively says "that includes a NULL-amount row -- I'm counting it because it's still a completed order," that's a strong answer. | Candidate doesn't notice the NULL at all. Their query returns `order_count = 4` for customer 102 and they don't question it. If you see this, prompt: "Order 11 has a NULL amount -- does that affect your results?" If they can explain the SUM/COUNT difference, that's a pass. If they can't identify how NULLs interact with aggregate functions even after the prompt, that's a concern. Not a dealbreaker for junior if everything else is solid, but it suggests they don't reason carefully about data quality. |
| **Correct result** | The query returns exactly two rows: customer 101 (order_count = 2, total_spent = 650.00) and customer 102 (order_count = 3 or 4, total_spent = 660.00). No other customers should appear. Customer 103 spent only 360.00 on completed orders (below 500) and customer 104 spent 350.00 (also below). | Result includes customers who shouldn't be there, or the totals are wrong. Common mistakes: including cancelled orders in the sum (inflates totals), forgetting the status filter entirely, or having the wrong HAVING threshold. If the candidate gets the wrong answer, ask them to walk through the data row by row -- this helps you see whether the logic is flawed or they just made a typo. |
| **Code clarity** | Clean formatting, meaningful column aliases (e.g. `order_count`, `total_spent` rather than `count1` or unnamed columns). Query is easy to read at a glance. | Messy formatting, unclear or missing aliases, hard to follow. Not a dealbreaker on its own -- some strong candidates just write sloppy SQL under time pressure. Judge this lightly compared to the other criteria. |

### Interviewer Hints

Use these if the candidate gets stuck. Give the gentler hint first; only escalate if they're still struggling.

| Stuck on... | Hint 1 (gentle nudge) | Hint 2 (more direct) |
|---|---|---|
| **Doesn't know where to start** | "Start by thinking about which rows you need and which you don't. What's the first thing you'd filter out?" | "You only care about completed orders. Try writing a WHERE clause that keeps only those rows, then think about grouping." |
| **Puts status filter in HAVING instead of WHERE** | "Think about whether `status = 'completed'` is a condition on individual rows or on groups. Where should row-level filters go?" | "WHERE filters individual rows *before* grouping. HAVING filters *after* grouping. Since `status` is a property of each row, not of a group, it belongs in WHERE." |
| **Writes `WHERE SUM(amount) > 500` and gets a syntax error** | "Read the error message carefully. It's telling you that aggregate functions can't appear in a certain clause. Which clause *is* designed for filtering on aggregates?" | "You can't use SUM() in WHERE because WHERE runs before GROUP BY -- the groups haven't been formed yet. Move that condition to HAVING, which runs after grouping." |
| **Forgets GROUP BY entirely** | "You need a total per customer. When you want one result row per customer, what SQL clause makes that happen?" | "Add `GROUP BY customer_id` so that SUM and COUNT compute their values within each customer's group of rows." |
| **Gets wrong totals (likely including cancelled orders)** | "Your total for customer 101 seems high. Can you check which rows are being included in the sum?" | "Customer 101 has a cancelled order (order 3, EUR120). Make sure your WHERE clause excludes cancelled orders before the aggregation." |
| **Doesn't notice the NULL in order 11** | Don't hint proactively -- let them finish first. Then ask: "Order 11 has a NULL amount. Does that affect your results?" | "SUM ignores NULLs, so the total is fine. But COUNT(*) counts all rows including NULLs, while COUNT(amount) skips them. Which count did you use, and is the result what you intended?" |
| **Uses a subquery to avoid HAVING** | This is valid -- let them finish. Then say: "That works. Can you rewrite the outer WHERE filter using HAVING instead? I'd like to see that you're comfortable with both approaches." | "Instead of wrapping in a subquery, you can put the aggregate condition directly in HAVING: `HAVING SUM(amount) > 500`. This does the same thing but in a single query level." |

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
        c.customer_id,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name, c.customer_id
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
        c.customer_id,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name, c.customer_id
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
        c.customer_id,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
      AND o.order_date >= '2024-01-01'
      AND o.order_date < '2024-04-01'
    GROUP BY c.region, c.customer_name, c.customer_id
    HAVING SUM(o.amount) >= 300
) AS customer_spend
WHERE region IN (
    SELECT region
    FROM (
        SELECT
            c.region,
            c.customer_id,
            SUM(o.amount) AS total_spent
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'completed'
          AND o.order_date >= '2024-01-01'
          AND o.order_date < '2024-04-01'
        GROUP BY c.region, c.customer_id
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
| **Recognises two-pass problem** | This question cannot be solved with a single GROUP BY. The candidate needs to first group by customer to find who spent >=EUR300, and then group by region to count how many customers qualified. A strong candidate recognises this and uses a CTE (`WITH ... AS`) or a subquery to break the problem into two steps. They should be able to explain *why* a single pass won't work -- you can't filter on "number of qualifying customers per region" and "total spend per customer" in the same GROUP BY. | Candidate tries to solve everything in one query with a single GROUP BY and either gets stuck or produces wrong results. If they're struggling, you can prompt: "Can this be done in one GROUP BY, or do you need to aggregate twice?" If they still can't see the two-step structure, that's a significant gap for mid-level. |
| **JOIN correctness** | Candidate joins orders to customers using `JOIN customers c ON o.customer_id = c.customer_id` (or equivalent). This is a straightforward equi-join -- look for the correct column on both sides. The join should be INNER JOIN (or just JOIN, which defaults to inner). A LEFT JOIN would also produce correct results here since all customer_ids in orders exist in customers, but INNER is more appropriate. | Candidate joins on the wrong columns, uses a cross join by accident (no ON clause), or forgets the join entirely and tries to query both tables separately. If you see a query that references `customers.region` without any JOIN to the customers table, that's the issue. |
| **WHERE placement** | Candidate filters `status = 'completed'` and the date range in the WHERE clause, *before* any aggregation. This is the same principle tested in Stage 3 -- row-level conditions belong in WHERE so that only relevant rows enter the GROUP BY. Look for both the status filter and the date filter appearing before GROUP BY in the query. | Candidate puts `status = 'completed'` or the date filter inside HAVING. This is the same mistake from Stage 3 -- if they didn't learn from it, that's a concern. Technically HAVING can filter on non-aggregated columns in some databases, but it's wrong in principle and may produce unexpected results. |
| **Both filters present** | The query must enforce two filters: (1) per-customer spend >= EUR300, and (2) per-region qualifying customer count >= 2. How these are expressed depends on the approach -- `HAVING` at both levels in a CTE+subquery, `HAVING` + `WHERE` on a window function result, or two `HAVING` clauses in separate CTEs are all valid. The key is that both filters exist and are applied correctly. A strong candidate handles both without prompting. | Candidate gets one level of filtering but misses the other. Typical mistake: they correctly find customers who spent >=EUR300 but then return *all* of them without checking whether the region has >=2 qualifying customers. If their result includes Dave (South, 350.00), they missed the second filter -- South only has 1 qualifying customer and should be excluded. |
| **Date handling** | Candidate correctly restricts to Q1 2024 (January through March). The preferred pattern is `>= '2024-01-01' AND < '2024-04-01'` -- this "half-open interval" is a best practice because it works correctly whether the column is a DATE or a TIMESTAMP. Using `BETWEEN '2024-01-01' AND '2024-03-31'` is also acceptable here since the column is DATE. Do not penalise either approach. | Candidate uses the wrong date range -- for example, includes April data (order 9) or misses March. How to spot this: if Bob appears in the result (he has an April order worth EUR500), the date filter is probably wrong. You can also check: does the candidate's range include `2024-03-31`? If they wrote `< '2024-03-01'`, they've cut off all of March. |
| **Code quality** | Candidate uses a CTE (`WITH ... AS`) to make the two-step logic readable. Each step has a clear name and the overall query reads top to bottom. Meaningful aliases throughout. | Candidate writes deeply nested subqueries where the same logic is repeated in multiple places, making it hard to follow. This is a minor concern on its own -- the logic may still be correct. If they use nested subqueries, it's a good prompt to ask: "Do you know a way to avoid repeating that inner query?" This leads to CTEs and tests whether they know the syntax. |

### Interviewer Hints

Use these if the candidate gets stuck. Give the gentler hint first; only escalate if they're still struggling.

| Stuck on... | Hint 1 (gentle nudge) | Hint 2 (more direct) |
|---|---|---|
| **Doesn't know where to start / overwhelmed by the question** | "There's a lot going on in this question. Try breaking it into smaller pieces. What's the first thing you need to figure out?" | "Start with just one piece: for each customer, calculate their total spend on completed orders in Q1. Don't worry about regions or the 'at least 2 customers' part yet -- just get the per-customer totals first." |
| **Tries to solve it in a single GROUP BY** | "You have two different levels of filtering here: one per customer and one per region. Can both of those live in the same GROUP BY?" | "Think of it as two steps. Step 1: find which customers spent >= EUR300. Step 2: count how many qualifying customers each region has and only keep regions with at least 2. You'll need a subquery or CTE to separate these steps." |
| **Forgets the JOIN to the customers table** | "Where does the region information live? Is it in the orders table?" | "Region is in the customers table, not in orders. You need to JOIN orders to customers on customer_id to bring in the region column." |
| **Gets the date range wrong** | "Q1 means the first quarter -- January through March. Double-check your date boundaries." | "Use `order_date >= '2024-01-01' AND order_date < '2024-04-01'`. The less-than on April 1st catches all of March without accidentally including April." |
| **Gets the per-customer spend right but skips the region filter** | "Look at your results. The question says 'only show regions where at least 2 customers met the threshold.' Does every region in your output satisfy that?" | "South only has Dave as a qualifying customer -- that's fewer than 2, so South should be excluded. You need a second aggregation step that counts qualifying customers per region and filters to >= 2." |
| **Doesn't know CTE syntax** | "Have you used `WITH ... AS` before? It lets you name a query result and reference it like a table in the rest of your query." | "The syntax is: `WITH my_cte AS (SELECT ... FROM ... WHERE ...) SELECT ... FROM my_cte WHERE ...`. Write your per-customer aggregation inside the CTE, then query it to apply the region-level filter." |
| **Result includes Bob (wrong date range or missing status filter)** | "Bob's total looks higher than expected. Can you check which of his orders are included?" | "Bob has an order in April (order 9, EUR500). That's Q2, not Q1. Make sure your date filter excludes it. Also confirm you're excluding cancelled orders." |
| **Result includes Dave / South region** | "How many qualifying customers does South have? Is that enough to meet the requirement?" | "South only has one qualifying customer (Dave, EUR350). The question requires at least 2 qualifying customers per region, so South should be excluded from the final result." |
