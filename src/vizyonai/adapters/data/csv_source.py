from pathlib import Path

import pandas as pd

from vizyonai.config.settings import DATA_PRODUCTS_PATH, DATA_PHONES_PATH

REQUIRED_PRODUCT_COLUMNS = {"kategori", "port", "watt", "stok_kodu", "urun_adi"}
REQUIRED_PHONE_COLUMNS = {"model"}
PRODUCT_COLUMN_ALIASES = {
    "port": ("port", "cikis_tipi"),
}


def _project_root() -> Path:
    # src/vizyonai/adapters/data/csv_source.py -> repo root
    return Path(__file__).resolve().parents[4]


def _resolve_csv_path(path_value: str) -> Path:
    candidate = Path(path_value).expanduser()
    candidates: list[Path] = []

    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.extend(
            [
                Path.cwd() / candidate,
                _project_root() / candidate,
            ]
        )

    for path in candidates:
        if path.exists():
            return path

    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"CSV file not found for '{path_value}'. Searched: {searched}"
    )


def _ensure_columns(df: pd.DataFrame, required: set[str], dataset_name: str) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )


def _normalize_product_columns(products: pd.DataFrame) -> pd.DataFrame:
    # Map alternate CSV headers to the canonical names used by the engine.
    rename_map: dict[str, str] = {}
    for canonical, aliases in PRODUCT_COLUMN_ALIASES.items():
        if canonical in products.columns:
            continue
        for alias in aliases:
            if alias in products.columns:
                rename_map[alias] = canonical
                break

    if rename_map:
        products = products.rename(columns=rename_map)

    return products


def load_dataframes() -> tuple[pd.DataFrame, pd.DataFrame]:
<<<<<<< codex/refactor-ui-with-modular-components
    products_path = _resolve_csv_path(DATA_PRODUCTS_PATH)
    products = pd.read_csv(products_path)
=======
    products = pd.read_csv(DATA_PRODUCTS_PATH)
    products = _normalize_product_columns(products)
>>>>>>> main
    candidate_paths = [
        "data/phone_specs.csv",
        DATA_PHONES_PATH,
        "data/phonespecs.csv",
    ]

    phones = None
    for path in candidate_paths:
        try:
            resolved_path = _resolve_csv_path(path)
        except FileNotFoundError:
            continue

        if resolved_path.exists():
            phones = pd.read_csv(resolved_path)
            break

    if phones is None:
        phones = pd.read_csv(_resolve_csv_path(DATA_PHONES_PATH))

    _ensure_columns(products, REQUIRED_PRODUCT_COLUMNS, "products")
    _ensure_columns(phones, REQUIRED_PHONE_COLUMNS, "phones")

    return products, phones
