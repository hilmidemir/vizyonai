import re

def extract_watt(q: str):
    m = re.search(r"(\d{2,3})\s*w", q.lower())
    return int(m.group(1)) if m else None

def extract_port(q: str):
    t = q.lower()
    if "lightning" in t:
        return "Lightning"
    if "type-c" in t or "type c" in t or "usb-c" in t or "usb c" in t:
        return "USB-C"
    return None
