import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import pandas as pd
from datetime import datetime
import os


class BudgetCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор бюджета")
        self.root.geometry("1000x700")

        # Данные
        self.income_data = []
        self.expense_data = []
        self.categories = ['Продукты', 'Транспорт', 'Жилье', 'Развлечения',
                           'Здоровье', 'Одежда', 'Образование', 'Другое']

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text='Ввод данных')
        self.setup_input_tab()

        self.visual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_frame, text='Визуализация')
        self.setup_visual_tab()

        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text='История')
        self.setup_history_tab()

        self.status_bar = ttk.Label(self.root, text="Готов к работе",
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_input_tab(self):
        income_frame = ttk.LabelFrame(self.input_frame, text="Доходы", padding=10)
        income_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(income_frame, text="Источник дохода:").grid(row=0, column=0, padx=5)
        self.income_source = ttk.Entry(income_frame, width=20)
        self.income_source.grid(row=0, column=1, padx=5)

        ttk.Label(income_frame, text="Сумма:").grid(row=0, column=2, padx=5)
        self.income_amount = ttk.Entry(income_frame, width=15)
        self.income_amount.grid(row=0, column=3, padx=5)

        ttk.Button(income_frame, text="Добавить доход",
                   command=self.add_income).grid(row=0, column=4, padx=10)

        expense_frame = ttk.LabelFrame(self.input_frame, text="Расходы", padding=10)
        expense_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(expense_frame, text="Категория:").grid(row=0, column=0, padx=5)
        self.expense_category = ttk.Combobox(expense_frame, values=self.categories, width=15)
        self.expense_category.grid(row=0, column=1, padx=5)
        self.expense_category.set('Продукты')

        ttk.Label(expense_frame, text="Описание:").grid(row=0, column=2, padx=5)
        self.expense_desc = ttk.Entry(expense_frame, width=20)
        self.expense_desc.grid(row=0, column=3, padx=5)

        ttk.Label(expense_frame, text="Сумма:").grid(row=0, column=4, padx=5)
        self.expense_amount = ttk.Entry(expense_frame, width=15)
        self.expense_amount.grid(row=0, column=5, padx=5)

        ttk.Button(expense_frame, text="Добавить расход",
                   command=self.add_expense).grid(row=0, column=6, padx=10)

        summary_frame = ttk.LabelFrame(self.input_frame, text="Текущая сводка", padding=10)
        summary_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.summary_text = tk.Text(summary_frame, height=10, width=80)
        self.summary_text.pack(fill='both', expand=True)

        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить сводку",
                   command=self.update_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить в CSV",
                   command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить все",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

    def setup_visual_tab(self):
        self.visual_canvas_frame = ttk.Frame(self.visual_frame)
        self.visual_canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(self.visual_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Обновить графики",
                   command=self.update_visualization).pack(side=tk.LEFT, padx=5)

    def setup_history_tab(self):
        columns = ('Дата', 'Тип', 'Категория/Источник', 'Описание', 'Сумма')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns,
                                         show='headings', height=20)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL,
                                  command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Обновить историю",
                   command=self.update_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить запись",
                   command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Загрузить из CSV",
                   command=self.load_from_csv).pack(side=tk.LEFT, padx=5)

    def add_income(self):
        source = self.income_source.get()
        amount = self.income_amount.get()

        if not source or not amount:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return

        try:
            amount = float(amount)
            record = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'type': 'Доход',
                'category': source,
                'description': source,
                'amount': amount
            }
            self.income_data.append(record)
            self.save_to_csv(record)
            self.update_summary()
            self.update_history()

            self.income_source.delete(0, tk.END)
            self.income_amount.delete(0, tk.END)

            self.status_bar.config(text=f"Доход {amount} руб. добавлен")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")

    def add_expense(self):
        category = self.expense_category.get()
        description = self.expense_desc.get()
        amount = self.expense_amount.get()

        if not description or not amount:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return

        try:
            amount = float(amount)
            record = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'type': 'Расход',
                'category': category,
                'description': description,
                'amount': amount
            }
            self.expense_data.append(record)
            self.save_to_csv(record)
            self.update_summary()
            self.update_history()

            self.expense_desc.delete(0, tk.END)
            self.expense_amount.delete(0, tk.END)

            self.status_bar.config(text=f"Расход {amount} руб. добавлен в категорию {category}")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")

    def update_summary(self):
        total_income = sum(r['amount'] for r in self.income_data)
        total_expense = sum(r['amount'] for r in self.expense_data)
        balance = total_income - total_expense

        expense_by_category = {}
        for expense in self.expense_data:
            cat = expense['category']
            expense_by_category[cat] = expense_by_category.get(cat, 0) + expense['amount']

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "=" * 50 + "\n")
        self.summary_text.insert(tk.END, "СВОДКА ПО БЮДЖЕТУ\n")
        self.summary_text.insert(tk.END, "=" * 50 + "\n\n")

        self.summary_text.insert(tk.END, f"Всего доходов: {total_income:,.2f} руб.\n")
        self.summary_text.insert(tk.END, f"Всего расходов: {total_expense:,.2f} руб.\n")
        self.summary_text.insert(tk.END, f"Баланс: {balance:,.2f} руб.\n\n")

        if balance > 0:
            self.summary_text.insert(tk.END, "Положительный баланс\n\n")
        elif balance < 0:
            self.summary_text.insert(tk.END, "⚠Отрицательный баланс\n\n")
        else:
            self.summary_text.insert(tk.END, "➡Нулевой баланс\n\n")

        self.summary_text.insert(tk.END, "Расходы по категориям:\n")
        self.summary_text.insert(tk.END, "-" * 30 + "\n")

        for category in self.categories:
            amount = expense_by_category.get(category, 0)
            if amount > 0:
                percent = (amount / total_expense * 100) if total_expense > 0 else 0
                self.summary_text.insert(tk.END,
                                         f"{category}: {amount:,.2f} руб. ({percent:.1f}%)\n")

    def update_visualization(self):
        for widget in self.visual_canvas_frame.winfo_children():
            widget.destroy()

        if not self.expense_data:
            ttk.Label(self.visual_canvas_frame,
                      text="Нет данных для визуализации").pack()
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        expense_by_category = {}
        for expense in self.expense_data:
            cat = expense['category']
            expense_by_category[cat] = expense_by_category.get(cat, 0) + expense['amount']

        categories = list(expense_by_category.keys())
        amounts = list(expense_by_category.values())

        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Распределение расходов по категориям')

        total_income = sum(r['amount'] for r in self.income_data)
        total_expense = sum(r['amount'] for r in self.expense_data)

        ax2.bar(['Доходы', 'Расходы'], [total_income, total_expense],
                color=['green', 'red'])
        ax2.set_title('Сравнение доходов и расходов')
        ax2.set_ylabel('Сумма (руб)')

        for i, v in enumerate([total_income, total_expense]):
            ax2.text(i, v + max(total_income, total_expense) * 0.01,
                     f'{v:,.0f} руб.', ha='center')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.visual_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for record in self.income_data:
            self.history_tree.insert('', 'end', values=(
                record['date'],
                record['type'],
                record['category'],
                record['description'],
                f"{record['amount']:,.2f} руб."
            ))

        for record in self.expense_data:
            self.history_tree.insert('', 'end', values=(
                record['date'],
                record['type'],
                record['category'],
                record['description'],
                f"{record['amount']:,.2f} руб."
            ))

    def delete_record(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        item = self.history_tree.item(selected[0])
        values = item['values']

        for i, record in enumerate(self.income_data):
            if (record['date'] == values[0] and record['type'] == values[1] and
                    record['amount'] == float(values[4].replace(' руб.', '').replace(',', ''))):
                del self.income_data[i]
                break

        for i, record in enumerate(self.expense_data):
            if (record['date'] == values[0] and record['type'] == values[1] and
                    record['amount'] == float(values[4].replace(' руб.', '').replace(',', ''))):
                del self.expense_data[i]
                break

        self.update_history()
        self.update_summary()
        self.status_bar.config(text="Запись удалена")

    def save_to_csv(self, record=None):
        filename = 'budget_data.csv'
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'type', 'category',
                                                   'description', 'amount'])
            if not file_exists:
                writer.writeheader()
            if record:
                writer.writerow(record)

        if not record:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'type', 'category',
                                                       'description', 'amount'])
                writer.writeheader()
                writer.writerows(self.income_data + self.expense_data)
            messagebox.showinfo("Сохранение", "Данные сохранены в budget_data.csv")
            self.status_bar.config(text="Данные сохранены")

    def load_from_csv(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                df = pd.read_csv(filename)
                self.income_data = []
                self.expense_data = []

                for _, row in df.iterrows():
                    record = row.to_dict()
                    if record['type'] == 'Доход':
                        self.income_data.append(record)
                    else:
                        self.expense_data.append(record)

                self.update_history()
                self.update_summary()
                self.status_bar.config(text=f"Загружено из {filename}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def load_data(self):
        filename = 'budget_data.csv'
        if os.path.isfile(filename):
            try:
                df = pd.read_csv(filename)
                self.income_data = []
                self.expense_data = []

                for _, row in df.iterrows():
                    record = row.to_dict()
                    if record['type'] == 'Доход':
                        self.income_data.append(record)
                    else:
                        self.expense_data.append(record)

                self.update_history()
                self.update_summary()
                self.status_bar.config(text="Данные загружены из budget_data.csv")

            except Exception as e:
                self.status_bar.config(text="Ошибка загрузки данных")

    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Очистить все данные?"):
            self.income_data = []
            self.expense_data = []
            self.update_summary()
            self.update_history()
            self.status_bar.config(text="Все данные очищены")


def main():
    root = tk.Tk()
    app = BudgetCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()