from vizyonai.domains.electronics.extractors import extract_watt
from vizyonai.domains.electronics.intents import detect_intent


def test_detect_intent_handles_ascii_turkish_input() -> None:
    assert detect_intent("sarj adaptoru lazim") == "charger"


def test_extract_watt_parses_value() -> None:
    assert extract_watt("S21 icin 25W sarj") == 25
