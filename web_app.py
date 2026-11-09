import streamlit as st
import pandas as pd
from calculations import Model

st.set_page_config(page_title="Калькулятор смет под ключ", layout="centered")
P_ADMIN, P_GUEST = "admin", "123"

def draw_text_header(text, size=24, is_main=False):
    html_code = f"""<div style="font-family: Arial, sans-serif; font-size: clamp({size-4}px, 3.5vw, {size}px); font-weight: bold; color: currentColor; white-space: nowrap; margin-bottom: {'20px' if is_main else '10px'};">{'🏗️ ' if is_main else ''}{text}</div>"""
    st.markdown(html_code, unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state.auth, st.session_state.role = False, None
if not st.session_state.auth:
    draw_text_header("Вход в Калькулятор Смет", size=26, is_main=True)
    user_pass = st.text_input("Введите код доступа:", type="password")
    if st.button("Войти", type="primary", use_container_width=True):
        if user_pass == P_ADMIN: st.session_state.auth, st.session_state.role = True, "admin"; st.rerun()
        elif user_pass == P_GUEST: st.session_state.auth, st.session_state.role = True, "guest"; st.rerun()
        else: st.error("Неверный код доступа!")
    st.stop()

if "model" not in st.session_state:
    st.session_state.model = Model()
    st.session_state.h_tot, st.session_state.e_tot, st.session_state.p_tot = 0, 0, 0

m = st.session_state.model
draw_text_header("Инженерный калькулятор смет", size=28, is_main=True)

t_list = ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "📊 Расход", "💰 Цены", "🧾 Итог"] if st.session_state.role == "admin" else ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "🧾 Итог"]
tabs = st.tabs(t_list)

if st.session_state.role == "admin": tab_hvac, tab_elec, tab_plumb, tab_coef, tab_prices, tab_est = tabs
else: tab_hvac, tab_elec, tab_plumb, tab_est = tabs; tab_coef, tab_prices = None, None

# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ГЕНЕРАЦИИ ПОЛЕЙ ВВОДА НА ВКЛАДКАХ ---
def render_calc_tab(tab, title, section_rus, points_key=None):
    with tab:
        draw_text_header(title, size=20)
        inputs = {}
        points_val = 0
        sect_code = "hvac" if section_rus == "Климат" else ("electric" if section_rus == "Ед_Изм" else "plumbing")
        
        # Если в разделе есть авто-коэффициенты, сначала просим ввести количество главных точек
        if points_key:
            for k, item in m.prices.get(points_key, {}).items():
                if item["Тип_Ввода"] == "число" and ("точек" in item["Наименование"] or "блоков" in item["Наименование"]):
                    points_val = st.number_input(f"{item['Наименование']} ({item['Ед_Изм']})", min_value=0, value=0, key=f"p_{k}")
                    inputs[k] = points_val

        # Генерируем поля для всех остальных ручных пунктов "число"
        for k, item in m.prices.get(sect_code, {}).items():
            if item["Тип_Ввода"] == "число" and k not in inputs:
                inputs[k] = st.number_input(f"{item['Наименование']} ({item['Ед_Изм']})", min_value=0, value=0, key=f"inp_{k}")

        if st.button(f"Рассчитать {section_rus.lower()}", type="primary", key=f"btn_{section_rus}"):
            res_list, total = m.calc_section(section_rus, inputs, points_qty=points_val)
            st.success(f"Всего по разделу: {total} руб.")
            return total
    return 0

# Отрендеринг вкладок
h_t = render_calc_tab(tab_hvac, "Кондиционирование и вентиляция", "Климат", "hvac")
if h_t: st.session_state.h_tot = h_t

e_t = render_calc_tab(tab_elec, "Электрика и силовые щиты", "Электрика", "electric")
if e_t: st.session_state.e_tot = e_t

p_t = render_calc_tab(tab_plumb, "Сантехника и Отопление дома", "Сантехника", "plumbing")
if p_t: st.session_state.p_tot = p_t

if tab_coef:
    with tab_coef:
        draw_text_header("Нормы расхода материалов", size=20)
        m.cc = st.number_input("Кабель на точку (м)", value=m.cc)
        m.cp = st.number_input("Труба PEX на точку (м)", value=m.cp)

if tab_prices:
    with tab_prices:
        draw_text_header("Управление прайс-листом", size=20)
        for sect_name, sect_rus in [("hvac", "❄️ ЦЕНЫ: КЛИМАТ"), ("electric", "⚡ ЦЕНЫ: ЭЛЕКТРИКА"), ("plumbing", "🚰 ЦЕНЫ: САНТЕХНИКА")]:
            with st.expander(sect_rus, expanded=False):
                for k, item in m.prices.get(sect_name, {}).items():
                    item["Цена"] = st.number_input(f"{item['Наименование']} (руб)", value=int(item["Цена"]), key=f"pr_{k}")
        
        if st.button("💾 СОХРАНИТЬ ПРАЙС-ЛИСТ НА СЕРВЕРЕ", type="primary", use_container_width=True):
            if m.save_local_prices(): st.success("Прайс-лист успешно зафиксирован!")
            else: st.error("Ошибка сохранения.")

with tab_est:
    draw_text_header("Итоговая смета инженерии объекта", size=20)
    grand_total = st.session_state.h_tot + st.session_state.e_tot + st.session_state.p_tot
    st.metric(label="ИТОГОВАЯ СУММА ПОД КЛЮЧ", value=f"{grand_total} руб.")
    full_list = m.h_data + m.e_data + m.p_data
    if full_list:
        st.dataframe(pd.DataFrame(full_list)[["Раздел", "Наименование", "Кол-во", "Ед.изм", "Цена", "Сумма"]], use_container_width=True)
        col1, col2 = st.columns(2)
        with col1: st.download_button(label="🟢 СКАЧАТЬ В EXCEL", data=m.get_excel_bytes(full_list, grand_total), file_name="Смета.xlsx", use_container_width=True)
        with col2: st.download_button(label="🔵 СКАЧАТЬ В TXT", data=m.get_txt_bytes(full_list, grand_total), file_name="КП_Инженерия.txt", mime="text/plain", use_container_width=True)
    else: st.info("Проведите расчет в разделах.")

if st.sidebar.button("Выйти из системы"): st.session_state.auth = False; st.rerun()
