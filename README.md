# Manual de Uso — Decision Analyzer

**Objetivo:** Guiar paso a paso el uso del programa para analizar y elegir proveedores.

---

## ¿Qué es Decision Analyzer?

Aplicación de escritorio que ayuda a empresas a elegir entre múltiples proveedores o alternativas de negocio. El usuario proporciona sus datos en un archivo Excel y el sistema aplica dos métodos matemáticos complementarios para dar una recomendación clara:

- **AHP/WSM:** Evalúa qué tan buena es cada alternativa según criterios ponderados (Costos, Calidad, Entrega, etc.).
- **Monte Carlo:** Simula 10,000 escenarios posibles para medir el riesgo e incertidumbre de cada alternativa.

El resultado es una recomendación con tabla comparativa y alertas de riesgo, **sin necesidad de conocimientos matemáticos o de programación**.

---

## Preparación del archivo Excel (.xlsx)

El programa requiere un archivo `.xlsx` con **tres hojas** estructuradas de la siguiente manera:

### Hoja 1 — Alternativas

Lista de los proveedores o alternativas con sus valores mínimos y máximos por cada criterio.

| Alternativa | Costo_Min | Costo_Max | Entrega_Min | Entrega_Max | Calidad_Min | Calidad_Max |
|-------------|-----------|-----------|-------------|-------------|-------------|-------------|
| China       | 800       | 1200      | 15          | 45          | 6           | 8           |
| USA         | 1400      | 1600      | 3           | 7           | 8           | 10          |
| Mexico      | 1100      | 1300      | 5           | 15          | 7           | 9           |

- **Alternativa:** Nombre del proveedor o alternativa (texto libre).
- **Min/Max:** Rango real o estimado del valor para ese proveedor. El sistema simulará valores dentro de ese rango.

---

### Hoja 2 — Criterios

Define la importancia de cada criterio y si se busca minimizarlo o maximizarlo.

| Criterio | Importancia (1-10) | Tipo       |
|----------|--------------------|------------|
| Costo    | 9                  | minimizar  |
| Entrega  | 7                  | minimizar  |
| Calidad  | 8                  | maximizar  |

- **Importancia 1-10:** Qué tan relevante es este criterio para tu empresa. El sistema lo convierte en porcentaje automáticamente.
- **Minimizar:** Se prefiere el valor MÁS BAJO (costo, tiempo de entrega, riesgo).
- **Maximizar:** Se prefiere el valor MÁS ALTO (calidad, confiabilidad, experiencia).

---

### Hoja 3 — Configuración

| Parametro   | Valor                          |
|-------------|-------------------------------|
| Iteraciones | 10000                         |
| Nombre      | Selección de proveedor Q1 2025 |

> ⚠️ **Dato importante:** Los nombres de las hojas deben estar estrictamente bien escritos. Si existe un error de tipografía, el programa avisará exactamente qué corregir.

---

## Uso del Programa

### Pantalla Principal

Al abrir la aplicación verás la pantalla principal con las siguientes opciones:

1. **Cargar Excel** — Selecciona tu archivo `.xlsx` ya preparado.
2. **Ejecutar Análisis** — Inicia el procesamiento de los datos.

---

## Resultados

Una vez ejecutado el análisis, se mostrará el **Dashboard de Resultados** con la recomendación final.

### Caso A — Los modelos coinciden

Cuando AHP y Monte Carlo recomiendan el mismo proveedor:

> *"Con alta confianza, la mejor opción para [nombre decisión] es [ganador]. Esta alternativa es superior tanto en criterios (AHP) como en riesgo (Monte Carlo)."*

### Caso B — Los modelos NO coinciden

Cuando AHP y Monte Carlo recomiendan proveedores distintos:

> *"Existe una discrepancia entre los modelos para [nombre decisión]."*
> - AHP sugiere **USA** por mejores características técnicas.
> - Monte Carlo sugiere **México** por resultados más seguros y predecibles.
>
> **Consejo:** Si prioriza beneficio técnico, elija AHP. Si prefiere estabilidad, elija Monte Carlo.

---

## Ejemplo de Resultados

En el ejemplo ejecutado con `plantilla.xlsx`:

| Alternativa | Score Técnico (AHP) | Valor Esperado (MC) | Nivel de Riesgo | Prob. de Ganar |
|-------------|---------------------|---------------------|-----------------|----------------|
| USA         | 0.6250              | 0.5715              | BAJO            | 35.4%          |
| Mexico      | 0.6250              | 0.5977              | BAJO            | 56.7%          |
| China       | 0.3750              | 0.4698              | MEDIO           | 7.9%           |

---

## Alertas y Riesgos

El sistema genera alertas automáticas en los siguientes casos:

- **Riesgo alto:** La desviación estándar de los scores es `>= 0.15`. Significa que los resultados reales podrían variar mucho.
- **Prob. de ganar < 60%:** La alternativa ganó menos del 60% de los 10,000 escenarios simulados. No es una apuesta segura.

> En el ejemplo, las tres alternativas recibieron alerta de prob. < 60% porque ninguna dominó claramente. Esto indica que la decisión es competida.

Si no hay riesgos críticos, el sistema mostrará:

>  *No se detectaron riesgos críticos ni variabilidad excesiva.*
