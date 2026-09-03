import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Biodigestor Educativo", 
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Simulador Educativo de Biodigestión Anaerobia")

# --- CARGA DE DATOS ROBUSTA ---
@st.cache_data
def cargar_datos():
    archivos = {
        "sustratos": "data/sustratos.csv",
        "parametros": "data/parametros.csv",
        "agitacion": "data/agitacion.csv",
        "purificacion": "data/purificacion.csv"
    }
    
    dfs = {}
    for nombre, ruta in archivos.items():
        try:
            dfs[nombre] = pd.read_csv(ruta, sep=";", quotechar='"', engine="python")
        except FileNotFoundError:
            st.error(f"❌ **Falta un archivo:** No se encontró la tabla `{ruta}`. Verificá que esté dentro de la carpeta `data/`.")
            st.stop()
        except pd.errors.ParserError:
            st.error(f"⚠️ **Error de formato en `{ruta}`:** Hay una fila con inconsistencias en el número de delimitadores (`;`). Revisá el archivo en un editor de texto.")
            st.stop()
        except Exception as e:
            st.error(f"❌ **Error al leer `{ruta}`:** {e}")
            st.stop()

    try:
        df_sustratos = dfs["sustratos"]
        df_params = dfs["parametros"].set_index("parametro")
        df_agitacion = dfs["agitacion"].set_index("modo")
        df_purif = dfs["purificacion"].set_index("tecnologia")
    except KeyError as e:
        st.error(f"⚠️ **Error en la estructura del CSV:** Falta una clave o columna obligatoria: {e}")
        st.stop()

    return df_sustratos, df_params, df_agitacion, df_purif

# Cargar datasets
df_sustratos, df_params, df_agitacion, df_purif = cargar_datos()

