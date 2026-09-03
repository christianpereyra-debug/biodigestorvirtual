import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Simulador de Biodigestor Educativo", layout="wide")

st.title("🌱 Simulador Educativo de Biodigestión Anaerobia")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    df_sustratos = pd.read_csv("data/sustratos.csv")
    df_params = pd.read_csv("data/parametros.csv").set_index("parametro")
    df_agitacion = pd.read_csv("data/agitacion.csv").set_index("modo")
    df_purif = pd.read_csv("data/purificacion.csv").set_index("tecnologia")
    return df_sustratos, df_params, df_agitacion, df_purif

try:
    df_sustratos, df_params, df_agitacion, df_purif = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar los archivos CSV: {e}")
    st.stop()

# --- SELECTOR DE MODO DE USO ---
st.sidebar.markdown("## 🎯 Modo de Uso")
modo_interfaz = st.sidebar.radio(
    "Seleccione el nivel del simulador:",
    ["🌱 Modo Simple (Inicial / Divulgación)", "🔬 Modo Avanzado (Técnico / CHP)"],
    index=0
)

es_avanzado = "Avanzado" in modo_interfaz

st.sidebar.divider()

# --- BARRA LATERAL: PARÁMETROS COMUNES (SIMPLE & AVANZADO) ---
st.sidebar.header("⚙️ 1. Entradas Principales")
sustrato_sel = st.sidebar.selectbox("Sustrato u Orgánico:", df_sustratos["sustrato"].unique())
datos_sust = df_sustratos[df_sustratos["sustrato"] == sustrato_sel].iloc[0]

masa_diaria = st.sidebar.slider("Masa de entrada (kg/día):", 50, 5000, 1000, step=50)

# --- VALORES POR DEFECTO / AVANZADOS ---
if es_avanzado:
    st.sidebar.header("🌡️ 2. Parámetros Operativos")
    temperatura = st.sidebar.slider("Temperatura del digestor (°C):", 15, 45, 35)
    trh = st.sidebar.slider("Tiempo de Retención (TRH días):", 15, 60, 30)

    st.sidebar.header("🔄 3. Mezclado / Agitación")
    modo_agit = st.sidebar.selectbox("Agitación:", list(df_agitacion.index), format_func=lambda x: x.replace("_", " ").title())
    info_agit = df_agitacion.loc[modo_agit]

    st.sidebar.header("🧼 4. Filtro de Biogás")
    tec_purif = st.sidebar.selectbox("Purificación:", list(df_purif.index), format_func=lambda x: x.replace("_", " ").title())
    info_purif = df_purif.loc[tec_purif]

    st.sidebar.header("🔥 5. Cogeneración CHP")
    temp_ambiente = st.sidebar.slider("Temperatura ambiente (°C):", -5, 35, 15)
    ef_elec_chp = st.sidebar.slider("Eficiencia Eléctrica CHP (%):", 25, 45, int(df_params.loc["eficiencia_electrica_chp", "valor"]*100)) / 100.0
    ef_term_chp = st.sidebar.slider("Eficiencia Térmica CHP (%):", 30, 60, int(df_params.loc["eficiencia_termica_chp", "valor"]*100)) / 100.0
else:
    # Valores estándar automáticos para el Modo Simple
    temperatura = 35 # Óptimo mesofílico
    trh = 30
    info_agit = df_agitacion.loc["intermitente"]
    info_purif = df_purif.loc["trampa_condensados"]
    temp_ambiente = 15
    ef_elec_chp = df_params.loc["eficiencia_electrica_chp", "valor"]
    ef_term_chp = df_params.loc["eficiencia_termica_chp", "valor"]

# --- CÁLCULOS TÉCNICOS ---
def calcular_presion_vapor_kPa(t_c):
    return (10 ** (8.07131 - (1730.63 / (233.426 + t_c)))) * 0.133322

st_kg = masa_diaria * (datos_sust["st_pct"] / 100)
sv_kg = st_kg * (datos_sust["sv_pct_st"] / 100)
vol_digestor = (masa_diaria / df_params.loc["densidad_agua", "valor"]) * trh

factor_temp = max(0.2, 1.0 - abs(temperatura - 35) * df_params.loc["factor_eficiencia_temp", "valor"])
ef_ag = info_agit["eficiencia_mezclado"]

m3_ch4_seco = sv_kg * datos_sust["rendimiento_ch4_m3_kgsv"] * factor_temp * ef_ag
pct_ch4_seco = datos_sust["pct_ch4"]
pct_co2_seco = 100.0 - pct_ch4_seco
m3_gas_seco = m3_ch4_seco / (pct_ch4_seco / 100)

P_sat = calcular_presion_vapor_kPa(temperatura)
pct_h2o_crudo = (P_sat / 101.325) * 100
m3_biogas_crudo = m3_gas_seco / (1 - pct_h2o_crudo / 100)

rem_h2s = info_purif["eficiencia_h2s_pct"] / 100.0
rem_h2o = info_purif["eficiencia_h2o_pct"] / 100.0
rem_co2 = info_purif["eficiencia_co2_pct"] / 100.0

