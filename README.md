# Proyecto Final - Estadística para la Inteligencia de Negocios

**Instituto Tecnológico de Tizimín**  
**Tecnológico Nacional de México**

## Título del Proyecto
**Sistema web para gestión y análisis de satisfacción de clientes en tres áreas de atención**  
(Farmacia · Movilización · Planta de alimentos)

## Objetivo
Desarrollar un análisis estadístico completo sobre datos de satisfacción del cliente que permita tomar decisiones de negocio basadas en evidencia, alineado con el sistema web de residencia profesional.

---

## Contenido del Entregable (.zip)

| Archivo | Descripción |
|---------|-------------|
| `satisfaccion_clientes.csv` / `.xlsx` | Dataset simulado realista (2,200 registros) |
| `formulas_verificacion_estadistica.xlsx` | Excel con fórmulas de Excel (AVERAGE, STDEV.S, SKEW, etc.) para comprobar resultados. 4 pestañas: Descriptiva, Inferencial, Hipótesis, Regresión |
| `analizador_estadistico_satisfaccion.py` | Aplicación Streamlit (Python) completa: descriptiva, inferencial, hipótesis, regresión + diagnósticos |
| `verificacion_estadistica.py` | Script Python de comprobación que imprime todos los resultados clave |
| `README.md` | Este archivo |
| `INSTRUCCIONES_POWERBI.md` | Guía para construir el dashboard .pbix de toma de decisiones |
| `Reporte_Estadistico_Satisfaccion.pdf` | Reporte formal del proyecto (máx. 20 páginas) |

---

## Requisitos del Dataset (cumplidos)

- ✅ ≥ 500 registros → **2,200**
- ✅ ≥ 8 variables numéricas → **10**
- ✅ ≥ 2 variables categóricas → **4** (área, género, tipo_cliente, turno)
- ✅ Variable objetivo clara → **satisfaccion_general**

### Variables

**Categóricas:**
- `area_servicio`: Farmacia | Movilización | Planta de alimentos
- `genero`: Masculino | Femenino | Otro
- `tipo_cliente`: Nuevo | Frecuente
- `turno`: Mañana | Tarde | Noche

**Numéricas (escala 1-10 salvo edad y minutos):**
1. `satisfaccion_general` ← **Variable objetivo**
2. `amabilidad_personal`
3. `tiempo_espera` (calificación)
4. `calidad_servicio`
5. `limpieza_instalaciones`
6. `claridad_informacion`
7. `resolucion_problema`
8. `probabilidad_recomendar` (NPS)
9. `edad_cliente`
10. `tiempo_atencion_minutos`

---

## Cómo ejecutar el analizador Streamlit

```bash
pip install streamlit pandas numpy scipy statsmodels plotly openpyxl
streamlit run analizador_estadistico_satisfaccion.py
```

Coloca `satisfaccion_clientes.csv` en la misma carpeta (o súbelo desde la interfaz).

---

## Cómo verificar con el script Python

```bash
python verificacion_estadistica.py
```

Compara los valores impresos con los del Excel y del software.

---

## Estructura del análisis realizado

### Parte 1 – Descriptiva
- Medidas de tendencia central y dispersión (media, mediana, moda, desv. estándar, varianza, rango, IQR, cuartiles)
- Asimetría y curtosis
- Tablas de frecuencia categóricas
- Histogramas, boxplots, dispersión, matriz de correlación

### Parte 2 – Inferencial
- Intervalos de confianza 90%, 95%, 99% para la media de la variable objetivo y 2 variables clave
- Prueba T de una muestra
- Prueba T de dos muestras independientes (Welch) por área de servicio

### Parte 3 – Hipótesis
- **H1**: Correlación Pearson entre variable determinante (amabilidad) y satisfacción general
- **H2**: Influencia de múltiples variables independientes (t-tests de coeficientes en regresión múltiple)

### Parte 4 – Regresión
- Regresión lineal simple
- Regresión lineal múltiple
- Diagnósticos: VIF, Shapiro-Wilk, Breusch-Pagan, Durbin-Watson
- Gráficos de residuos, QQ-plot, Cook’s distance
- Comparación de modelos (R², R² adj, RMSE, AIC, BIC)

### Parte 5 – Power BI
- Página “TOMA DE DECISIONES” con controles de escenario, predicción en tiempo real, comparador y recomendaciones dinámicas (ver `INSTRUCCIONES_POWERBI.md`)

### Parte 6 – Reporte PDF
- Portada, resumen ejecutivo, análisis por secciones, recomendaciones y conclusiones

---

## Principales hallazgos (resumen)

| Hallazgo | Resultado |
|----------|-----------|
| Media satisfacción general | ≈ 7.14 / 10 |
| Área con mayor satisfacción | Planta de alimentos (≈ 7.60) |
| Área con menor satisfacción | Movilización (≈ 6.73) |
| Correlación amabilidad ↔ satisfacción | r ≈ 0.49 (significativa) |
| Modelo múltiple R² | ≈ 0.44 |
| Variable de mayor impacto | `resolucion_problema` (β ≈ 0.19) |
| Multicolinealidad | No problemática (todos VIF < 5) |
| Residuos | Normales, homocedásticos, sin autocorrelación |

---

## Autor
Proyecto de Residencia Profesional + Proyecto Final de Estadística  
Instituto Tecnológico de Tizimín
