import pandas as pd

from vizyonai.domains.recommender import recommend


def test_recommend_requires_80_score_for_phone_match() -> None:
    phones_df = pd.DataFrame(
        [
            {"model": "Galaxy S23", "charge_port": "Type-C", "max_watt": 25},
            {"model": "Galaxy S24 Ultra", "charge_port": "Type-C", "max_watt": 45},
        ]
    )
    products_df = pd.DataFrame(
        [
            {
                "kategori": "Sarj Adaptoru",
                "port": "USB-C",
                "watt": 45,
                "stok_kodu": "W45",
                "urun_adi": "45W",
            },
            {
                "kategori": "Sarj Adaptoru",
                "port": "USB-C",
                "watt": 25,
                "stok_kodu": "W25",
                "urun_adi": "25W",
            },
        ]
    )

    result = recommend("galxy s24 ultra sarj", products_df, phones_df)
    assert result["match_score"] < 80
    assert result["phone_row"] is None


def test_match_phone_model_prefers_fe_variant() -> None:
    phones_df = pd.DataFrame(
        [
            {"model": "Galaxy S25", "charge_port": "Type-C", "max_watt": 25},
            {"model": "Galaxy S25 FE", "charge_port": "Type-C", "max_watt": 25},
        ]
    )
    products_df = pd.DataFrame(
        [
            {
                "kategori": "Sarj Adaptoru",
                "port": "USB-C",
                "watt": 25,
                "stok_kodu": "W25",
                "urun_adi": "25W",
            }
        ]
    )

    result = recommend(
        "Samsung S25 FE icin sarj aleti oner",
        products_df,
        phones_df,
    )

    assert result["phone_model"] == "Galaxy S25 FE"
