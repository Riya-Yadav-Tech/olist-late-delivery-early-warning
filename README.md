# Olist Late-Delivery Early Warning

Predicts, at the moment an order is placed, how likely it is to arrive after its promised delivery date. Built on the public Olist e-commerce dataset (Brazil, 2016-2018) with a Streamlit demo.

## Why this project

Late deliveries upset customers. An operations team cannot check every order, so the model ranks orders by risk and the team checks the riskiest ones first.

## Data

- Source: Brazilian E-Commerce Public Dataset by Olist (Kaggle), 9 CSV tables. The data is not stored in this repository. Check the dataset license before reusing it.
- 99,441 orders. 96,470 were delivered with valid dates and form the working group.
- Target: late = the order arrived on a later calendar day than the promised day. Overall late rate: 6.77%.
- Reviews were used only for the business story (late orders average 2.3 stars, on-time orders 4.3). They are never a model input, because they are written after delivery.

## Method

1. Audited all tables: missing values, duplicates, key uniqueness, impossible dates.
2. Built one row per order. One-to-many tables (items, payments, geolocation) were summarised before joining, and the row count was checked after every join.
3. Used only clues known when the order is placed: promised days, distance, distance per promised day, seller hand-over deadline, parcel weight and size, price and delivery charge, customer and seller state, product category, payment type, and the recent late rate of the seller and the route. Recent late rates use only orders already delivered before the purchase time (checked with a test).
4. Split by time, not randomly. Learning period: Jan 2017 - Apr 2018 (70,851 orders; Jan-Dec 2017 for training and Jan-Apr 2018 for validation). Test period: May - Aug 2018 (25,352 orders), used once. 267 orders from 2016 were left out because there were too few.
5. Compared a lazy baseline, logistic regression, random forest and LightGBM on the validation period only. The final model is logistic regression, retrained on the whole learning period.

## Results

Validation (Jan - Apr 2018, late rate 10.8%):

| Model | PR-AUC | ROC-AUC |
|---|---|---|
| Lazy baseline | 0.108 | 0.500 |
| Logistic regression (final clues) | 0.234 | 0.695 |
| LightGBM, simple (same clues) | 0.231 | 0.675 |

Random forest scored lower (PR-AUC 0.204, ROC-AUC 0.668) on an earlier clue set.

Held-out test (May - Aug 2018, late rate 4.4%):

- ROC-AUC 0.665 and PR-AUC 0.092 (a lazy model gets 0.044).
- The riskiest 5% of orders were late about 3.1 times as often as average and contained 15.7% of all late orders.
- The riskiest 10% were late about 2.6 times as often as average and contained 25.9% of all late orders.

Risk bands in the app (test period):

| Band | Orders | Really late | Compared with average |
|---|---|---|---|
| Low | 14,637 | 2.88% | 0.65x |
| Medium | 6,015 | 4.64% | 1.05x |
| High | 4,700 | 8.83% | 2.01x |

## What the model learned

The most important clue is how demanding the promise is (distance divided by promised days), followed by promised days and the customer's state. Same-state delivery and parcel weight matter less. The seller's own history was a weak clue. These are patterns, not proven causes.

## Limitations

- Ranking ability is modest (test ROC-AUC 0.66). Late delivery also depends on things unknown at order time, such as weather, strikes and courier problems.
- The percentages are not reliable across periods. In the calmer test months the model's scores were too high (riskiest tenth: predicted 35.5%, actual 11.4%). The app therefore shows bands instead of percentages. The model needs recalibration on recent data.
- The model is weak inside Sao Paulo state: about half of all late orders, but the top-10% rule caught only 6.8% of them.
- It cannot follow month-to-month swings (real late rate from 1.2% to 6.6% in the test months).
- Only about two years of data from one company.
- The label is for the whole order. Items from different sellers may arrive separately. Orders with several sellers are rare (1.3%) and rarely late (1.0%); the reason is unknown.
- Some training orders were delivered after the split date, so their outcome was not yet known on that date. This is a small simplification.
- It was not tested whether acting on a warning actually reduces delays.

## What did not work

- Adding the recent late rate of all orders (14 and 30 days) lowered the scores.
- A random split gave higher scores (LightGBM ROC-AUC 0.74 against 0.67 with a time split), but it is not an honest test of predicting the future.
- Month as a clue misled the tree models, because late months differ between years.

## How to run

    pip install -r requirements.txt
    streamlit run app/app.py

To rebuild the model, download the Olist CSV files into the DATA folder and run the notebooks in order.

## Repository layout

    NOTEBOOK/   notebooks (analysis and packaging)
    DATA/       data files (not included)
    src/        small helper code used by the saved model
    models/     saved model and settings
    app/        Streamlit app
    tests/      automatic checks
