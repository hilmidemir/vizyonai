import pandas as pd

from vizyonai.domains.recommender import _pick_products_for_charger
from vizyonai.llm.render import _fallback_answer


def test_pick_products_for_charger_handles_invalid_watt_and_port_values() -> None:
    products_df = pd.DataFrame(
        [
            {
                "kategori": "Şarj Adaptörü",
                "port": "USB-C",
                "watt": "invalid",
                "stok_kodu": "A1",
                "urun_adi": "Adaptör A",
            },
            {
                "kategori": "Şarj Adaptörü",
                "port": "USB C",
                "watt": 30,
                "stok_kodu": "A2",
                "urun_adi": "Adaptör B",
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
    assert answer.splitlines()[0].startswith("Öneri:")
    assert answer.splitlines()[1].startswith("Alternatif:")
