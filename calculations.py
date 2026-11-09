import pandas as pd, io

class Model:
    def __init__(self):
        self.prices = {
            "hvac": {"work_standard": 6000, "work_stage_1": 4500, "work_stage_2": 2500, "pipe": 1500, "bracket": 1200, "drain": 250, "pump": 5500, "box": 450, "chasing_brick": 500, "chasing_concrete": 1000, "coring": 2500},
            "electric": {"point": 450, "cable_1.5": 75, "cable_2.5": 110, "cable_4.0": 180, "corrugation": 40, "clips": 5, "breaker": 350, "chasing": 350},
            "plumbing": {"point": 3500, "pipe_16": 220, "pipe_20": 310, "collector": 8500, "fitting": 600}
        }
        self.cc, self.cp, self.cf = 5.0, 6.0, 2
        self.h_data, self.e_data, self.p_data = [], [], []

    def calc_hvac(self, b, p, mode, pump, box, ch_b, ch_c, core):
        pr = self.prices["hvac"]; self.h_data = []
        if mode == "В один этап (Стандарт)": self.h_data.append({"Раздел": "Klimat", "Наименование": f"Montazh kondicionera standart ({b} sht.)", "Кол-во": b, "Ед.изм": "sht.", "Цена": pr["work_standard"], "Сумма": b * pr["work_standard"]})
        elif mode == "1-й этап (Закладка трасс)": self.h_data.append({"Раздел": "Klimat", "Наименование": f"Kondicioner: 1 etap zakladki ({b} sht.)", "Кол-во": b, "Ед.изм": "sht.", "Цена": pr["work_stage_1"], "Сумма": b * pr["work_stage_1"]})
        elif mode == "2-й этап (Навеска блоков)": self.h_data.append({"Раздел": "Klimat", "Наименование": f"Kondicioner: 2 etap naveski ({b} sht.)", "Кол-во": b, "Ед.изм": "sht.", "Цена": pr["work_stage_2"], "Сумма": b * pr["work_stage_2"]})
        if mode != "2-й этап (Навеска блоков)":
            if p > 0:
                self.h_data.append({"Раздел": "Klimat", "Наименование": f"Mednaya freonovaya trassa ({p} m.)", "Кол-во": p, "Ед.изм": "m.", "Цена": pr["pipe"], "Сумма": p * pr["pipe"]})
                self.h_data.append({"Раздел": "Klimat", "Наименование": f"Drenazhniy shlang ({p} m.)", "Кол-во": p, "Ед.изм": "m.", "Цена": pr["drain"], "Сумма": p * pr["drain"]})
            if b > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": f"Kronshteyni vneshnego bloka ({b} kompl.)", "Кол-во": b, "Ед.изм": "kompl.", "Цена": pr["bracket"], "Сумма": b * pr["bracket"]})
        if pump > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": "Ustanovka drenazhnoy pompi", "Кол-во": pump, "Ед.изм": "sht.", "Цена": pr["pump"], "Сумма": pump * pr["pump"]})
        if box > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": "Montazh dekorativnogo koroba", "Кол-во": box, "Ед.изм": "m.", "Цена": pr["box"], "Сумма": box * pr["box"]})
        if ch_b > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": "Shtroba pod trassu (Kirpich)", "Кол-во": ch_b, "Ед.изм": "m.", "Цена": pr["chasing_brick"], "Сумма": ch_b * pr["chasing_brick"]})
        if ch_c > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": "Shtroba pod trassu (Monolit)", "Кол-во": ch_c, "Ед.изм": "m.", "Цена": pr["chasing_concrete"], "Сумма": ch_c * pr["chasing_concrete"]})
        if core > 0: self.h_data.append({"Раздел": "Klimat", "Наименование": "Almaznoe burenie otverstiya", "Кол-во": core, "Ед.изм": "sht.", "Цена": pr["coring"], "Сумма": core * pr["coring"]})
        return sum(i["Сумма"] for i in self.h_data)

    def calc_elec(self, pt, ch, breakers):
        pr = self.prices["electric"]; total_cable = pt * self.cc
        c_15, c_25, c_40 = round(total_cable * 0.3, 1), round(total_cable * 0.6, 1), round(total_cable * 0.1, 1)
        clips_qty = int(total_cable * 3)
        self.e_data = [
            {"Раздел": "Elektrika", "Наименование": f"Montazh tochek ({pt} sht.)", "Кол-во": pt, "Ед.изм": "sht.", "Цена": pr["point"], "Сумма": pt * pr["point"]},
            {"Раздел": "Elektrika", "Наименование": f"Shtroblenie sten ({ch} m.)", "Кол-во": ch, "Ед.изм": "m.", "Цена": pr["chasing"], "Сумма": ch * pr["chasing"]},
            {"Раздел": "Elektrika", "Наименование": "Ustanovka avtomatov v schit", "Кол-во": breakers, "Ед.изм": "sht.", "Цена": pr["breaker"], "Сумма": breakers * pr["breaker"]},
            {"Раздел": "Elektrika", "Наименование": "Kabel VVGng 3x1.5 (Svet)", "Кол-во": c_15, "Ед.изм": "m.", "Цена": pr["cable_1.5"], "Сумма": c_15 * pr["cable_1.5"]},
            {"Раздел": "Elektrika", "Наименование": "Kabel VVGng 3x2.5 (Rozetki)", "Кол-во": c_25, "Ед.изм": "m.", "Цена": pr["cable_2.5"], "Сумма": c_25 * pr["cable_2.5"]},
            {"Раздел": "Elektrika", "Наименование": "Kabel VVGng 3x4.0 (Silovoy)", "Кол-во": c_40, "Ед.изм": "m.", "Цена": pr["cable_4.0"], "Сумма": c_40 * pr["cable_4.0"]},
            {"Раздел": "Elektrika", "Наименование": "Gofra zaschitnaya", "Кол-во": total_cable, "Ед.изм": "m.", "Цена": pr["corrugation"], "Сумма": total_cable * pr["corrugation"]},
            {"Раздел": "Elektrika", "Наименование": "Krepezh/Klipsi dlya gofri", "Кол-во": clips_qty, "Ед.изм": "sht.", "Цена": pr["clips"], "Сумма": clips_qty * pr["clips"]}
        ]
        return sum(i["Сумма"] for i in self.e_data)

    def calc_plumb(self, pt, col):
        pr = self.prices["plumbing"]; total_pipe = pt * self.cp
        p_16, p_20, fit = round(total_pipe * 0.8, 1), round(total_pipe * 0.2, 1), pt * self.cf
        self.p_data = [
            {"Раздел": "Santehnika", "Наименование": f"Montazh tochek vodorazbora ({pt} sht.)", "Кол-во": pt, "Ед.изм": "sht.", "Цена": pr["point"], "Сумма": pt * pr["point"]},
            {"Раздел": "Santehnika", "Наименование": "Ustanovka kollektorov", "Кол-во": col, "Ед.изм": "sht.", "Цена": pr["collector"], "Сумма": col * pr["collector"]},
            {"Раздел": "Santehnika", "Наименование": "Truba PEX 16mm", "Кол-во": p_16, "Ед.изм": "m.", "Цена": pr["pipe_16"], "Сумма": p_16 * pr["pipe_16"]},
            {"Раздел": "Santehnika", "Наименование": "Truba PEX 20mm (magistral)", "Кол-во": p_20, "Ед.изм": "m.", "Цена": pr["pipe_20"], "Сумма": p_20 * pr["pipe_20"]},
            {"Раздел": "Santehnika", "Наименование": "Aksialnie fitingi/vodorozetki", "Кол-во": fit, "Ед.изм": "sht.", "Цена": pr["fitting"], "Сумма": fit * pr["fitting"]}
        ]
        return sum(i["Сумма"] for i in self.p_data)

    def get_excel_bytes(self, f_list, grand):
        df = pd.DataFrame(f_list); df_tot = pd.DataFrame([{"Раздел": "ИТОГО", "Наименование": "ОБЩАЯ СТОИМОСТЬ", "Кол-во": "", "Ед.изм": "", "Цена": "", "Сумма": grand}])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w: pd.concat([df, df_tot], ignore_index=True).to_excel(w, index=False)
        return buf.getvalue()

    def get_pdf_bytes(self, f_list, grand):
        # Используем только стандартные, встроенные в интернет-сервер модули сборки текстового бланка
        txt = "=========================================\n"
        txt += "   KOMMERCHESKOE PREDLOZHENIE (SMETA)\n"
        txt += "=========================================\n\n"
        for i in f_list:
            txt += f"[{i['Раздел']}] {i['Наименование']}\n"
            txt += f"  {i['Кол-во']} {i['Ед.изм']} x {i['Цена']} rub. = {i['Сумма']} rub.\n\n"
        txt += "-----------------------------------------\n"
        txt += f"ITOGOVAYA STOIMOST: {grand} rub."
        return io.BytesIO(txt.encode('utf-8'))
