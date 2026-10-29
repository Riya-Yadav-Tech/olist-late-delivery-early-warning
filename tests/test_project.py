import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))
from olist_tools import Winsorizer

FORBIDDEN = [
    "order_delivered_customer_date", "order_delivered_carrier_date",
    "delivery_days", "review_score", "delivered_at", "is_late",
]


@pytest.fixture(scope="module")
def settings():
    with open(BASE / "models" / "settings.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def model():
    return joblib.load(BASE / "models" / "late_delivery_model.joblib")


def test_no_forbidden_clues(settings):
    clues = settings["numeric_clues"] + settings["category_clues"]
    assert not any(c in clues for c in FORBIDDEN)


def test_bands_are_in_the_right_order(settings):
    assert settings["cut_medium"] < settings["cut_high"]
    rates = {b["band"]: b["late_rate_pct"] for b in settings["band_stats"]}
    assert rates["Low"] < rates["Medium"] < rates["High"]


def test_typical_order_gets_a_valid_score(model, settings):
    cols = settings["numeric_clues"] + settings["category_clues"]
    X = pd.DataFrame([settings["defaults"]])[cols]
    p = model.predict_proba(X)[0, 1]
    assert 0 <= p <= 1


def test_missing_values_do_not_crash(model, settings):
    cols = settings["numeric_clues"] + settings["category_clues"]
    row = dict(settings["defaults"])
    row["distance_km"] = np.nan
    row["main_category"] = np.nan
    X = pd.DataFrame([row])[cols]
    p = model.predict_proba(X)[0, 1]
    assert 0 <= p <= 1


def test_winsorizer_caps_extreme_values():
    X = np.concatenate([np.arange(100), [10_000]]).reshape(-1, 1)
    out = Winsorizer().fit(X).transform(X)
    assert out.max() < 10_000


def test_time_split_has_no_overlap():
    path = BASE / "data" / "full_v2.pkl"
    if not path.exists():
        pytest.skip("data file not available on this computer")
    full = pd.read_pickle(path)
    assert full["order_id"].is_unique
    learn = full[full["order_purchase_timestamp"] < "2018-05-01"]
    test = full[full["order_purchase_timestamp"] >= "2018-05-01"]
    assert learn["order_purchase_timestamp"].max() < test["order_purchase_timestamp"].min()
