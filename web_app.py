import streamlit as st
import pandas as pd
from calculations import Model

st.set_page_config(page_title="Калькулятор смет под ключ", layout="centered")
P_ADMIN, P_GUEST = "admin", "123"

# --- ПРОФЕССИОНАЛЬНАЯ ФУНКЦИЯ ДЛЯ АДАПТИВНЫХ ЗАГОЛОВКОВ-КАРТОЧЕК ---
# padding и border-radius делают красивую подложку, а 5.5vw адаптирует текст под экран телефона
def draw_text_header(text, is_main=False):
    emoji = "🏗️ " if is_main else ""
    
    if is_main:
        # Стили для главного баннера: легкий фон, скругление, отступы и адаптивный шрифт
        html_code = f"""
        <div style="
            background: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #1f538d;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            margin-top: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <span style="font-size: 22px; vertical-align: middle;">{emoji}</span>
            <span style="
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: calc(18px + 1.5vw); 
                font-weight: 800; 
                color: currentColor;
                line-height: 1.3;
            ">{text}</span>
        </div>
        """
    else:
        # Стили для обычных подзаголовков внутри вкладок (не рвутся уродливо, аккуратно переносятся)
        html_code = f"""
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif; 
            font-size: calc(16px + 0.8vw); 
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

# Экран ввода пароля
if "auth" not in st.session_state:
    st.session_state.auth, st.session_state.role = False, None

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

# Главный заголовок сайта в виде фирменной карточки
draw_text_header("Инженерный калькулятор смет", is_main=True)
st.caption(f"Роль: {'Администратор' if st.session_state.role == 'admin' else 'Гость'}")

t_list = ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "📊 Расход", "💰 Цены", "🧾 Итог"] if st.session_state.role == "admin" else ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "🧾 Итог"]
tabs = st.tabs(t_list)

if st.session_state.role == "admin": tab_hvac, tab_elec, tab_plumb, tab_coef, tab_prices, tab_est = tabs
else: tab_hvac, tab_elec, tab_plumb, tab_est = tabs; tab_coef, tab_prices = None, None

with tab_hvac:
    draw_text_header("Кондиционирование и вентиляция", size=20)
    b = st.number_input("Блоки (шт)", min_value=0, value=0)
    p = st.number_input("Трасса (м)", min_value=0.0, value=0.0)
    mode = st.selectbox("Схема", ["В один этап (Стандарт)", "1-й этап (Закладка трасс)", "2-й этап (Навеска блоков)"])
    with st.expander("Дополнительные усложнения"):
        pump = st.number_input("Помпы (шт)", min_value=0, value=0)
        box = st.number_input("Короб (м)", min_value=0.0, value=0.0)
        core = st.number_input("Бурение отверстий (шт)", min_value=0, value=0)
        ch_b = st.number_input("Штроба кирпич (м)", min_value=0.0, value=0.0)
        ch_c = st.number_input("Штроба монолит (м)", min_value=0.0, value=0.0)
    if st.button("Рассчитать климат", type="primary"):
        st.session_state.h_tot = m.calc_hvac(b, p, mode, pump, box, ch_b, ch_c, core)
        st.success(f"Всего: {st.session_state.h_tot} руб.")

with tab_elec:
    draw_text_header("Электрика и силовые щиты", size=20)
    pt = st.number_input("Количество точек (шт)", min_value=0, value=0)
    ch = st.number_input("Штроба всего (м)", min_value=0.0, value=0.0)
    eb = st.number_input("Автоматы в щит (шт)", min_value=0, value=0)
    if st.button("Рассчитать электрику", type="primary"):
        st.session_state.e_tot = m.calc_elec(pt, ch, eb)
        st.success(f"Всего: {st.session_state.e_tot} руб.")

with tab_plumb:
    draw_text_header("Сантехника и Отопление дома", size=20)
    p_pt = st.number_input("Точки водоснабжения (шт)", min_value=0, value=0)
    col = st.number_input("Коллекторы (шт)", min_value=0, value=0)
    if st.button("Рассчитать сантехнику", type="primary"):
        st.session_state.p_tot = m.calc_plumb(p_pt, col)
        st.success(f"Всего: {st.session_state.p_tot} руб.")

if tab_coef:
    with tab_coef:
        draw_text_header("Нормы расхода материалов", size=20)
        m.cc = st.number_input("Кабель на точку (м)", value=m.cc)
        m.cp = st.number_input("Труба PEX на точку (м)", value=m.cp)

if tab_prices:
    with tab_prices:
        draw_text_header("Управление прайс-листом", size=20)
        
        with st.expander("❄️ ЦЕНЫ: КЛИМАТ", expanded=False):
            m.prices["hvac"]["work_standard"] = st.number_input("Стандартный монтаж (руб)", value=int(m.prices["hvac"]["work_standard"]))
            m.prices["hvac"]["work_stage_1"] = st.number_input("Закладка трасс 1-й этап (руб)", value=int(m.prices["hvac"]["work_stage_1"]))
            m.prices["hvac"]["work_stage_2"] = st.number_input("Навеска блоков 2-й этап (руб)", value=int(m.prices["hvac"]["work_stage_2"]))
            m.prices["hvac"]["pipe"] = st.number_input("Труба медная за метр (руб)", value=int(m.prices["hvac"]["pipe"]))
            m.prices["hvac"]["bracket"] = st.number_input("Кронштейны внешнего блока (руб)", value=int(m.prices["hvac"]["bracket"]))
            m.prices["hvac"]["drain"] = st.number_input("Дренажный шланг за метр (руб)", value=int(m.prices["hvac"]["drain"]))
            m.prices["hvac"]["pump"] = st.number_input("Монтаж дренажной помпы (руб)", value=int(m.prices["hvac"]["pump"]))
            m.prices["hvac"]["box"] = st.number_input("Монтаж короба за метр (руб)", value=int(m.prices["hvac"]["box"]))
            m.prices["hvac"]["chasing_brick"] = st.number_input("Штроба кирпич за метр (руб)", value=int(m.prices["hvac"]["chasing_brick"]))
            m.prices["hvac"]["chasing_concrete"] = st.number_input("Штроба монолит за метр (руб)", value=int(m.prices["hvac"]["chasing_concrete"]))
            m.prices["hvac"]["coring"] = st.number_input("Алмазное бурение отверстия (руб)", value=int(m.prices["hvac"]["coring"]))

        with st.expander("⚡ ЦЕНЫ: ЭЛЕКТРИКА", expanded=False):
            m.prices["electric"]["point"] = st.number_input("Монтаж точки / подрозетника (руб)", value=int(m.prices["electric"]["point"]))
            m.prices["electric"]["cable_1.5"] = st.number_input("Кабель 3х1.5 свет за метр (руб)", value=int(m.prices["electric"]["cable_1.5"]))
            m.prices["electric"]["cable_2.5"] = st.number_input("Кабель 3х2.5 розетки за метр (руб)", value=int(m.prices["electric"]["cable_2.5"]))
            m.prices["electric"]["cable_4.0"] = st.number_input("Кабель 3х4.0 сила за метр (руб)", value=int(m.prices["electric"]["cable_4.0"]))
            m.prices["electric"]["corrugation"] = st.number_input("Гофра за метр (руб)", value=int(m.prices["electric"]["corrugation"]))
            m.prices["electric"]["clips"] = st.number_input("Клипса за штуку (руб)", value=int(m.prices["electric"]["clips"]))
            m.prices["electric"]["breaker"] = st.number_input("Установка автомата в щит (руб)", value=int(m.prices["electric"]["breaker"]))
            m.prices["electric"]["chasing"] = st.number_input("Штробление за метр (руб)", value=int(m.prices["electric"]["chasing"]))

        with st.expander("🚰 ЦЕНЫ: САНТЕХНИКА", expanded=False):
            m.prices["plumbing"]["point"] = st.number_input("Монтаж точки водоразбора (руб)", value=int(m.prices["plumbing"]["point"]))
            m.prices["plumbing"]["pipe_16"] = st.number_input("Труба PEX 16мм за метр (руб)", value=int(m.prices["plumbing"]["pipe_16"]))
            m.prices["plumbing"]["pipe_20"] = st.number_input("Труба PEX 20мм за метр (руб)", value=int(m.prices["plumbing"]["pipe_20"]))
            m.prices["plumbing"]["collector"] = st.number_input("Сборка коллектора (руб)", value=int(m.prices["plumbing"]["collector"]))
            m.prices["plumbing"]["fitting"] = st.number_input("Фитинги/Водорозетки за шт (руб)", value=int(m.prices["plumbing"]["fitting"]))

        if st.button("💾 СОХРАНИТЬ ПРАЙС-ЛИСТ НА СЕРВЕРЕ", type="primary", use_container_width=True):
            if m.save_local_prices(): st.success("Прайс-лист успешно перезаписан и зафиксирован для всех пользователей!")
            else: st.error("Ошибка сохранения файла на сервере.")

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
