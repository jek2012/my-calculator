import pandas as pd, io, urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        if mode == "В один этап (Стандарт)": self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера стандартный ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["work_standard"], "Сумма": b * pr["work_standard"]})
        elif mode == "1-й этап (Закладка трасс)": self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 1-й этап закладки ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["work_stage_1"], "Сумма": b * pr["work_stage_1"]})
        elif mode == "2-й этап (Навеска блоков)": self.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 2-й этап навески ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["work_stage_2"], "Сумма": b * pr["work_stage_2"]})
        if mode != "2-й этап (Навеска блоков)":
            if p > 0:
                self.h_data.append({"Раздел": "Климат", "Наименование": f"Медная фреоновая трасса ({p} м.)", "Кол-во": p, "Ед.изм": "м.", "Цена": pr["pipe"], "Сумма": p * pr["pipe"]})
                self.h_data.append({"Раздел": "Климат", "Наименование": f"Дренажный шланг ({p} м.)", "Кол-во": p, "Ед.изм": "м.", "Цена": pr["drain"], "Сумма": p * pr["drain"]})
            if b > 0: self.h_data.append({"Раздел": "Климат", "Наименование": f"Кронштейны внешнего блока ({b} компл.)", "Кол-во": b, "Ед.изм": "компл.", "Цена": pr["bracket"], "Сумма": b * pr["bracket"]})
        if pump > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Установка дренажной помпы", "Кол-во": pump, "Ед.изм": "шт.", "Цена": pr["pump"], "Сумма": pump * pr["pump"]})
        if box > 0: self.h_data.append({"Раздел": "Климат", "Наименование": "Монтаж декоративного короба", "Кол-во": box, "Ед.изм": "м.", "Цена": pr["box"], "Сумма": box * pr["box"]})
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
            {"Раздел": "Электрика", "Наименование": "Гофра защитная", "Кол-во": total_cable, "Ед.изм": "м.", "Цена": pr["corrugation"], "Сумма": total_cable * pr["corrugation"]},
            {"Раздел": "Электрика", "Наименование": "Крепеж/Клипсы для гофры", "Кол-во": clips_qty, "Ед.изм": "шт.", "Цена": pr["clips"], "Сумма": clips_qty * pr["clips"]}
        ]
        return sum(i["Сумма"] for i in self.e_data)

    def calc_plumb(self, pt, col):
        pr = self.prices["plumbing"]; total_pipe = pt * self.cp
        p_16, p_20, fit = round(total_pipe * 0.8, 1), round(total_pipe * 0.2, 1), pt * self.cf
        self.p_data = [
            {"Раздел": "Сантехника", "Наименование": f"Монтаж точек водоразбора ({pt} шт.)", "Кол-во": pt, "Ед.изм": "шт.", "Цена": pr["point"], "Сумма": pt * pr["point"]},
            {"Раздел": "Сантехника", "Наименование": "Установка коллекторов", "Кол-во": col, "Ед.изм": "шт.", "Цена": pr["collector"], "Сумма": col * pr["collector"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 16мм", "Кол-во": p_16, "Ед.изм": "м.", "Цена": pr["pipe_16"], "Сумма": p_16 * pr["pipe_16"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 20мм (магистраль)", "Кол-во": p_20, "Ед.изм": "м.", "Цена": pr["pipe_20"], "Сумма": p_20 * pr["pipe_20"]},
            {"Раздел": "Сантехника", "Наименование": "Аксиальные фитинги/водорозетки", "Кол-во": fit, "Ед.изм": "шт.", "Цена": pr["fitting"], "Сумма": fit * pr["fitting"]}
        ]
        return sum(i["Сумма"] for i in self.p_data)

    def get_excel_bytes(self, f_list, grand):
        df = pd.DataFrame(f_list); df_tot = pd.DataFrame([{"Раздел": "ИТОГО", "Наименование": "ОБЩАЯ СТОИМОСТЬ", "Кол-во": "", "Ед.изм": "", "Цена": "", "Сумма": grand}])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w: pd.concat([df, df_tot], ignore_index=True).to_excel(w, index=False)
        return buf.getvalue()

    def get_pdf_bytes(self, f_list, grand):
        font_res = urllib.request.urlopen("https://github.com")
        pdfmetrics.registerFont(TTFont('DejaVu', io.BytesIO(font_res.read())))
        buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30); story = []
        styles = getSampleStyleSheet()
        t_style = ParagraphStyle('T', parent=styles['Heading1'], fontName='DejaVu', fontSize=14, spaceAfter=20, alignment=1)
        c_style = ParagraphStyle('C', parent=styles['Normal'], fontName='DejaVu', fontSize=8, leading=10)
        h_style = ParagraphStyle('H', parent=styles['Normal'], fontName='DejaVu', fontSize=9, textColor=colors.whitesmoke)
        story.append(Paragraph("<b>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ ПО ИНЖЕНЕРИИ</b>", t_style)); story.append(Spacer(1, 10))
        t_data = [[Paragraph("<b>Раздел</b>", h_style), Paragraph("<b>Наименование работ</b>", h_style), Paragraph("<b>Кол-во</b>", h_style), Paragraph("<b>Ед.</b>", h_style), Paragraph("<b>Цена</b>", h_style), Paragraph("<b>Сумма</b>", h_style)]]
        for i in f_list: t_data.append([Paragraph(str(i["Раздел"]), c_style), Paragraph(str(i["Наименование"]), c_style), Paragraph(str(i["Кол-во"]), c_style), Paragraph(str(i["Ед.изм"]), c_style), Paragraph(f"{i['Цена']}", c_style), Paragraph(f"{i['Сумма']}", c_style)])
        tot_style = ParagraphStyle('Tot', parent=styles['Normal'], fontName='DejaVu', fontSize=9)
        t_data.append([Paragraph("<b>ИТОГО</b>", tot_style), Paragraph("<b>ОБЩАЯ СТОИМОСТЬ ПОД КЛЮЧ</b>", tot_style), "", "", "", Paragraph(f"<b>{grand} руб.</b>", tot_style)])
        t = Table(t_data, colWidths=[65, 250, 45, 35, 55, 70])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f538d')), ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        story.append(t); doc.build(story); buf.seek(0)
        return buf.getvalue()
