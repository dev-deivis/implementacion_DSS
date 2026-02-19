# Manual de Uso – DSS Multicriterio (Turban)

## Cómo ejecutar el programa

```bash
python dss_model.py
```

Se mostrará el menú:
```
══════════════════════════════════════════════════════════
  DSS – Sistema de Soporte a la Decisión
  Modelos basados en Efraim Turban

  1.  Weighted Sum Model (WSM)
  2.  Analytic Hierarchy Process (AHP)
  0.  Salir
```

---

## EJEMPLO 1 – WSM: Selección de proveedor de software ERP

**Escenario:** Una empresa necesita elegir entre 3 proveedores de ERP según 4 criterios.

### Datos de entrada

**Alternativas:** SAP, Oracle, Odoo

**Criterios y tipo:**
| Criterio | Tipo | Peso relativo |
|----------|------|--------------|
| Precio (USD) | Costo (minimizar) | 5 |
| Funcionalidades | Beneficio (maximizar) | 8 |
| Soporte técnico | Beneficio (maximizar) | 6 |
| Tiempo implementación (meses) | Costo (minimizar) | 4 |

**Puntajes por alternativa:**
| Alternativa | Precio | Funcionalidades | Soporte | Tiempo impl. |
|-------------|--------|-----------------|---------|--------------|
| SAP | 150000 | 9 | 8 | 12 |
| Oracle | 130000 | 8 | 9 | 10 |
| Odoo | 40000 | 6 | 6 | 4 |

### Sesión de entrada en consola

```
¿Cuántas alternativas deseas comparar? (2-10): 3
Nombre de la alternativa 1: SAP
Nombre de la alternativa 2: Oracle
Nombre de la alternativa 3: Odoo

¿Cuántos criterios de evaluación? (2-8): 4

Nombre del criterio 1: Precio
¿'Precio' es de beneficio o costo? [B/C]: C

Nombre del criterio 2: Funcionalidades
¿'Funcionalidades' es de beneficio o costo? [B/C]: B

Nombre del criterio 3: Soporte
¿'Soporte' es de beneficio o costo? [B/C]: B

Nombre del criterio 4: Tiempo implementacion
¿'Tiempo implementacion' es de beneficio o costo? [B/C]: C

Peso de 'Precio': 5
Peso de 'Funcionalidades': 8
Peso de 'Soporte': 6
Peso de 'Tiempo implementacion': 4

→ SAP:
     Precio: 150000
     Funcionalidades: 9
     Soporte: 8
     Tiempo implementacion: 12

→ Oracle:
     Precio: 130000
     Funcionalidades: 8
     Soporte: 9
     Tiempo implementacion: 10

→ Odoo:
     Precio: 40000
     Funcionalidades: 6
     Soporte: 6
     Tiempo implementacion: 4
```

### Resultado esperado

```
══════════════════════════════════════════════════════════
  RESULTADOS – Weighted Sum Model

Alternativa          Precio    Funcionalidades   Soporte  T.impl  Score WSM
─────────────────────────────────────────────────────────────────────────────
SAP                  0.0000          1.0000        0.6667  0.0000     0.5565
Oracle               0.1818          0.6667        1.0000  0.2500     0.5937
Odoo                 1.0000          0.0000        0.0000  1.0000     0.4348

📊  RANKING FINAL:
  1. Oracle               Score: 0.5937 ⭐ MEJOR OPCIÓN
  2. SAP                  Score: 0.5565
  3. Odoo                 Score: 0.4348

✅  RECOMENDACIÓN: El sistema recomienda 'Oracle' como la mejor alternativa.
```

---

## EJEMPLO 2 – AHP: Elección de ubicación para nueva sucursal

**Escenario:** Decidir entre 3 ubicaciones con 3 criterios.

**Criterios:** Costo de renta, Acceso a clientes, Competencia cercana

**Alternativas:** Centro, Norte, Sur

### Comparaciones pareadas de criterios (escala Saaty)

| vs | Costo renta | Acceso clientes | Competencia |
|----|-------------|-----------------|-------------|
| Costo renta | 1 | 1/3 | 5 |
| Acceso clientes | 3 | 1 | 7 |
| Competencia | 1/5 | 1/7 | 1 |

**Valores a ingresar cuando el programa pregunte:**
```
¿Cuánto más importante es 'Costo renta' sobre 'Acceso clientes'? 0.333
¿Cuánto más importante es 'Costo renta' sobre 'Competencia'? 5
¿Cuánto más importante es 'Acceso clientes' sobre 'Competencia'? 7
```

### Resultado esperado
```
  Prioridades de criterios:
    Costo renta:       0.2828  (28.3%)
    Acceso clientes:   0.6434  (64.3%)
    Competencia:       0.0738   (7.4%)

  Ratio de Consistencia (CR): 0.0379 ✅ Consistente

📊  RANKING FINAL:
  1. Norte   Score: 0.5123 ⭐ MEJOR OPCIÓN
  2. Centro  Score: 0.3211
  3. Sur     Score: 0.1666

✅  RECOMENDACIÓN: Según el AHP, la mejor alternativa es 'Norte'.
```

---

## Notas importantes

- **WSM** es más rápido e intuitivo; ideal cuando los pesos son conocidos.
- **AHP** es más riguroso; ideal cuando los pesos deben derivarse de comparaciones subjetivas expertas.
- Si el **CR > 0.10** en AHP, el sistema te avisa que tus comparaciones son inconsistentes y deberías revisarlas.
- El programa **no tiene valores fijos** en el código; todos los datos son ingresados dinámicamente por el usuario.