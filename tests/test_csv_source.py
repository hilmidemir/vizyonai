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


def test_load_dataframes_prefers_phone_specs_when_present(monkeypatch, tmp_path) -> None:
    products_path = tmp_path / "products.csv"
    wrong_phones_path = tmp_path / "phones.csv"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    specs_path = data_dir / "phone_specs.csv"

    pd.DataFrame(
        [
            {
                "kategori": "Sarj",
                "port": "USB-C",
                "watt": 25,
                "stok_kodu": "A1",
                "urun_adi": "Adaptor",
            }
        ]
    ).to_csv(products_path, index=False)
    pd.DataFrame([{"model": "Wrong Model"}]).to_csv(wrong_phones_path, index=False)
    pd.DataFrame([{"model": "Specs Model"}]).to_csv(specs_path, index=False)

    monkeypatch.setattr(csv_source, "DATA_PRODUCTS_PATH", str(products_path))
    monkeypatch.setattr(csv_source, "DATA_PHONES_PATH", str(wrong_phones_path))
    monkeypatch.chdir(tmp_path)

    _, phones = csv_source.load_dataframes()
    assert phones.iloc[0]["model"] == "Specs Model"


<<<<<<< codex/refactor-ui-with-modular-components
def test_load_dataframes_resolves_relative_paths_from_project_root(monkeypatch, tmp_path) -> None:
=======
def test_load_dataframes_maps_cikis_tipi_to_port(monkeypatch, tmp_path) -> None:
>>>>>>> main
    products_path = tmp_path / "products.csv"
    phones_path = tmp_path / "phones.csv"

    pd.DataFrame(
        [
            {
                "kategori": "Sarj",
<<<<<<< codex/refactor-ui-with-modular-components
                "port": "USB-C",
=======
                "cikis_tipi": "USB-C",
>>>>>>> main
                "watt": 25,
                "stok_kodu": "A1",
                "urun_adi": "Adaptor",
            }
        ]
    ).to_csv(products_path, index=False)
    pd.DataFrame([{"model": "S21"}]).to_csv(phones_path, index=False)

<<<<<<< codex/refactor-ui-with-modular-components
    monkeypatch.setattr(csv_source, "DATA_PRODUCTS_PATH", "data/products.csv")
    monkeypatch.setattr(csv_source, "DATA_PHONES_PATH", "data/phone_specs.csv")
    monkeypatch.setattr(csv_source, "_project_root", lambda: tmp_path)
    other_dir = tmp_path / "tests"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    products_path.rename(data_dir / "products.csv")
    phones_path.rename(data_dir / "phone_specs.csv")

    products, phones = csv_source.load_dataframes()

    assert len(products) == 1
    assert len(phones) == 1
=======
    monkeypatch.setattr(csv_source, "DATA_PRODUCTS_PATH", str(products_path))
    monkeypatch.setattr(csv_source, "DATA_PHONES_PATH", str(phones_path))

    products, _ = csv_source.load_dataframes()
    assert "port" in products.columns
    assert products.iloc[0]["port"] == "USB-C"
>>>>>>> main
