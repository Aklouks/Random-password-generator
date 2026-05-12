import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import string
import json
import os
from datetime import datetime

HISTORY_FILE = "password_history.json"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("650x650")
        self.root.resizable(True, True)
        
        # Загрузка истории
        self.history = self.load_history()
        
        # Стили
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Arial", 14, "bold"))
        self.style.configure("History.TLabel", font=("Arial", 12, "bold"))
        
        # Основной контейнер
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔐 Генератор безопасных паролей", style="Title.TLabel")
        title_label.pack(pady=(0, 15))
        
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Длина пароля
        length_frame = ttk.Frame(settings_frame)
        length_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(length_frame, text="Длина пароля:").pack(side=tk.LEFT)
        
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(length_frame, from_=4, to=64, 
                                       variable=self.length_var, 
                                       orient=tk.HORIZONTAL, 
                                       length=300,
                                       command=self.update_length_label)
        self.length_scale.pack(side=tk.LEFT, padx=10)
        
        self.length_label = ttk.Label(length_frame, text="12", width=3)
        self.length_label.pack(side=tk.LEFT)
        
        self.length_spinbox = ttk.Spinbox(length_frame, from_=4, to=64, 
                                          width=5, textvariable=self.length_var,
                                          command=self.sync_scale_from_spinbox)
        self.length_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Чекбоксы
        checkboxes_frame = ttk.Frame(settings_frame)
        checkboxes_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(checkboxes_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.uppercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkboxes_frame, text="Строчные буквы (a-z)", 
                       variable=self.lowercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkboxes_frame, text="Цифры (0-9)", 
                       variable=self.digits_var).pack(anchor=tk.W)
        ttk.Checkbutton(checkboxes_frame, text="Специальные символы (!@#$%^&*)", 
                       variable=self.special_var).pack(anchor=tk.W)
        
        # Кнопки
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.generate_btn = ttk.Button(buttons_frame, text="🎲 Сгенерировать пароль", 
                                       command=self.generate_password, 
                                       style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.copy_btn = ttk.Button(buttons_frame, text="📋 Копировать", 
                                   command=self.copy_to_clipboard, 
                                   state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_history_btn = ttk.Button(buttons_frame, text="🗑 Очистить историю", 
                                           command=self.clear_history)
        self.clear_history_btn.pack(side=tk.RIGHT)
        
        # Поле для пароля
        password_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding="10")
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.password_var = tk.StringVar(value="Нажмите 'Сгенерировать пароль'")
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                        font=("Courier", 14), state="readonly")
        self.password_entry.pack(fill=tk.X)
        
        # История
        history_frame = ttk.LabelFrame(main_frame, text="📜 История паролей", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица истории
        columns = ("Дата", "Пароль", "Длина", "Типы символов")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                         show="headings", height=8)
        
        self.history_tree.heading("Дата", text="Дата создания")
        self.history_tree.heading("Пароль", text="Пароль")
        self.history_tree.heading("Длина", text="Длина")
        self.history_tree.heading("Типы символов", text="Типы символов")
        
        self.history_tree.column("Дата", width=150)
        self.history_tree.column("Пароль", width=250)
        self.history_tree.column("Длина", width=60)
        self.history_tree.column("Типы символов", width=120)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Загрузка истории
        self.update_history_display()
        
        # Дополнительная информация
        info_label = ttk.Label(main_frame, 
                              text="💡 Совет: Используйте длинные пароли с разными типами символов для максимальной безопасности",
                              font=("Arial", 9), foreground="gray")
        info_label.pack(pady=(10, 0))
    
    def update_length_label(self, *args):
        """Обновление метки длины и синхронизация со Spinbox"""
        value = int(self.length_var.get())
        self.length_label.config(text=str(value))
        self.length_spinbox.delete(0, tk.END)
        self.length_spinbox.insert(0, str(value))
    
    def sync_scale_from_spinbox(self):
        """Синхронизация ползунка со Spinbox"""
        try:
            value = int(self.length_spinbox.get())
            if 4 <= value <= 64:
                self.length_var.set(value)
        except ValueError:
            pass
    
    def validate_input(self):
        """Проверка корректности ввода"""
        length = self.length_var.get()
        
        if length < 4 or length > 64:
            messagebox.showerror("Ошибка", "Длина пароля должна быть от 4 до 64 символов!")
            return False
        
        if not any([self.uppercase_var.get(), self.lowercase_var.get(), 
                   self.digits_var.get(), self.special_var.get()]):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return False
        
        return True
    
    def generate_password(self):
        """Генерация пароля на основе выбранных параметров"""
        if not self.validate_input():
            return
        
        length = self.length_var.get()
        characters = ""
        char_types = []
        
        if self.uppercase_var.get():
            characters += string.ascii_uppercase
            char_types.append("A-Z")
        if self.lowercase_var.get():
            characters += string.ascii_lowercase
            char_types.append("a-z")
        if self.digits_var.get():
            characters += string.digits
            char_types.append("0-9")
        if self.special_var.get():
            characters += string.punctuation
            char_types.append("!@#...")
        
        # Генерация пароля с гарантией минимум одного символа каждого типа
        password = self.generate_strong_password(length, characters)
        
        self.password_var.set(password)
        self.copy_btn.config(state=tk.NORMAL)
        
        # Сохранение в историю
        self.add_to_history(password, length, "+".join(char_types))
    
    def generate_strong_password(self, length, characters):
        """Генерация пароля с гарантией наличия всех выбранных типов символов"""
        password = ""
        
        # Добавляем по одному символу каждого выбранного типа
        if self.uppercase_var.get():
            password += random.choice(string.ascii_uppercase)
        if self.lowercase_var.get():
            password += random.choice(string.ascii_lowercase)
        if self.digits_var.get():
            password += random.choice(string.digits)
        if self.special_var.get():
            password += random.choice(string.punctuation)
        
        # Заполняем остальную длину случайными символами
        remaining_length = length - len(password)
        if remaining_length > 0:
            password += ''.join(random.choices(characters, k=remaining_length))
        
        # Перемешиваем символы для большей случайности
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password and password != "Нажмите 'Сгенерировать пароль'":
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
    
    def add_to_history(self, password, length, char_types):
        """Добавление пароля в историю"""
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "char_types": char_types
        }
        
        self.history.insert(0, history_entry)  # Добавляем в начало
        
        # Ограничиваем историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[:50]
        
        self.save_history()
        self.update_history_display()
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Сохранение истории в JSON файл"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def update_history_display(self):
        """Обновление отображения истории"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Заполнение таблицы
        for entry in self.history:
            self.history_tree.insert("", 0, values=(
                entry["date"],
                entry["password"][:30] + "..." if len(entry["password"]) > 30 else entry["password"],
                entry["length"],
                entry["char_types"]
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю паролей?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()