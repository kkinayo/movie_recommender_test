# Movie Recommender (Семантический рекомендатор фильмов) ((test))

Приложение на базе Tkinter.
Рекомендует фильмы на основе их рецензий (Kinopoisk dataset) и пользовательского описания/запроса.

1. **Sentence Transformers** (модель `distiluse-base-multilingual-cased`) создаёт семантические эмбеддинги для каждой рецензии.
2. **K-Nearest Neighbors** ищет 50 ближайших по косинусной дистанции рецензий к запросу пользователя.
3. **SpaCy** для лемматизации слов-исключений, чтобы убрать фильмы, где упоминаются нежелательные вещи.
4. Предусмотрен код, который сохраняет эмбеддинги в файл `embeddings.npy`.

## Установка
Python 3.10+
```bash
pip install -r requirements.txt
python -m spacy download ru_core_news_sm
