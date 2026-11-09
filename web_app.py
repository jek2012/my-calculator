import streamlit as st
import pandas as pd
from calculations import Model

st.set_page_config(page_title="Калькулятор смет под ключ", layout="centered")
P_ADMIN, P_GUEST = "admin", "123"

# --- ВОЗВРАЩЕНА НАША ИДЕАЛЬНАЯ ФУНКЦИЯ НЕБЬЮЩИХСЯ ЗАГОЛОВКОВ ---
def draw_text_header(text, is_main=False):
    emoji = "🏗️ " if is_main else ""
    margin_bottom = "20px" if is_main else "10px"
    
    if is_main:
        # Фирменная карточка-баннер для главного заголовка
        html_code = f"""
        <div style="
            background: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #1f538d;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: {margin_bottom};
            margin-top: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <span style="font-size: 22px; vertical-align: middle;">{emoji}</span>
            <span style="
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: clamp(20px, 4vw, 26px); 
                font-weight: 800; 
                color: currentColor;
                line-height: 1.3;
            ">{text}</span>
        </div>
        """
    else:
        # Четкие подзаголовки внутри вкладок с автопереносом строк
        html_code = f"""
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif; 
            font-size: clamp(16px, 2.5vw, 20px); 
            font-weight: 600; 
            color: currentColor; 
            line-height: 1.4;
            margin-bottom: 15px;
            margin-top: 15px;
        ">
            {text}
        </div>
        """
    st.markdown(html_code, unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state.auth, st.session_state.role = False, None
if not st.session_state.auth:
    draw_text_header("Вход в Калькулятор Смет", is_main=True)
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
draw_text_header("Инженерный калькулятор смет", is_main=True)
st.caption(f"Роль: {'Администратор' if st.session_state.role == 'admin' else 'Гость'}")

t_list = ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "📊 Расход", "💰 Цены", "🧾 Итог"] if st.session_state.role == "admin" else ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "🧾 Итог"]
tabs = st.tabs(t_list)

if st.session_state.role == "admin": tab_hvac, tab_elec, tab_plumb, tab_coef, tab_prices, tab_est = tabs
else: tab_hvac, tab_elec, tab_plumb, tab_est = tabs; tab_coef, tab_prices = None, None

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
        st.session_state.h_tot = m.calc_hvac(b, p, mode, pump, box, ch_b, ch_c, core)
        st.success(f"Всего по разделу: {st.session_state.h_tot} руб.")

with tab_elec:
    draw_text_header("Электрика и силовые щиты")
    pt = st.number_input("Количество точек (шт)", min_value=0, value=0, key="e_pt")
    ch = st.number_input("Штроба всего (м)", min_value=0.0, value=0.0, key="e_ch")
    eb = st.number_input("Автоматы в щит (шт)", min_value=0, value=0, key="e_eb")
    if st.button("Рассчитать электрику", type="primary", key="btn_e"):
        st.session_state.e_tot = m.calc_elec(pt, ch, eb)
        st.success(f"Всего по разделу: {st.session_state.e_tot} руб.")

with tab_plumb:
    draw_text_header("Сантехника и Отопление")
    p_pt = st.number_input("Точки водоснабжения (шт)", min_value=0, value=0, key="p_pt")
    col = st.number_input("Коллекторы (шт)", min_value=0, value=0, key="p_col")
    if st.button("Рассчитать сантехнику", type="primary", key="btn_p"):
        st.session_state.p_tot = m.calc_plumb(p_pt, col)
        st.success(f"Всего по разделу: {st.session_state.p_tot} руб.")

if tab_coef:
    with tab_coef:
        draw_text_header("Нормы расхода материалов")
        m.cc = st.number_input("Кабель на точку (м)", value=m.cc, key="c_cc")
        m.cp = st.number_input("Труба PEX на точку (м)", value=m.cp, key="c_cp")

