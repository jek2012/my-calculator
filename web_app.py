import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Калькулятор смет под ключ", layout="centered")
P_ADMIN, P_GUEST = "admin", "123"

# --- ИНИЦИАЛИЗАЦИЯ БАЗОВОГО ПРАЙС-ЛИСТА И ПАМЯТИ СЕРВЕРА ---
if "prices" not in st.session_state:
    st.session_state.prices = {
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
    st.session_state.cc, st.session_state.cp, st.session_state.cf = 5.0, 6.0, 2
    st.session_state.h_data, st.session_state.e_data, st.session_state.p_data = [], [], []
    
    # Автоматическое считывание сохраненных админом цен из файла local_prices.txt
    if os.path.exists("local_prices.txt"):
        try:
            with open("local_prices.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=")
                        for s in ["hvac", "electric", "plumbing"]:
                            if k in st.session_state.prices[s]:
                                st.session_state.prices[s][k] = float(v)
        except:
            pass

pr = st.session_state.prices

# --- НАША ИДЕАЛЬНАЯ ГРАФИЧЕСКАЯ ФУНКЦИЯ ДЛЯ ЗАГОЛОВКОВ ---
def draw_text_header(text, is_main=False):
    margin_b = "20px" if is_main else "15px"
    if is_main:
        html = f"""<div style="background:rgba(255,255,255,0.05);border-left:5px solid #1f538d;padding:15px 20px;border-radius:8px;margin-bottom:{margin_b};margin-top:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);"><span style="font-size:22px;vertical-align:middle;">🏗️ </span><span style="font-family:'Segoe UI',Arial,sans-serif;font-size:clamp(20px,4vw,26px);font-weight:800;color:currentColor;line-height:1.3;">{text}</span></div>"""
    else:
        html = f"""<div style="font-family:'Segoe UI',Arial,sans-serif;font-size:clamp(16px,2.5vw,20px);font-weight:600;color:currentColor;line-height:1.4;margin-bottom:{margin_b};margin-top:15px;">{text}</div>"""
    st.markdown(html, unsafe_allow_html=True)

# --- ЭКРАН ЗАЩИТЫ И АВТОРИЗАЦИИ ---
if "auth" not in st.session_state:
    st.session_state.auth, st.session_state.role = False, None

if not st.session_state.auth:
    draw_text_header("Вход в Калькулятор Смет", is_main=True)
    user_pass = st.text_input("Введите код доступа:", type="password")
    if st.button("Войти", type="primary", use_container_width=True):
        if user_pass == P_ADMIN:
            st.session_state.auth, st.session_state.role = True, "admin"
            st.rerun()
        elif user_pass == P_GUEST:
            st.session_state.auth, st.session_state.role = True, "guest"
            st.rerun()
        else:
            st.error("Неверный код доступа!")
    st.stop()

# --- ОТРИСОВКА ГЛАВНОЙ ШАПКИ И ТАБОВ ---
draw_text_header("Инженерный калькулятор смет", is_main=True)
st.caption(f"Роль: {'Администратор' if st.session_state.role == 'admin' else 'Гость'}")

t_list = ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "📊 Расход", "💰 Цены", "🧾 Итог"] if st.session_state.role == "admin" else ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "🧾 Итог"]
tabs = st.tabs(t_list)

if st.session_state.role == "admin":
    tab_hvac, tab_elec, tab_plumb, tab_coef, tab_prices, tab_est = tabs
else:
    tab_hvac, tab_elec, tab_plumb, tab_est = tabs
    tab_coef, tab_prices = None, None
