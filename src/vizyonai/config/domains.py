from vizyonai.config.settings import DOMAIN

def get_domain_name() -> str:
    return DOMAIN

def get_domain_plugin_path(domain: str) -> str:
    # yeni domain eklemek = burada bir satır daha
    mapping = {
        "electronics": "vizyonai.domains.electronics.plugin",
    }
    if domain not in mapping:
        raise ValueError(f"Unknown domain: {domain}. Available: {list(mapping.keys())}")
    return mapping[domain]
