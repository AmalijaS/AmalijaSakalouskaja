import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import math
import json
import os

class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер цветовых моделей - RGB ↔ XYZ ↔ LAB")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Текущие значения цвета
        self.rgb = [0, 0, 0]
        self.xyz = [0.0, 0.0, 0.0]
        self.lab = [0.0, 0.0, 0.0]
        self.warning_shown = False
        self.updating = False
        
        # Константы для преобразований
        self.REF_X = 95.047  # Белая точка D65
        self.REF_Y = 100.000
        self.REF_Z = 108.883
        
        self.setup_ui()
        self.update_all_displays()
        
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Конвертер цветовых моделей RGB ↔ XYZ ↔ LAB", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Фрейм предпросмотра цвета и выбора
        preview_frame = ttk.LabelFrame(main_frame, text="Предпросмотр цвета", padding="15")
        preview_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Предпросмотр цвета
        self.color_preview = tk.Canvas(preview_frame, width=150, height=150, bg='#000000', 
                                       relief=tk.RAISED, bd=2)
        self.color_preview.grid(row=0, column=0, padx=(0, 20))
        
        # Информация о цвете
        color_info_frame = ttk.Frame(preview_frame)
        color_info_frame.grid(row=0, column=1, padx=20)
        
        self.hex_label = ttk.Label(color_info_frame, text="HEX: #000000", font=("Arial", 12))
        self.hex_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.rgb_label = ttk.Label(color_info_frame, text="RGB: 0, 0, 0", font=("Arial", 12))
        self.rgb_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Кнопка выбора цвета
        self.pick_color_btn = ttk.Button(preview_frame, text="Выбрать цвет...", 
                                         command=self.pick_color)
        self.pick_color_btn.grid(row=0, column=2, padx=20)
        
        # Предупреждение
        self.warning_label = ttk.Label(main_frame, text="", foreground="red")
        self.warning_label.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Модель RGB
        self.rgb_frame = self.create_color_model_frame(main_frame, "RGB модель", 
                                                      ["R (Красный)", "G (Зеленый)", "B (Синий)"],
                                                      [(0, 255), (0, 255), (0, 255)], 3)
        self.rgb_frame.grid(row=3, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Модель XYZ
        self.xyz_frame = self.create_color_model_frame(main_frame, "XYZ модель (CIE 1931)", 
                                                      ["X", "Y", "Z"],
                                                      [(0, 200), (0, 200), (0, 200)], 4)
        self.xyz_frame.grid(row=3, column=1, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Модель LAB
        self.lab_frame = self.create_color_model_frame(main_frame, "LAB модель (CIE L*a*b*)", 
                                                      ["L* (Светлота)", "a* (Зелено-Красный)", "b* (Сине-Желтый)"],
                                                      [(0, 100), (-128, 127), (-128, 127)], 4)
        self.lab_frame.grid(row=3, column=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
      
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Случайный цвет", command=self.random_color).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сбросить", command=self.reset_color).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить цвет", command=self.save_color).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Загрузить цвет", command=self.load_color).pack(side=tk.LEFT, padx=5)
        
    def create_color_model_frame(self, parent, title, labels, ranges, decimals):
        """Создает фрейм для цветовой модели"""
        frame = ttk.LabelFrame(parent, text=title, padding="15")
        
        # Списки для хранения элементов управления
        sliders = []
        entries = []
        value_labels = []
        
        for i, (label, (min_val, max_val)) in enumerate(zip(labels, ranges)):
            # Метка
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            # Ползунок
            var = tk.DoubleVar(value=0)
            slider = ttk.Scale(frame, from_=min_val, to=max_val, variable=var,
                              command=lambda v, idx=i, m=title: self.on_slider_change(v, idx, m))
            slider.grid(row=i, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
            
            # Поле ввода
            entry_var = tk.StringVar(value="0")
            entry = ttk.Entry(frame, textvariable=entry_var, width=10)
            entry.grid(row=i, column=2, padx=(0, 10), pady=5)
            entry.bind('<Return>', lambda e, idx=i, m=title: self.on_entry_change(e, idx, m))
            
            # Метка значения
            value_label = ttk.Label(frame, text="0", width=10)
            value_label.grid(row=i, column=3, pady=5)
            
            sliders.append(slider)
            entries.append(entry)
            value_labels.append(value_label)
        
        # Сохраняем ссылки
        if title == "RGB модель":
            self.rgb_sliders = sliders
            self.rgb_entries = entries
            self.rgb_value_labels = value_labels
        elif title == "XYZ модель (CIE 1931)":
            self.xyz_sliders = sliders
            self.xyz_entries = entries
            self.xyz_value_labels = value_labels
        elif title == "LAB модель (CIE L*a*b*)":
            self.lab_sliders = sliders
            self.lab_entries = entries
            self.lab_value_labels = value_labels
            
        return frame
    
    def show_warning(self, message):
        """Показывает предупреждение"""
        self.warning_label.config(text=message)
        self.warning_shown = True
        self.root.after(3000, self.clear_warning)
    
    def clear_warning(self):
        """Очищает предупреждение"""
        self.warning_label.config(text="")
        self.warning_shown = False
    
    def update_color_preview(self):
        """Обновляет предпросмотр цвета"""
        hex_color = f"#{self.rgb[0]:02x}{self.rgb[1]:02x}{self.rgb[2]:02x}"
        self.color_preview.config(bg=hex_color)
        self.hex_label.config(text=f"HEX: {hex_color}")
        self.rgb_label.config(text=f"RGB: {self.rgb[0]}, {self.rgb[1]}, {self.rgb[2]}")
    
    # ========== ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ЦВЕТОВ ==========
    
    def rgb_to_xyz(self, r, g, b):
        """Преобразование RGB в XYZ"""
        # Нормализация
        rn = r / 255.0
        gn = g / 255.0
        bn = b / 255.0
        
        # Гамма-коррекция
        rn = self.gamma_correction(rn)
        gn = self.gamma_correction(gn)
        bn = self.gamma_correction(bn)
        
        # Преобразование в XYZ
        x = rn * 0.4124564 + gn * 0.3575761 + bn * 0.1804375
        y = rn * 0.2126729 + gn * 0.7151522 + bn * 0.0721750
        z = rn * 0.0193339 + gn * 0.1191920 + bn * 0.9503041
        
        return [x * 100, y * 100, z * 100]
    
    def xyz_to_rgb(self, x, y, z):
        """Преобразование XYZ в RGB"""
        # Нормализация
        x = x / 100.0
        y = y / 100.0
        z = z / 100.0
        
        # Матричное преобразование
        r = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
        g = -x * 0.9692660 + y * 1.8760108 + z * 0.0415560
        b = x * 0.0556434 - y * 0.2040259 + z * 1.0572252
        
        # Обратная гамма-коррекция
        r = self.inverse_gamma_correction(r)
        g = self.inverse_gamma_correction(g)
        b = self.inverse_gamma_correction(b)
        
        # Преобразование к диапазону 0-255
        r = int(round(r * 255))
        g = int(round(g * 255))
        b = int(round(b * 255))
        
        # Проверка на выход за границы
        clamped = False
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            clamped = True
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
        
        return [r, g, b, clamped]
    
    def gamma_correction(self, value):
        """Гамма-коррекция для sRGB"""
        if value > 0.04045:
            return ((value + 0.055) / 1.055) ** 2.4
        else:
            return value / 12.92
    
    def inverse_gamma_correction(self, value):
        """Обратная гамма-коррекция для sRGB"""
        if value > 0.0031308:
            return 1.055 * (value ** (1/2.4)) - 0.055
        else:
            return 12.92 * value
    
    def xyz_to_lab(self, x, y, z):
        """Преобразование XYZ в LAB"""
        # Нормализация относительно белой точки
        x = x / self.REF_X
        y = y / self.REF_Y
        z = z / self.REF_Z
        
        # Функция f для преобразования
        def f(t):
            delta = 6/29
            if t > delta ** 3:
                return t ** (1/3)
            else:
                return t / (3 * delta * delta) + 4/29
        
        l = 116 * f(y) - 16
        a = 500 * (f(x) - f(y))
        b = 200 * (f(y) - f(z))
        
        return [l, a, b]
    
    def lab_to_xyz(self, l, a, b):
        """Преобразование LAB в XYZ"""
        # Функция обратного преобразования
        def f_inv(t):
            delta = 6/29
            if t > delta:
                return t ** 3
            else:
                return 3 * delta * delta * (t - 4/29)
        
        fy = (l + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200
        
        x = self.REF_X * f_inv(fx)
        y = self.REF_Y * f_inv(fy)
        z = self.REF_Z * f_inv(fz)
        
        return [x, y, z]
    
    # ========== ОБРАБОТЧИКИ СОБЫТИЙ ==========
    
    def on_slider_change(self, value, index, model):
        """Обработчик изменения ползунка"""
        if self.updating:
            return
            
        self.updating = True
        
        try:
            value = float(value)
            
            if model == "RGB модель":
                self.rgb[index] = int(value)
                self.rgb_entries[index].delete(0, tk.END)
                self.rgb_entries[index].insert(0, str(self.rgb[index]))
                self.rgb_value_labels[index].config(text=str(self.rgb[index]))
                
                # Преобразуем RGB -> XYZ -> LAB
                self.xyz = self.rgb_to_xyz(*self.rgb)
                self.lab = self.xyz_to_lab(*self.xyz)
                
                self.update_xyz_display()
                self.update_lab_display()
                
            elif model == "XYZ модель (CIE 1931)":
                self.xyz[index] = value
                self.xyz_entries[index].delete(0, tk.END)
                self.xyz_entries[index].insert(0, f"{value:.4f}")
                self.xyz_value_labels[index].config(text=f"{value:.4f}")
                
                # Преобразуем XYZ -> RGB -> LAB
                rgb_result = self.xyz_to_rgb(*self.xyz)
                self.rgb = rgb_result[:3]
                if rgb_result[3]:  # Если было обрезание
                    self.show_warning("Внимание: Цвет вышел за границы RGB. Значения обрезаны.")
                
                self.lab = self.xyz_to_lab(*self.xyz)
                
                self.update_rgb_display()
                self.update_lab_display()
                
            elif model == "LAB модель (CIE L*a*b*)":
                self.lab[index] = value
                self.lab_entries[index].delete(0, tk.END)
                self.lab_entries[index].insert(0, f"{value:.4f}")
                self.lab_value_labels[index].config(text=f"{value:.4f}")
                
                # Преобразуем LAB -> XYZ -> RGB
                self.xyz = self.lab_to_xyz(*self.lab)
                rgb_result = self.xyz_to_rgb(*self.xyz)
                self.rgb = rgb_result[:3]
                if rgb_result[3]:  # Если было обрезание
                    self.show_warning("Внимание: Цвет вышел за границы RGB. Значения обрезаны.")
                
                self.update_rgb_display()
                self.update_xyz_display()
            
            self.update_color_preview()
            
        except ValueError:
            pass
        finally:
            self.updating = False
    
    def on_entry_change(self, event, index, model):
        """Обработчик изменения поля ввода"""
        if self.updating:
            return
            
        self.updating = True
        
        try:
            if model == "RGB модель":
                value = int(self.rgb_entries[index].get())
                value = max(0, min(255, value))
                self.rgb[index] = value
                self.rgb_sliders[index].set(value)
                self.rgb_value_labels[index].config(text=str(value))
                
                # Преобразуем RGB -> XYZ -> LAB
                self.xyz = self.rgb_to_xyz(*self.rgb)
                self.lab = self.xyz_to_lab(*self.xyz)
                
                self.update_xyz_display()
                self.update_lab_display()
                
            elif model == "XYZ модель (CIE 1931)":
                value = float(self.xyz_entries[index].get())
                self.xyz[index] = value
                self.xyz_sliders[index].set(value)
                self.xyz_value_labels[index].config(text=f"{value:.4f}")
                
                # Преобразуем XYZ -> RGB -> LAB
                rgb_result = self.xyz_to_rgb(*self.xyz)
                self.rgb = rgb_result[:3]
                if rgb_result[3]:
                    self.show_warning("Внимание: Цвет вышел за границы RGB. Значения обрезаны.")
                
                self.lab = self.xyz_to_lab(*self.xyz)
                
                self.update_rgb_display()
                self.update_lab_display()
                
            elif model == "LAB модель (CIE L*a*b*)":
                value = float(self.lab_entries[index].get())
                self.lab[index] = value
                self.lab_sliders[index].set(value)
                self.lab_value_labels[index].config(text=f"{value:.4f}")
                
                # Преобразуем LAB -> XYZ -> RGB
                self.xyz = self.lab_to_xyz(*self.lab)
                rgb_result = self.xyz_to_rgb(*self.xyz)
                self.rgb = rgb_result[:3]
                if rgb_result[3]:
                    self.show_warning("Внимание: Цвет вышел за границы RGB. Значения обрезаны.")
                
                self.update_rgb_display()
                self.update_xyz_display()
            
            self.update_color_preview()
            
        except ValueError:
            self.show_warning("Ошибка: Введите корректное числовое значение")
        finally:
            self.updating = False
    
    def update_rgb_display(self):
        """Обновляет отображение RGB"""
        for i in range(3):
            self.rgb_sliders[i].set(self.rgb[i])
            self.rgb_entries[i].delete(0, tk.END)
            self.rgb_entries[i].insert(0, str(self.rgb[i]))
            self.rgb_value_labels[i].config(text=str(self.rgb[i]))
    
    def update_xyz_display(self):
        """Обновляет отображение XYZ"""
        for i in range(3):
            self.xyz_sliders[i].set(self.xyz[i])
            self.xyz_entries[i].delete(0, tk.END)
            self.xyz_entries[i].insert(0, f"{self.xyz[i]:.4f}")
            self.xyz_value_labels[i].config(text=f"{self.xyz[i]:.4f}")
    
    def update_lab_display(self):
        """Обновляет отображение LAB"""
        for i in range(3):
            self.lab_sliders[i].set(self.lab[i])
            self.lab_entries[i].delete(0, tk.END)
            self.lab_entries[i].insert(0, f"{self.lab[i]:.4f}")
            self.lab_value_labels[i].config(text=f"{self.lab[i]:.4f}")
    
    def update_all_displays(self):
        """Обновляет все отображения"""
        self.update_rgb_display()
        self.update_xyz_display()
        self.update_lab_display()
        self.update_color_preview()
    
    def pick_color(self):
        """Открывает диалог выбора цвета"""
        color = colorchooser.askcolor(title="Выберите цвет", initialcolor=self.get_hex_color())
        if color[0]:
            r, g, b = [int(c) for c in color[0]]
            self.rgb = [r, g, b]
            self.xyz = self.rgb_to_xyz(r, g, b)
            self.lab = self.xyz_to_lab(*self.xyz)
            self.update_all_displays()
    
    def get_hex_color(self):
        """Возвращает текущий цвет в HEX формате"""
        return f"#{self.rgb[0]:02x}{self.rgb[1]:02x}{self.rgb[2]:02x}"
    
    def random_color(self):
        """Генерирует случайный цвет"""
        import random
        self.rgb = [random.randint(0, 255) for _ in range(3)]
        self.xyz = self.rgb_to_xyz(*self.rgb)
        self.lab = self.xyz_to_lab(*self.xyz)
        self.update_all_displays()
    
    def reset_color(self):
        """Сбрасывает цвет к черному"""
        self.rgb = [0, 0, 0]
        self.xyz = [0.0, 0.0, 0.0]
        self.lab = [0.0, 0.0, 0.0]
        self.update_all_displays()
    
    def save_color(self):
        """Сохраняет текущий цвет в файл"""
        color_data = {
            'rgb': self.rgb,
            'xyz': self.xyz,
            'lab': self.lab,
            'hex': self.get_hex_color()
        }
        
        try:
            with open('saved_color.json', 'w') as f:
                json.dump(color_data, f, indent=2)
            self.show_warning("Цвет сохранен в файл saved_color.json")
        except Exception as e:
            self.show_warning(f"Ошибка при сохранении: {str(e)}")
    
    def load_color(self):
        """Загружает цвет из файла"""
        try:
            if os.path.exists('saved_color.json'):
                with open('saved_color.json', 'r') as f:
                    color_data = json.load(f)
                
                self.rgb = color_data['rgb']
                self.xyz = color_data['xyz']
                self.lab = color_data['lab']
                self.update_all_displays()
                self.show_warning("Цвет загружен из файла")
            else:
                self.show_warning("Файл saved_color.json не найден")
        except Exception as e:
            self.show_warning(f"Ошибка при загрузке: {str(e)}")

def main():
    root = tk.Tk()
    app = ColorConverterApp(root)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()