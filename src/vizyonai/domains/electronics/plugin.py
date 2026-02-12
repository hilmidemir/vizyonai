from vizyonai.domains.recommender import recommend as domain_recommend


def recommend(q: str, products_df, phones_df) -> dict:
    return domain_recommend(q=q, products_df=products_df, phones_df=phones_df)
