import streamlit as st
import pandas as pd
from calculations import Model

st.set_page_config(page_title="Калькулятор смет под ключ", layout="centered")
P_ADMIN, P_GUEST = "admin", "123"

# ВПИШИТЕ СЮДА ССЫЛКУ НА ВАШ GITHUB (Для чтения прайса)
REPO_URL = "https://github.com" + st.experimental_user.to_dict().get("username", "bober") + "/my-calculator" if hasattr(st, "experimental_user") else "https://github.combober/my-calculator"

if "auth" not in st.session_state:
    st.session_state.auth, st.session_state.role = False, None

if not st.session_state.auth:
    st.title("🏗️ Вход в Калькулятор Смет")
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
# ВСЕГДА ПОДТЯГИВАЕМ СВЕЖИЙ ПРАЙС ИЗ ИНТЕРНЕТА ПЕРЕД СТАРТОМ
m.load_remote_prices(REPO_URL)

st.title("🏗️ Инженерный калькулятор смет")
st.caption(f"Роль: {'Администратор' if st.session_state.role == 'admin' else 'Рабочий/Гость'}")

t_list = ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "📊 Расход", "💰 Цены", "🧾 Итог"] if st.session_state.role == "admin" else ["❄️ Климат", "⚡ Электрика", "🚰 Сантехника", "🧾 Итог"]
tabs = st.tabs(t_list)

if st.session_state.role == "admin": tab_hvac, tab_elec, tab_plumb, tab_coef, tab_prices, tab_est = tabs
else: tab_hvac, tab_elec, tab_plumb, tab_est = tabs; tab_coef, tab_prices = None, None

with tab_hvac:
    st.header("Кондиционирование")
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
    st.header("Электрика и щиты")
    pt = st.number_input("Количество точек (шт)", min_value=0, value=0)
    ch = st.number_input("Штроба всего (м)", min_value=0.0, value=0.0)
    eb = st.number_input("Автоматы в щит (шт)", min_value=0, value=0)
    if st.button("Рассчитать электрику", type="primary"):
        st.session_state.e_tot = m.calc_elec(pt, ch, eb)
        st.success(f"Всего: {st.session_state.e_tot} руб.")

with tab_plumb:
    st.header("Сантехника и Отопление")
    p_pt = st.number_input("Точки водоснабжения (шт)", min_value=0, value=0)
    col = st.number_input("Коллекторы (шт)", min_value=0, value=0)
    if st.button("Рассчитать сантехнику", type="primary"):
        st.session_state.p_tot = m.calc_plumb(p_pt, col)
        st.success(f"Всего: {st.session_state.p_tot} руб.")

if tab_coef:
    with tab_coef:
        st.header("Нормы расхода")
        m.cc = st.number_input("Кабель на точку (м)", value=m.cc)
        m.cp = st.number_input("Труба PEX на точку (м)", value=m.cp)

if tab_prices:
    with tab_prices:
        st.header("Управление прайс-листом")
        st.info("Ваши цены надёжно зафиксированы в файле 'prices.txt' на GitHub! Чтобы обновить расценки на постоянной основе для всех устройств, просто измените цифры в этом файле через браузер. Калькулятор мгновенно подхватит новые значения.")

with tab_est:
    st.header("Итоговая смета объекта")
    grand_total = st.session_state.h_tot + st.session_state.e_tot + st.session_state.p_tot
    st.metric(label="ИТОГОВАЯ СУММА ПОД КЛЮЧ", value=f"{grand_total} руб.")

    full_list = m.h_data + m.e_data + m.p_data
    if full_list:
        st.dataframe(pd.DataFrame(full_list)[["Раздел", "Наименование", "Кол-во", "Ед.изм", "Цена", "Сумма"]], use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="🟢 СКАЧАТЬ В EXCEL", data=m.get_excel_bytes(full_list, grand_total), file_name="Смета.xlsx", use_container_width=True)
        with col2:
            st.download_button(label="🔵 СКАЧАТЬ В PDF", data=m.get_pdf_bytes(full_list, grand_total), file_name="КП_Инженерия.txt", mime="text/plain", use_container_width=True)
    else: st.info("Проведите расчет в разделах.")

if st.sidebar.button("Выйти из системы"): st.session_state.auth = False; st.rerun()
