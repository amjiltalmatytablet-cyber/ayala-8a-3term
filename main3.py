# Қажетті кітапханаларды орнату:
# pip install streamlit pandas plotly numpy

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Беттің баптаулары
st.set_page_config(page_title="Инфляция Аналитикасы: Қазақстан", layout="wide")

# Financial Blue стилі үшін CSS
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #003366; }
    </style>
    """, unsafe_allow_html=True)

# 1. Деректерді имитациялау (2021-2026)
@st.cache_data
def load_data():
    dates = pd.date_range(start="2021-01-01", end="2026-12-01", freq="MS")
    n = len(dates)
    
    # Инфляция трендтері (пайызбен)
    np.random.seed(42)
    food_inflation = 10 + np.cumsum(np.random.normal(0.2, 0.5, n))
    fuel_inflation = 8 + np.cumsum(np.random.normal(0.15, 0.6, n))
    rent_inflation = 12 + np.cumsum(np.random.normal(0.3, 0.4, n))
    
    df = pd.DataFrame({
        "Күн": dates,
        "Азық-түлік": food_inflation,
        "Жанармай": fuel_inflation,
        "Жалдау ақысы": rent_inflation
    })
    return df

df = load_data()

# Тақырып
st.title("📈 Қазақстандағы инфляция және сатып алу қабілеті (2021-2026)")
st.info("Бұл қолданба Ұлттық статистика бюросының ресми трендтеріне негізделген имитациялық деректерді ұсынады.")

# --- 3. st.metric КАРТАЛАРЫ ---
st.subheader("Соңғы айдағы көрсеткіштер (Жылдық %)")
col1, col2, col3 = st.columns(3)

current_vals = df.iloc[-1]
prev_vals = df.iloc[-2]

def get_delta(curr, prev):
    return f"{curr - prev:.1f}%"

with col1:
    st.metric("Азық-түлік", f"{current_vals['Азық-түлік']:.1f}%", get_delta(current_vals['Азық-түлік'], prev_vals['Азық-түлік']))
with col2:
    st.metric("Жанармай", f"{current_vals['Жанармай']:.1f}%", get_delta(current_vals['Жанармай'], prev_vals['Жанармай']))
with col3:
    st.metric("Жалдау ақысы", f"{current_vals['Жалдау ақысы']:.1f}%", get_delta(current_vals['Жалдау ақысы'], prev_vals['Жалдау ақысы']))

st.divider()

# --- 1. PLOTLY LINE CHART ---
col_charts_left, col_charts_right = st.columns([2, 1])

with col_charts_left:
    st.subheader("Бағалардың өсу динамикасы")
    fig_line = px.line(df, x="Күн", y=["Азық-түлік", "Жанармай", "Жалдау ақысы"],
                      labels={"value": "Инфляция (%)", "variable": "Санаттар"},
                      color_discrete_sequence=["#003366", "#336699", "#6699CC"])
    fig_line.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_line, use_container_width=True)

# --- 2. DONUT CHART (Тұтыну себеті) ---
with col_charts_right:
    st.subheader("Тұтыну себетінің құрылымы")
    basket_data = {
        "Санаттар": ["Азық-түлік", "Азық-түлік емес тауарлар", "Ақылы қызметтер"],
        "Үлес": [40.5, 30.2, 29.3]
    }
    fig_donut = px.pie(basket_data, values="Үлес", names="Санаттар", hole=0.5,
                      color_discrete_sequence=["#002147", "#0047AB", "#87CEEB"])
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

# --- 4. CALCULATOR МОДУЛІ ---
st.subheader("🧮 Сатып алу қабілетінің калькуляторы")
calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    salary = st.number_input("Сіздің айлық жалақыңыз (теңге):", min_value=0, value=250000, step=10000)
    period = st.slider("Қанша жыл бұрынғымен салыстыру?", 1, 5, 3)

with calc_col2:
    # Инфляцияның орташа әсерін есептеу (соңғы 'period' жылдағы жиынтық инфляция)
    total_inflation_raw = (current_vals['Азық-түлік'] + current_vals['Жалдау ақысы']) / 2
    # Сатып алу қабілетінің төмендеуін есептеу формуласы
    real_value = salary / (1 + (total_inflation_raw / 100) * period)
    loss = salary - real_value
    
    st.write(f"### {period} жылдан кейінгі жағдай:")
    st.write(f"Инфляцияны ескергендегі жалақыңыздың нақты құны: **{int(real_value):,} ₸**")
    st.error(f"Сатып алу қабілетінің жоғалуы: -{int(loss):,} ₸")

st.markdown("""
---
**Анықтама:** Бұл калькулятор инфляцияның жиынтық әсерін көрсетеді. 
Нақты құн — бұл бүгінгі жалақыңызбен өткен уақыттағы бағамен қанша тауар алуға болатынын білдіреді.
""")