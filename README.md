# SmartDecide: Toma de Decisiones con Simulacion y AHP
SmartDecide es una plataforma analitica desenada para mitigar el riesgo en la toma de decisiones complejas. Una herrameinta avanzada deisenada para ayudar a empresas y tomadoras de decisiones a elegir la mejor opcion
(proveedores, rutas, proyectos) mediante kla combiancion de dos metodologias potentes: el **Proceso de Jeraraquia Analitica (AHP)** y la **Simulacion de Monte Carlo**.

## Que problema resuelve? 

Basado en el caso de una manufacturera en México, el sistema resuelve la incertidumbre al elegir proveedores con variables volátiles:
* **Costos variables:** Diferencias entre precios mínimos y máximos por lote.
* **Tiempos de entrega:** Rangos que contemplan desde el mejor escenario hasta retrasos logísticos (ej. China vs USA vs México).
* **Calidad y Riesgo:** Evaluación técnica frente a la estabilidad operativa.


## Las Metodologias

El sistema no utiliza valores estaticos,si no que analiza el comportamiento de los datos mediante:

**AHP / WSM (Weighted Sum Model):** Evalua criterios tecnicos(Costo, Calidad, Tiempo) asignandolos pasos segun la importancia definida por el usuario. 
Implementado en `ahp_wsm.py`, el sistema normaliza los datos (escala 0-1) y aplica pesos de importancia (1-10) para dar un puntaje técnico a cada alternativa. 
* *Fórmula de minimización (Costos/Tiempo):* `(max - x) / (max - min)`
* *Fórmula de maximización (Calidad):* `(x - min) / (max - min)`

**Simulacion de Monte Carlo:** Ejecuta 10,000 iteraciones automaticas utilizando rangos(minimo y maximo) para calcular la probabilidad de exito de cada alternativa.


## Estructura 

`app.py`: Interfaz visual (Streamlit).
`ahp_wsm.py`: Lógica del modelo de pesos y criterios.
`montecarlo.py`: Motor de simulaciones probabilísticas.
`recomendacion.py`: Generador de informes y tablas comparativas.
`excel_reader.py`: Módulo para la lectura y validación de datos desde Excel.
`crear_plantilla.py`: Script de utilidad para generar archivos Excel compatibles.

## Dependencias

Este proyecto esta desarrollado integramnete en Python debido a su robustez en el manejo de datos cientificos. 
Las librerias principales utilizadas:

**Pandas** : Para la manipulacion de estructuras de dtaos y la lectura eficiente de archivps Excel.

**NumPy** : Esel motor de calculo para la Simualcon de Monte Carlo, permitiedno generar 10,000 escenarios aleatorios en milisegundos.

**Streamlit** : Utilizando para cxrear lainterfa web interactiva. Peermite convertir scripts de datos en aplicaciones compartibles.

**Ploty** : Para la visualizacion de datos dinamica (graficas de radar y curvas de campana), permitiendo al usuario interactuar con los resultados. 

**OpenPyXL** : Motor necesario para que Pandas pueda escribir y leer archvivos.

## Flujo de Usuario

Carga de Dtaos: El usuario sube el archivo Excel validado por `excel_reader.py`.
Procesameinto: El sistema activa los modelos matematicos al hacer clic en "Analizar".
Visualizacion:
  - Banner Ganadora : Identifica la opcion optima inmedianta.
  - Grafica de Radar: Comparativa visual de fortalezas por criterio.
  - Curva de Campana(Monte Carlo): Muestra la probabilidad de exito y la dispersion del riesgo.
  - Recomendacin Inteligente: Texto narrativo que explica si la opcion es "Solida" o "Riesgosa". 

# Manual de Uso 
## Objetivo

Este sistema permite evaluar alternativas bajo multiples criterios considerando tanto desempeno tecnico como riesgo e incertidumbre. 

## El sistema

Nuestro sistema sigue 5 etapas:
1- Validacion del archivo Excel
2- Normalizacion de criterios(AHP)
3- Ranking tecnico(WSM)
4- Simulacion Monte Carlo
5-Generacion automatica de recomendacion 

