# DSS – Sistema de Soporte a la Decisión Multicriterio
**Basado en: Efraim Turban – *Decision Support Systems and Intelligent Systems***

---

## Descripción
Este proyecto implementa dos modelos matemáticos de toma de decisiones multicriterio (MCDM) descritos por Turban en su capítulo de modelos cuantitativos para DSS:

| Modelo | Técnica | Sección Turban | Páginas |
|--------|---------|----------------|---------|
| **WSM** | Weighted Sum Model (Suma Ponderada) | Sección 4.7 Decision Tables / 4.10 Multiple Goals | pp. 161–163, 173 |
| **AHP** | Analytic Hierarchy Process (Saaty) | Sección 4.7 Multicriteria Decision Analysis | p. 163 |

Ambos modelos permiten a un directivo o usuario **comparar alternativas** (proveedores, proyectos, inversiones, etc.) tomando en cuenta **múltiples criterios** con distintos niveles de importancia, y obtener una **recomendación clara y justificada**.

---

## Requisitos
- **Python 3.7+** (sin librerías externas, solo módulos estándar)

Verificar versión instalada:
```bash
python --version
```

---

## Ejecución
```bash
# Clonar o descargar el repositorio
git clone https://github.com/TU_USUARIO/dss-turban.git
cd dss-turban

# Ejecutar el sistema
python dss_model.py
```

Al iniciar, verás el menú principal con las dos opciones de modelo.

---

## Estructura del proyecto
```
dss-turban/
│
├── dss_model.py          # Código fuente principal (WSM + AHP)
├── README.md             # Este archivo
├── manual_de_uso.md      # Manual con ejemplos detallados
└── logica_del_modelo.pdf # Documento de lógica matemática
```

---

## Modelos implementados

### 1. Weighted Sum Model (WSM)
**Fórmula:**
```
Score(Aᵢ) = Σ [ wⱼ × rᵢⱼ ]
```
Donde:
- `wⱼ` = peso normalizado del criterio j
- `rᵢⱼ` = puntaje normalizado de la alternativa i en el criterio j

**Normalización min-max:**
- Criterio de beneficio: `rᵢⱼ = (xᵢⱼ - min) / (max - min)`
- Criterio de costo: `rᵢⱼ = (max - xᵢⱼ) / (max - min)`

### 2. Analytic Hierarchy Process (AHP)
Basado en el método de Thomas Saaty (1980), integrado en DSS por Turban.
- Construye matrices de comparación pareada
- Calcula vectores de prioridad por promedio de columnas normalizadas
- Verifica consistencia mediante el **Ratio de Consistencia (CR ≤ 0.10)**
- Combina prioridades locales para obtener el score global

---

## Autores
- [Nombre del integrante 1] – commits: modelo WSM
- [Nombre del integrante 2] – commits: modelo AHP
- [Nombre del integrante 3] – commits: documentación y pruebas

---

## Referencia bibliográfica
> Turban, E., Aronson, J. E., & Liang, T. P. (2005). *Decision Support Systems and Intelligent Systems* (7th ed.). Pearson Prentice Hall.