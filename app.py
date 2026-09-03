import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Biodigestor Virtual", 
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Biodigestor Virtual")

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

# --- FUNCIÓN ANIMACIÓN SVG ESTILO PhET CON MEJORAS DE DISEÑO ---
def mostrar_animacion_biodigestor(volumen_m3, temp_c, modo_agitacion, ph_entrada, ph_reactor, masa_kg_dia, m3_biogas_dia):
    # 1. Configuración de agitación
    if modo_agitacion == "continua":
        dur_agit = "1.5s"
        anim_agit = "indefinite"
    elif modo_agitacion == "intermitente":
        dur_agit = "4s"
        anim_agit = "indefinite"
    else:
        dur_agit = "0s"
        anim_agit = "0"

    # 2. Frecuencia de burbujeo según tasa de biogás
    dur_burbuja = "1.2s" if m3_biogas_dia > 200 else ("2.5s" if m3_biogas_dia > 50 else "4.5s")
    
    # 3. Nivel de carga en la tolva de entrada (20 a 70 px)
    alto_cuba_biomasa = int(min(70, max(15, (masa_kg_dia / 5000) * 70)))
    y_inicio_biomasa = 230 - alto_cuba_biomasa

    # 4. Posición Y en escala de pH (0 a 14 -> Y: 250 a 80)
    y_sonda_escala = int(250 - (ph_reactor / 14.0) * 170)

    html_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; background-color: #ffffff; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <svg width="480" height="310" viewBox="0 0 480 310">
            <defs>
                <!-- Gradiente Cúpula VERDE de Gas -->
                <linearGradient id="gasDomeGreenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#2ecc71" stop-opacity="0.85"/>
                    <stop offset="100%" stop-color="#a8e6cf" stop-opacity="0.30"/>
                </linearGradient>

                <!-- Gradiente Digestato Líquido -->
                <linearGradient id="digestatoGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#795548"/>
                    <stop offset="50%" stop-color="#5D4037"/>
                    <stop offset="100%" stop-color="#4E342E"/>
                </linearGradient>

                <!-- Gradiente Escala pH estilo PhET -->
                <linearGradient id="phScaleGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stop-color="#e74c3c"/>     <!-- pH 0 Rojo -->
                    <stop offset="35%" stop-color="#f39c12"/>    <!-- pH 5 Ácido -->
                    <stop offset="50%" stop-color="#2ecc71"/>    <!-- pH 7 Neutro -->
                    <stop offset="75%" stop-color="#3498db"/>    <!-- pH 10 Básico -->
                    <stop offset="100%" stop-color="#2c3e50"/>   <!-- pH 14 Alcalino -->
                </linearGradient>
            </defs>

            <!-- ================= ESCALA DE pH VERTICAL ================= -->
            <g id="escala_ph">
                <!-- Barra Gradiente -->
                <rect x="18" y="80" width="18" height="170" rx="3" fill="url(#phScaleGrad)" stroke="#4a5568" stroke-width="1.2"/>
                
                <!-- Marcas de pH (14, 7, 0) -->
                <line x1="36" y1="80" x2="41" y2="80" stroke="#4a5568" stroke-width="1"/>
                <text x="44" y="83" font-size="8" fill="#4a5568" font-weight="bold">14</text>

                <line x1="36" y1="165" x2="43" y2="165" stroke="#27ae60" stroke-width="1.5"/>
                <text x="45" y="168" font-size="9" fill="#27ae60" font-weight="bold">7</text>

                <line x1="36" y1="250" x2="41" y2="250" stroke="#4a5568" stroke-width="1"/>
                <text x="44" y="253" font-size="8" fill="#4a5568" font-weight="bold">0</text>

                <!-- Lectura de pH flotante en escala -->
                <polygon points="36,{y_sonda_escala} 44,{y_sonda_escala-4} 44,{y_sonda_escala+4}" fill="#2d3748"/>
                <rect x="44" y="{y_sonda_escala-10}" width="38" height="20" rx="4" fill="#2d3748"/>
                <text x="63" y="{y_sonda_escala+3}" text-anchor="middle" fill="#ffffff" font-size="9" font-weight="bold">{ph_reactor:.2f}</text>

                <!-- Cable de sonda curvo hacia el reactor -->
                <path d="M 63 {y_sonda_escala+10} C 63 285, 230 285, 250 210" fill="none" stroke="#4a5568" stroke-width="2" stroke-dasharray="3 2"/>
            </g>

            <!-- ================= CUBA DE ALIMENTACIÓN ================= -->
            <g id="cuba_alimentacion">
                <path d="M 100 155 L 138 155 L 130 230 L 108 230 Z" fill="#edf2f7" stroke="#718096" stroke-width="2"/>
                <path d="M 102 {y_inicio_biomasa} L 136 {y_inicio_biomasa} L 130 230 L 108 230 Z" fill="#6d4c41"/>
                <path d="M 119 220 L 119 240 L 165 240" stroke="#5d4037" stroke-width="5" fill="none"/>
                
                <!-- Tag pH de Entrada -->
                <rect x="95" y="132" fill="#319795" width="48" height="16" rx="3"/>
                <text x="119" y="143" text-anchor="middle" fill="white" font-size="8.5" font-weight="bold">in pH {ph_entrada:.1f}</text>
            </g>

            <!-- ================= REACTOR PRINCIPAL ================= -->
            <!-- Cúpula Verde Biogás -->
            <path d="M 160 110 Q 290 20 420 110 Z" fill="url(#gasDomeGreenGrad)" stroke="#27ae60" stroke-width="2">
                <animate attributeName="d" 
                         values="M 160 110 Q 290 20 420 110 Z; M 160 110 Q 290 15 420 110 Z; M 160 110 Q 290 20 420 110 Z" 
                         dur="3s" repeatCount="indefinite" />
            </path>

            <!-- Cuerpo del Reactor -->
            <path d="M 160 100 L 160 255 A 25 25 0 0 0 185 280 L 395 280 A 25 25 0 0 0 420 255 L 420 100" 
                  fill="none" stroke="#718096" stroke-width="4.5" stroke-linejoin="round"/>

            <!-- Digestato Líquido -->
            <path d="M 163 125 L 163 253 A 22 22 0 0 0 185 275 L 395 275 A 22 22 0 0 0 417 253 L 417 125 Z" 
                  fill="url(#digestatoGrad)"/>
            <ellipse cx="290" cy="125" rx="127" ry="6" fill="#4E342E"/>

            <!-- Burbujas de Metano -->
            <g id="burbujas">
                <circle cx="220" cy="230" r="3" fill="#e8f8f5" opacity="0.8">
                    <animate attributeName="cy" values="230;125" dur="{dur_burbuja}" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.8;0" dur="{dur_burbuja}" repeatCount="indefinite"/>
                </circle>
                <circle cx="280" cy="250" r="4" fill="#e8f8f5" opacity="0.8">
                    <animate attributeName="cy" values="250;125" dur="1.8s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.9;0" dur="1.8s" repeatCount="indefinite"/>
                </circle>
                <circle cx="340" cy="220" r="3" fill="#e8f8f5" opacity="0.8">
                    <animate attributeName="cy" values="220;125" dur="2.2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.8;0" dur="2.2s" repeatCount="indefinite"/>
                </circle>
            </g>

            <!-- Agitador -->
            <line x1="290" y1="35" x2="290" y2="215" stroke="#2d3748" stroke-width="3.5"/>
            <g transform="translate(290, 215)">
                <g>
                    <ellipse cx="-20" cy="0" rx="16" ry="5" fill="#cbd5e0" stroke="#2d3748" stroke-width="1.2" transform="rotate(-15 -20 0)"/>
                    <ellipse cx="20" cy="0" rx="16" ry="5" fill="#cbd5e0" stroke="#2d3748" stroke-width="1.2" transform="rotate(-15 20 0)"/>
                    <circle cx="0" cy="0" r="4" fill="#2d3748"/>
                    {f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{dur_agit}" repeatCount="{anim_agit}" />' if modo_agitacion != "sin_agitacion" else ''}
                </g>
            </g>

            <!-- Mira de la Sonda en Licor -->
            <g transform="translate(250, 210)">
                <circle cx="0" cy="0" r="10" fill="#2d3748" opacity="0.9"/>
                <circle cx="0" cy="0" r="7" fill="none" stroke="#ffffff" stroke-width="1.2"/>
                <line x1="-5" y1="0" x2="5" y2="0" stroke="#ffffff" stroke-width="1.2"/>
                <line x1="0" y1="-5" x2="0" y2="5" stroke="#ffffff" stroke-width="1.2"/>
            </g>

            <!-- Tubería de Salida de Biogás -->
            <path d="M 290 25 L 290 12 L 420 12 L 420 30" stroke="#27ae60" stroke-width="3.5" fill="none"/>

            <!-- ETIQUETA FASE GAS UBICADA SOBRE LA TUBERÍA (DESPEJADA DE LÍNEAS) -->
            <rect x="330" y="22" width="115" height="20" rx="4" fill="#e8f8f5" stroke="#27ae60" stroke-width="1.2"/>
            <text x="387" y="36" text-anchor="middle" fill="#1e8449" font-weight="bold" font-size="10.5">Fase Gas (CH₄ / CO₂)</text>

            <!-- Badge Temperatura -->
            <rect x="175" y="250" fill="#2ecc71" width="48" height="18" rx="4"/>
            <text x="199" y="262" text-anchor="middle" fill="white" font-weight="bold" font-size="10">{temp_c}°C</text>
        </svg>
    </div>
    """
    components.html(html_code, height=320)

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
        height=310,
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

# pH del Alimento Ingresante
ph_entrada = st.sidebar.slider(
    "🧪 pH de Alimento / Carga:", 
    min_value=3.0, 
    max_value=9.0, 
    value=6.8, 
    step=0.1,
    help="Indica la acidez del sustrato al ingresar a la cuba."
)

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
    temperatura = 35
    trh = 30
    modo_agit = "intermitente" if "intermitente" in df_agitacion.index else list(df_agitacion.index)[0]
    info_agit = df_agitacion.loc[modo_agit]
    tec_purif = "trampa_condensados" if "trampa_condensados" in df_purif.index else list(df_purif.index)[0]
    info_purif = df_purif.loc[tec_purif]
    temp_ambiente = 15
    ef_elec_chp = float(df_params.loc["eficiencia_electrica_chp", "valor"])
    ef_term_chp = float(df_params.loc["eficiencia_termica_chp", "valor"])

# --- CÁLCULO DE pH EN EL REACTOR Y FACTOR DE IMPACTO ---
ph_reactor = 7.2 + (ph_entrada - 7.0) * (masa_diaria / 5000.0) * 0.8
ph_reactor = max(4.0, min(9.0, ph_reactor))

if 6.8 <= ph_reactor <= 7.6:
    factor_ph = 1.0
elif 6.0 <= ph_reactor < 6.8:
    factor_ph = 0.65
elif ph_reactor < 6.0:
    factor_ph = 0.15
else:
    factor_ph = 0.55

# --- CÁLCULOS TÉCNICOS ---
def calcular_presion_vapor_kPa(t_c):
    return (10 ** (8.07131 - (1730.63 / (233.426 + t_c)))) * 0.133322

st_kg = masa_diaria * (float(datos_sust["st_pct"]) / 100.0)
sv_kg = st_kg * (float(datos_sust["sv_pct_st"]) / 100.0)
vol_digestor = (masa_diaria / float(df_params.loc["densidad_agua", "valor"])) * trh

factor_temp = max(0.2, 1.0 - abs(temperatura - 35) * float(df_params.loc["factor_eficiencia_temp", "valor"]))
ef_ag = float(info_agit["eficiencia_mezclado"])

m3_ch4_seco = sv_kg * float(datos_sust["rendimiento_ch4_m3_kgsv"]) * factor_temp * ef_ag * factor_ph
pct_ch4_seco = float(datos_sust["pct_ch4"])
pct_co2_seco = 100.0 - pct_ch4_seco
m3_gas_seco = m3_ch4_seco / (pct_ch4_seco / 100.0) if pct_ch4_seco > 0 else 0.0

P_sat = calcular_presion_vapor_kPa(temperatura)
pct_h2o_crudo = (P_sat / 101.325) * 100.0
m3_biogas_crudo = m3_gas_seco / (1.0 - pct_h2o_crudo / 100.0) if (1.0 - pct_h2o_crudo / 100.0) > 0 else 0.0

rem_h2s = float(info_purif["eficiencia_h2s_pct"]) / 100.0
rem_h2o = float(info_purif["eficiencia_h2o_pct"]) / 100.0
rem_co2 = float(info_purif["eficiencia_co2_pct"]) / 100.0

h2s_tratado_ppm = float(datos_sust["h2s_ppm_base"]) * (1.0 - rem_h2s)
pct_h2o_tratado = pct_h2o_crudo * (1.0 - rem_h2o)

m3_co2_tratado = (m3_gas_seco * (pct_co2_seco / 100.0)) * (1.0 - rem_co2)
m3_biogas_tratado = (m3_ch4_seco + m3_co2_tratado) / (1.0 - pct_h2o_tratado / 100.0) if (1.0 - pct_h2o_tratado / 100.0) > 0 else 0.0
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

col_anim, col_chart = st.columns([1.1, 1.1])

with col_anim:
    mostrar_animacion_biodigestor(
        volumen_m3=vol_digestor, 
        temp_c=temperatura, 
        modo_agitacion=modo_agit, 
        ph_entrada=ph_entrada,
        ph_reactor=ph_reactor, 
        masa_kg_dia=masa_diaria, 
        m3_biogas_dia=m3_biogas_crudo
    )
    st.caption(f"📏 **Volumen reactor:** {vol_digestor:.1f} m³ | 🧪 **pH del Alimento:** {ph_entrada:.1f} | 🧪 **pH Medido en Reactor:** {ph_reactor:.2f}")

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

# --- ALERTAS BIOLÓGICAS DE pH ---
if ph_reactor < 6.5:
    st.error(f"🚨 **ALERTA BIOLÓGICA (Acidosis - pH {ph_reactor:.2f}):** El alimento ingresante ({ph_entrada:.1f}) desequilibró el reactor. La producción de biogás cayó a un **{factor_ph*100:.0f}%** debido a la inhibición de las bacterias metanogénicas.")
elif ph_reactor > 7.8:
    st.warning(f"⚠️ **ALERTA DE ALCALINIDAD (pH {ph_reactor:.2f}):** Riesgo de toxicidad por amonio libre ($NH_3$).")

# --- SECCIÓN DE RESULTADOS SEGÚN EL MODO ---
if not es_avanzado:
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
    
    np.random.seed(42)
    dias = np.arange(1, 31)
    df_chart = pd.DataFrame({
        "Día": dias,
        "Biogás (m³/día)": m3_biogas_crudo * np.random.normal(1.0, 0.02, size=len(dias))
    }).set_index("Día")
    
    st.subheader("📈 Estimación de Producción a 30 Días")
    st.line_chart(df_chart)

else:
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
