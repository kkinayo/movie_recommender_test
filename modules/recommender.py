# Sentence Transformer + k-ближайших соседей + лемматизация + кэширование эмбеддингов

import os
import random
import spacy
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

nlp = spacy.load("ru_core_news_sm")


class MovieRecommender:
    def __init__(self, data: pd.DataFrame) -> None:

        # датасет с рецензиями
        self.data = data

        # мультиязычная модель
        self.model = SentenceTransformer('distiluse-base-multilingual-cased')

        # путь к файлу с эмбеддингами
        self.embeddings_path = "embeddings.npy"

        # есть ли сохранённые эмбеддинги
        if os.path.exists(self.embeddings_path):
            print(f"[INFO] Нашёл сохранённые эмбеддинги: {self.embeddings_path}")
            self.embeddings = np.load(self.embeddings_path)

            # проверка ембеддинги = количество рецензий
            if self.embeddings.shape[0] != len(self.data):
                print("[WARNING] Размер сохранённых эмбеддингов не совпадает с числом строк в DataFrame")
                print("[INFO] Пересчитываем эмбеддинги заново...")
                self._calculate_and_save_embeddings()
        else:
            print(f"[INFO] Файл эмбеддингов не найден: {self.embeddings_path}")
            print("[INFO] Считаем и сохраняем эмбеддинги...")
            self._calculate_and_save_embeddings()

        # инициализация + обучение KNN
        self.nn_model = NearestNeighbors(
            n_neighbors=50,
            algorithm='brute',
            metric='cosine'
        )
        self.nn_model.fit(self.embeddings)

    def _calculate_and_save_embeddings(self) -> None:

        # Вспомогательный метод для подсчёта эмбеддингов и сохранения их в файл (self.embeddings_path)

        # эмбеддинги рецензий (convert_to_tensor=True => pytorch tensor)
        print("[INFO] Идёт процесс расчёта эмбеддингов... (может занять время)")
        emb = self.model.encode(
            self.data["content"].tolist(),
            convert_to_tensor=True,
            show_progress_bar=True,
            batch_size=16
        )
        # перевод тензоров в numpy (для работы sklearn)
        emb = emb.cpu().numpy()

        # сохраненение в файл
        np.save(self.embeddings_path, emb)
        self.embeddings = emb
        print(f"[INFO] Эмбеддинги сохранены в файл: {self.embeddings_path}")

    def _lemmas_set(self, text: str) -> set[str]:

        # лемматизация текста + трим
        doc = nlp(text.lower())
        return {token.lemma_ for token in doc if not token.is_space and not token.is_punct}

    def recommend(
        self,
        query: str,
        num_recommendations: int,
        exclude_keywords: list[str]
    ) -> list[tuple[str, str, int, str]]:


        # запрос пользователя -> эмбеддинг
        query_emb = self.model.encode([query], convert_to_tensor=True).cpu().numpy()

        # ближайшие 50 рецензий (по косинусной близости)
        _, indices = self.nn_model.kneighbors(query_emb, n_neighbors=50)

        # лемматизация ключевых слов, каждый элемент => множество лемм
        exclude_lemmas_list = []
        for kw in exclude_keywords:
            lemmas = self._lemmas_set(kw)
            if lemmas:  # на случай пустой строки
                exclude_lemmas_list.append(lemmas)

        # фильтрация рецензий
        filtered_indices = []
        for idx in indices[0]:
            content_text = self.data.iloc[idx]['content']
            # лемматизация рецензии
            text_lemmas = self._lemmas_set(content_text)

            # проверка на исключающие леммы
            should_exclude = False
            for exclude_lemmas in exclude_lemmas_list:
                # если пересечение непустое => есть слово из exclude => исключаем
                if text_lemmas & exclude_lemmas:
                    should_exclude = True
                    break

            # если не исключили => добавляем
            if not should_exclude:
                filtered_indices.append(idx)

        # если найдено меньше, чем нужно => берём все; иначе => случайную выборку
        if len(filtered_indices) < num_recommendations:
            selected_indices = filtered_indices
        else:
            selected_indices = random.sample(filtered_indices, num_recommendations)

        # список рекомендаций
        recommendations = []
        for idx in selected_indices:
            row = self.data.iloc[idx]
            movie_name = row['movie_name']
            content_text = row['content']
            grade3 = row['grade3']
            title = row.get('title', None)

            recommendations.append((movie_name, title, grade3, content_text))

        return recommendations
