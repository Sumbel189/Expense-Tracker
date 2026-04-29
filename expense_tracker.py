import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "data.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Личный трекер расходов")
        self.root.geometry("900x600")
        
        # Данные
        self.expenses = self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        # Рамка для ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Коммунальные услуги", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=20)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set(categories[0])
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка добавить
        add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        filter_categories = ["Все"] + categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=filter_categories, width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по дате (период)
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.date_from_entry = ttk.Entry(filter_frame, width=12)
        self.date_from_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5, pady=5)
        self.date_to_entry = ttk.Entry(filter_frame, width=12)
        self.date_to_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка применить фильтр
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        filter_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Кнопка сброса фильтра
        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # Таблица расходов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Сумма", "Категория", "Дата"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=100)
        self.tree.column("Категория", width=150)
        self.tree.column("Дата", width=120)
        
        self.tree.pack(fill="both", expand=True)
        
        # Рамка для итогов
        total_frame = ttk.Frame(self.root)
        total_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(total_frame, text="Итого за выбранный период:").pack(side="left", padx=5)
        self.total_label = ttk.Label(total_frame, text="0.00 ₽", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=5)
        
        # Кнопка удалить выбранную запись
        delete_btn = ttk.Button(self.root, text="Удалить выбранный расход", command=self.delete_expense)
        delete_btn.pack(pady=5)
    
    def validate_amount(self, amount_str):
        """Проверка суммы"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть положительным числом"
            return True, amount
        except ValueError:
            return False, "Сумма должна быть числом"
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, date_str
        except ValueError:
            return False, "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2024-01-15)"
    
    def add_expense(self):
        """Добавление расхода"""
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_entry.get().strip()
        
        # Валидация
        amount_valid, amount_result = self.validate_amount(amount_str)
        if not amount_valid:
            messagebox.showerror("Ошибка", amount_result)
            return
        
        if not category:
            messagebox.showerror("Ошибка", "Категория не может быть пустой")
            return
        
        date_valid, date_result = self.validate_date(date_str)
        if not date_valid:
            messagebox.showerror("Ошибка", date_result)
            return
        
        # Создание ID
        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        
        # Добавление
        self.expenses.append({
            "id": new_id,
            "amount": amount_result,
            "category": category,
            "date": date_result
        })
        
        self.save_data()
        self.refresh_table()
        
        # Очистка полей (кроме даты)
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Еда")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        
        confirm = messagebox.askyesno("Подтверждение", "Удалить выбранный расход?")
        if confirm:
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            self.save_data()
            self.refresh_table()
    
    def filter_expenses(self):
        """Фильтрация расходов по категории и дате"""
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]
        
        # Фильтр по дате (период)
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()
        
        if date_from:
            valid, _ = self.validate_date(date_from)
            if valid:
                filtered = [e for e in filtered if e["date"] >= date_from]
            elif date_from:
                messagebox.showwarning("Предупреждение", f"Неверный формат даты 'от': {date_from}")
        
        if date_to:
            valid, _ = self.validate_date(date_to)
            if valid:
                filtered = [e for e in filtered if e["date"] <= date_to]
            elif date_to:
                messagebox.showwarning("Предупреждение", f"Неверный формат даты 'до': {date_to}")
        
        return filtered
    
    def calculate_total(self, expenses_list):
        """Подсчёт суммы расходов"""
        total = sum(e["amount"] for e in expenses_list)
        return total
    
    def refresh_table(self):
        """Обновление таблицы и итогов"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Применение фильтра
        filtered_expenses = self.filter_expenses()
        
        # Заполнение таблицы
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))
        
        # Подсчёт и отображение итога
        total = self.calculate_total(filtered_expenses)
        self.total_label.config(text=f"{total:.2f} ₽")
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()