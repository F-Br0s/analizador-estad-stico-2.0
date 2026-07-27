# Instrucciones para el Dashboard Power BI – Toma de Decisiones

## Objetivo de la página “TOMA DE DECISIONES”

Permitir que el usuario (gerente / administrador del sistema de satisfacción) manipule variables controlables y vea en tiempo real el impacto sobre la **satisfacción general** predicha, con recomendaciones accionables.

---

## 1. Preparación de datos

1. Abre Power BI Desktop.
2. **Obtener datos** → Excel o CSV → selecciona `satisfaccion_clientes.xlsx` / `.csv`.
3. En Power Query:
   - Asegúrate de que las columnas numéricas sean tipo *Número decimal* o *Entero*.
   - Las categóricas como *Texto*.
   - Crea una columna calculada opcional de mes/año a partir de `fecha` si deseas filtros temporales.
4. Cierra y aplica.

---

## 2. Modelo de predicción (DAX)

Crea una **tabla de parámetros** (What-if parameters) o una tabla auxiliar con sliders:

### Parámetros What-if (Modelado → Nuevo parámetro):

| Nombre del parámetro | Mín | Máx | Incremento | Valor por defecto |
|----------------------|-----|-----|------------|-------------------|
| Amabilidad (param)   | 1   | 10  | 1          | 7                 |
| Tiempo espera (param)| 1   | 10  | 1          | 7                 |
| Calidad (param)      | 1   | 10  | 1          | 7                 |
| Limpieza (param)     | 1   | 10  | 1          | 7                 |
| Claridad (param)     | 1   | 10  | 1          | 7                 |
| Resolución (param)   | 1   | 10  | 1          | 7                 |

### Medida DAX de predicción (usando los coeficientes del modelo múltiple):

```dax
Satisfaccion Predicha = 
0.9235 
+ 0.1424 * [Amabilidad (param) Valor]
+ 0.1248 * [Tiempo espera (param) Valor]
+ 0.1388 * [Calidad (param) Valor]
+ 0.1428 * [Limpieza (param) Valor]
+ 0.1344 * [Claridad (param) Valor]
+ 0.1891 * [Resolución (param) Valor]
```

*(Los coeficientes salen del script `verificacion_estadistica.py` / Excel pestaña 4. Si regeneras el modelo, actualiza los números.)*

### Medida de impacto vs escenario base (todo en 7):

```dax
Impacto vs Base = 
[Satisfaccion Predicha] - (0.9235 + 0.1424*7 + 0.1248*7 + 0.1388*7 + 0.1428*7 + 0.1344*7 + 0.1891*7)
```

---

## 3. Elementos de la página “TOMA DE DECISIONES”

### Elemento 1 – Controles de escenario
- Coloca los **6 slicers/sliders** de los parámetros What-if en la parte izquierda o superior.
- Título: “Variables que puedes controlar”

### Elemento 2 – Predicción en tiempo real
- Tarjeta grande (Card) con la medida `[Satisfaccion Predicha]`
- Formato: 1 decimal, color condicional (rojo < 6.5, amarillo 6.5-7.5, verde > 7.5)
- Título: “Satisfacción General Predicha”

### Elemento 3 – Comparador de escenarios
- Crea 2 sets de parámetros (Escenario A y Escenario B) o usa bookmarks.
- Tabla o tarjetas lado a lado mostrando predicción A vs B y la diferencia.

### Elemento 4 – Tabla de recomendaciones dinámicas

Crea una medida o usa lógica condicional en una tabla:

```dax
Recomendacion 1 = 
VAR pred = [Satisfaccion Predicha]
RETURN
IF(pred < 6.5, 
   "URGENTE: Capacitación intensiva en resolución de problemas y amabilidad (especialmente Movilización)",
IF(pred < 7.5,
   "Mejorar procesos de resolución de problemas y reducir tiempos de espera percibidos",
   "Mantener estándares actuales y monitorear indicadores mensualmente"))
```

Muestra 3 recomendaciones con:
- Impacto estimado (usa el coeficiente × cambio posible)
- Acción concreta

### Elemento 5 – Análisis de sensibilidad
- Gráfico de barras o línea que muestre el cambio en la predicción al variar cada variable ±1 punto (manteniendo las demás fijas).
- Se puede hacer con una tabla auxiliar de sensibilidad o con DAX + campo calculado.

### Elemento 6 – Tablero de control de decisiones

| Decisión                    | Estado Actual | Impacto estimado | Recomendación          |
|-----------------------------|---------------|------------------|------------------------|
| Mejorar amabilidad          | Slider        | +0.14 por punto  | Capacitación soft skills |
| Mejorar resolución problemas| Slider        | +0.19 por punto  | Protocolos de seguimiento |
| ...                         | ...           | ...              | ...                    |

---

## 4. Páginas adicionales sugeridas

1. **Resumen Ejecutivo** – KPIs principales (media satisfacción por área, NPS, n de encuestas)
2. **Descriptiva** – Histogramas, boxplots por área, tablas de frecuencia
3. **Inferencial** – Intervalos de confianza visualizados
4. **Correlaciones** – Matriz de calor
5. **TOMA DE DECISIONES** – La página principal descrita arriba

---

## 5. Script de actualización (opcional)

Si el sistema web genera el Excel diariamente, en Power BI:

- Configura **Actualización programada** (si usas Power BI Service)
- O usa **Power Automate** / script Python + `pbix` refresh

---

## 6. Entrega del .pbix

1. Guarda el archivo como `Dashboard_Satisfaccion_Clientes.pbix`
2. Incluye en el .zip junto con el resto de entregables
3. En el reporte PDF menciona: “El archivo .pbix permite al usuario manipular las variables controlables y obtener predicciones y recomendaciones en tiempo real según el modelo de regresión múltiple ajustado.”

---

## Coeficientes de referencia (modelo actual)

```
satisfaccion_general ≈ 0.9235 
    + 0.1424·amabilidad_personal 
    + 0.1248·tiempo_espera 
    + 0.1388·calidad_servicio 
    + 0.1428·limpieza_instalaciones 
    + 0.1344·claridad_informacion 
    + 0.1891·resolucion_problema
```

R² ≈ 0.44 | Todos los coeficientes significativos (p < 0.001)
