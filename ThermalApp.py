import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image

try:
    from PIL import ImageTk
except ImportError:
    ImageTk = None

from VisionProcessor import VisionProcessor

class ThermalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вариант 31 — Тепловой фильтр с сохранением")
        self.geometry("600x550")
        
        self.processor = VisionProcessor()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        self.tab_load = ttk.Frame(self.notebook)
        self.tab_filter = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_load, text="Загрузка")
        self.notebook.add(self.tab_filter, text="Тепловой фильтр")
        
        self._init_tab_load()
        self._init_tab_filter()

    def _init_tab_load(self):
        """Интерфейс первой вкладки"""
        btn_browse = ttk.Button(self.tab_load, text="Выбрать изображение", command=self._open_file)
        btn_browse.pack(pady=20)
        
        self.lbl_orig_preview = ttk.Label(self.tab_load, text="Изображение не загружено")
        self.lbl_orig_preview.pack(expand=True)

    def _init_tab_filter(self):
        """Интерфейс второй вкладки"""
        ctrl_frame = ttk.Frame(self.tab_filter)
        ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(ctrl_frame, text="Выберите палитру:").pack(side="left", padx=5)
        
        self.combo_style = ttk.Combobox(ctrl_frame, values=["Сине-красный (Jet)", "Черно-красный (Hot)"], state="readonly")
        self.combo_style.current(0)
        self.combo_style.pack(side="left", padx=5)
        
        self.combo_style.bind("<<ComboboxSelected>>", lambda event: self._update_thermal_view())

        # Кнопка сохранения обработанного кадра
        self.btn_save = ttk.Button(ctrl_frame, text="Сохранить результат", command=self._save_file, state="disabled")
        self.btn_save.pack(side="right", padx=5)
        
        self.lbl_result_view = ttk.Label(self.tab_filter)
        self.lbl_result_view.pack(expand=True)

    def _open_file(self):
        """Логика кнопки 'Выбрать изображение'"""
        file_path = filedialog.askopenfilename(
            parent=self,
            initialdir=".",
            filetypes=[
                ("Изображения", "*.jpg"),
                ("Изображения", "*.jpeg"),
                ("Изображения", "*.png"),
                ("Все файлы", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            loaded = self.processor.load_image(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        if loaded:
            try:
                img = Image.open(file_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть изображение для предпросмотра:\n{e}")
                return

            img.thumbnail((400, 350))

            self.photo_orig = self._pil_image_to_photo(img)
            self.lbl_orig_preview.configure(image=self.photo_orig, text="")

            self.btn_save.configure(state="normal")

            self._update_thermal_view()
        else:
            messagebox.showerror("Ошибка", "Не удалось прочитать файл")

    def _update_thermal_view(self):
        """Обновление изображения на вкладке фильтра"""
        if self.processor.gray_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение на вкладке 'Загрузка'")
            return

        selected_style = self.combo_style.get()

        try:
            rgb_matrix = self.processor.apply_thermal_filter(selected_style)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр:\n{e}")
            return

        if rgb_matrix is None:
            messagebox.showerror("Ошибка", "Не удалось обработать изображение")
            return

        try:
            img = Image.fromarray(rgb_matrix)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать изображение:\n{e}")
            return

        img.thumbnail((400, 350))

        self.photo_result = self._pil_image_to_photo(img)
        self.lbl_result_view.configure(image=self.photo_result)

    def _save_file(self):
        """Логика кнопки 'Сохранить результат'"""
        if self.processor.current_processed_rgb is None:
            messagebox.showwarning("Предупреждение", "Сначала примените фильтр к изображению")
            return

        save_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
            title="Сохранить обработанное изображение"
        )

        if not save_path:
            return

        try:
            saved = self.processor.save_image(save_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
            return

        if saved:
            messagebox.showinfo("Успех", "Изображение успешно сохранено!")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл.")

    def _pil_image_to_photo(self, pil_img):
        if ImageTk is not None:
            return ImageTk.PhotoImage(pil_img)
        import io
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return tk.PhotoImage(data=buf.getvalue(), format="png")

if __name__ == "__main__":
    app = ThermalApp()
    app.mainloop()