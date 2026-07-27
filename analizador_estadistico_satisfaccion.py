"""
Analizador Estadístico para Satisfacción del Cliente
Proyecto: Sistema web para gestión y análisis de satisfacción de clientes
Áreas: Farmacia, Movilización, Planta de alimentos
Instituto Tecnológico de Tizimín - Estadística para la Inteligencia de Negocios
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from io import BytesIO
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Análisis de Satisfacción del Cliente",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analizador Estadístico - Satisfacción del Cliente")
st.caption("Farmacia · Movilización · Planta de alimentos | Instituto Tecnológico de Tizimín")

# ==================== CARGA DE DATOS ====================
UPLOAD_FOLDER = "datos_cargados"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if 'datasets' not in st.session_state:
    st.session_state.datasets = {}

# Cargar CSV predeterminado si existe
default_csv = "satisfaccion_clientes.csv"
if os.path.exists(default_csv) and default_csv not in st.session_state.datasets:
    try:
        st.session_state.datasets[default_csv] = pd.read_csv(default_csv)
    except Exception:
        pass

for filename in os.listdir(UPLOAD_FOLDER):
    if filename.endswith(".csv") and filename not in st.session_state.datasets:
        try:
            df = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename))
            st.session_state.datasets[filename] = df
        except Exception:
            pass

st.sidebar.header("📁 Carga de Datos")
uploaded_files = st.sidebar.file_uploader(
    "Sube CSV (se guardan automáticamente)",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        try:
            df = pd.read_csv(file_path)
            st.session_state.datasets[file.name] = df
            st.sidebar.success(f"✅ {file.name} guardado")
        except Exception:
            st.sidebar.error(f"Error en {file.name}")

if st.session_state.datasets:
    st.sidebar.write("**Archivos disponibles:**")
    for name in list(st.session_state.datasets.keys()):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"• {name}")
        with col2:
            if st.button("🗑", key=f"del_{name}"):
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, name))
                except Exception:
                    pass
                del st.session_state.datasets[name]
                st.rerun()
else:
    st.info("Sube el archivo CSV de satisfacción de clientes o coloca 'satisfaccion_clientes.csv' en la carpeta.")
    st.stop()

dataset_name = st.sidebar.selectbox("Seleccionar dataset", list(st.session_state.datasets.keys()))
df = st.session_state.datasets[dataset_name].copy()

# Forzar numéricos
for col in df.columns:
    if col not in ['fecha', 'area_servicio', 'genero', 'tipo_cliente', 'turno']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

num_cols = df.select_dtypes(include=np.number).columns.tolist()
# Excluir id si existe
num_cols = [c for c in num_cols if c.lower() not in ['id_encuesta', 'id']]
cat_cols = [c for c in df.columns if c not in num_cols and c != 'fecha']

if not num_cols:
    st.error("⚠️ No se detectaron columnas numéricas.")
    st.dataframe(df.head())
    st.stop()

# Variable objetivo sugerida
obj_sugerida = 'satisfaccion_general' if 'satisfaccion_general' in num_cols else num_cols[0]

st.sidebar.markdown("---")
st.sidebar.header("🎯 Configuración del Análisis")
var_objetivo = st.sidebar.selectbox("Variable Objetivo (Y)", num_cols, 
                                    index=num_cols.index(obj_sugerida) if obj_sugerida in num_cols else 0)
vars_independientes = [c for c in num_cols if c != var_objetivo]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Descriptiva",
    "🔬 Inferencial",
    "🧪 Hipótesis",
    "📉 Regresión",
    "📊 Correlaciones & Export"
])

# ====================== TAB 1: DESCRIPTIVA ======================
with tab1:
    st.header("1. Estadística Descriptiva")
    
    st.subheader("1.1 Estructura del Dataset")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Registros", len(df))
    col_b.metric("Variables numéricas", len(num_cols))
    col_c.metric("Variables categóricas", len(cat_cols))
    
    st.write("**Variables categóricas:**", ", ".join(cat_cols) if cat_cols else "Ninguna")
    st.write("**Variables numéricas:**", ", ".join(num_cols))
    
    selected_vars = st.multiselect(
        "Variables para análisis descriptivo",
        num_cols,
        default=num_cols[:min(8, len(num_cols))]
    )
    
    if selected_vars:
        st.subheader("1.2 Medidas de Tendencia Central y Dispersión")
        desc = df[selected_vars].describe().T
        desc['mediana'] = df[selected_vars].median()
        desc['moda'] = df[selected_vars].mode().iloc[0]
        desc['varianza'] = df[selected_vars].var()
        desc['rango'] = desc['max'] - desc['min']
        desc['IQR'] = desc['75%'] - desc['25%']
        desc['asimetría'] = df[selected_vars].skew()
        desc['curtosis'] = df[selected_vars].kurtosis()
        
        cols_order = ['count', 'mean', 'mediana', 'moda', 'std', 'varianza',
              'min', '25%', '50%', '75%', 'max', 'rango', 'IQR',
              'asimetría', 'curtosis']
        st.dataframe(desc[[c for c in cols_order if c in desc.columns]].round(4),
             use_container_width=True)
        
        st.markdown("""
        **Interpretación de asimetría y curtosis:**
        - **Asimetría ≈ 0**: distribución simétrica | **> 0**: sesgo positivo (cola derecha) | **< 0**: sesgo negativo
        - **Curtosis ≈ 0** (exceso): mesocúrtica | **> 0**: leptocúrtica (picos altos) | **< 0**: platicúrtica (aplanada)
        """)
        
        st.subheader("1.3 Tablas de Frecuencia (Categóricas)")
        for cat in cat_cols:
            freq = df[cat].value_counts().reset_index()
            freq.columns = [cat, 'Frecuencia Absoluta']
            freq['Frecuencia Relativa (%)'] = (freq['Frecuencia Absoluta'] / len(df) * 100).round(2)
            st.write(f"**{cat}**")
            st.dataframe(freq, use_container_width=True, hide_index=True)
        
        st.subheader("1.4 Visualizaciones")
        for var in selected_vars[:4]:  # limitar a 4 para no saturar
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=var, nbins=15, title=f"Histograma - {var}",
                                   color_discrete_sequence=['#1f77b4'])
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig_box = px.box(df, y=var, title=f"Boxplot - {var}",
                                 color_discrete_sequence=['#ff7f0e'])
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Boxplot por área si existe
        if 'area_servicio' in df.columns and var_objetivo in df.columns:
            fig_area = px.box(df, x='area_servicio', y=var_objetivo,
                              title=f"Boxplot de {var_objetivo} por Área de Servicio",
                              color='area_servicio')
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Dispersión ejemplo
if len(selected_vars) >= 2:
    x_var = selected_vars[0] if selected_vars[0] != var_objetivo else selected_vars[1]
    fig_sc = px.scatter(df, x=x_var, y=var_objetivo,
                        title=f"Dispersión: {x_var} vs {var_objetivo}",
                        trendline="ols", opacity=0.5)
    st.plotly_chart(fig_sc, use_container_width=True)

# ====================== TAB 2: INFERENCIAL ======================
with tab2:
    st.header("2. Estadística Inferencial")
    
    st.subheader("2.1 Intervalos de Confianza para la Media")
    
    vars_ic = st.multiselect(
        "Variables para intervalos de confianza",
        num_cols,
        default=[var_objetivo] + vars_independientes[:2]
    )
    
    if vars_ic:
        resultados_ic = []
        for var in vars_ic:
            data = df[var].dropna()
            n = len(data)
            mean = data.mean()
            se = data.std(ddof=1) / np.sqrt(n)
            for conf, z in [(0.90, 1.645), (0.95, 1.96), (0.99, 2.576)]:
                li = mean - z * se
                ls = mean + z * se
                resultados_ic.append({
                    'Variable': var,
                    'n': n,
                    'Media': round(mean, 4),
                    'Nivel Confianza': f"{int(conf*100)}%",
                    'Límite Inferior': round(li, 4),
                    'Límite Superior': round(ls, 4),
                    'Margen de Error': round(z * se, 4)
                })
        st.dataframe(pd.DataFrame(resultados_ic), use_container_width=True, hide_index=True)
        st.info("""
        **Interpretación de negocio:** Con un nivel de confianza del X%, la media poblacional 
        de la variable se encuentra entre el límite inferior y superior. A mayor confianza, 
        el intervalo es más amplio (más conservador).
        """)
    
    st.subheader("2.2 Prueba Z / T para una muestra")
    var_one = st.selectbox("Variable", num_cols, key="one_sample_var")
    mu0 = st.number_input("Valor de referencia (μ₀)", value=7.0, step=0.1)
    alpha_one = st.select_slider("α", options=[0.01, 0.05, 0.10], value=0.05, key="alpha_one")
    
    if st.button("Ejecutar prueba de una muestra"):
        data = df[var_one].dropna()
        n = len(data)
        mean = data.mean()
        std = data.std(ddof=1)
        se = std / np.sqrt(n)
        # Usamos t siempre (más correcto con σ desconocida)
        t_stat = (mean - mu0) / se
        p_val = 2 * stats.t.sf(np.abs(t_stat), df=n-1)
        test_name = "Z-test (aprox. n≥30)" if n >= 30 else "T-test"
        
        st.success(f"**Prueba:** {test_name} | n={n}")
        st.write(f"**Media muestral:** {mean:.4f} | **μ₀:** {mu0}")
        st.write(f"**Estadístico t:** {t_stat:.4f} | **p-value:** {p_val:.6f}")
        decision = "Rechazar H₀" if p_val < alpha_one else "No rechazar H₀"
        st.write(f"**Decisión (α={alpha_one}):** {decision}")
        if p_val < alpha_one:
            st.write(f"La media de **{var_one}** es significativamente diferente de {mu0}.")
        else:
            st.write(f"No hay evidencia suficiente para afirmar que la media difiere de {mu0}.")
    
    st.subheader("2.3 Prueba T para dos muestras independientes")
    if cat_cols:
        group_col = st.selectbox("Columna de agrupación", cat_cols, key="group_col")
        var_two = st.selectbox("Variable numérica a comparar", num_cols, key="two_sample_var")
        alpha_two = st.select_slider("α", options=[0.01, 0.05, 0.10], value=0.05, key="alpha_two")
        
        groups = df[group_col].dropna().unique()
        if len(groups) >= 2:
            g1_name, g2_name = st.selectbox("Grupo 1", groups, key="g1"), st.selectbox("Grupo 2", [g for g in groups if g != groups[0]], key="g2")
            if st.button("Ejecutar prueba de dos muestras"):
                g1 = df[df[group_col] == g1_name][var_two].dropna()
                g2 = df[df[group_col] == g2_name][var_two].dropna()
                t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
                st.success(f"**T-test (Welch)** | n1={len(g1)}, n2={len(g2)}")
                st.write(f"**Media {g1_name}:** {g1.mean():.4f} | **Media {g2_name}:** {g2.mean():.4f}")
                st.write(f"**t:** {t_stat:.4f} | **p-value:** {p_val:.6f}")
                decision = "Rechazar H₀" if p_val < alpha_two else "No rechazar H₀"
                st.write(f"**Decisión:** {decision} (α={alpha_two})")
        else:
            st.warning("La columna de grupos debe tener al menos 2 categorías.")

# ====================== TAB 3: HIPÓTESIS ======================
with tab3:
    st.header("3. Pruebas de Hipótesis Específicas")
    
    st.subheader("HIPÓTESIS #1: Correlación entre Variable Determinante y Variable Objetivo")
    
    var_x_h1 = st.selectbox("Variable Determinante (X)", vars_independientes, key="h1_x")
    alpha_h = 0.05
    
    st.markdown(f"""
    **PREGUNTA DE INVESTIGACIÓN**  
    ¿Existe una relación estadísticamente significativa entre **{var_x_h1}** y **{var_objetivo}**?
    
    **PLANTEAMIENTO**  
    - H₀: ρ = 0 (No existe correlación lineal significativa)  
    - H₁: ρ ≠ 0 (Existe correlación lineal significativa)  
    - Notación: H₀: ρ = 0  vs  H₁: ρ ≠ 0  
    - Nivel de significancia: α = 0.05  
    - Prueba: Correlación de Pearson (o Spearman si no normalidad)
    """)
    
    if st.button("Ejecutar Hipótesis #1"):
        data_clean = df[[var_x_h1, var_objetivo]].dropna()
        r, p = stats.pearsonr(data_clean[var_x_h1], data_clean[var_objetivo])
        rs, ps = stats.spearmanr(data_clean[var_x_h1], data_clean[var_objetivo])
        
        st.write("### RESULTADOS")
        res_h1 = pd.DataFrame({
            'Métrica': ['r de Pearson', 'p-value Pearson', 'ρ de Spearman', 'p-value Spearman', 'n'],
            'Valor': [round(r, 4), f"{p:.6f}", round(rs, 4), f"{ps:.6f}", len(data_clean)]
        })
        st.dataframe(res_h1, hide_index=True)
        
        decision = "Rechazar H₀" if p < alpha_h else "No rechazar H₀"
        st.write(f"**DECISIÓN:** {decision} (p = {p:.6f} {'<' if p < alpha_h else '≥'} 0.05)")
        
        if p < alpha_h:
            fuerza = "fuerte" if abs(r) > 0.7 else ("moderada" if abs(r) > 0.4 else "débil")
            direccion = "positiva" if r > 0 else "negativa"
            st.success(f"**CONCLUSIÓN DE NEGOCIO:** Existe una correlación {fuerza} {direccion} "
                       f"(r={r:.3f}) entre {var_x_h1} y {var_objetivo}. "
                       f"Mejorar {var_x_h1} tiende a {'aumentar' if r>0 else 'disminuir'} la satisfacción general.")
        else:
            st.warning(f"**CONCLUSIÓN DE NEGOCIO:** No se encontró evidencia de correlación significativa "
                       f"entre {var_x_h1} y {var_objetivo}. Otras variables pueden ser más relevantes.")
    
    st.markdown("---")
    st.subheader("HIPÓTESIS #2: Influencia de Múltiples Variables Independientes")
    
    vars_h2 = st.multiselect(
        "Variables independientes a evaluar",
        vars_independientes,
        default=vars_independientes[:min(6, len(vars_independientes))],
        key="h2_vars"
    )
    
    st.markdown(f"""
    **PREGUNTA DE INVESTIGACIÓN**  
    ¿Cuáles de las siguientes variables tienen influencia significativa sobre **{var_objetivo}**?  
    Variables consideradas: {', '.join(vars_h2) if vars_h2 else 'Ninguna'}
    
    **PLANTEAMIENTO (para cada Xi)**  
    - H₀: βᵢ = 0 (La variable NO tiene influencia significativa)  
    - H₁: βᵢ ≠ 0 (La variable SÍ tiene influencia significativa)  
    - Modelo: {var_objetivo} ~ {' + '.join(vars_h2) if vars_h2 else '...'}  
    - Prueba: t-test para cada coeficiente | α = 0.05
    """)
    
    if st.button("Ejecutar Hipótesis #2") and vars_h2:
        X = df[vars_h2].dropna()
        y = df[var_objetivo].loc[X.index]
        X_const = sm.add_constant(X)
        model = sm.OLS(y, X_const).fit()
        
        st.write("### RESULTADOS INDIVIDUALES")
        coef_df = pd.DataFrame({
            'Variable': model.params.index,
            'Coeficiente (β)': model.params.values.round(4),
            'Error Estándar': model.bse.values.round(4),
            't': model.tvalues.values.round(4),
            'p-value': model.pvalues.values.round(6),
            'Decisión': ['Rechazar H₀' if p < 0.05 else 'No rechazar H₀' for p in model.pvalues]
        })
        st.dataframe(coef_df, hide_index=True, use_container_width=True)
        
        sig = coef_df[(coef_df['Variable'] != 'const') & (coef_df['Decisión'] == 'Rechazar H₀')]['Variable'].tolist()
        no_sig = coef_df[(coef_df['Variable'] != 'const') & (coef_df['Decisión'] == 'No rechazar H₀')]['Variable'].tolist()
        
        st.write("**VARIABLES SIGNIFICATIVAS:**", ", ".join(sig) if sig else "Ninguna")
        st.write("**VARIABLES NO SIGNIFICATIVAS:**", ", ".join(no_sig) if no_sig else "Ninguna")
        
        st.write("### ANÁLISIS DE COEFICIENTES")
        for _, row in coef_df[coef_df['Variable'] != 'const'].iterrows():
            if row['Decisión'] == 'Rechazar H₀':
                direccion = "aumenta" if row['Coeficiente (β)'] > 0 else "disminuye"
                st.write(f"- **{row['Variable']}**: por cada unidad que aumenta, {var_objetivo} {direccion} en promedio "
                         f"{abs(row['Coeficiente (β)']):.3f} puntos (p={row['p-value']:.4f}).")
        
        st.success(f"**CONCLUSIÓN DE NEGOCIO:** Las variables realmente importantes para predecir "
                   f"{var_objetivo} son: {', '.join(sig) if sig else 'ninguna de las evaluadas'}. "
                   f"Se recomienda enfocar recursos de mejora en ellas.")

# ====================== TAB 4: REGRESIÓN ======================
with tab4:
    st.header("4. Regresión Lineal")
    
    st.subheader("4.1 Regresión Lineal Simple")
    var_x_simple = st.selectbox("Variable independiente (X)", vars_independientes, key="reg_simple_x")
    
    if st.button("Ajustar Regresión Simple"):
        data = df[[var_x_simple, var_objetivo]].dropna()
        X = sm.add_constant(data[var_x_simple])
        y = data[var_objetivo]
        model_s = sm.OLS(y, X).fit()
        
        st.write("### Ecuación del modelo")
        st.code(f"{var_objetivo} = {model_s.params['const']:.4f} + {model_s.params[var_x_simple]:.4f} · {var_x_simple}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("R²", f"{model_s.rsquared:.4f}")
        col2.metric("r (correlación)", f"{np.sqrt(model_s.rsquared)*np.sign(model_s.params[var_x_simple]):.4f}")
        col3.metric("p-valor modelo", f"{model_s.f_pvalue:.6f}")
        col4.metric("n", len(data))
        
        st.write("**Coeficientes:**")
        st.dataframe(pd.DataFrame({
            'Parámetro': ['β₀ (intercepto)', f'β₁ ({var_x_simple})'],
            'Valor': [model_s.params['const'], model_s.params[var_x_simple]],
            'Error Estándar': [model_s.bse['const'], model_s.bse[var_x_simple]],
            't': [model_s.tvalues['const'], model_s.tvalues[var_x_simple]],
            'p-value': [model_s.pvalues['const'], model_s.pvalues[var_x_simple]]
        }).round(4), hide_index=True)
        
        decision = "Rechazar H₀ → La variable SÍ es predictora" if model_s.pvalues[var_x_simple] < 0.05 else "No rechazar H₀ → La variable NO es predictora"
        st.write(f"**Decisión:** {decision}")
        
        fig = px.scatter(data, x=var_x_simple, y=var_objetivo, trendline="ols",
                         title=f"Regresión Simple: {var_objetivo} ~ {var_x_simple}",
                         opacity=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
        st.session_state['model_simple'] = model_s
        st.session_state['var_x_simple'] = var_x_simple
    
    st.subheader("4.2 Regresión Lineal Múltiple")
    vars_multi = st.multiselect(
        "Variables independientes",
        vars_independientes,
        default=vars_independientes[:min(6, len(vars_independientes))],
        key="reg_multi"
    )
    
    if st.button("Ajustar Regresión Múltiple") and vars_multi:
        data = df[vars_multi + [var_objetivo]].dropna()
        X = sm.add_constant(data[vars_multi])
        y = data[var_objetivo]
        model_m = sm.OLS(y, X).fit()
        
        eq = f"{var_objetivo} = {model_m.params['const']:.4f}"
        for v in vars_multi:
            eq += f" + {model_m.params[v]:.4f}·{v}"
        st.write("### Ecuación del modelo")
        st.code(eq)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("R²", f"{model_m.rsquared:.4f}")
        col2.metric("R² Ajustado", f"{model_m.rsquared_adj:.4f}")
        col3.metric("RMSE", f"{np.sqrt(model_m.mse_resid):.4f}")
        col4.metric("F-statistic", f"{model_m.fvalue:.2f}")
        col5.metric("p-valor (F)", f"{model_m.f_pvalue:.6f}")
        
        st.write("**Coeficientes:**")
        coef_m = pd.DataFrame({
            'Variable': model_m.params.index,
            'β': model_m.params.values.round(4),
            'EE': model_m.bse.values.round(4),
            't': model_m.tvalues.values.round(4),
            'p-value': model_m.pvalues.values.round(6)
        })
        st.dataframe(coef_m, hide_index=True, use_container_width=True)
        
        decision_f = "Rechazar H₀ → El modelo ES significativo" if model_m.f_pvalue < 0.05 else "No rechazar H₀ → El modelo NO es significativo"
        st.write(f"**Prueba ANOVA (F):** {decision_f}")
        
        # Diagnósticos
        st.subheader("4.3 Diagnóstico del Modelo")
        
        # VIF
        st.write("**VIF (Multicolinealidad)** — Valores > 10 indican problemas graves")
        vif_data = pd.DataFrame()
        vif_data['Variable'] = vars_multi
        vif_data['VIF'] = [variance_inflation_factor(X.values, i+1) for i in range(len(vars_multi))]
        st.dataframe(vif_data.round(3), hide_index=True)
        
        # Residuos
        residuos = model_m.resid
        ajustados = model_m.fittedvalues
        
        # Shapiro-Wilk (muestra si n grande)
        sample_res = residuos.sample(min(500, len(residuos)), random_state=42) if len(residuos) > 500 else residuos
        shapiro_stat, shapiro_p = stats.shapiro(sample_res)
        st.write(f"**Shapiro-Wilk (normalidad de residuos):** W={shapiro_stat:.4f}, p={shapiro_p:.6f} "
                 f"→ {'Residuos normales' if shapiro_p > 0.05 else 'Residuos NO normales (aprox.)'}")
        
        # Breusch-Pagan
        bp_stat, bp_p, _, _ = het_breuschpagan(residuos, X)
        st.write(f"**Breusch-Pagan (homocedasticidad):** LM={bp_stat:.4f}, p={bp_p:.6f} "
                 f"→ {'Homocedasticidad' if bp_p > 0.05 else 'Heterocedasticidad detectada'}")
        
        # Durbin-Watson
        dw = durbin_watson(residuos)
        st.write(f"**Durbin-Watson (autocorrelación):** {dw:.4f} "
                 f"(≈2 → sin autocorrelación; <1.5 o >2.5 → posible problema)")
        
        # Gráficos de diagnóstico
        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=("Residuos vs Ajustados", "QQ-Plot",
                                            "Histograma de Residuos", "Cook's Distance"))
        
        fig.add_trace(go.Scatter(x=ajustados, y=residuos, mode='markers',
                                 marker=dict(opacity=0.4, size=4), name="Residuos"), row=1, col=1)
        fig.add_hline(y=0, line_dash="dash", row=1, col=1)
        
        # QQ
        qq = stats.probplot(residuos, dist="norm")
        fig.add_trace(go.Scatter(x=qq[0][0], y=qq[0][1], mode='markers',
                                 marker=dict(opacity=0.4, size=4), name="QQ"), row=1, col=2)
        
        fig.add_trace(go.Histogram(x=residuos, nbinsx=30, name="Hist"), row=2, col=1)
        
        # Cook's distance
        influence = model_m.get_influence()
        cooks = influence.cooks_distance[0]
        fig.add_trace(go.Scatter(x=list(range(len(cooks))), y=cooks, mode='markers',
                                 marker=dict(opacity=0.4, size=4), name="Cook"), row=2, col=2)
        
        fig.update_layout(height=700, showlegend=False, title_text="Diagnósticos de Residuos")
        st.plotly_chart(fig, use_container_width=True)
        
        st.session_state['model_multi'] = model_m
        st.session_state['vars_multi'] = vars_multi
    
    # Comparación de modelos
    if 'model_simple' in st.session_state and 'model_multi' in st.session_state:
        st.subheader("4.4 Comparación de Modelos")
        ms = st.session_state['model_simple']
        mm = st.session_state['model_multi']
        comp = pd.DataFrame({
            'Métrica': ['R²', 'R² Ajustado', 'RMSE', 'AIC', 'BIC'],
            'Simple': [ms.rsquared, ms.rsquared_adj, np.sqrt(ms.mse_resid), ms.aic, ms.bic],
            'Múltiple': [mm.rsquared, mm.rsquared_adj, np.sqrt(mm.mse_resid), mm.aic, mm.bic]
        }).round(4)
        st.dataframe(comp, hide_index=True)
        st.info("El modelo con mayor R² Ajustado y menor AIC/BIC suele preferirse.")

# ====================== TAB 5: CORRELACIONES & EXPORT ======================
with tab5:
    st.header("Matriz de Correlaciones y Exportación")
    
    method = st.selectbox("Método de correlación", ["pearson", "spearman"])
    corr = df[num_cols].corr(method=method)
    
    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title=f"Matriz de Correlación ({method})")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Exportar resultados descriptivos")
    if st.button("Generar Excel de resumen"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            desc_full = df[num_cols].describe().T
            desc_full['mediana'] = df[num_cols].median()
            desc_full['moda'] = df[num_cols].mode().iloc[0]
            desc_full['varianza'] = df[num_cols].var()
            desc_full['asimetría'] = df[num_cols].skew()
            desc_full['curtosis'] = df[num_cols].kurtosis()
            desc_full.to_excel(writer, sheet_name='Descriptiva')
            corr.to_excel(writer, sheet_name='Correlaciones')
            df.head(100).to_excel(writer, sheet_name='Muestra_Datos', index=False)
        output.seek(0)
        st.download_button(
            "⬇️ Descargar Excel",
            output,
            file_name=f"resumen_estadistico_{dataset_name.replace('.csv','')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.info("💡 Este analizador cubre todas las partes del proyecto: Descriptiva, Inferencial, "
            "Hipótesis, Regresión (simple/múltiple + diagnósticos) y Correlaciones.")