h2s_tratado_ppm = datos_sust["h2s_ppm_base"] * (1.0 - rem_h2s)
pct_h2o_tratado = pct_h2o_crudo * (1.0 - rem_h2o)

m3_co2_tratado = (m3_gas_seco * (pct_co2_seco / 100)) * (1.0 - rem_co2)
m3_biogas_tratado = (m3_ch4_seco + m3_co2_tratado) / (1.0 - pct_h2o_tratado / 100)
pct_ch4_final = (m3_ch4_seco / m3_biogas_tratado) * 100

pci_metano = df_params.loc["pci_metano", "valor"]
potencia_primaria_kwh = m3_ch4_seco * pci_metano

energia_elec_bruta_kwh = potencia_primaria_kwh * ef_elec_chp
energia_term_bruta_kwh = potencia_primaria_kwh * ef_term_chp

delta_t = max(0, temperatura - temp_ambiente)
calor_calentamiento_sustrato_kJ = masa_diaria * df_params.loc["calor_especifico_agua", "valor"] * delta_t
calor_autoconsumo_kwh = calor_calentamiento_sustrato_kJ / 3600.0
calor_neto_exportable_kwh = max(0.0, energia_term_bruta_kwh - calor_autoconsumo_kwh)

# --- VISTAS / RESULTADOS SEGÚN MODO ---

if not es_avanzado:
    # 🟢 INTERFAZ MODO SIMPLE
    st.subheader("💡 Resultados Rápidos Estimados")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Biogás Producido", f"{m3_biogas_crudo:.1f} m³/día")
    col2.metric("Energía Eléctrica Generada", f"{energia_elec_bruta_kwh:.1f} kWh/día")
    
    # Equivalencia didáctica (Consumo aprox de un hogar promedio: 8 kWh/día)
    casas_equivalentes = energia_elec_bruta_kwh / 8.0
    col3.metric("Equivalente a Abastecer", f"~ {casas_equivalentes:.1f} hogares/día")
    
    st.divider()
    
    st.info(f"""
    **¿Sabías qué?**  
    Procesando **{masa_diaria} kg/día** de *{sustrato_sel}*, estás generando **{m3_ch4_seco:.1f} m³ de metano puro**, 
    evitando que esa materia orgánica se descomponga al aire libre emitiendo gases de efecto invernadero.
    """)
    
    # Gráfico simple de producción mensual
    dias = np.arange(1, 31)
    df_chart = pd.DataFrame({
        "Día": dias,
        "Biogás (m³/día)": m3_biogas_crudo * np.random.normal(1.0, 0.02, size=len(dias))
    }).set_index("Día")
    
    st.subheader("📈 Estimación de Biogás a 30 Días")
    st.line_chart(df_chart)

else:
    # 🔬 INTERFAZ MODO AVANZADO (CHP & Upgrading Completo)
    st.subheader("⚡ Balance Avanzado CHP (Combined Heat and Power)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Potencia Primaria Biogás", f"{potencia_primaria_kwh:.1f} kWh/día")
    c2.metric("Energía Eléctrica Bruta", f"{energia_elec_bruta_kwh:.1f} kWh/día", delta=f"{energia_elec_bruta_kwh/24:.2f} kW avg")
    c3.metric("Calor Bruto Recuperable", f"{energia_term_bruta_kwh:.1f} kWh/día")
    c4.metric("Calor Neto Exportable", f"{calor_neto_exportable_kwh:.1f} kWh/día", delta=f"Autoconsumo: {calor_autoconsumo_kwh:.1f} kWh")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔴 Biogás Crudo vs 🟢 Biogás Tratado")
        df_comp = pd.DataFrame({
            "Métrica": ["Metano (CH₄ %)", "Humedad (H₂O %)", "H₂S (ppm)"],
            "Crudo": [pct_ch4_seco * (1 - pct_h2o_crudo/100), pct_h2o_crudo, datos_sust["h2s_ppm_base"]],
            "Tratado": [pct_ch4_final, pct_h2o_tratado, h2s_tratado_ppm]
        }).set_index("Métrica")
        st.dataframe(df_comp, use_container_width=True)

    with col_right:
        st.subheader("📊 Distribución Energética CH₄")
        energia_perdida_kwh = potencia_primaria_kwh - (energia_elec_bruta_kwh + energia_term_bruta_kwh)
        df_dist = pd.DataFrame({
            "Destino": ["Eléctrica", "Autoconsumo Térmico", "Calor Exportable", "Pérdidas"],
            "kWh/día": [energia_elec_bruta_kwh, min(energia_term_bruta_kwh, calor_autoconsumo_kwh), calor_neto_exportable_kwh, max(0.0, energia_perdida_kwh)]
        }).set_index("Destino")
        st.bar_chart(df_dist)

    if h2s_tratado_ppm > 100:
        st.error(f"⚠️ **Alerta Técnica:** Nivel de $H_2S$ ({h2s_tratado_ppm:.0f} ppm) demasiado alto para el motogenerador.")