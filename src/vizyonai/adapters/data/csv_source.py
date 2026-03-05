from pathlib import Path

import pandas as pd

from vizyonai.config.settings import DATA_PRODUCTS_PATH, DATA_PHONES_PATH

REQUIRED_PRODUCT_COLUMNS = {"kategori", "port", "watt", "stok_kodu", "urun_adi"}
REQUIRED_PHONE_COLUMNS = {"model"}


def _ensure_columns(df: pd.DataFrame, required: set[str], dataset_name: str) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )


def load_dataframes() -> tuple[pd.DataFrame, pd.DataFrame]:
    products = pd.read_csv(DATA_PRODUCTS_PATH)
    candidate_paths = [
        "data/phone_specs.csv",
        DATA_PHONES_PATH,
        "data/phonespecs.csv",
    ]

    phones = None
    for path in candidate_paths:
        if Path(path).exists():
            phones = pd.read_csv(path)
            break

    if phones is None:
        phones = pd.read_csv(DATA_PHONES_PATH)

    _ensure_columns(products, REQUIRED_PRODUCT_COLUMNS, "products")
    _ensure_columns(phones, REQUIRED_PHONE_COLUMNS, "phones")

    return products, phones