if tab_prices:
    with tab_prices:
        draw_text_header("Управление прайс-листом")
        with st.expander("❄️ ЦЕНЫ: КЛИМАТ", expanded=False):
            m.prices["hvac"]["work_standard"] = st.number_input("Стандартный монтаж (руб)", value=int(m.prices["hvac"]["work_standard"]), key="pr_ws")
            m.prices["hvac"]["work_stage_1"] = st.number_input("Закладка трасс 1-й этап (руб)", value=int(m.prices["hvac"]["work_stage_1"]), key="pr_s1")
            m.prices["hvac"]["work_stage_2"] = st.number_input("Навеска блоков 2-й этап (руб)", value=int(m.prices["hvac"]["work_stage_2"]), key="pr_s2")
            m.prices["hvac"]["pipe"] = st.number_input("Труба медная за метр (руб)", value=int(m.prices["hvac"]["pipe"]), key="pr_pi")
            m.prices["hvac"]["bracket"] = st.number_input("Кронштейны внешнего блока (руб)", value=int(m.prices["hvac"]["bracket"]), key="pr_br")
            m.prices["hvac"]["drain"] = st.number_input("Дренажный шланг за метр (руб)", value=int(m.prices["hvac"]["drain"]), key="pr_dr")
            m.prices["hvac"]["pump"] = st.number_input("Монтаж дренажной помпы (руб)", value=int(m.prices["hvac"]["pump"]), key="pr_pu")
            m.prices["hvac"]["box"] = st.number_input("Монтаж короба за метр (руб)", value=int(m.prices["hvac"]["box"]), key="pr_bo")
            m.prices["hvac"]["chasing_brick"] = st.number_input("Штроба кирпич за метр (руб)", value=int(m.prices["hvac"]["chasing_brick"]), key="pr_cb")
            m.prices["hvac"]["chasing_concrete"] = st.number_input("Штроба монолит за метр (руб)", value=int(m.prices["hvac"]["chasing_concrete"]), key="pr_cc")
            m.prices["hvac"]["coring"] = st.number_input("Алмазное бурение отверстия (руб)", value=int(m.prices["hvac"]["coring"]), key="pr_co")
        with st.expander("⚡ ЦЕНЫ: ЭЛЕКТРИКА", expanded=False):
            m.prices["electric"]["point"] = st.number_input("Монтаж точки / подрозетника (руб)", value=int(m.prices["electric"]["point"]), key="pr_ep")
            m.prices["electric"]["cable_1.5"] = st.number_input("Кабель 3х1.5 свет за метр (руб)", value=int(m.prices["electric"]["cable_1.5"]), key="pr_c1")
            m.prices["electric"]["cable_2.5"] = st.number_input("Кабель 3х2.5 розетки за метр (руб)", value=int(m.prices["electric"]["cable_2.5"]), key="pr_c2")
            m.prices["electric"]["cable_4.0"] = st.number_input("Кабель 3х4.0 сила за метр (руб)", value=int(m.prices["electric"]["cable_4.0"]), key="pr_c4")
            m.prices["electric"]["corrugation"] = st.number_input("Гофра за метр (руб)", value=int(m.prices["electric"]["corrugation"]), key="pr_eco")
            m.prices["electric"]["clips"] = st.number_input("Клипса за штуку (руб)", value=int(m.prices["electric"]["clips"]), key="pr_ecl")
            m.prices["electric"]["breaker"] = st.number_input("Установка автомата в щит (руб)", value=int(m.prices["electric"]["breaker"]), key="pr_ebr")
            m.prices["electric"]["chasing"] = st.number_input("Штробление за метр (руб)", value=int(m.prices["electric"]["chasing"]), key="pr_ech")
        with st.expander("🚰 ЦЕНЫ: САНТЕХНИКА", expanded=False):
            m.prices["plumbing"]["point"] = st.number_input("Монтаж точки водоразбора (руб)", value=int(m.prices["plumbing"]["point"]), key="pr_pp")
            m.prices["plumbing"]["pipe_16"] = st.number_input("Труба PEX 16мм за метр (руб)", value=int(m.prices["plumbing"]["pipe_16"]), key="pr_p16")
            m.prices["plumbing"]["pipe_20"] = st.number_input("Труба PEX 20мм за метр (руб)", value=int(m.prices["plumbing"]["pipe_20"]), key="pr_p20")
            m.prices["plumbing"]["collector"] = st.number_input("Сборка коллектора (руб)", value=int(m.prices["plumbing"]["collector"]), key="pr_pco")
            m.prices["plumbing"]["fitting"] = st.number_input("Фитинги/Водорозетки за шт (руб)", value=int(m.prices["plumbing"]["fitting"]), key="pr_pfi")
        if st.button("💾 СОХРАНИТЬ ПРАЙС-ЛИСТ НА СЕРВЕРЕ", type="primary", use_container_width=True, key="btn_save_p"):
            if m.save_local_prices(): st.success("Прайс-лист успешно сохранён!")
            else: st.error("Ошибка сохранения.")
with tab_est:
    draw_text_header("Итоговая смета инженерии объекта", size=20)
    grand_total = st.session_state.h_tot + st.session_state.e_tot + st.session_state.p_tot
    st.metric(label="ИТОГОВАЯ СУММА ПОД КЛЮЧ", value=f"{grand_total} руб.")
    full_list = m.h_data + m.e_data + m.p_data
    if full_list:
        st.dataframe(pd.DataFrame(full_list)[["Раздел", "Наименование", "Кол-во", "Ед.изм", "Цена", "Сумма"]], use_container_width=True)
        col1, col2 = st.columns(2)
        with col1: st.download_button(label="🟢 СКАЧАТЬ В EXCEL", data=m.get_excel_bytes(full_list, grand_total), file_name="Смета.xlsx", use_container_width=True, key="down_ex")
        with col2: st.download_button(label="🔵 СКАЧАТЬ В TXT", data=m.get_txt_bytes(full_list, grand_total), file_name="КП_Инженерия.txt", mime="text/plain", use_container_width=True, key="down_tx")
    else: st.info("Проведите расчет в разделах.")

if st.sidebar.button("Выйти из системы", key="btn_logout"): st.session_state.auth = False; st.rerun()
