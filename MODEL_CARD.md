# Model Card: Olist Late-Delivery Risk

Last updated: 2026-10-30

## Model details

- Type: logistic regression in one scikit-learn pipeline (cleaning, scaling and encoding learned from the learning period only).
- Clues: 33 (29 number clues and 4 category clues), all known when the order is placed. See DATA_DICTIONARY.md.
- Output: a risk score and a risk band (Low, Medium, High). High = riskiest 10% of scores in the learning period, Medium = next 20%, Low = the rest.
- Files: models/late_delivery_model.joblib and models/settings.json.

## Intended use

- Help an operations team decide which orders to look at first, for example "check the High band each week".
- A demo for learning and for a portfolio.

## Not intended for

- Automatic decisions about customers, such as refusing or cancelling an order.
- Exact probabilities. Use the bands.
- Other countries, other companies or periods far from 2017-2018, without checking again.

## Data

- Olist public dataset (Brazil). 96,470 delivered orders with valid dates, 96,203 used after leaving out 267 orders from 2016.
- Learning period: Jan 2017 - Apr 2018 (70,851 orders). Test period: May - Aug 2018 (25,352 orders), used once.
- Target: late = arrived on a later calendar day than the promised day. Late rate was 5.65% in training months, 10.8% in Jan-Apr 2018 and 4.4% in the test months.
- No personal data about customers is used. Only geography (state, ZIP prefix) and order details.

## Performance on the test period

- ROC-AUC 0.665. PR-AUC 0.092 (a lazy model gets 0.044).
- Riskiest 5% of orders: 3.1x the average late rate, 15.7% of late orders found.
- Riskiest 10% of orders: 2.6x the average late rate, 25.9% of late orders found.

| Band | Orders | Really late | Compared with average |
|---|---|---|---|
| Low | 14,637 | 2.88% | 0.65x |
| Medium | 6,015 | 4.64% | 1.05x |
| High | 4,700 | 8.83% | 2.01x |

Low does not mean safe: about 38% of late orders in the test period were in the Low band.

## Where the model works less well (test period)

- Customers in Sao Paulo state (46% of orders, about half of late orders): only 1.9% of their orders were flagged by the top-10% rule and only 6.8% of their late orders were found.
- Customers in Rio de Janeiro state: the model said 15.7% late on average, the real rate was 4.2%, so it over-warns there.
- Customers in Bahia, Espirito Santo and Pernambuco: 53-63% of late orders were found, but many orders were flagged.
- By month: the top-10% rule found 33.6% of late orders in May 2018 but only 16.5% in August 2018.
- Scores were too high in the calmer test months (riskiest tenth: predicted 35.5%, actual 11.4%).

## Other limitations

- Modest ranking ability. Late delivery also depends on weather, strikes and courier problems, which are unknown when the order is placed.
- The label is for the whole order. Items from different sellers may arrive separately.
- Only the first seller of each order is used for seller clues.
- Some training orders were delivered after the split date, so their outcome was not known on that date.
- Clue effects are associations, not causes.
- It was not tested whether acting on a warning reduces delays.

## Proposed monitoring (not yet in place)

- Each week, compare the real late rate of each band with the test table above.
- Watch the share of orders that land in the High band. A big jump means the late rate or the order mix has changed.
- Retrain, and recalibrate the bands, on the most recent months when the bands stop separating late orders (High no longer clearly above Low).

## Ethical notes

- Location is a clue, so the model can treat regions differently. Use it to prioritise checks and extra help, not to reduce service to a region.
- A human should review flagged orders.
