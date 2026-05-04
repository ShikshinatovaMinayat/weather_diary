import json
import os
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class CalendarDialog:
    """Простой календарь для выбора даты"""
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title("Выберите дату")
        self.window.geometry("300x250")
        self.window.resizable(False, False)
        
        # Переменные для года и месяца
        self.current_year = date.today().year
        self.current_month = date.today().month
        
        # Заголовок с навигацией
        self.header_frame = tk.Frame(self.window)
        self.header_frame.pack(pady=10)
        
        self.prev_btn = tk.Button(self.header_frame, text="◀", command=self.prev_month)
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        self.month_label = tk.Label(self.header_frame, text="", font=("Arial", 12, "bold"))
        self.month_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = tk.Button(self.header_frame, text="▶", command=self.next_month)
        self.next_btn.pack(side=tk.LEFT, padx=10)
        
        # Календарная сетка
        self.calendar_frame = tk.Frame(self.window)
        self.calendar_frame.pack()
        
        self.update_calendar()
        
        # Кнопка Отмена
        self.cancel_btn = tk.Button(self.window, text="Отмена", command=self.window.destroy)
        self.cancel_btn.pack(pady=10)
    
    def update_calendar(self):
        # Очистка старого календаря
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Дни недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, width=4, font=("Arial", 9, "bold"),
                    borderwidth=1, relief="solid").grid(row=0, column=i, padx=1, pady=1)
        
        # Обновление заголовка
        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        self.month_label.config(text=f"{months[self.current_month-1]} {self.current_year}")
        
        # Получение первого дня месяца и количества дней
        first_day = date(self.current_year, self.current_month, 1)
        start_weekday = first_day.weekday()  # 0 = понедельник
        
        # Определение количества дней в месяце
        if self.current_month == 12:
            next_month = date(self.current_year + 1, 1, 1)
        else:
            next_month = date(self.current_year, self.current_month + 1, 1)
        days_in_month = (next_month - first_day).days
        
        # Заполнение календаря
        row = 1
        col = start_weekday
        
        for day_num in range(1, days_in_month + 1):
            day_btn = tk.Button(self.calendar_frame, text=str(day_num), width=4,
                                command=lambda d=day_num: self.select_date(d))
            day_btn.grid(row=row, column=col, padx=1, pady=1)
            
            # Выделение сегодняшнего дня
            if (self.current_year == date.today().year and 
                self.current_month == date.today().month and 
                day_num == date.today().day):
                day_btn.config(bg="lightblue")
            
            col += 1
            if col > 6:
                col = 0
                row += 1
    
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()
    
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()
    
    def select_date(self, day):
        self.result = date(self.current_year, self.current_month, day)
        self.window.destroy()

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.data_file = "weather_data.json"
        self.entries = []
        
        # Загрузка данных из файла
        self.load_from_file()
        
        self.create_widgets()
        self.update_table()
    
    def create_widgets(self):
        # === Панель ввода ===
        input_frame = tk.LabelFrame(self.root, text="Добавление записи", bg="#f0f0f0", font=("Arial", 10, "bold"))
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Дата
        tk.Label(input_frame, text="Дата:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, date.today().strftime("%d.%m.%Y"))
        
        self.calendar_btn = tk.Button(input_frame, text="📅 Календарь", command=self.show_calendar, bg="#e0e0e0")
        self.calendar_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Температура
        tk.Label(input_frame, text="Температура (°C):", bg="#f0f0f0").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Описание
        tk.Label(input_frame, text="Описание:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.desc_entry = tk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        # Осадки
        self.precip_var = tk.BooleanVar()
        self.precip_check = tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var, bg="#f0f0f0")
        self.precip_check.grid(row=1, column=4, padx=5, pady=5)
        
        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="➕ Добавить запись", command=self.add_entry, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        add_btn.grid(row=2, column=0, columnspan=5, pady=10)
        
        # === Панель фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", bg="#f0f0f0", font=("Arial", 10, "bold"))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Фильтр по дате:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.filter_calendar_btn = tk.Button(filter_frame, text="📅", command=self.show_filter_calendar, width=3)
        self.filter_calendar_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.clear_date_btn = tk.Button(filter_frame, text="✖", command=self.clear_date_filter, width=3)
        self.clear_date_btn.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Фильтр по температуре:", bg="#f0f0f0").grid(row=0, column=4, padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=5, padx=5, pady=5)
        tk.Label(filter_frame, text="°C (показать выше)", bg="#f0f0f0").grid(row=0, column=6, padx=5, pady=5)
        
        self.apply_filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.update_table, bg="#2196F3", fg="white")
        self.apply_filter_btn.grid(row=0, column=7, padx=10, pady=5)
        
        self.reset_filter_btn = tk.Button(filter_frame, text="Сброс", command=self.reset_filters, bg="#ff9800", fg="white")
        self.reset_filter_btn.grid(row=0, column=8, padx=5, pady=5)
        
        # === Таблица записей ===
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создание Treeview
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить запись", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # === Кнопки управления ===
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.save_btn = tk.Button(control_frame, text="💾 Сохранить в JSON", command=self.save_to_file, bg="#607D8B", fg="white", font=("Arial", 10, "bold"))
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = tk.Button(control_frame, text="📂 Загрузить из JSON", command=self.load_from_file_dialog, bg="#607D8B", fg="white", font=("Arial", 10, "bold"))
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_label = tk.Label(self.root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#f0f0f0")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_calendar(self):
        dialog = CalendarDialog(self.root)
        self.root.wait_window(dialog.window)
        if dialog.result:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, dialog.result.strftime("%d.%m.%Y"))
    
    def show_filter_calendar(self):
        dialog = CalendarDialog(self.root)
        self.root.wait_window(dialog.window)
        if dialog.result:
            self.filter_date_entry.delete(0, tk.END)
            self.filter_date_entry.insert(0, dialog.result.strftime("%d.%m.%Y"))
            self.update_table()
    
    def clear_date_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.update_table()
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ")
            return
        
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return
        
        # Добавление записи
        entry = {
            "date": date_str,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.entries.append(entry)
        self.update_table()
        
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime("%d.%m.%Y"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        self.status_label.config(text=f"Запись добавлена: {date_str}")
    
    def update_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация записей
        filtered = self.entries.copy()
        
        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            if self.validate_date(filter_date):
                filtered = [e for e in filtered if e["date"] == filter_date]
            else:
                self.status_label.config(text="Неверный формат даты фильтра")
        
        # Фильтр по температуре
        filter_temp = self.filter_temp_entry.get().strip()
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                filtered = [e for e in filtered if e["temperature"] > temp_threshold]
            except ValueError:
                self.status_label.config(text="Неверный формат температуры фильтра")
        
        # Заполнение таблицы
        for entry in filtered:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))
        
        self.status_label.config(text=f"Показано записей: {len(filtered)} (всего: {len(self.entries)})")
    
    def reset_filters(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            # Получаем значения выбранной строки
            values = self.tree.item(selected[0])["values"]
            date_str = values[0]
            temp = values[1]
            desc = values[2]
            
            # Удаляем из списка
            for i, entry in enumerate(self.entries):
                if (entry["date"] == date_str and 
                    entry["temperature"] == temp and 
                    entry["description"] == desc):
                    del self.entries[i]
                    break
            
            self.update_table()
            self.status_label.config(text="Запись удалена")
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def save_to_file(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            self.status_label.config(text=f"Сохранено в {self.data_file}")
            messagebox.showinfo("Успех", f"Данные сохранены в {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_from_file(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                self.update_table()
                self.status_label.config(text=f"Загружено из {self.data_file}")
            except Exception as e:
                self.entries = []
                self.status_label.config(text=f"Ошибка загрузки: {e}")
        else:
            self.entries = []
    
    def load_from_file_dialog(self):
        self.load_from_file()
        if self.entries:
            messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей")
        else:
            messagebox.showinfo("Инфо", "Нет данных для загрузки или файл не найден")

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()