import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os


from modules.recommender import MovieRecommender
from modules.data_utils import load_kinopoisk_dataset

def show_info() -> None:

    # информациия о приложении

    messagebox.showinfo(
        "Информация",
        (
            "Это приложение предоставляет рекомендации по фильмам на основе "
            "их описания и рецензий.\n\n"
            "Чтобы получить рекомендации, введите описание фильма в поле ввода, "
            "выберите количество рекомендаций и нажмите кнопку 'Рекомендовать'.\n\n"
            "При выборе одного из рекомендованных фильмов, можно увидеть его рецензию.\n\n"
            "Поле с исключаемыми словами опционально, но помогает исключать фильмы, "
            "в чьих рецензиях есть нежелательные слова."
        )
    )

def on_recommend_button_click(
    entry: tk.Entry,
    combo: ttk.Combobox,
    exclude_entry: tk.Entry,
    recommender: MovieRecommender,
    recommendation_list: tk.Listbox,
    review_dict: dict
):
    query = entry.get().strip()
    exclude_keywords = [kw.strip().lower() for kw in exclude_entry.get().split(',') if kw.strip()]

    if not query:
        messagebox.showwarning("Предупреждение", "Введите описание фильма.")
        return

    try:
        num_recommendations = int(combo.get())
    except ValueError:
        messagebox.showwarning("Предупреждение", "Некорректное число рекомендаций.")
        return

    # 2. Вызываем recommend, передавая выбранный тип
    recommendations = recommender.recommend(query, num_recommendations, exclude_keywords)

    recommendation_list.delete(0, tk.END)
    review_dict.clear()

    for idx, (movie_name, title, grade3, content) in enumerate(recommendations):
        display_text = f"{movie_name} ({grade3})"
        recommendation_list.insert(tk.END, display_text)
        review_dict[idx] = content

def on_recommendation_select(event: tk.Event, review_dict: dict) -> None:

    # сообщение с рецензией выбранного фильма

    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        content = review_dict.get(index, "Рецензия не найдена.")
        messagebox.showinfo("Рецензия", content)

def main():
    df = load_kinopoisk_dataset()
    recommender = MovieRecommender(df)
    review_dict = {}

    root = tk.Tk()
    root.title("Рекомендации фильмов")
    root.geometry("650x750")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text="Введите описание фильма:", font=("Arial", 14))
    label.pack(pady=5)

    entry = tk.Entry(frame, width=50, font=("Arial", 12))
    entry.pack(pady=5)

    combo_label = tk.Label(frame, text="Количество рекомендаций:", font=("Arial", 14))
    combo_label.pack(pady=5)

    combo = ttk.Combobox(frame, values=[5, 10, 15, 20, 25, 30], font=("Arial", 12), width=5)
    combo.current(1)
    combo.pack(pady=5)

    exclude_label = tk.Label(frame, text="Исключить ключевые слова (через запятую):", font=("Arial", 14))
    exclude_label.pack(pady=5)

    exclude_entry = tk.Entry(frame, width=50, font=("Arial", 12))
    exclude_entry.pack(pady=5)



    recommend_button = tk.Button(
        frame,
        text="Рекомендовать",
        font=("Arial", 12),
        command=lambda: on_recommend_button_click(
            entry,
            combo,
            exclude_entry,
            recommender,
            recommendation_list,
            review_dict
        )
    )
    recommend_button.pack(pady=5)

    recommendation_list = tk.Listbox(frame, font=("Arial", 12), height=20)
    recommendation_list.pack(pady=10, fill=tk.BOTH, expand=True)

    def on_recommendation_select(event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            content = review_dict.get(index, "Рецензия не найдена.")
            messagebox.showinfo("Рецензия", content)

    recommendation_list.bind('<<ListboxSelect>>', on_recommendation_select)


    icon_path = os.path.join("assets", "info_icon.png")
    if os.path.exists(icon_path):
        try:
            from PIL import Image, ImageTk
            info_image = Image.open(icon_path)
            info_image = info_image.resize((20, 20), Image.LANCZOS)
            info_icon = ImageTk.PhotoImage(info_image)
            info_button = tk.Button(frame, image=info_icon, command=show_info)
            info_button.pack(side=tk.RIGHT, padx=5, pady=5)
        except Exception:
            info_button = tk.Button(frame, text="Инфо", command=show_info, font=("Arial", 12))
            info_button.pack(side=tk.RIGHT, padx=5, pady=5)
    else:
        info_button = tk.Button(frame, text="Инфо", command=show_info, font=("Arial", 12))
        info_button.pack(side=tk.RIGHT, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
