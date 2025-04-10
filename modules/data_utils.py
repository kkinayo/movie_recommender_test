import pandas as pd
from datasets import load_dataset

def load_kinopoisk_dataset() -> pd.DataFrame:

    # датасет Kinopoisk (blinoff/kinopoisk) через библиотеку `datasets`.
    dataset = load_dataset("blinoff/kinopoisk")

    # трейн-часть датасета
    reviews = dataset['train'][:]

    df = pd.DataFrame(reviews)
    return df
