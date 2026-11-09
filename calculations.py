import pandas as pd, io, os

class Model:
    def __init__(self):
        self.prices = {
            "hvac": {
                "work_standard": 6000, "work_stage_1": 4500, "work_stage_2": 2500,
                "pipe": 1500, "bracket": 1200, "drain": 250, "pump": 5500,
                "box": 450, "chasing_brick": 500, "chasing_concrete": 1000, "coring": 2500
            },
            "electric": {
                "point": 450, "cable_1.5": 75, "cable_2.5": 110, "cable_4.0": 180,
                "corrugation": 40, "clips": 5, "breaker": 350, "chasing": 350
            },
            "plumbing": {
                "point": 3500, "pipe_16": 220, "pipe_20": 310, "collector": 8500, "fitting": 600
            }
        }
        self.cc, self.cp, self.cf = 5.0, 6.0, 2
        self.h_data, self.e_data, self.p_data = [], [], []
        self.load_local_prices()

    def load_local_prices(self):
        # Чтение сохраненного прайса из памяти сервера
        if os.path.exists("local_prices.txt"):
            try:
                p_map = {}
                with open("local_prices.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=")
                            p_map[k] = float(v)
                
                for k in self.prices["hvac"].keys():
                    if k in p_map: self.prices["hvac"][k] = p_map[k]
                    
                mapping_e = {"point": "point_el", "cable_1.5": "cable_1.5", "cable_2.5": "cable_2.5", "cable_4.0": "cable_4.0", "corrugation": "corrugation", "clips": "clips", "breaker": "breaker", "chasing": "chasing_el"}
                for k, target in mapping_e.items():
                    if target in p_map: self.prices["electric"][k] = p_map[target]
                    
                mapping_p = {"point": "point_pl", "pipe_16": "pipe_16", "pipe_20": "pipe_20", "collector": "collector", "fitting": "fitting"}
                for k, target in mapping_p.items():
                    if target in p_map: self.prices["plumbing"][k] = p_map[target]
            except: pass

    def save_local_prices(self):
        # Запись новых измененных админом цен в файл на сервере
        try:
            with open("local_prices.txt", "w", encoding="utf-8") as f:
                for k, v in self.prices["hvac"].items(): f.write(f"{k}={v}\n")
                
                mapping_e = {"point_el": "point", "cable_1.5": "cable_1.5", "cable_2.5": "cable_2.5", "cable_4.0": "cable_4.0", "corrugation": "corrugation", "clips": "clips", "breaker": "breaker", "chasing_el": "chasing"}
                for name_in_file, k in mapping_e.items(): f.write(f"{name_in_file}={self.prices['electric'][k]}\n")
                
                mapping_p = {"point_pl": "point", "pipe_16": "pipe_16", "pipe_20": "pipe_20", "collector": "collector", "fitting": "fitting"}
                for name_in_file, k in mapping_p.items(): f.write(f"{name_in_file}={self.prices['plumbing'][k]}\n")
            return True
        except: return False

    def calc_hvac(self, blocks, pipe, mode, pump, box, ch_b, ch_c, core):
        pr = self.prices["hvac"]; self.h_data = []
        if mode == "В один этап (Стандарт)":
            self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера стандартный ({blocks} шт.)", "Кол-во": blocks, "Ед.изм": "шт.", "Цена": pr["work_standard"], "Сумма": blocks * pr["work_standard"]})
        elif mode == "1-й этап (Закладка трасс)":
            self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 1-й этап закладки ({blocks} шт.)", "Кол-во": blocks, "Ед.изм": "шт.", "Цена": pr["work_stage_1"], "Сумма": blocks * pr["work_stage_1"]})
        elif mode == "2-й этап (Навеска блоков)":
            self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 2-й этап навески ({blocks} шт.)", "Кол-во": blocks, "Ед.изм": "шт.", "Цена": pr["work_stage_2"], "Сумма": blocks * pr["work_stage_2"]})
        if mode != "2-й этап (Навеска блоков)":
            if pipe > 0:
                self.h_data.append({"Раздел": "Климат", "Наименование": f"Медная фреоновая трасса ({pipe} м.)", "Кол-во": pipe, "Ед.изм": "м.", "Цена": pr["pipe"], "Сумма": pipe * pr["pipe"]})
                self.h_data.append({"Раздел": "Климат", "Наименование": f"Дренажный шланг ({pipe} м.)", "Кол-во": pipe, "Ед.изм": "м.", "Цена": pr["drain"], "Сумма": pipe * pr["drain"]})
            if blocks > 0:
                self.h_data.append({"Раздел": "Климат", "Наименование": f"Кронштейны внешнего блока ({blocks} компл.)", "Кол-во": blocks, "Ед.изм": "компл.", "Цена": pr["bracket"], "Сумма": blocks * pr["bracket"]})
        if pump > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Установка дренажной помпы", "Кол-во": pump, "Ед.изм": "шт.", "Цена": pr["pump"], "Сумма": pump * pr["pump"]})
        if box > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Монтаж декоративного короба", "Кол-во": box, "Ед.изм": "m.", "Цена": pr["box"], "Сумма": box * pr["box"]})
        if ch_b > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Штроба под трассу (Кирпич)", "Кол-во": ch_b, "Ед.изм": "м.", "Цена": pr["chasing_brick"], "Сумма": ch_b * pr["chasing_brick"]})
        if ch_c > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Штроба под трассу (Монолит)", "Кол-во": ch_c, "Ед.изм": "м.", "Цена": pr["chasing_concrete"], "Сумма": ch_c * pr["chasing_concrete"]})
        if core > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Алмазное бурение отверстия", "Кол-во": core, "Ед.изм": "шт.", "Цена": pr["coring"], "Сумма": core * pr["coring"]})
        return sum(i["Сумма"] for i in self.h_data)

    def calc_elec(self, pt, ch, breakers):
        pr = self.prices["electric"]; total_cable = pt * self.cc
        c_15, c_25, c_40 = round(total_cable * 0.3, 1), round(total_cable * 0.6, 1), round(total_cable * 0.1, 1)
        clips_qty = int(total_cable * 3)
        self.e_data = [
            {"Раздел": "Электрика", "Наименование": f"Монтаж точек ({pt} шт.)", "Кол-во": pt, "Ед.изм": "шт.", "Цена": pr["point"], "Сумма": pt * pr["point"]},
            {"Раздел": "Электрика", "Наименование": f"Штробление стен ({ch} м.)", "Кол-во": ch, "Ед.изм": "м.", "Цена": pr["chasing"], "Сумма": ch * pr["chasing"]},
            {"Раздел": "Электрика", "Наименование": "Установка автоматов в щит", "Кол-во": breakers, "Ед.изм": "шт.", "Цена": pr["breaker"], "Сумма": breakers * pr["breaker"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х1.5 (Свет)", "Кол-во": c_15, "Ед.изм": "м.", "Цена": pr["cable_1.5"], "Сумма": c_15 * pr["cable_1.5"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х2.5 (Розетки)", "Кол-во": c_25, "Ед.изм": "м.", "Цена": pr["cable_2.5"], "Сумма": c_25 * pr["cable_2.5"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х4.0 (Силовой)", "Кол-во": c_40, "Ед.изм": "м.", "Цена": pr["cable_4.0"], "Сумма": c_40 * pr["cable_4.0"]},
            {"Раздел": "Электрика", "Наименование": "Гофра защитная", "Кол-во": total_cable, "Ед.изм": "m.", "Цена": pr["corrugation"], "Сумма": total_cable * pr["corrugation"]},
            {"Раздел": "Электрика", "Наименование": "Крепеж/Клипсы для гофры", "Кол-во": clips_qty, "Ед.изм": "шт.", "Цена": pr["clips"], "Сумма": clips_qty * pr["clips"]}
        ]
        return sum(i["Сумма"] for i in self.e_data)

    def calc_plumb(self, pt, col):
        pr = self.prices["plumbing"]; total_pipe = pt * self.cp
        p_16, p_20, fit = round(total_pipe * 0.8, 1), round(total_pipe * 0.2, 1), pt * self.cf
        self.p_data = [
            {"Раздел": "Сантехника", "Наименование": f"Монтаж точек водоразбора ({pt} шт.)", "Кол-во": pt, "Ед.изм": "шт.", "Цена": pr["point"], "Сумма": pt * pr["point"]},
            {"Раздел": "Сантехника", "Наименование": "Установка коллекторов", "Кол-во": col, "Ед.изм": "шт.", "Цена": pr["collector"], "Сумма": col * pr["collector"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 16mm", "Кол-во": p_16, "Ед.изм": "м.", "Цена": pr["pipe_16"], "Сумма": p_16 * pr["pipe_16"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 20mm (magistral)", "Кол-во": p_20, "Ед.изм": "м.", "Цена": pr["pipe_20"], "Сумма": p_20 * pr["pipe_20"]},
            {"Раздел": "Сантехника", "Наименование": "Аксиальные фитинги/водорозетки", "Кол-во": fit, "Ед.изм": "шт.", "Цена": pr["fitting"], "Сумма": fit * pr["fitting"]}
        ]
        return sum(i["Сумма"] for i in self.p_data)

    def get_excel_bytes(self, full_list, grand_total):
        df = pd.DataFrame(full_list); df_tot = pd.DataFrame([{"Раздел": "ИТОГО", "Наименование": "ОБЩАЯ СТОИМОСТЬ", "Кол-во": "", "Ед.изм": "", "Цена": "", "Сумма": grand_total}])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer: pd.concat([df, df_tot], ignore_index=True).to_excel(writer, index=False)
        return buf.getvalue()

    def get_txt_bytes(self, full_list, grand_total):
        txt = "=========================================\n"
        txt += "   КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ (СМЕТА)\n"
        txt += "=========================================\n\n"
        for i in full_list:
            txt += f"[{i['Раздел']}] {i['Наименование']}\n  {i['Кол-во']} {i['Ед.изм']} х {i['Цена']} руб. = {i['Сумма']} руб.\n\n"
        txt += f"-----------------------------------------\nИТОГОВАЯ СТОИМОСТЬ ПОД КЛЮЧ: {grand_total} руб."
        return io.BytesIO(txt.encode('utf-8'))
