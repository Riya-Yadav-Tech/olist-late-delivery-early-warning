# ⏱️ Olist Late-Delivery Early Warning

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://olist-late-delivery-riya.streamlit.app)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-02569B?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

Predicts, **at the moment an order is placed**, how likely it is to arrive after its promised delivery date. Built on the public Olist e-commerce dataset (Brazil, 2016–2018), with an interactive Streamlit app.

---

## 🔑 Key Results at a Glance

| Metric (held-out test, May–Aug 2018) | Value |
|---|---|
| Orders analyzed | **96,470** delivered orders |
| Riskiest **10%** of orders | late **2.6×** more often than average, holding **25.9%** of all late orders |
| Riskiest **5%** of orders | late **3.1×** more often than average, holding **15.7%** of all late orders |
| PR-AUC | **0.092** (2× the 0.044 baseline) |
| ROC-AUC | **0.665** |
| Validation strategy | **Time-based split**, so no future data leaks into training |

---

## 💼 Why This Project

Late deliveries upset customers: late orders average **2.3★** reviews against **4.3★** for on-time orders. An operations team cannot check every order, so the model **ranks orders by risk** and the team checks the riskiest ones first.

---

## 📂 Data

- **Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle), 9 CSV tables. The data is not stored in this repository; check the dataset license before reusing it.
- **99,441** orders, of which **96,470** were delivered with valid dates and form the working group.
- **Target:** *late* = the order arrived on a later calendar day than the promised day. Overall late rate: **6.77%**.
- Reviews were used only for the business story. They are **never a model input**, because they are written after delivery.
- 📖 See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) and [`MODEL_CARD.md`](MODEL_CARD.md) for details.

---

## 🔄 Method

1. **Audited** all tables: missing values, duplicates, key uniqueness and impossible dates.
2. **Built one row per order.** One-to-many tables (items, payments, geolocation) were summarised before joining, and the row count was checked after every join.
3. **Used only clues known when the order is placed:** promised days, distance, distance per promised day, seller hand-over deadline, parcel weight and size, price and delivery charge, customer and seller state, product category, payment type, and the recent late rate of the seller and the route. Recent late rates use only orders already delivered before the purchase time (checked with a test).
4. **Split by time, not randomly.**
   - Learning period: Jan 2017 – Apr 2018 (70,851 orders; Jan–Dec 2017 for training, Jan–Apr 2018 for validation)
   - Test period: May – Aug 2018 (25,352 orders), used once
   - 267 orders from 2016 were left out because there were too few
5. **Compared models** on the validation period only: a lazy baseline, logistic regression, random forest and LightGBM. The final model is **logistic regression**, retrained on the whole learning period.

---

## 📊 Results

**Validation** (Jan – Apr 2018, late rate 10.8%):

| Model | PR-AUC | ROC-AUC |
|---|---|---|
| Lazy baseline | 0.108 | 0.500 |
| **Logistic regression (final clues)** | **0.234** | **0.695** |
| LightGBM, simple (same clues) | 0.231 | 0.675 |

Random forest scored lower (PR-AUC 0.204, ROC-AUC 0.668) on an earlier clue set.

**Risk bands in the app** (test period):

| Band | Orders | Really late | Compared with average |
|---|---|---|---|
| 🟢 Low | 14,637 | 2.88% | 0.65× |
| 🟡 Medium | 6,015 | 4.64% | 1.05× |
| 🔴 High | 4,700 | 8.83% | 2.01× |

---

## 🧠 What the Model Learned

The most important clue is **how demanding the promise is** (distance divided by promised days), followed by promised days and the customer's state. Same-state delivery and parcel weight matter less. The seller's own history was a weak clue. These are patterns, not proven causes.

---

## ⚠️ Limitations

- Ranking ability is modest (test ROC-AUC 0.66). Late delivery also depends on things unknown at order time, such as weather, strikes and courier problems.
- The percentages are not reliable across periods. In the calmer test months the model's scores were too high (riskiest tenth: predicted 35.5%, actual 11.4%). The app therefore shows **bands instead of percentages**, and the model needs recalibration on recent data.
- The model is weak inside São Paulo state, which has about half of all late orders: the top-10% rule caught only 6.8% of them.
- It cannot follow month-to-month swings (the real late rate ranged from 1.2% to 6.6% in the test months).
- It uses only about two years of data from one company.
- The label is for the whole order, but items from different sellers may arrive separately. Orders with several sellers are rare (1.3%) and rarely late (1.0%); the reason is unknown.
- Some training orders were delivered after the split date, so their outcome was not yet known on that date. This is a small simplification.
- It was not tested whether acting on a warning actually reduces delays.

---

## 🧪 What Did Not Work

- Adding the recent late rate of all orders (14 and 30 days) **lowered** the scores.
- A random split gave higher scores (LightGBM ROC-AUC 0.74 against 0.67 with a time split), but it is **not an honest test** of predicting the future.
- Using the month as a clue misled the tree models, because the late months differ between years.

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
```

```bash
streamlit run app/app.py
```

```bash
pytest tests/
```

To rebuild the model, download the Olist CSV files into the `DATA/` folder and run the notebooks in `NOTEBOOK/` in order.

---

## 📁 Repository Layout

```
olist-late-delivery-early-warning/
│
├── NOTEBOOK/            # Analysis (01) and model packaging (02) notebooks
├── DATA/                # Olist CSV files (not included)
├── src/                 # Helper code used by the saved model
├── models/              # Saved model and settings
├── app/                 # Streamlit app
├── tests/               # Automatic checks
├── DATA_DICTIONARY.md
├── MODEL_CARD.md
└── requirements.txt
```

---

## 👩‍💻 Author

**Riya Yadav** | B.Tech, Production & Industrial Engineering, NIT Jamshedpur
[LinkedIn](https://www.linkedin.com/in/riya-yadav-2b5688378) · [GitHub](https://github.com/Riya-Yadav-Tech)
