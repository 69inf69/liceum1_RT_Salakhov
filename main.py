import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_user).pack(side=tk.LEFT)

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.results_listbox = Listbox(results_frame, height=15)
        self.results_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопки действий
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Добавить в избранное",
                   command=self.add_to_favorites).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Удалить из избранного",
                   command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)

        # Список избранных
        favorites_frame = ttk.LabelFrame(self.root, text="Избранные пользователи")
        favorites_frame.pack(fill=tk.X, padx=10, pady=5)

        self.favorites_listbox = Listbox(favorites_frame, height=8)
        self.favorites_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.update_favorites_display()

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                user_data = response.json()
                display_text = f"{user_data['login']} - {user_data.get('name', 'No name')} ({user_data['public_repos']} repos)"
                self.results_listbox.delete(0, tk.END)
                self.results_listbox.insert(0, display_text)
            else:
                messagebox.showerror("Ошибка", f"Пользователь не найден (код: {response.status_code})")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска")
            return

        user_text = self.results_listbox.get(selection[0])
        username = user_text.split(" - ")[0]

        if username not in self.favorites:
            self.favorites.append(username)
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"{username} добавлен в избранное!")
        else:
            messagebox.showinfo("Информация", f"{username} уже в избранном")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из избранного")
            return

        username = self.favorites_listbox.get(selection[0])
        self.favorites.remove(username)
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", f"{username} удалён из избранного")

    def load_favorites(self):
        if os.path.exists("favorites.json"):
            try:
                with open("favorites.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def update_favorites_display(self):
        self.favorites_listbox.delete(0, tk.END)
        for username in self.favorites:
            self.favorites_listbox.insert(tk.END, username)


def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
