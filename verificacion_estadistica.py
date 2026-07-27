"""
Script de verificación estadística - Comprobación de resultados
Proyecto: Satisfacción del Cliente (Farmacia, Movilización, Planta de alimentos)
Instituto Tecnológico de Tizimín
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

# Cargar datos
df = pd.read_csv("satisfaccion_clientes.csv")
print("=" * 70)
print("VERIFICACIÓN ESTADÍSTICA - SATISFACCIÓN DEL CLIENTE")
print("=" * 70)
print(f"\nRegistros: {len(df)}")
print(f"Columnas: {list(df.columns)}")

num_cols = [
    'satisfaccion_general', 'amabilidad_personal', 'tiempo_espera',
    'calidad_servicio', 'limpieza_instalaciones', 'claridad_informacion',
    'resolucion_problema', 'probabilidad_recomendar', 'edad_cliente',
    'tiempo_atencion_minutos'
]
var_obj = 'satisfaccion_general'

# ========== 1. DESCRIPTIVA ==========
print("\n" + "=" * 70)
print("1. ESTADÍSTICA DESCRIPTIVA")
print("=" * 70)

desc = df[num_cols].describe().T
desc['mediana'] = df[num_cols].median()
desc['moda'] = df[num_cols].mode().iloc[0]
desc['varianza'] = df[num_cols].var()
desc['rango'] = desc['max'] - desc['min']
desc['IQR'] = desc['75%'] - desc['25%']
desc['asimetria'] = df[num_cols].skew()
desc['curtosis'] = df[num_cols].kurtosis()

print("\nMedidas descriptivas (primeras 5 variables):")
print(desc[['count', 'mean', 'mediana', 'std', 'min', 'max', 'asimetria', 'curtosis']].head().round(4))

print("\nTablas de frecuencia:")
for cat in ['area_servicio', 'genero', 'tipo_cliente', 'turno']:
    print(f"\n{cat}:")
    print(df[cat].value_counts(normalize=True).mul(100).round(2).to_string())

# ========== 2. INTERVALOS DE CONFIANZA ==========
print("\n" + "=" * 70)
print("2. INTERVALOS DE CONFIANZA (Media de satisfaccion_general y otras)")
print("=" * 70)

for var in [var_obj, 'amabilidad_personal', 'calidad_servicio']:
    data = df[var].dropna()
    n, mean, se = len(data), data.mean(), data.std(ddof=1) / np.sqrt(len(data))
    print(f"\n{var}: media={mean:.4f}, n={n}")
    for conf, z in [(0.90, 1.645), (0.95, 1.96), (0.99, 2.576)]:
        li, ls = mean - z * se, mean + z * se
        print(f"  {int(conf*100)}%: [{li:.4f}, {ls:.4f}]")

# ========== 3. PRUEBAS DE HIPÓTESIS ==========
print("\n" + "=" * 70)
print("3. PRUEBAS DE HIPÓTESIS")
print("=" * 70)

# H1: Correlación amabilidad vs satisfaccion
r, p = stats.pearsonr(df['amabilidad_personal'], df[var_obj])
print(f"\nH1 - Correlación Pearson (amabilidad_personal vs {var_obj}):")
print(f"  r = {r:.4f}, p-value = {p:.6e}")
print(f"  Decisión: {'Rechazar H0' if p < 0.05 else 'No rechazar H0'}")

# H2: Regresión múltiple - influencia de variables
vars_x = ['amabilidad_personal', 'tiempo_espera', 'calidad_servicio',
          'limpieza_instalaciones', 'claridad_informacion', 'resolucion_problema']
X = sm.add_constant(df[vars_x])
y = df[var_obj]
model = sm.OLS(y, X).fit()
print(f"\nH2 - Influencia de múltiples variables sobre {var_obj}:")
print(model.summary().tables[1])
print(f"\nR² = {model.rsquared:.4f}, R² adj = {model.rsquared_adj:.4f}")
print(f"F = {model.fvalue:.2f}, p(F) = {model.f_pvalue:.6e}")

# ========== 4. REGRESIÓN SIMPLE ==========
print("\n" + "=" * 70)
print("4. REGRESIÓN LINEAL SIMPLE (amabilidad_personal)")
print("=" * 70)

X_s = sm.add_constant(df['amabilidad_personal'])
model_s = sm.OLS(y, X_s).fit()
print(f"Ecuación: {var_obj} = {model_s.params['const']:.4f} + {model_s.params['amabilidad_personal']:.4f} * amabilidad_personal")
print(f"R² = {model_s.rsquared:.4f}")
print(f"p-valor β1 = {model_s.pvalues['amabilidad_personal']:.6e}")
print(f"Decisión: {'Rechazar H0 (es predictora)' if model_s.pvalues['amabilidad_personal'] < 0.05 else 'No rechazar H0'}")

# ========== 5. REGRESIÓN MÚLTIPLE + DIAGNÓSTICOS ==========
print("\n" + "=" * 70)
print("5. REGRESIÓN MÚLTIPLE + DIAGNÓSTICOS")
print("=" * 70)

print(f"Ecuación: {var_obj} = {model.params['const']:.4f}", end="")
for v in vars_x:
    print(f" + {model.params[v]:.4f}*{v}", end="")
print()

print(f"\nR² = {model.rsquared:.4f}, R² adj = {model.rsquared_adj:.4f}")
print(f"RMSE = {np.sqrt(model.mse_resid):.4f}")
print(f"AIC = {model.aic:.2f}, BIC = {model.bic:.2f}")

# VIF
print("\nVIF:")
for i, v in enumerate(vars_x):
    vif = variance_inflation_factor(X.values, i + 1)
    print(f"  {v}: {vif:.3f}")

# Diagnósticos
resid = model.resid
sample_r = resid.sample(min(500, len(resid)), random_state=42)
sw_stat, sw_p = stats.shapiro(sample_r)
print(f"\nShapiro-Wilk: W={sw_stat:.4f}, p={sw_p:.6f}")

bp_stat, bp_p, _, _ = het_breuschpagan(resid, X)
print(f"Breusch-Pagan: LM={bp_stat:.4f}, p={bp_p:.6f}")

dw = durbin_watson(resid)
print(f"Durbin-Watson: {dw:.4f}")

# ========== 6. COMPARACIÓN DE MEDIAS POR ÁREA ==========
print("\n" + "=" * 70)
print("6. COMPARACIÓN DE MEDIAS POR ÁREA DE SERVICIO")
print("=" * 70)

for area in df['area_servicio'].unique():
    m = df[df['area_servicio'] == area][var_obj].mean()
    print(f"  {area}: media = {m:.4f}")

# T-test ejemplo: Farmacia vs Movilización
g1 = df[df['area_servicio'] == 'Farmacia'][var_obj]
g2 = df[df['area_servicio'] == 'Movilización'][var_obj]
t, p = stats.ttest_ind(g1, g2, equal_var=False)
print(f"\nT-test Farmacia vs Movilización: t={t:.4f}, p={p:.6e}")

print("\n" + "=" * 70)
print("Verificación completada. Usa estos valores para validar el Excel y el software.")
print("=" * 70)

