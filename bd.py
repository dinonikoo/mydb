import csv
import os
from typing import List, Dict, Any


class mydb:
    def __init__(self, file_path: str):

        self.file_path = file_path

        self.index_files = {
            "SN": "index_sn.csv",
            "Name": "index_name.csv",
            "Date": "index_date.csv",
            "Compliance Index": "index_compliance_index.csv",
            "Sold": "index_sold.csv",
        }

        self.indicesSN = {}  # хэш-таблицы для индексации (по полям)
        self.indicesNAME = {}
        self.indicesDATE = {}
        self.indicesIND = {}
        self.indicesSOLD = {}

        self.indicesSN = self.load_index(self.index_files["SN"])
        self.indicesNAME = self.load_index(self.index_files["Name"])
        self.indicesDATE = self.load_index(self.index_files["Date"])
        self.indicesIND = self.load_index(self.index_files["Compliance Index"])
        self.indicesSOLD = self.load_index(self.index_files["Sold"])

        self.removed = self.load_removed('removed.txt')


        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as file:
                writer = csv.writer(file)
                #writer.writerow(["SN", "Name", "Date", "Compliance Index", "Sold"])


    def load_removed(self, file_path: str): # загрузка removed из файла
        with open("removed.txt", "r") as file:
            numbers_from_file = [int(line.strip()) for line in file]
        return numbers_from_file

    def load_index(self, file_path: str): # загрузка хэш-таблиц из файла
        if not os.path.exists(file_path):
            return {}

        index = {}
        with open(file_path, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    key = row[0]
                    offsets = list(map(int, row[1:]))
                    index[key] = offsets
        return index

    def save_indices(self): # сохранение всех индексов из ОЗУ в файлы
        # словарь соответствий полей и хеш-таблиц
        indices_mapping = {
            "SN": (self.index_files["SN"], self.indicesSN),
            "Name": (self.index_files["Name"], self.indicesNAME),
            "Date": (self.index_files["Date"], self.indicesDATE),
            "Compliance Index": (self.index_files["Compliance Index"], self.indicesIND),
            "Sold": (self.index_files["Sold"], self.indicesSOLD),
        }

        for field, (file_path, index) in indices_mapping.items():
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                for key, offsets in index.items():
                    writer.writerow([key] + offsets)

        with open("removed.txt", "w") as file:
            for number in self.removed:
                file.write(f"{number}\n")

    def _load_data(self) -> List[Dict[str, Any]]: # загрузка всех данных из БД (для gui)
        table = []
        with open(self.file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if not line.startswith("------") and not line.startswith("SN"):
                    line.strip()
                    table.append(list(line.split(',')))
                    #reader = csv.DictReader(file)
            #return list(reader)
        print(table)
        return table


    def _load_data_all(self) -> List[Dict[str, Any]]: # с учётом пустых строчек
        table = []
        with open(self.file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if not line.startswith("SN"):
                    line.strip()
                    line = line[:-1]
                    table.append(list(line.split(',')))
                    #reader = csv.DictReader(file)
            #return list(reader)
        print(table)
        return table


    def search(self, field: str, value: str) -> list[dict]: # поиск записей по полю
        print(value)

        if field == "Compliance Index":
            index = self.indicesIND

        else:
            index = getattr(self, f"indices{field.upper()}", None)
        if index is None:
            return []

        # получаем список смещений для заданного значения
        offsets = index.get(str(value), [])
        print(offsets)
        if not offsets:
            return []


        results = []
        with open(self.file_path, "r") as file:
            for offset in offsets:
                file.seek(offset)
                line = file.readline().strip()
                if line[0] != "------":
                    results.append(dict(zip(["SN", "Name", "Date", "Compliance Index", "Sold"], line.split(","))))

        return results

    def insert(self, record: dict): # вставка новой записи
        if record["SN"] in self.indicesSN:
            print("Значение первичного ключа должно быть уникальным")
            return

        if len(self.removed) == 0:
            with open(self.file_path, "a", newline="") as file:
                writer = csv.writer(file)
                # получаем текущее смещение перед записью
                offset = file.tell()
                writer.writerow(record.values())
        else:
            # если есть удаленные записи, вставка пойдет вместо них
            offset = self.removed.pop()
            with open(self.file_path, "r+", newline="") as file:
                file.seek(offset)
                # Используем writer, чтобы сохранить правильный формат CSV
                writer = csv.writer(file)
                writer.writerow(record.values())


        # ОБНОВЛЕНИЕ ТАБЛИЦ
        for field, value in record.items():
            if field == "Compliance Index":
                index = self.indicesIND
            else:
                index = getattr(self, f"indices{field.upper()}", None)

            if index is not None:
                if value not in index:
                    index[value] = []
                index[value].append(offset)

    def update(self, record: dict): # обновление записи по SN
        if record["SN"] not in self.indicesSN:
            raise ValueError(f"Запись с ID={record['SN']} не найдена.")

        offset = self.indicesSN[record["SN"]][0]

        with open(self.file_path, "r+") as file:
            file.seek(offset)
            line = file.readline().strip()
            fields = line.split(",")

            print(offset)
            print(self.indicesNAME[fields[1]])
            print(self.indicesDATE[fields[2]])
            print(self.indicesIND[fields[3]])
            print(self.indicesSOLD[fields[4]])

            name = fields[1]
            if (name != record['Name']):
                self.indicesNAME[name].remove(offset)
                if record['Name'] not in self.indicesNAME:
                    self.indicesNAME[record['Name']] = []
                self.indicesNAME[record['Name']].append(offset)

            date = fields[2]
            if (date != record['Date']):
                self.indicesDATE[date].remove(offset)
                if record['Date'] not in self.indicesDATE:
                    self.indicesDATE[record['Date']] = []
                self.indicesDATE[record['Date']].append(offset)

            ind = fields[3]
            if (ind != record['Compliance Index']):
                self.indicesIND[ind].remove(offset)
                if record['Compliance Index'] not in self.indicesIND:
                    self.indicesIND[record['Compliance Index']] = []
                self.indicesIND[record['Compliance Index']].append(offset)

            sold = fields[4]
            if (sold != record['Sold']):
                self.indicesSOLD[sold].remove(offset)
                if record['Sold'] not in self.indicesSOLD:
                    self.indicesSOLD[record['Sold']] = []
                self.indicesSOLD[record['Sold']].append(offset)

            # Перезаписываем строку
            file.seek(offset)
            file.write(",".join(record.values()) + "\n")

    def delete(self, field: str, value: str): # удаление записи по полю-значению
        if field == "Compliance Index":
            index = self.indicesIND
        else:
            index = getattr(self, f"indices{field.upper()}", None)

        if index is None:
            raise ValueError(f"Индекс для поля {field} не существует.")

        # список смещений
        offsets = index.get(value, [])
        if not offsets:
            print(f"Записи с {field} = {value} не найдены.")
            return  # если нет записей

        # Открываем файл в режиме чтения и записи
        with open(self.file_path, "r+") as file:
            for offset in sorted(offsets):
                file.seek(offset)

                line = file.readline()
                #print(f"Processing line at offset {offset}: {line.strip()}")

                if not line:
                    print(f"Ошибка: строка по смещению {offset} не найдена!")
                    continue

                fields = line.strip().split(",")

                SN = fields[0]
                if SN in self.indicesSN:
                    del self.indicesSN[SN]

                name = fields[1]
                self.indicesNAME[name].remove(offset)

                date = fields[2]
                self.indicesDATE[date].remove(offset)

                ind = fields[3]
                self.indicesIND[ind].remove(offset)

                sold = fields[4]
                self.indicesSOLD[sold].remove(offset)

                # обновляем строку, заменяя SN на "------"
                fields[0] = "------"
                updated_line = ",".join(fields) + "\n"

                file.seek(offset)
                file.write(updated_line)

                self.removed.append(offset)
                print(f"Updated line at offset {offset}: {updated_line.strip()}")


            if (field == "Name"):
                del self.indicesNAME[value]
            elif (field == "Date"):
                del self.indicesDATE[value]
            elif (field == "Compliance Index"):
                del self.indicesIND[value]
            elif (field == "Sold"):
                del self.indicesSOLD[value]


        # self.save_indices()



if __name__ == "__main__":
    db = mydb("database.csv")

# writer.writerow(["SN", "Name", "Date", "Compliance Index", "Sold"])


    #db.insert({"SN": "000001", "Name": "RUSJ6789", "Date": "01/01/2004", "Compliance Index": "092", "Sold": "+"})
    #db.insert({"SN": "000002", "Name": "RULJ6789", "Date": "03/01/2005", "Compliance Index": "087", "Sold": "+"})
    #db.insert({"SN": "000003", "Name": "RULJ6789", "Date": "13/12/2006", "Compliance Index": "100", "Sold": "-"})
    #db.insert({"SN": "000004", "Name": "RUSJ6789", "Date": "01/01/2004", "Compliance Index": "092", "Sold": "+"})
    #db.insert({"SN": "000005", "Name": "RULJ6789", "Date": "03/01/2005", "Compliance Index": "087", "Sold": "+"})
    db.insert({"SN": "000002", "Name": "RUSJ6789", "Date": "13/12/2006", "Compliance Index": "100", "Sold": "-"})


    print("Поиск по полю: ", db.search("Name", "RUSJ6789"))

    # удаление
    #db.delete("Name", "RUSJ6789")

    db.save_indices()

    # db.delete("2")


    db._load_data()
