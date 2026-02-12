import pandas as pd
from vizyonai.config.settings import DATA_PRODUCTS_PATH, DATA_PHONES_PATH

def load_dataframes():
    products = pd.read_csv(DATA_PRODUCTS_PATH)
    phones = pd.read_csv(DATA_PHONES_PATH)
    return products, phones
