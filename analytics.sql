
-- 1. Overall restaurant performance
SELECT
    COUNT(DISTINCT order_id) AS completed_orders,
    ROUND(SUM(line_revenue), 2) AS total_revenue,
    ROUND(
        SUM(line_revenue) * 1.0 /
        COUNT(DISTINCT order_id), 2
    ) AS average_order_value
FROM clean_sales
WHERE status = 'Completed';


-- 2. Top-selling menu items
SELECT
    item_name,
    SUM(quantity) AS units_sold,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM clean_sales
WHERE status = 'Completed'
GROUP BY item_name
ORDER BY units_sold DESC
LIMIT 10;


-- 3. Revenue by category
SELECT
    category,
    ROUND(SUM(line_revenue), 2) AS revenue
FROM clean_sales
WHERE status = 'Completed'
GROUP BY category
ORDER BY revenue DESC;


-- 4. Daily sales trend
SELECT
    order_date,
    ROUND(SUM(line_revenue), 2) AS daily_revenue
FROM clean_sales
WHERE status = 'Completed'
GROUP BY order_date
ORDER BY order_date;


-- 5. Orders by payment method
SELECT
    payment_method,
    COUNT(DISTINCT order_id) AS total_orders
FROM clean_sales
WHERE status = 'Completed'
GROUP BY payment_method
ORDER BY total_orders DESC;


-- 6. Cancelled orders
SELECT COUNT(*) AS cancelled_orders
FROM orders
WHERE status = 'Cancelled';
