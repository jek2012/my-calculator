import pandas as pd, io, os

class Model:
    def __init__(self):
        self.cc, self.cp, self.cf = 5.0, 6.0, 2
        self.h_data, self.e_data, self.p_data = [], [], []
        self.prices = {}
        self.load_base_table()

    def load_base_table(self):
        if os.path.exists("price_base.xlsx"):
            try:
                df = pd.read_excel("price_base.xlsx")
                for _, row in df.iterrows():
                    sect = "hvac" if row["Раздел"] == "Климат" else ("electric" if row["Раздел"] == "Электрика" else "plumbing")
                    if sect not in self.prices: self.prices[sect] = {}
                    # Принудительно сопоставляем столбцы, чтобы Ед_Изм и Ед.изм не путались
                    self.prices[sect][row["Тех_Имя"]] = {
                        "Наименование": row["Наименование"],
                        "Ед.изм": row["Ед_Изм"], # Делаем внутренний ключ, который ищет web_app.py
                        "Цена": row["Цена_База"],
                        "Тип_Ввода": row["Тип_Ввода"],
                        "Раздел_Рус": row["Раздел"]
                    }
            except: pass
        self.load_local_prices()

    def load_local_prices(self):
        if os.path.exists("local_prices.txt") and self.prices:
            try:
                with open("local_prices.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=")
                            for sect in self.prices.values():
                                if k in sect: sect[k]["Цена"] = float(v)
            except: pass

    def save_local_prices(self):
        try:
            with open("local_prices.txt", "w", encoding="utf-8") as f:
                for sect in self.prices.values():
                    for k, item in sect.items():
                        f.write(f"{k}={item['Цена']}\n")
            return True
        except: return False

    def calc_section(self, section_name, inputs, points_qty=0):
        sect = "hvac" if section_name == "Климат" else ("electric" if section_name == "Электрика" else "plumbing")
        result_data = []
        if sect not in self.prices: return [], 0

        for k, item in self.prices[sect].items():
            qty = 0
            if item["Тип_Ввода"] == "число" and k in inputs:
                qty = inputs[k]
            elif item["Тип_Ввода"] == "коэффициент" and points_qty > 0:
                if sect == "electric":
                    coef = self.cc
                    if "1.5" in item["Наименование"]: qty = round(points_qty * coef * 0.3, 1)
                    elif "2.5" in item["Наименование"]: qty = round(points_qty * coef * 0.6, 1)
                    elif "4.0" in item["Наименование"]: qty = round(points_qty * coef * 0.1, 1)
                    elif "clips" in k or "Крепеж" in item["Наименование"]: qty = int(points_qty * coef * 3)
                    else: qty = points_qty * coef
                elif sect == "plumbing":
                    coef = self.cp
                    if "16mm" in k or "16мм" in item["Наименование"]: qty = round(points_qty * coef * 0.8, 1)
                    elif "20mm" in k or "20мм" in item["Наименование"]: qty = round(points_qty * coef * 0.2, 1)
                    elif "fitting" in k or "Фитинги" in item["Наименование"]: qty = points_qty * self.cf

            if qty > 0:
                result_data.append({
                    "Раздел": item["Раздел_Рус"],
                    "Наименование": item["Наименование"],
                    "Кол-во": qty,
                    "Ед.изм": item["Ед.изм"],
                    "Цена": item["Цена"],
                    "Сумма": qty * item["Цена"]
                })

        total = sum(i["Сумма"] for i in result_data)
        if sect == "hvac": self.h_data = result_data
        elif sect == "electric": self.e_data = result_data
        else: self.p_data = result_data
        return result_data, total
