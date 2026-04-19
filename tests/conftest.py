from pathlib import Path

import pandas as pd
import pytest

CSV_PATH = Path(__file__).parent.parent / "Sales_data(EDA Exported).csv"


@pytest.fixture(scope="session")
def df_full() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


@pytest.fixture
def sample_df(df_full) -> pd.DataFrame:
    return df_full.head(100).copy()
