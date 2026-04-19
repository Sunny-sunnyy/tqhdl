import pandas as pd

from data import apply_filters, load_csv


def test_load_csv_returns_dataframe_with_expected_columns():
    df = load_csv()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 64104
    required = {
        "order_number",
        "order_date",
        "customer_name",
        "channel",
        "product_name",
        "quantity",
        "unit_price",
        "revenue",
        "cost",
        "state",
        "state_name",
        "us_region",
        "profit",
        "profit_margin_pct",
        "order_month_name",
        "order_month_num",
        "order_month",
    }
    assert required.issubset(df.columns)


def test_load_csv_parses_order_date_as_datetime():
    df = load_csv()
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])


def test_apply_filters_empty_returns_all(df_full):
    filtered = apply_filters(df_full, {})
    assert len(filtered) == len(df_full)


def test_apply_filters_year(df_full):
    filtered = apply_filters(df_full, {"year": [2017]})
    assert filtered["order_date"].dt.year.unique().tolist() == [2017]


def test_apply_filters_channel(df_full):
    filtered = apply_filters(df_full, {"channel": ["Wholesale"]})
    assert filtered["channel"].unique().tolist() == ["Wholesale"]


def test_apply_filters_region(df_full):
    filtered = apply_filters(df_full, {"us_region": ["West"]})
    assert filtered["us_region"].unique().tolist() == ["West"]


def test_apply_filters_product_multiselect(df_full):
    filtered = apply_filters(
        df_full, {"product_name": ["Product 26", "Product 27"]}
    )
    assert set(filtered["product_name"].unique()) == {"Product 26", "Product 27"}


def test_apply_filters_combined(df_full):
    filtered = apply_filters(
        df_full,
        {"year": [2017], "channel": ["Export"], "us_region": ["West"]},
    )
    assert filtered["order_date"].dt.year.unique().tolist() == [2017]
    assert filtered["channel"].unique().tolist() == ["Export"]
    assert filtered["us_region"].unique().tolist() == ["West"]


def test_apply_filters_empty_list_means_no_filter(df_full):
    filtered = apply_filters(df_full, {"channel": []})
    assert set(filtered["channel"].unique()) == set(df_full["channel"].unique())
