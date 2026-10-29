import json, sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

st.set_page_config(page_title="Olist Late-Delivery Risk")


@st.cache_resource
def load():
    model = joblib.load(BASE / "models" / "late_delivery_model.joblib")
    with open(BASE / "models" / "settings.json") as f:
        settings = json.load(f)
    return model, settings


model, S = load()
D = S["defaults"]

FRIENDLY = {
    "distance_km": "Distance and speed needed to meet the promise",
    "km_per_promised_day": "Distance and speed needed to meet the promise",
    "promise_days": "Promised delivery time",
    "courier_window_days": "Time left for the courier",
    "days_to_last_limit": "Seller hand-over deadline",
    "days_to_first_limit": "Seller hand-over deadline",
    "same_state": "Seller and customer in the same state",
    "customer_state": "Customer state",
    "seller_state": "Seller state",
    "main_category": "Product category",
    "main_payment_type": "Payment type",
    "total_weight_g": "Parcel weight",
    "max_weight_g": "Parcel weight",
    "total_volume_cm3": "Parcel size",
    "total_price": "Price and delivery charge",
    "total_freight": "Price and delivery charge",
    "freight_ratio": "Price and delivery charge",
    "total_payment": "Price and delivery charge",
    "route_60d_rate": "Route's recent late rate",
    "seller_90d_rate": "Seller's recent late rate",
    "n_items": "Number of items",
    "n_products": "Number of items",
}


def group_name(col):
    return FRIENDLY.get(col, col.replace("_", " "))


def to_dense(x):
    return x.toarray() if hasattr(x, "toarray") else np.asarray(x)


try:
    with open(BASE / "models" / "category_translation.json", encoding="utf-8") as f:
        NAMES = json.load(f)
except Exception:
    NAMES = {}


def show_name(value):
    return NAMES.get(value, str(value).replace("_", " "))


def pick(label, key):
    options = S["choices"][key]
    default = D[key]
    index = options.index(default) if default in options else 0
    return st.selectbox(label, options, index=index, format_func=show_name)


st.title("Olist Late-Delivery Early Warning")
st.caption(
    "Demo built on Olist data (Brazil, 2017-2018). It shows patterns, not causes, "
    "and it has not been tested as a way to prevent delays."
)

left, right = st.columns(2)
with left:
    customer_state = pick("Customer state", "customer_state")
    seller_state = pick("Seller state", "seller_state")
    category = pick("Product category", "main_category")
    payment = pick("Payment type", "main_payment_type")
    n_items = st.number_input("Number of items", min_value=1, max_value=10, value=1)
with right:
    distance = st.slider("Distance seller to customer (km)", 0, 3500, int(D["distance_km"]), step=10)
    promise = st.slider("Promised delivery time (days)", 3, 60, int(min(max(D["promise_days"], 3), 60)))
    handover = st.slider(
        "Seller hand-over deadline (days after purchase)",
        1.0, 30.0, float(min(max(round(D["days_to_last_limit"], 1), 1.0), 30.0)), step=0.5,
    )
    weight = st.number_input("Total parcel weight (grams)", min_value=0.0, value=float(D["total_weight_g"]), step=100.0)
    price = st.number_input("Total product price", min_value=0.0, value=float(D["total_price"]), step=10.0)
    freight = st.number_input("Delivery charge (freight)", min_value=0.0, value=float(D["total_freight"]), step=1.0)

with st.expander("Advanced: recent late rates from past delivered orders"):
    seller_rate = st.slider("Seller's late rate, last 90 days (%)", 0.0, 50.0,
                            float(min(round(D["seller_90d_rate"] * 100, 1), 50.0)), step=0.5)
    route_rate = st.slider("Route's late rate, last 60 days (%)", 0.0, 50.0,
                           float(min(round(D["route_60d_rate"] * 100, 1), 50.0)), step=0.5)

row = dict(D)
row.update({
    "customer_state": customer_state,
    "seller_state": seller_state,
    "main_category": category,
    "main_payment_type": payment,
    "n_items": float(n_items),
    "n_products": float(n_items),
    "distance_km": float(distance),
    "promise_days": float(promise),
    "km_per_promised_day": distance / promise,
    "days_to_last_limit": handover,
    "days_to_first_limit": handover,
    "courier_window_days": promise - handover,
    "same_state": float(customer_state == seller_state),
    "total_weight_g": weight,
    "max_weight_g": weight / n_items,
    "total_price": price,
    "total_freight": freight,
    "freight_ratio": freight / (price + 1),
    "total_payment": price + freight,
    "seller_90d_rate": seller_rate / 100,
    "route_60d_rate": route_rate / 100,
})

cols = S["numeric_clues"] + S["category_clues"]
X = pd.DataFrame([row])[cols]
X0 = pd.DataFrame([D])[cols]

score = float(model.predict_proba(X)[0, 1])
if score >= S["cut_high"]:
    band = "High"
elif score >= S["cut_medium"]:
    band = "Medium"
else:
    band = "Low"
stats = {b["band"]: b for b in S["band_stats"]}[band]

st.divider()
st.subheader("Risk band: " + band)
text = (
    f"In the test months (May to Aug 2018), orders in this band were late "
    f"{stats['late_rate_pct']}% of the time, about {stats['times_average']} times the "
    f"overall average of {S['test_late_rate'] * 100:.1f}%."
)
if band == "High":
    st.warning(text)
    st.write("Suggested action: consider a manual check. Confirm that the seller hands the parcel "
             "to the courier on time and that the promised date is realistic. "
             "We have not tested whether this action prevents delays.")
elif band == "Medium":
    st.info(text)
    st.write("Suggested action: keep normal monitoring.")
else:
    st.success(text)
    st.write("Suggested action: normal handling. Low risk does not mean no risk, "
             "because some late orders are also found in this band.")

prep = model.named_steps["prep"]
coef = model.named_steps["model"].coef_[0]
names = prep.get_feature_names_out()
delta = to_dense(prep.transform(X))[0] - to_dense(prep.transform(X0))[0]
contrib = coef * delta

groups = {}
for name, value in zip(names, contrib):
    clean = name.split("__", 1)[1].replace("missingindicator_", "")
    base = clean
    for c in S["category_clues"]:
        if clean.startswith(c + "_"):
            base = c
            break
    label = group_name(base)
    groups[label] = groups.get(label, 0.0) + float(value)

top = sorted(groups.items(), key=lambda kv: abs(kv[1]), reverse=True)[:4]
top = [kv for kv in top if abs(kv[1]) > 0.01]

st.markdown("**What moves this score compared with a typical order**")
if not top:
    st.write("This order looks like a typical order, so no factor stands out.")
else:
    lines = []
    for label, value in top:
        lines.append("- " + label + ": " + ("raises risk" if value > 0 else "lowers risk"))
    st.markdown("\n".join(lines))

with st.expander("Technical details"):
    st.write(f"Raw model score: {score:.3f} (High starts at {S['cut_high']:.3f}, "
             f"Medium at {S['cut_medium']:.3f}).")
    st.write("The raw score is not a true percentage. In the newest months the model's "
             "scores were higher than the real late rates, so use the band instead.")
    st.write("Model: logistic regression trained on orders from " + S["train_period"] +
             " and tested on " + S["test_period"] + ".")

st.caption("Limits: one country, two years of data, purchase-time information only. "
           "Clues that are not shown here are filled with typical values.")