with tab_hvac:
    draw_text_header("Кондиционирование и вентиляция")
    b = st.number_input("Блоки (шт)", min_value=0, value=0, key="h_b")
    p = st.number_input("Трасса (м)", min_value=0.0, value=0.0, key="h_p")
    mode = st.selectbox("Схема", ["В один этап (Стандарт)", "1-й этап (Закладка трасс)", "2-й этап (Навеска блоков)"])
    with st.expander("Доп.Работы"):
        pump = st.number_input("Помпы (шт)", min_value=0, value=0, key="h_pump")
        box = st.number_input("Короб (м)", min_value=0.0, value=0.0, key="h_box")
        core = st.number_input("Бурение отверстий (шт)", min_value=0, value=0, key="h_core")
        ch_b = st.number_input("Штроба кирпич (м)", min_value=0.0, value=0.0, key="h_ch_b")
        ch_c = st.number_input("Штроба монолит (м)", min_value=0.0, value=0.0, key="h_ch_c")
    if st.button("Рассчитать климат", type="primary", key="btn_h"):
        st.session_state.h_data = []
        if mode == "В один этап (Стандарт)":
            st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера стандартный ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["hvac"]["work_standard"], "Сумма": b * pr["hvac"]["work_standard"]})
        elif mode == "1-й этап (Закладка трасс)":
            st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 1-й этап закладки ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["hvac"]["work_stage_1"], "Сумма": b * pr["hvac"]["work_stage_1"]})
        elif mode == "2-й этап (Навеска блоков)":
            st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Монтаж кондиционера: 2-й этап навески ({b} шт.)", "Кол-во": b, "Ед.изм": "шт.", "Цена": pr["hvac"]["work_stage_2"], "Сумма": b * pr["hvac"]["work_stage_2"]})
        if mode != "2-й этап (Навеска блоков)":
            if p > 0:
                st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Медная фреоновая трасса ({p} м.)", "Кол-во": p, "Ед.изм": "м.", "Цена": pr["hvac"]["pipe"], "Сумма": p * pr["hvac"]["pipe"]})
                st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Дренажный шланг ({p} м.)", "Кол-во": p, "Ед.изм": "м.", "Цена": pr["hvac"]["drain"], "Сумма": p * pr["hvac"]["drain"]})
            if b > 0:
                st.session_state.h_data.append({"Раздел": "Климат", "Наименование": f"Кронштейны внешнего блока ({b} компл.)", "Кол-во": b, "Ед.изм": "компл.", "Цена": pr["hvac"]["bracket"], "Сумма": b * pr["hvac"]["bracket"]})
        if pump > 0: st.session_state.h_data.append({"Раздел": "Климат", "Наименование": "Установка дренажной помпы", "Кол-во": pump, "Ед.изм": "шт.", "Цена": pr["hvac"]["pump"], "Сумма": pump * pr["hvac"]["pump"]})
        if box > 0: st.session_state.h_data.append({"Раздел": "Климат", "Наименование": "Монтаж декоративного короба", "Кол-во": box, "Ед.изм": "m.", "Цена": pr["hvac"]["box"], "Сумма": box * pr["hvac"]["box"]})
        if ch_b > 0: st.session_state.h_data.append({"Раздел": "Климат", "Наименование": "Штроба под трассу (Кирпич)", "Кол-во": ch_b, "Ед.изм": "м.", "Цена": pr["hvac"]["chasing_brick"], "Сумма": ch_b * pr["hvac"]["chasing_brick"]})
        if ch_c > 0: st.session_state.h_data.append({"Раздел": "Климат", "Наименование": "Штроба под трассу (Монолит)", "Кол-во": ch_c, "Ед.изм": "м.", "Цена": pr["hvac"]["chasing_concrete"], "Сумма": ch_c * pr["hvac"]["chasing_concrete"]})
        if core > 0: st.session_state.h_data.append({"Раздел": "Климат", "Наименование": "Алмазное бурение отверстия", "Кол-во": core, "Ед.изм": "шт.", "Цена": pr["hvac"]["coring"], "Сумма": core * pr["hvac"]["coring"]})
        st.success(f"Всего по разделу: {sum(i['Сумма'] for i in st.session_state.h_data)} руб.")

