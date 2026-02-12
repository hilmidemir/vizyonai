import pandas as pd

def sort_by_closest_watt(df: pd.DataFrame, target_watt: int):
    df = df.copy()
    df["watt_num"] = pd.to_numeric(df["watt"], errors="coerce").fillna(0)
    df["watt_dist"] = (df["watt_num"] - target_watt).abs()
    # önce en yakın, eşitse daha yüksek watt öne
    df = df.sort_values(["watt_dist", "watt_num"], ascending=[True, False])
    return df
