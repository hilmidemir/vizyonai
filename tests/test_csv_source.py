import pandas as pd
import pytest

from vizyonai.adapters.data import csv_source


def test_load_dataframes_validates_required_columns(monkeypatch, tmp_path) -> None:
    products_path = tmp_path / "products.csv"
    phones_path = tmp_path / "phones.csv"

    pd.DataFrame(
        [
            {
                "kategori": "Şarj",
                "port": "USB-C",
                "watt": 25,
                "stok_kodu": "A1",
            }
        ]
    ).to_csv(products_path, index=False)
    pd.DataFrame([{"model": "S21"}]).to_csv(phones_path, index=False)

    monkeypatch.setattr(csv_source, "DATA_PRODUCTS_PATH", str(products_path))
    monkeypatch.setattr(csv_source, "DATA_PHONES_PATH", str(phones_path))

    with pytest.raises(ValueError, match="products is missing required columns"):
        csv_source.load_dataframes()


def test_load_dataframes_reads_valid_csv(monkeypatch, tmp_path) -> None:
    products_path = tmp_path / "products.csv"
    phones_path = tmp_path / "phones.csv"

    pd.DataFrame(
        [
            {
                "kategori": "Şarj",
                "port": "USB-C",
                "watt": 25,
                "stok_kodu": "A1",
                "urun_adi": "Adaptör",
            }
        ]
    ).to_csv(products_path, index=False)
    pd.DataFrame([{"model": "S21", "charge_port": "USB-C", "max_watt": 25}]).to_csv(
        phones_path, index=False
    )

    monkeypatch.setattr(csv_source, "DATA_PRODUCTS_PATH", str(products_path))
    monkeypatch.setattr(csv_source, "DATA_PHONES_PATH", str(phones_path))

    products, phones = csv_source.load_dataframes()

    assert len(products) == 1
    assert len(phones) == 1
