import csv
import shutil
import tkinter as tk
from tkinter import messagebox

from openpyxl.workbook import Workbook
from tkcalendar import DateEntry
from tkinter import ttk


class mygui:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("mydb")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()

    def create_widgets(self):

        validate_sn = self.root.register(self.validate_sn)
        validate_name = self.root.register(self.validate_name)

        # кнопки вверху справа
        self.print_button = tk.Button(self.root, text="Print Table", command=self.print)
        self.print_button.grid(row=0, column=3)

        self.erase_button = tk.Button(self.root, text="Delete Null Spaces", command=self.hard_erase)
        self.erase_button.grid(row=0, column=2)

        self.delete_button = tk.Button(self.root, text="DELETE ALL", command=self.delete_all)
        self.delete_button.grid(row=1, column=2)

        self.backup_button = tk.Button(self.root, text="Make backup files", command=self.backup)
        self.backup_button.grid(row=1, column=3)

        self.load_button = tk.Button(self.root, text="Load from backup", command=self.load_from_backup)
        self.load_button.grid(row=2, column=3)

        self.import_button = tk.Button(self.root, text="Import to .xlsx", command=self.import_)
        self.import_button.grid(row=3, column=3)


        # поля для ввода
        self.sn_label = tk.Label(self.root, text="SN:")
        self.sn_label.grid(row=0, column=0)

        self.sn_entry = tk.Entry(self.root, validate="key", validatecommand=(validate_sn, "%P"))
        self.sn_entry.grid(row=0, column=1)

        self.name_label = tk.Label(self.root, text="Name:")
        self.name_label.grid(row=1, column=0)
        self.name_entry = tk.Entry(self.root, validate="key", validatecommand=(validate_name, "%P"))
        self.name_entry.grid(row=1, column=1)


        self.date_label = tk.Label(self.root, text="Date:")
        self.date_label.grid(row=2, column=0)
        self.date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=2, column=1)

        self.compliance_label = tk.Label(self.root, text="Compliance Index:")
        self.compliance_label.grid(row=4, column=0)

        # Ползунок от 0 до 1 с шагом 0.01
        self.compliance_scale = tk.Scale(self.root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01, length=300)
        self.compliance_scale.grid(row=4, column=1)

        self.sold_label = tk.Label(self.root, text="Sold:")
        self.sold_label.grid(row=5, column=0)

        self.sold_var = tk.StringVar(self.root)
        self.sold_var.set("-")
        self.sold_option = tk.OptionMenu(self.root, self.sold_var, "-", "+")
        self.sold_option.grid(row=5, column=0, columnspan = 2)

        self.insert_button = tk.Button(self.root, text="Insert Record", command=self.insert_record)
        self.insert_button.grid(row=7, column=0, columnspan=2)

        self.update_button = tk.Button(self.root, text="Update Record (by SN)", command=self.update_record)
        self.update_button.grid(row=7, column=1, columnspan=2)

        self.search_label = tk.Label(self.root, text="Search by:")
        self.search_label.grid(row=8, column=0)
        self.search_var = tk.StringVar(self.root)
        self.search_var.set("SN")
        self.search_option = tk.OptionMenu(self.root, self.search_var, "SN", "Name", "Date", "Compliance Index", "Sold")  # Опции для выбора
        self.search_option.grid(row=8, column=1)
        self.key_entry = tk.Entry(self.root)
        self.key_entry.grid(row=8, column=2)

        self.search_button = tk.Button(self.root, text="Search", command=self.search_record)
        self.search_button.grid(row=9, column=0, columnspan=2)

        self.delete_button = tk.Button(self.root, text="Delete found records", command=self.delete_record)
        self.delete_button.grid(row=11, column=0, columnspan=2)



        self.tree = ttk.Treeview(self.root, columns=("SN", "Name", "Date", "Compliance Index", "Sold"), show="headings")
        self.tree.grid(row=13, column=0, columnspan=3)
        # заголовки
        self.tree.heading("SN", text="SN")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Sold", text="Sold")
        self.tree.heading("Compliance Index", text="Compliance Index")


        self.tree.column("SN", width=100, anchor="center")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Sold", width=50, anchor="center")
        self.tree.column("Compliance Index", width=150, anchor="center")

    def validate_sn(self, value):

        if value == "":
            return True
        if value.isdigit() and len(value) <= 6:
            return True
        else:
            return False

    def validate_name(self, value):

        if value == "":
            return True
        if len(value) <= 6:
            return True
        else:
            return False

    def insert_record(self):

        sn = self.sn_entry.get()
        name = self.name_entry.get()
        date = self.date_entry.get()
        compliance_index = self.compliance_scale.get()
        sold = self.sold_var.get()

        # проверка за заполненность полей
        if not sn or not name or not date or not compliance_index or not sold:
            messagebox.showerror("Error", "Заполните все поля! Они должны быть не пусты или больше 0")
            return

        if len(sn) != 6:
            messagebox.showerror("Error", "Серийный номер должен быть длиной 6 символов")
            return

        if len(name) != 6:
            messagebox.showerror("Error", "Название детали должно быть длиной 6 символов")
            return

        date_ = list(date.split('/'))
        print(date_)
        date_ = [i.zfill(2) for i in date_]
        dat = '/'.join(date_)
        print(dat)

        cid = str(compliance_index)
        if len(cid) < 4:
            cid += '0'

        record = {
            "SN": sn,
            "Name": name,
            "Date": dat,
            "Compliance Index": cid,
            "Sold": sold,
        }
        self.db.insert(record) # добавление
        self.print() # печать таблицы

       # self.sn_entry.delete(0, tk.END)
       # self.name_entry.delete(0, tk.END)
       # self.date_entry.delete(0, tk.END)
       # self.compliance_entry.delete(0, tk.END)
       # self.sold_entry.delete(0, tk.END)



    def update_record(self):

        sn = self.sn_entry.get()
        name = self.name_entry.get()
        date = self.date_entry.get()
        compliance_index = self.compliance_scale.get()
        sold = self.sold_var.get()

        # проверка
        if not sn or not name or not date or not compliance_index or not sold:
            messagebox.showerror("Error", "Заполните все поля! Они должны быть не пусты или больше 0")
            return

        date_ = list(date.split('/'))
        print(date_)
        date_ = [i.zfill(2) for i in date_]
        dat = '/'.join(date_)
        print(dat)

        cid = str(compliance_index)
        if len(cid) < 4:
            cid += '0'

        record = {
            "SN": sn,
            "Name": name,
            "Date": dat,
            "Compliance Index": cid,
            "Sold": sold,
        }
        self.db.update(record) # обновление записи
        self.print()


       # self.sn_entry.delete(0, tk.END)
       # self.name_entry.delete(0, tk.END)
       # self.date_entry.delete(0, tk.END)
       # self.compliance_entry.delete(0, tk.END)
       # self.sold_entry.delete(0, tk.END)

    def on_closing(self):

        self.db.save_indices()
        messagebox.showinfo("Info", "Сохранение индексов перед закрытием...")
        self.root.destroy()

    def search_record(self):
        # значение для поиска
        key = self.key_entry.get()

        if not key:
            messagebox.showerror("Error", "Введите что-нибудь!")
            return
        search = self.search_var.get()
        #print(key)
        # поиск записей
        results = self.db.search(search, str(key))

        #
        #self.results_text.delete(1.0, tk.END)
        #if not results:
        #    self.results_text.insert(tk.END, "No records found.")
        #else:
        #    for record in results:
        #        self.results_text.insert(tk.END, f"{record}\n")

        # очистка старой таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # добавляем новые
        if len(results) != 0:
            for record in results:
                    self.tree.insert("", "end", values=(
                        record['SN'], record['Name'], record['Date'], record['Compliance Index'], record['Sold']))



    def print(self):
            # очистка
            for row in self.tree.get_children():
                self.tree.delete(row)

            # получаем из бд
            records = self.db._load_data()
            print(records)
            # выводим (добавляем в таблицу)
            if len(records) != 0:
                for record in records:
                    if len(record)==5:
                        self.tree.insert("", "end", values=(
                 record[0], record[1], record[2], record[3], record[4]))

    def delete_record(self):
        # значение для удаления
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Введите что-нибудь!")
            return

        search = self.search_var.get()

        # удаление
        self.db.delete(search, str(key))
        #self.results_text.delete(1.0, tk.END)

        self.print()


    def hard_erase(self):       # убирает удалённые записи из файлов

            records = self.db._load_data()

            # список без удаленных строк
            updated_records = []

            for record in records:
                if record[0] != "------":
                    if '+' in record[4]:
                        record[4] = '+'
                    if '-' in record[4]:
                        record[4] = '-'
                    # строки с "------" в поле SN считаются удалёнными
                    updated_records.append(record)

            print(updated_records)
            self.db.indicesSN = {}
            self.db.indicesNAME = {}
            self.db.indicesDATE = {}
            self.db.indicesIND = {}
            self.db.indicesSOLD = {}

            with open(self.db.file_path, "w", newline="") as file:
                for row in updated_records:
                    print(row)
                    writer = csv.writer(file)
                    # получаем смещение
                    offset = file.tell()
                    writer.writerow(row)
                    if row[0] not in self.db.indicesSN:
                        self.db.indicesSN[row[0]] = []
                    self.db.indicesSN[row[0]].append(offset)

                    if row[1] not in self.db.indicesNAME:
                        self.db.indicesNAME[row[1]] = []
                    self.db.indicesNAME[row[1]].append(offset)
                    if row[2] not in self.db.indicesDATE:
                        self.db.indicesDATE[row[2]] = []
                    self.db.indicesDATE[row[2]].append(offset)
                    if row[3] not in self.db.indicesIND:
                        self.db.indicesIND[row[3]] = []
                    self.db.indicesIND[row[3]].append(offset)
                    if row[4] not in self.db.indicesSOLD:
                        self.db.indicesSOLD[row[4]] = []
                    self.db.indicesSOLD[row[4]].append(offset)
            self.db.removed = []
            print("Все удалённые записи перезаписаны, и хэш-таблицы пересозданы.")


    def delete_all(self):
        with open("database.csv", "w") as file:
            pass
        with open("index_sn.csv", "w") as file:
            pass
        with open("index_name.csv", "w") as file:
            pass
        with open("index_date.csv", "w") as file:
            pass
        with open("index_compliance_index.csv", "w") as file:
            pass
        with open("index_sold.csv", "w") as file:
            pass
        with open("removed.txt", "w") as file:
            pass

        self.db.indicesSN = {}
        self.db.indicesNAME = {}
        self.db.indicesDATE = {}
        self.db.indicesIND = {}
        self.db.indicesSOLD = {}
        self.db.removed = []

        self.print()

    def backup(self):
        self.db.save_indices()
        shutil.copy('database.csv', 'backup_database.csv')
        shutil.copy('index_sn.csv', 'backup_index_sn.csv')
        shutil.copy('index_name.csv', 'backup_index_name.csv')
        shutil.copy('index_date.csv', 'backup_index_date.csv')
        shutil.copy('index_compliance_index.csv', 'backup_index_compliance_index.csv')
        shutil.copy('index_sold.csv', 'backup_index_sold.csv')
        shutil.copy('removed.txt', 'backup_removed.txt')
        messagebox.showinfo("Info", "Таблица и служебные файлы сохранены в backup.")

    def load_from_backup(self):
        self.db.save_indices()
        shutil.copy('backup_database.csv', 'database.csv')
        self.db.indicesSN = self.db.load_index('backup_index_sn.csv')
        self.db.indicesNAME = self.db.load_index('backup_index_name.csv')
        self.db.indicesDATE = self.db.load_index('backup_index_date.csv')
        self.db.indicesIND = self.db.load_index('backup_index_compliance_index.csv')
        self.db.indicesSOLD = self.db.load_index('backup_index_sold.csv')
        self.db.removed = self.db.load_removed('backup_removed.txt')
        messagebox.showinfo("Info", "Таблица и служебные файлы загружены из backup.")


    def import_(self):

        rows = self.db._load_data()

        # новый список строк без удалённых
        updated_rows = []


        for idx, row in enumerate(rows):
            if row[0] != "------":
                updated_rows.append(row)

        workbook = Workbook()
        sheet = workbook.active  # активный лист

        # заголовки
        sheet.append(["SN", "Name", "Date", "Compliance Index", "Sold"])

        for row in updated_rows:
            sheet.append(row)

        workbook.save("imported.xlsx")

        messagebox.showinfo("Info", "Создан файл imported.xlsx!")