with tab_elec:
    draw_text_header("Электрика и силовые щиты")
    pt = st.number_input("Количество точек (шт)", min_value=0, value=0, key="e_pt")
    ch = st.number_input("Штроба всего (м)", min_value=0.0, value=0.0, key="e_ch")
    eb = st.number_input("Автоматы в щит (шт)", min_value=0, value=0, key="e_eb")
    if st.button("Рассчитать электрику", type="primary", key="btn_e"):
        tc = pt * st.session_state.cc
        c15, c25, c40 = round(tc * 0.3, 1), round(tc * 0.6, 1), round(tc * 0.1, 1)
        cl = int(tc * 3)
        st.session_state.e_data = [
            {"Раздел": "Электрика", "Наименование": f"Монтаж точек ({pt} шт.)", "Кол-во": pt, "Ед.изм": "шт.", "Цена": pr["electric"]["point"], "Сумма": pt * pr["electric"]["point"]},
            {"Раздел": "Электрика", "Наименование": f"Штробление стен ({ch} м.)", "Кол-во": ch, "Ед.изм": "м.", "Цена": pr["electric"]["chasing"], "Сумма": ch * pr["electric"]["chasing"]},
            {"Раздел": "Электрика", "Наименование": "Установка автоматов в щит", "Кол-во": eb, "Ед.изм": "шт.", "Цена": pr["electric"]["breaker"], "Сумма": eb * pr["electric"]["breaker"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х1.5 (Свет)", "Кол-во": c15, "Ед.изм": "м.", "Цена": pr["electric"]["cable_1.5"], "Сумма": c15 * pr["electric"]["cable_1.5"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х2.5 (Розетки)", "Кол-во": c25, "Ед.изм": "м.", "Цена": pr["electric"]["cable_2.5"], "Сумма": c25 * pr["electric"]["cable_2.5"]},
            {"Раздел": "Электрика", "Наименование": "Кабель ВВГнг 3х4.0 (Силовой)", "Кол-во": c40, "Ед.изм": "м.", "Цена": pr["electric"]["cable_4.0"], "Сумма": c40 * pr["electric"]["cable_4.0"]},
            {"Раздел": "Электрика", "Наименование": "Гофра защитная", "Кол-во": tc, "Ед.изм": "m.", "Цена": pr["electric"]["corrugation"], "Сумма": tc * pr["electric"]["corrugation"]},
            {"Раздел": "Электрика", "Наименование": "Крепеж/Клипсы для гофры", "Кол-во": cl, "Ед.изм": "шт.", "Цена": pr["electric"]["clips"], "Сумма": cl * pr["electric"]["clips"]}
        ]
        st.success(f"Всего по разделу: {sum(i['Сумма'] for i in st.session_state.e_data)} руб.")

with tab_plumb:
    draw_text_header("Сантехника и Отопление")
    p_pt = st.number_input("Точки водоснабжения (шт)", min_value=0, value=0, key="p_pt")
    col = st.number_input("Коллекторы (шт)", min_value=0, value=0, key="p_col")
    if st.button("Рассчитать сантехнику", type="primary", key="btn_p"):
        tp = p_pt * st.session_state.cp
        p16, p20, fit = round(tp * 0.8, 1), round(tp * 0.2, 1), p_pt * st.session_state.cf
        st.session_state.p_data = [
            {"Раздел": "Сантехника", "Наименование": f"Монтаж точек водоразбора ({p_pt} шт.)", "Кол-во": p_pt, "Ед.изм": "шт.", "Цена": pr["plumbing"]["point"], "Сумма": p_pt * pr["plumbing"]["point"]},
            {"Раздел": "Сантехника", "Наименование": "Установка коллекторов", "Кол-во": col, "Ед.изм": "шт.", "Цена": pr["plumbing"]["collector"], "Сумма": col * pr["plumbing"]["collector"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 16mm", "Кол-во": p16, "Ед.изм": "м.", "Цена": pr["plumbing"]["pipe_16"], "Сумма": p16 * pr["plumbing"]["pipe_16"]},
            {"Раздел": "Сантехника", "Наименование": "Труба PEX 20mm (magistral)", "Кол-во": p20, "Ед.изм": "м.", "Цена": pr["plumbing"]["pipe_20"], "Сумма": p20 * pr["plumbing"]["pipe_20"]},
            {"Раздел": "Сантехника", "Наименование": "Аксиальные фитинги/водорозетки", "Кол-во": fit, "Ед.изм": "шт.", "Цена": pr["plumbing"]["fitting"], "Сумма": fit * pr["plumbing"]["fitting"]}
        ]
        st.success(f"Всего по разделу: {sum(i['Сумма'] for i in st.session_state.p_data)} руб.")

if tab_coef:
    with tab_coef:
        draw_text_header("Нормы расхода материалов")
        st.session_state.cc = st.number_input("Кабель на точку (м)", value=st.session_state.cc, key="c_cc")
        st.session_state.cp = st.number_input("Труба PEX на точку (м)", value=st.session_state.cp, key="c_cp")

if tab_prices:
    with tab_prices:
        draw_text_header("Управление прайс-листом")
        
        with st.expander("❄️ ЦЕНЫ: КЛИМАТ", expanded=False):
            pr["hvac"]["work_standard"] = st.number_input("Стандартный монтаж (руб)", value=int(pr["hvac"]["work_standard"]), key="pr_ws")
            pr["hvac"]["work_stage_1"] = st.number_input("Закладка трасс 1-й этап (руб)", value=int(pr["hvac"]["work_stage_1"]), key="pr_s1")
            pr["hvac"]["work_stage_2"] = st.number_input("Навеска блоков 2-й этап (руб)", value=int(pr["hvac"]["work_stage_2"]), key="pr_s2")
            pr["hvac"]["pipe"] = st.number_input("Труба медная за метр (руб)", value=int(pr["hvac"]["pipe"]), key="pr_pi")
            pr["hvac"]["bracket"] = st.number_input("Кронштейны внешнего блока (руб)", value=int(pr["hvac"]["bracket"]), key="pr_br")
            pr["hvac"]["drain"] = st.number_input("Дренажный шланг за метр (руб)", value=int(pr["hvac"]["drain"]), key="pr_dr")
            pr["hvac"]["pump"] = st.number_input("Монтаж дренажной помпы (руб)", value=int(pr["hvac"]["pump"]), key="pr_pu")
            pr["hvac"]["box"] = st.number_input("Монтаж короба за метр (руб)", value=int(pr["hvac"]["box"]), key="pr_bo")
            pr["hvac"]["chasing_brick"] = st.number_input("Штроба кирпич за метр (руб)", value=int(pr["hvac"]["chasing_brick"]), key="pr_cb")
            pr["hvac"]["chasing_concrete"] = st.number_input("Штроба монолит за метр (руб)", value=int(pr["hvac"]["chasing_concrete"]), key="pr_cc")
            pr["hvac"]["coring"] = st.number_input("Алмазное бурение отверстия (руб)", value=int(pr["hvac"]["coring"]), key="pr_co")
            
        with st.expander("⚡ ЦЕНЫ: ЭЛЕКТРИКА", expanded=False):
            pr["electric"]["point"] = st.number_input("Монтаж точки / подрозетника (руб)", value=int(pr["electric"]["point"]), key="pr_ep")
            pr["electric"]["cable_1.5"] = st.number_input("Кабель 3х1.5 свет за метр (руб)", value=int(pr["electric"]["cable_1.5"]), key="pr_c1")
            pr["electric"]["cable_2.5"] = st.number_input("Кабель 3х2.5 розетки за метр (руб)", value=int(pr["electric"]["cable_2.5"]), key="pr_c2")
            pr["electric"]["cable_4.0"] = st.number_input("Кабель 3х4.0 сила за метр (руб)", value=int(pr["electric"]["cable_4.0"]), key="pr_c4")
            pr["electric"]["corrugation"] = st.number_input("Гофра за метр (руб)", value=int(pr["electric"]["corrugation"]), key="pr_eco")
            pr["electric"]["clips"] = st.number_input("Клипса за штуку (руб)", value=int(pr["electric"]["clips"]), key="pr_ecl")
            pr["electric"]["breaker"] = st.number_input("Установка автомата в щит (руб)", value=int(pr["electric"]["breaker"]), key="pr_ebr")
            pr["electric"]["chasing"] = st.number_input("Штробление за метр (руб)", value=int(pr["electric"]["chasing"]), key="pr_ech")
            
        with st.expander("🚰 ЦЕНЫ: САНТЕХНИКА", expanded=False):
            pr["plumbing"]["point"] = st.number_input("Монтаж точки водоразбора (руб)", value=int(pr["plumbing"]["point"]), key="pr_pp")
            pr["plumbing"]["pipe_16"] = st.number_input("Труба PEX 16мм за метр (руб)", value=int(pr["plumbing"]["pipe_16"]), key="pr_p16")
            pr["plumbing"]["pipe_20"] = st.number_input("Труба PEX 20мм за метр (руб)", value=int(pr["plumbing"]["pipe_20"]), key="pr_p20")
            pr["plumbing"]["collector"] = st.number_input("Сборка коллектора (руб)", value=int(pr["plumbing"]["collector"]), key="pr_pco")
            pr["plumbing"]["fitting"] = st.number_input("Фитинги/Водорозетки за шт (руб)", value=int(pr["plumbing"]["fitting"]), key="pr_pfi")
            
        if st.button("💾 СОХРАНИТЬ ПРАЙС-ЛИСТ НА СЕРВЕРЕ", type="primary", use_container_width=True, key="btn_save_p"):
            try:
                with open("local_prices.txt", "w", encoding="utf-8") as f:
                    for s in ["hvac", "electric", "plumbing"]:
                        for k, v in pr[s].items(): f.write(f"{k}={v}\n")
                st.success("Прайс-лист успешно сохранён!")
            except: st.error("Ошибка сохранения.")

with tab_est:
    draw_text_header("Итоговая смета инженерии объекта")
    grand_total = sum(i["Сумма"] for i in st.session_state.h_data) + sum(i["Сумма"] for i in st.session_state.e_data) + sum(i["Сумма"] for i in st.session_state.p_data)
    st.metric(label="ИТОГОВАЯ СУММА ПОД КЛЮЧ", value=f"{grand_total} руб.")
    full_list = st.session_state.h_data + st.session_state.e_data + st.session_state.p_data
    if full_list:
        st.dataframe(pd.DataFrame(full_list)[["Раздел", "Наименование", "Кол-во", "Ед.изм", "Цена", "Сумма"]], use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            df_tot = pd.DataFrame([{"Раздел": "ИТОГО", "Наименование": "ОБЩАЯ СТОИМОСТЬ", "Кол-во": "", "Ед.изм": "", "Цена": "", "Сумма": grand_total}])
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w: pd.concat([pd.DataFrame(full_list), df_tot], ignore_index=True).to_excel(w, index=False)
            st.download_button(label="🟢 СКАЧАТЬ В EXCEL", data=buf.getvalue(), file_name="Смета.xlsx", use_container_width=True, key="down_ex")
        with col2:
            txt = "=========================================\n   КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ (СМЕТА)\n=========================================\n\n"
            for i in full_list: txt += f"[{i['Раздел']}] {i['Наименование']}\n  {i['Кол-во']} {i['Ед.изм']} х {i['Цена']} руб. = {i['Сумма']} руб.\n\n"
            txt += f"-----------------------------------------\nИТОГОВАЯ СТОИМОСТЬ ПОД КЛЮЧ: {grand_total} руб."
            st.download_button(label="🔵 СКАЧАТЬ В TXT", data=io.BytesIO(txt.encode('utf-8')), file_name="КП_Инженерия.txt", mime="text/plain", use_container_width=True, key="down_tx")
    else: st.info("Проведите расчет в разделах.")

if st.sidebar.button("Выйти из системы", key="btn_logout"): st.session_state.auth = False; st.rerun()
