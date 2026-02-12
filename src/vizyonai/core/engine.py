import importlib
from vizyonai.config.domains import get_domain_name, get_domain_plugin_path

class Engine:
    def __init__(self, products_df, phones_df):
        self.products_df = products_df
        self.phones_df = phones_df

        domain = get_domain_name()
        plugin_path = get_domain_plugin_path(domain)
        mod = importlib.import_module(plugin_path)
        self.plugin = mod  # plugin.recommend()

    def handle_query(self, q: str) -> dict:
        return self.plugin.recommend(q, self.products_df, self.phones_df)
