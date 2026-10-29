# Data Dictionary

The model uses 33 clues. All of them are known when the order is placed. Source tables are from the Olist dataset.

## Target

| Name | Meaning |
|---|---|
| is_late | 1 if the order arrived on a later calendar day than the promised day, otherwise 0. Only delivered orders with valid dates are used. |

## Clues: timing and promise

| Name | Meaning | Source |
|---|---|---|
| purchase_dow | Day of the week of the purchase (0 = Monday) | orders |
| purchase_hour | Hour of the purchase | orders |
| is_weekend | 1 if bought on Saturday or Sunday | orders |
| promise_days | Days from the purchase day to the promised delivery day | orders |
| days_to_first_limit | Days from purchase to the earliest seller hand-over deadline in the order | order items |
| days_to_last_limit | Days from purchase to the latest seller hand-over deadline in the order | order items |
| courier_window_days | Days between the last seller deadline and the promised delivery date | orders, order items |

## Clues: location

| Name | Meaning | Source |
|---|---|---|
| distance_km | Straight-line distance between seller and customer. One median map point per ZIP prefix, points outside Brazil removed | sellers, customers, geolocation |
| km_per_promised_day | distance_km divided by promise_days. How demanding the promise is | derived |
| same_state | 1 if seller and customer are in the same state | derived |
| customer_state | Customer's state | customers |
| seller_state | State of the order's first seller | sellers |

## Clues: order contents

| Name | Meaning | Source |
|---|---|---|
| n_items | Number of items in the order | order items |
| n_products | Number of different products | order items |
| n_sellers | Number of different sellers | order items |
| multi_seller | 1 if the order has more than one seller | derived |
| total_price | Sum of item prices | order items |
| total_freight | Sum of delivery charges | order items |
| freight_ratio | total_freight divided by (total_price + 1) | derived |
| total_weight_g | Sum of product weights in grams | products |
| max_weight_g | Weight of the heaviest product | products |
| total_volume_cm3 | Sum of product volumes (length x height x width) | products |
| density_g_per_cm3 | total_weight_g divided by total_volume_cm3 | derived |
| main_category | Category of the order's first product (Portuguese name; the app shows English) | products, translation |

## Clues: payment

| Name | Meaning | Source |
|---|---|---|
| n_payments | Number of payment records | order payments |
| total_payment | Total value paid | order payments |
| max_installments | Largest number of installments | order payments |
| main_payment_type | Type of the first payment | order payments |

## Clues: recent history (past delivered orders only)

| Name | Meaning |
|---|---|
| seller_prev_orders | Earlier orders of the same seller that were already delivered before this purchase |
| seller_prev_late | How many of those were late |
| seller_late_rate_smooth | (late + 10 x average late rate) divided by (orders + 10). The average comes from the training period only |
| seller_90d_rate | Smoothed late rate of the seller's orders delivered in the 90 days before this purchase |
| route_60d_rate | Smoothed late rate of the same seller state to customer state route in the 60 days before this purchase |

## Never used as clues

- Actual delivery dates, delivery duration, carrier hand-over date, order status.
- Reviews (written after delivery).
- IDs, exact dates and ZIP codes.
- Month of purchase (removed because it misled the tree models).

## How missing values are handled

Inside the model pipeline, with limits learned from the learning period only: numbers are capped at the 1st and 99th percentile, filled with the median (plus a "was missing" flag), and scaled. Missing categories become "unknown". Categories with fewer than 100 orders are grouped together.