# --- FUNCIÓN ANIMACIÓN SVG BIODIGESTOR ---
def mostrar_animacion_biodigestor(volumen_m3, temp_c, modo_agitacion):
    # Configurar velocidad de rotación según el modo de agitación
    if modo_agitacion == "continua":
        duracion_agit = "2s"
        anim_status = "indefinite"
    elif modo_agitacion == "intermitente":
        duracion_agit = "5s"
        anim_status = "indefinite"
    else:  # sin_agitacion
        duracion_agit = "0s"
        anim_status = "0"

    html_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; background-color: #ffffff; padding: 10px; border-radius: 12px; border: 1px solid #e0e0e0;">
        <svg width="340" height="300" viewBox="0 0 340 300">
            <defs>
                <linearGradient id="gasDomeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#f39c12" stop-opacity="0.85"/>
                    <stop offset="100%" stop-color="#f1c40f" stop-opacity="0.4"/>
                </linearGradient>
            </defs>

            <!-- CÚPULA / GASÓMETRO FLEXIBLE SUPERIOR -->
            <path d="M 60 120 Q 170 20 280 120 Z" fill="url(#gasDomeGrad)" stroke="#d35400" stroke-width="3">
                <animate attributeName="d" 
                         values="M 60 120 Q 170 20 280 120 Z; M 60 120 Q 170 12 280 120 Z; M 60 120 Q 170 20 280 120 Z" 
                         dur="3s" repeatCount="indefinite" />
            </path>
            <text x="170" y="70" text-anchor="middle" fill="#d35400" font-weight="bold" font-size="13">Biogás (CH₄ / CO₂)</text>

            <!-- TANQUE CILÍNDRICO / DIGESTOR BASE -->
            <rect x="60" y="120" width="220" height="150" rx="8" fill="#f8f9fa" stroke="#4a5568" stroke-width="4" />

            <!-- NÚCLEO CIRCULAR VERDE BIOLÓGICO -->
            <circle cx="170" cy="195" r="65" fill="#1e7e1e" stroke="#2d3748" stroke-width="3"/>

            <!-- Trayectoria circular punteada de agitación -->
            <circle cx="170" cy="195" r="45" fill="none" stroke="#2e8b57" stroke-width="2" stroke-dasharray="4 4" />

            <!-- BURBUJAS ASCENDENTES HACIA LA CÚPULA -->
            <circle cx="145" cy="220" r="3.5" fill="#ffffff" opacity="0.8">
                <animate attributeName="cy" values="220;90" dur="2.2s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.9;0" dur="2.2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="170" cy="210" r="4.5" fill="#ffffff" opacity="0.8">
                <animate attributeName="cy" values="210;85" dur="1.8s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.9;0" dur="1.8s" repeatCount="indefinite"/>
            </circle>
            <circle cx="195" cy="225" r="3.0" fill="#ffffff" opacity="0.8">
                <animate attributeName="cy" values="225;95" dur="2.6s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.9;0" dur="2.6s" repeatCount="indefinite"/>
            </circle>

            <!-- AGITADOR CENTRAL GIRATORIO CON PALETAS -->
            <line x1="170" y1="120" x2="170" y2="195" stroke="#4a5568" stroke-width="4" />
            <g transform="translate(170, 195)">
                <g>
                    <line x1="-30" y1="0" x2="30" y2="0" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
                    <line x1="0" y1="-30" x2="0" y2="30" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
                    <circle cx="0" cy="0" r="6" fill="#4a5568" />
                    {'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="' + duracion_agit + '" repeatCount="' + anim_status + '" />' if modo_agitacion != "sin_agitacion" else ''}
                </g>
            </g>

            <!-- TUBERÍA DE SALIDA DE BIOGÁS -->
            <path d="M 170 45 L 170 15 L 290 15" stroke="#f39c12" stroke-width="5" fill="none" />
            <text x="235" y="30" fill="#e67e22" font-size="11" font-weight="bold">Salida CH₄</text>

            <!-- ETIQUETA TEMPERATURA -->
            <rect x="215" y="240" fill="#2ecc71" width="50" height="22" rx="4"/>
            <text x="240" y="255" text-anchor="middle" fill="white" font-weight="bold" font-size="11">{temp_c}°C</text>
        </svg>
    </div>
    """
    components.html(html_code, height=310)

# --- FUNCIÓN GRÁFICO COMPOSICIÓN DE GAS ---
def mostrar_grafico_composicion(pct_ch4, pct_co2, pct_h2o, pct_n2=2.0, h2s_ppm=0.0):
    componentes = ["NH3 (ppm)", "H2S (ppm)", "N2", "H2O", "CO2", "CH4"]
    valores = [0.0, 0.0, pct_n2, pct_h2o, pct_co2, pct_ch4]
    colores = ["#e74c3c", "#e67e22", "#6c5ce7", "#e67e22", "#008000", "#0d5cdd"]

    fig = go.Figure()
    
    for comp, val, col in zip(componentes, valores, colores):
        text_label = f"{val:.1f}%" if val > 0 else ""
        fig.add_trace(go.Bar(
            y=[comp],
            x=[val],
            orientation='h',
            marker=dict(color=col),
            text=text_label,
            textposition='auto' if val > 8 else 'outside',
            hoverinfo='y+x',
            showlegend=False
        ))

    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Volume (%) →", dtick=10),
        yaxis=dict(autorange="reversed"),
        height=320,
        margin=dict(l=20, r=20, t=10, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    st.plotly_chart(fig, use_container_width=True)

# --- SELECTOR DE MODO DE USO ---
st.sidebar.markdown("## 🎯 Modo de Uso")
modo_interfaz = st.sidebar.radio(
    "Seleccione el nivel del simulador:",
    ["🌱 Modo Simple (Inicial / Divulgación)", "🔬 Modo Avanzado (Técnico / CHP)"],
    index=0
)

es_avanzado = "Avanzado" in modo_interfaz
st.sidebar.divider()

# --- BARRA LATERAL: ENTRADAS PRINCIPALES ---
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
    modo_agit = st.sidebar.selectbox("Agitación:", list(df_agitacion.index), format_func=lambda x: str(x).replace("_", " ").title())
    info_agit = df_agitacion.loc[modo_agit]

    st.sidebar.header("🧼 4. Filtro de Biogás")
    tec_purif = st.sidebar.selectbox("Purificación:", list(df_purif.index), format_func=lambda x: str(x).replace("_", " ").title())
    info_purif = df_purif.loc[tec_purif]

    st.sidebar.header("🔥 5. Cogeneración CHP")
    temp_ambiente = st.sidebar.slider("Temperatura ambiente (°C):", -5, 35, 15)
    ef_elec_chp = st.sidebar.slider("Eficiencia Eléctrica CHP (%):", 25, 45, int(df_params.loc["eficiencia_electrica_chp", "valor"] * 100)) / 100.0
    ef_term_chp = st.sidebar.slider("Eficiencia Térmica CHP (%):", 30, 60, int(df_params.loc["eficiencia_termica_chp", "valor"] * 100)) / 100.0
else:
    temperatura = 35  # Óptimo mesofílico
    trh = 30
    modo_agit = "intermitente" if "intermitente" in df_agitacion.index else list(df_agitacion.index)[0]
    info_agit = df_agitacion.loc[modo_agit]
    tec_purif = "trampa_condensados" if "trampa_condensados" in df_purif.index else list(df_purif.index)[0]
    info_purif = df_purif.loc[tec_purif]
    temp_ambiente = 15
    ef_elec_chp = float(df_params.loc["eficiencia_electrica_chp", "valor"])
    ef_term_chp = float(df_params.loc["eficiencia_termica_chp", "valor"])

# --- CÁLCULOS TÉCNICOS ---
def calcular_presion_vapor_kPa(t_c):
    return (10 ** (8.07131 - (1730.63 / (233.426 + t_c)))) * 0.133322

st_kg = masa_diaria * (float(datos_sust["st_pct"]) / 100.0)
sv_kg = st_kg * (float(datos_sust["sv_pct_st"]) / 100.0)
vol_digestor = (masa_diaria / float(df_params.loc["densidad_agua", "valor"])) * trh

factor_temp = max(0.2, 1.0 - abs(temperatura - 35) * float(df_params.loc["factor_eficiencia_temp", "valor"]))
ef_ag = float(info_agit["eficiencia_mezclado"])

m3_ch4_seco = sv_kg * float(datos_sust["rendimiento_ch4_m3_kgsv"]) * factor_temp * ef_ag
pct_ch4_seco = float(datos_sust["pct_ch4"])
pct_co2_seco = 100.0 - pct_ch4_seco
m3_gas_seco = m3_ch4_seco / (pct_ch4_seco / 100.0)

P_sat = calcular_presion_vapor_kPa(temperatura)
pct_h2o_crudo = (P_sat / 101.325) * 100.0
m3_biogas_crudo = m3_gas_seco / (1.0 - pct_h2o_crudo / 100.0)

rem_h2s = float(info_purif["eficiencia_h2s_pct"]) / 100.0
rem_h2o = float(info_purif["eficiencia_h2o_pct"]) / 100.0
rem_co2 = float(info_purif["eficiencia_co2_pct"]) / 100.0

h2s_tratado_ppm = float(datos_sust["h2s_ppm_base"]) * (1.0 - rem_h2s)
pct_h2o_tratado = pct_h2o_crudo * (1.0 - rem_h2o)

m3_co2_tratado = (m3_gas_seco * (pct_co2_seco / 100.0)) * (1.0 - rem_co2)
m3_biogas_tratado = (m3_ch4_seco + m3_co2_tratado) / (1.0 - pct_h2o_tratado / 100.0)
pct_ch4_final = (m3_ch4_seco / m3_biogas_tratado) * 100.0 if m3_biogas_tratado > 0 else 0.0

pci_metano = float(df_params.loc["pci_metano", "valor"])
potencia_primaria_kwh = m3_ch4_seco * pci_metano

energia_elec_bruta_kwh = potencia_primaria_kwh * ef_elec_chp
energia_term_bruta_kwh = potencia_primaria_kwh * ef_term_chp

delta_t = max(0.0, temperatura - temp_ambiente)
calor_calentamiento_sustrato_kJ = masa_diaria * float(df_params.loc["calor_especifico_agua", "valor"]) * delta_t
calor_autoconsumo_kwh = calor_calentamiento_sustrato_kJ / 3600.0
calor_neto_exportable_kwh = max(0.0, energia_term_bruta_kwh - calor_autoconsumo_kwh)

# --- ESQUEMA ANIMADO Y COMPOSICIÓN DE GAS ---
st.subheader("🖼️ Esquema del Biodigestor y Composición del Biogás")

col_anim, col_chart = st.columns([1, 1.2])

with col_anim:
    mostrar_animacion_biodigestor(vol_digestor, temperatura, modo_agit)
    st.caption(f"📏 **Volumen estimado:** {vol_digestor:.1f} m³ | 🌡️ **Temperatura:** {temperatura}°C")

with col_chart:
    st.markdown("**Composición volumétrica estimada del biogás:**")
    pct_co2_calc = max(0.0, 100.0 - pct_ch4_seco - pct_h2o_crudo - 2.0)
    mostrar_grafico_composicion(
        pct_ch4=pct_ch4_seco, 
        pct_co2=pct_co2_calc, 
        pct_h2o=pct_h2o_crudo, 
        pct_n2=2.0,
        h2s_ppm=float(datos_sust["h2s_ppm_base"])
    )

st.divider()

# --- SECCIÓN DE RESULTADOS SEGÚN EL MODO ---
if not es_avanzado:
    # 🟢 MODO SIMPLE
    st.subheader("💡 Resultados Rápidos Estimados")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Biogás Producido", f"{m3_biogas_crudo:.1f} m³/día")
    col2.metric("Energía Eléctrica Generada", f"{energia_elec_bruta_kwh:.1f} kWh/día")
    
    casas_equivalentes = energia_elec_bruta_kwh / 8.0
    col3.metric("Equivalente a Abastecer", f"~ {casas_equivalentes:.1f} hogares/día")
    
    st.divider()
    
    st.info(f"""
    **¿Sabías qué?**  
    Procesando **{masa_diaria:,} kg/día** de *{sustrato_sel}*, estás generando **{m3_ch4_seco:.1f} m³ de metano puro**, 
    evitando que esa materia orgánica se descomponga al aire libre emitiendo gases de efecto invernadero.
    """)
    
    # Gráfico simple
    np.random.seed(42)
    dias = np.arange(1, 31)
    df_chart = pd.DataFrame({
        "Día": dias,
        "Biogás (m³/día)": m3_biogas_crudo * np.random.normal(1.0, 0.02, size=len(dias))
    }).set_index("Día")
    
    st.subheader("📈 Estimación de Producción a 30 Días")
    st.line_chart(df_chart)

else:
    # 🔬 MODO AVANZADO
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
            "Crudo": [pct_ch4_seco * (1 - pct_h2o_crudo/100.0), pct_h2o_crudo, float(datos_sust["h2s_ppm_base"])],
            "Tratado": [pct_ch4_final, pct_h2o_tratado, h2s_tratado_ppm]
        }).set_index("Métrica")
        st.dataframe(df_comp, use_container_width=True)

    with col_right:
        st.subheader("📊 Distribución Energética CH₄")
        energia_perdida_kwh = potencia_primaria_kwh - (energia_elec_bruta_kwh + energia_term_bruta_kwh)
        df_dist = pd.DataFrame({
            "Destino": ["Eléctrica", "Autoconsumo Térmico", "Calor Exportable", "Pérdidas"],
            "kWh/día": [
                energia_elec_bruta_kwh, 
                min(energia_term_bruta_kwh, calor_autoconsumo_kwh), 
                calor_neto_exportable_kwh, 
                max(0.0, energia_perdida_kwh)
            ]
        }).set_index("Destino")
        st.bar_chart(df_dist)

    if h2s_tratado_ppm > 100:
        st.error(f"⚠️ **Alerta Técnica:** Nivel de $H_2S$ ({h2s_tratado_ppm:.0f} ppm) elevado para el motogenerador (Límite sugerido: 100 ppm).")