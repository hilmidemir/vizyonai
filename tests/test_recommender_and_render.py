import pandas as pd

from vizyonai.domains.recommender import _pick_products_for_charger, recommend
from vizyonai.llm.render import _fallback_answer


def test_pick_products_for_charger_handles_invalid_watt_and_port_values() -> None:
    products_df = pd.DataFrame(
        [
            {
                "kategori": "Sarj Adaptoru",
                "port": "USB-C",
                "watt": "invalid",
                "stok_kodu": "A1",
                "urun_adi": "Adaptor A",
            },
            {
                "kategori": "Sarj Adaptoru",
                "port": "USB C",
                "watt": 30,
                "stok_kodu": "A2",
                "urun_adi": "Adaptor B",
            },
        ]
    )

    picked = _pick_products_for_charger(
        products_df=products_df,
        phone_row={"charge_port": "USB-C", "max_watt": "not-a-number"},
        requested_watt=None,
        requested_port=None,
    )

    assert len(picked) == 2
    assert picked[0]["stok_kodu"] == "A2"


def test_fallback_answer_is_two_lines() -> None:
    answer = _fallback_answer(
        [
            {"stok_kodu": "X1", "urun_adi": "Urun 1", "watt": 25, "port": "USB-C"},
            {"stok_kodu": "X2", "urun_adi": "Urun 2", "watt": 20, "port": "USB-C"},
        ]
    )

    assert len(answer.splitlines()) == 2
    assert ":" in answer.splitlines()[0]
    assert answer.splitlines()[1].startswith("Alternatif:")


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
    assert result["phone_row"]["model"] == "inferred-galaxy"


def test_pick_products_for_charger_prefers_exact_watt_match() -> None:
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
                "watt": 33,
                "stok_kodu": "W33",
                "urun_adi": "33W",
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

    picked = _pick_products_for_charger(
        products_df=products_df,
        phone_row={"charge_port": "USB-C", "max_watt": 25},
        requested_watt=None,
        requested_port=None,
    )

    assert len(picked) == 1
    assert picked[0]["stok_kodu"] == "W25"


def test_match_phone_model_prefers_ultra_over_base_model() -> None:
    phones_df = pd.DataFrame(
        [
            {"model": "Galaxy S25", "charge_port": "Type-C", "max_watt": 25},
            {"model": "Galaxy S25 Ultra", "charge_port": "Type-C", "max_watt": 45},
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
            }
        ]
    )

    result = recommend(
        "Samsung Galaxy S25 Ultra icin sarj aleti onerir misin",
        products_df,
        phones_df,
    )

    assert result["phone_model"] == "Galaxy S25 Ultra"
    assert result["phone_row"]["max_watt"] == 45


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
