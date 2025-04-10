import tkinter as tk
import ttkbootstrap as ttk

class PreviewWindow(ttk.Toplevel):
    """Универсальное окно предпросмотра данных"""
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title("Просмотр данных")
        self.geometry("800x400")
        
        # Создание Treeview
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = list(data.columns)
        
        # Настройка колонок
        for col in data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Добавление данных
        for _, row in data.head(100).iterrows():
            self.tree.insert("", "end", values=list(row))
        
        # Скроллбары
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)