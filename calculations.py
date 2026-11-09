
import pandas as pd
import os

def load_excel_items():
    dynamic_items = {"hvac": {}, "electric": {}, "plumbing": {}}
    if os.path.exists("price_base.xlsx"):
        try:
            df = pd.read_excel("price_base.xlsx")
            for _, row in df.iterrows():
                sect = "hvac" if row["Раздел"] == "Климат" else ("electric" if row["Раздел"] == "Электрика" else "plumbing")
                t_name = str(row["Тех_Имя"]).strip()
                # Запоминаем только НОВЫЕ доп. позиции, которых изначально нет в коде
                standard_keys = ["work_standard", "work_stage_1", "work_stage_2", "pipe", "bracket", "drain", "pump", "box", "chasing_brick", "chasing_concrete", "coring", "point", "cable_1.5", "cable_2.5", "cable_4.0", "corrugation", "clips", "breaker", "chasing", "collector", "pipe_16", "pipe_20", "fitting"]
                if t_name not in standard_keys:
                    dynamic_items[sect][t_name] = {
                        "Наименование": row["Наименование"],
                        "Ед.изм": row["Ед_Изм"],
                        "Цена": float(row["Цена_База"])
                    }
        except:
            pass
    return dynamic_items
