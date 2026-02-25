import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import copy
import pandas as pd

from excel_reader import leer_alternativas, leer_criterios, leer_configuracion, validar_excel
from ahp_wsm import rankear_alternativas, normalizar_pesos
from montecarlo import simular_todas
from recomendacion import generar_recomendacion, generar_razones, generar_advertencias, generar_tabla_resumen

# --- CONFIGURACIÓN ESTÉTICA PLANA ---
BG_COLOR      = "#ffffff"
SURFACE_COLOR = "#f8f9fa"
BORDER_COLOR  = "#dee2e6"
TEXT_PRIMARY  = "#212529"
TEXT_MUTED    = "#6c757d"
ACCENT_COLOR  = "#0d6efd"
SUCCESS_COLOR = "#198754"
DANGER_COLOR  = "#dc3545"
WARN_COLOR    = "#fd7e14"

FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI Bold", 10)
FONT_TITLE  = ("Segoe UI Semibold", 16)
FONT_SMALL  = ("Segoe UI", 9)


# ─────────────────────────────────────────────────────────
#  HELPERS GLOBALES
# ─────────────────────────────────────────────────────────

class AutoScrollbar(ttk.Scrollbar):
    """Scrollbar que solo aparece cuando el contenido no cabe."""
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            info = self.pack_info() if self.winfo_ismapped() else {}
            if not info:
                # Re-pack in the same side it was configured
                self.pack(**self._pack_kwargs)
        super().set(lo, hi)

    def configure_pack(self, **kwargs):
        """Save pack kwargs so we can restore them on demand."""
        self._pack_kwargs = kwargs
        self.pack(**kwargs)


def col_width(header: str, rows: list, key: str, char_px: int = 9, pad: int = 20) -> int:
    """Calculate column width based on header + longest cell value."""
    max_len = len(str(header))
    for row in rows:
        val = str(row.get(key, ""))
        if len(val) > max_len:
            max_len = len(val)
    return max(100, max_len * char_px + pad)


# ─────────────────────────────────────────────────────────
#  DIÁLOGOS AUXILIARES
# ─────────────────────────────────────────────────────────

class DialogCriterio(tk.Toplevel):
    """Popup para agregar o editar un criterio."""

    def __init__(self, parent, datos_existentes=None):
        super().__init__(parent)
        self.title("Criterio")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.grab_set()           # modal
        self.resultado = None

        datos = datos_existentes or {}

        tk.Label(self, text="Nombre del criterio:", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.ent_nombre = tk.Entry(self, font=FONT_MAIN, width=24)
        self.ent_nombre.insert(0, datos.get("Criterio", ""))
        self.ent_nombre.grid(row=0, column=1, padx=15, pady=(15, 5))

        tk.Label(self, text="Importancia (1-10):", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.ent_imp = tk.Entry(self, font=FONT_MAIN, width=24)
        self.ent_imp.insert(0, str(datos.get("Importancia (1-10)", "")))
        self.ent_imp.grid(row=1, column=1, padx=15, pady=5)

        tk.Label(self, text="Tipo:", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.tipo_var = tk.StringVar(value=datos.get("Tipo", "minimizar"))
        frame_radio = tk.Frame(self, bg=BG_COLOR)
        frame_radio.grid(row=2, column=1, padx=15, pady=5, sticky="w")
        tk.Radiobutton(frame_radio, text="minimizar", variable=self.tipo_var,
                       value="minimizar", bg=BG_COLOR, font=FONT_MAIN).pack(side="left")
        tk.Radiobutton(frame_radio, text="maximizar", variable=self.tipo_var,
                       value="maximizar", bg=BG_COLOR, font=FONT_MAIN).pack(side="left", padx=10)

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        tk.Button(btn_frame, text="Guardar", command=self._guardar,
                  bg=ACCENT_COLOR, fg="white", font=FONT_BOLD,
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                  bg=SURFACE_COLOR, fg=TEXT_PRIMARY, font=FONT_MAIN,
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="left")

        self.ent_nombre.focus()

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        imp_str = self.ent_imp.get().strip()
        tipo    = self.tipo_var.get()

        if not nombre:
            messagebox.showwarning("Validación", "El nombre no puede estar vacío.", parent=self)
            return
        try:
            imp = float(imp_str)
            if not (1 <= imp <= 10):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "La importancia debe ser un número entre 1 y 10.", parent=self)
            return

        self.resultado = {"Criterio": nombre, "Importancia (1-10)": imp, "Tipo": tipo}
        self.destroy()


class DialogAlternativa(tk.Toplevel):
    """Popup para agregar o editar una alternativa (campos dinámicos según criterios)."""

    def __init__(self, parent, criterios, datos_existentes=None):
        super().__init__(parent)
        self.title("Alternativa")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        self.criterios = criterios

        datos = datos_existentes or {}
        row_idx = 0

        tk.Label(self, text="Nombre de la alternativa:", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=row_idx, column=0, padx=15,
                                                     pady=(15, 5), sticky="w")
        self.ent_nombre = tk.Entry(self, font=FONT_MAIN, width=22)
        self.ent_nombre.insert(0, datos.get("Alternativa", ""))
        self.ent_nombre.grid(row=row_idx, column=1, columnspan=2, padx=15, pady=(15, 5))
        row_idx += 1

        # Cabeceras de rango
        tk.Label(self, text="Mínimo", font=FONT_BOLD, bg=BG_COLOR,
                 fg=TEXT_MUTED).grid(row=row_idx, column=1, pady=(8, 2))
        tk.Label(self, text="Máximo", font=FONT_BOLD, bg=BG_COLOR,
                 fg=TEXT_MUTED).grid(row=row_idx, column=2, pady=(8, 2))
        row_idx += 1

        self.entries = {}  # {criterio: (entry_min, entry_max)}

        for crit in criterios:
            nombre_c = crit["Criterio"]
            col_min = f"{nombre_c}_Min"
            col_max = f"{nombre_c}_Max"

            tk.Label(self, text=f"{nombre_c}:", font=FONT_MAIN,
                     bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=row_idx, column=0,
                                                         padx=15, pady=4, sticky="w")
            ent_min = tk.Entry(self, font=FONT_MAIN, width=10)
            ent_min.insert(0, str(datos.get(col_min, "")))
            ent_min.grid(row=row_idx, column=1, padx=8, pady=4)

            ent_max = tk.Entry(self, font=FONT_MAIN, width=10)
            ent_max.insert(0, str(datos.get(col_max, "")))
            ent_max.grid(row=row_idx, column=2, padx=8, pady=4)

            self.entries[nombre_c] = (ent_min, ent_max)
            row_idx += 1

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.grid(row=row_idx, column=0, columnspan=3, pady=15)
        tk.Button(btn_frame, text="Guardar", command=self._guardar,
                  bg=ACCENT_COLOR, fg="white", font=FONT_BOLD,
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                  bg=SURFACE_COLOR, fg=TEXT_PRIMARY, font=FONT_MAIN,
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="left")

        self.ent_nombre.focus()

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre no puede estar vacío.", parent=self)
            return

        fila = {"Alternativa": nombre}
        for nombre_c, (ent_min, ent_max) in self.entries.items():
            try:
                v_min = float(ent_min.get())
                v_max = float(ent_max.get())
            except ValueError:
                messagebox.showwarning(
                    "Validación",
                    f"Los valores de '{nombre_c}' deben ser números.",
                    parent=self
                )
                return
            if v_max < v_min:
                messagebox.showwarning(
                    "Validación",
                    f"En '{nombre_c}', el máximo debe ser ≥ al mínimo.",
                    parent=self
                )
                return
            fila[f"{nombre_c}_Min"] = v_min
            fila[f"{nombre_c}_Max"] = v_max

        self.resultado = fila
        self.destroy()


# ─────────────────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Decision Analyzer — Professional Edition")
        self.geometry("1150x780")
        self.configure(bg=BG_COLOR)

        self.archivo_path = None

        # Estado en memoria (editor + análisis)
        self.datos_alternativas: list[dict] = []
        self.datos_criterios:    list[dict] = []
        self.datos_config:       dict       = {"Iteraciones": 10000, "Nombre Decision": "Decisión"}

        self._build_ui()

    # ── UI PRINCIPAL ──────────────────────────────────────

    def _build_ui(self):
        # HEADER
        header = tk.Frame(self, bg=BG_COLOR, pady=18, padx=30)
        header.pack(fill="x")
        tk.Label(header, text="Analizador de Decisiones", font=FONT_TITLE,
                 fg=TEXT_PRIMARY, bg=BG_COLOR).pack(side="left")

        # TOOLBAR
        toolbar = tk.Frame(self, bg=SURFACE_COLOR, pady=10, padx=30,
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        toolbar.pack(fill="x")

        self._btn(toolbar, "Cargar Excel", self._cargar_archivo).pack(side="left", padx=5)
        self.lbl_archivo = tk.Label(toolbar, text="No se ha seleccionado archivo",
                                    font=FONT_MAIN, fg=TEXT_MUTED, bg=SURFACE_COLOR)
        self.lbl_archivo.pack(side="left", padx=15)

        self._btn(toolbar, "▶ Ejecutar Análisis", self._ejecutar, primary=True).pack(side="right", padx=5)

        # NOTEBOOK
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background=BG_COLOR,      borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE_COLOR, padding=[18, 7], font=FONT_MAIN)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_COLOR)],
                  foreground=[("selected", ACCENT_COLOR)])

        # Treeview styling
        style.configure("Custom.Treeview",
                         background=BG_COLOR, fieldbackground=BG_COLOR,
                         rowheight=26, font=FONT_MAIN, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                         background=SURFACE_COLOR, font=FONT_BOLD,
                         relief="flat", borderwidth=0)
        style.map("Custom.Treeview", background=[("selected", "#cfe2ff")])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=15)

        # --- TAB 1: Dashboard ---
        self.tab_dashboard = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_dashboard, text="  Dashboard  ")
        self.lbl_espera = tk.Label(
            self.tab_dashboard,
            text="Cargue un archivo (o use el Editor) y presione '▶ Ejecutar' para ver resultados.",
            font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_COLOR, pady=120
        )
        self.lbl_espera.pack()

        # --- TAB 2: Vista Previa ---
        self.tab_preview = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_preview, text="  Vista Previa  ")
        self._build_preview_tab()

        # --- TAB 3: Editor ---
        self.tab_editor = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_editor, text="  Editor de Datos  ")
        self._build_editor_tab()

        # STATUS BAR
        self.status_var = tk.StringVar(value="Listo  •  Sin datos cargados")
        tk.Label(self, textvariable=self.status_var,
                 bg=SURFACE_COLOR, fg=TEXT_MUTED, anchor="w",
                 padx=12, pady=5,
                 highlightbackground=BORDER_COLOR, highlightthickness=1
                 ).pack(fill="x", side="bottom")

    # ── TAB: VISTA PREVIA ─────────────────────────────────

    def _build_preview_tab(self):
        """Crea la estructura vacía de la pestaña de vista previa."""
        self.preview_container = tk.Frame(self.tab_preview, bg=BG_COLOR)
        self.preview_container.pack(fill="both", expand=True, padx=20, pady=15)

        self.lbl_preview_vacio = tk.Label(
            self.preview_container,
            text="Cargue un archivo Excel o agregue datos en el Editor para ver la vista previa.",
            font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_COLOR, pady=100
        )
        self.lbl_preview_vacio.pack()

    def _actualizar_preview(self):
        """Refresca los datos mostrados en Vista Previa."""
        for w in self.preview_container.winfo_children():
            w.destroy()

        if not self.datos_criterios and not self.datos_alternativas:
            tk.Label(self.preview_container,
                     text="Sin datos para mostrar.",
                     font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_COLOR, pady=80).pack()
            return

        canvas = tk.Canvas(self.preview_container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.preview_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_configure(e):
            canvas.itemconfig(win_id, width=e.width)
        scroll_frame.bind("<Configure>", _on_frame_configure)
        win_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sección Criterios
        if self.datos_criterios:
            self._preview_seccion(scroll_frame, "Criterios", self.datos_criterios)

        # Sección Alternativas
        if self.datos_alternativas:
            self._preview_seccion(scroll_frame, "Alternativas", self.datos_alternativas)

        # Sección Configuración
        if self.datos_config:
            config_lista = [{"Parámetro": k, "Valor": v} for k, v in self.datos_config.items()]
            self._preview_seccion(scroll_frame, "Configuración", config_lista)

    def _preview_seccion(self, parent, titulo, datos: list[dict]):
        """Dibuja un bloque con título + treeview de sólo lectura."""
        tk.Label(parent, text=titulo, font=FONT_BOLD, bg=BG_COLOR,
                 fg=ACCENT_COLOR, pady=6).pack(anchor="w", pady=(12, 0))

        sep = tk.Frame(parent, bg=ACCENT_COLOR, height=2)
        sep.pack(fill="x", pady=(0, 8))

        cols = list(datos[0].keys()) if datos else []

        tree_wrap = tk.Frame(parent, bg=BG_COLOR)
        tree_wrap.pack(fill="x", pady=(0, 5))

        scr_x = AutoScrollbar(tree_wrap, orient="horizontal")
        scr_x.configure_pack(side="bottom", fill="x")

        tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                             height=min(len(datos), 8), style="Custom.Treeview",
                             xscrollcommand=scr_x.set)
        scr_x.config(command=tree.xview)

        for c in cols:
            w = col_width(c, datos, c, char_px=9, pad=24)
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=w, minwidth=w, stretch=False)

        for row in datos:
            tree.insert("", "end", values=[str(row.get(c, "")) for c in cols])

        tree.pack(fill="x")

        # línea divisora
        tk.Frame(parent, bg=BORDER_COLOR, height=1).pack(fill="x", pady=4)

    # ── TAB: EDITOR DE DATOS ──────────────────────────────

    def _build_editor_tab(self):
        """Construye el editor completo."""
        top_bar = tk.Frame(self.tab_editor, bg=SURFACE_COLOR, pady=8, padx=15,
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="Editor de Datos", font=FONT_BOLD,
                 bg=SURFACE_COLOR, fg=TEXT_PRIMARY).pack(side="left")

        self._btn(top_bar, "💾  Guardar como Excel", self._guardar_excel, primary=True
                  ).pack(side="right", padx=5)
        self._btn(top_bar, "🔄  Recargar desde archivo", self._recargar_desde_archivo
                  ).pack(side="right", padx=5)

        body = tk.Frame(self.tab_editor, bg=BG_COLOR)
        body.pack(fill="both", expand=True, padx=20, pady=12)
        body.columnconfigure(0, weight=0, minsize=420)
        body.columnconfigure(1, weight=1)

        # ── Panel izquierdo: Criterios + Config (scrollable) ──
        left_outer = tk.Frame(body, bg=BG_COLOR)
        left_outer.grid(row=0, column=0, sticky="ns", padx=(0, 12))

        left_canvas = tk.Canvas(left_outer, bg=BG_COLOR, highlightthickness=0, width=420)
        left_scroll_y = AutoScrollbar(left_outer, orient="vertical", command=left_canvas.yview)
        left = tk.Frame(left_canvas, bg=BG_COLOR)

        left.bind("<Configure>",
                  lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scroll_y.set)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scroll_y.configure_pack(side="right", fill="y")

        # ─ Criterios ─
        self._seccion_editor(left, "Criterios")
        crit_ctrl = tk.Frame(left, bg=BG_COLOR)
        crit_ctrl.pack(fill="x", pady=(0, 4))
        self._btn(crit_ctrl, "+ Agregar",  self._agregar_criterio ).pack(side="left", padx=2)
        self._btn(crit_ctrl, "✎ Editar",   self._editar_criterio  ).pack(side="left", padx=2)
        self._btn(crit_ctrl, "✕ Eliminar", self._eliminar_criterio, danger=True
                  ).pack(side="left", padx=2)

        crit_tree_frame = tk.Frame(left, bg=BG_COLOR)
        crit_tree_frame.pack(fill="x")

        crit_scroll_y = AutoScrollbar(crit_tree_frame, orient="vertical")
        crit_scroll_y.configure_pack(side="right", fill="y")

        crit_scroll_x = AutoScrollbar(crit_tree_frame, orient="horizontal")
        crit_scroll_x.configure_pack(side="bottom", fill="x")

        self.tree_crit = ttk.Treeview(
            crit_tree_frame,
            columns=("Criterio", "Importancia (1-10)", "Tipo"),
            show="headings", height=8, style="Custom.Treeview",
            xscrollcommand=crit_scroll_x.set,
            yscrollcommand=crit_scroll_y.set
        )
        crit_scroll_x.config(command=self.tree_crit.xview)
        crit_scroll_y.config(command=self.tree_crit.yview)
        for col, w in [("Criterio", 140), ("Importancia (1-10)", 130), ("Tipo", 100)]:
            self.tree_crit.heading(col, text=col)
            self.tree_crit.column(col, anchor="center", width=w, minwidth=w, stretch=False)
        self.tree_crit.pack(fill="x")

        # ─ Configuración ─
        self._seccion_editor(left, "Configuración")
        conf_frame = tk.Frame(left, bg=BG_COLOR)
        conf_frame.pack(fill="x", pady=(0, 6))

        tk.Label(conf_frame, text="Iteraciones:", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=4)
        self.ent_iter = tk.Entry(conf_frame, font=FONT_MAIN, width=12)
        self.ent_iter.insert(0, str(self.datos_config.get("Iteraciones", 10000)))
        self.ent_iter.grid(row=0, column=1, padx=8, pady=4)

        tk.Label(conf_frame, text="Nombre decisión:", font=FONT_MAIN,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", pady=4)
        self.ent_nombre_dec = tk.Entry(conf_frame, font=FONT_MAIN, width=26)
        self.ent_nombre_dec.insert(0, str(self.datos_config.get("Nombre Decision", "Decisión")))
        self.ent_nombre_dec.grid(row=1, column=1, columnspan=2, padx=8, pady=4)

        self._btn(conf_frame, "Aplicar config", self._aplicar_config
                  ).grid(row=2, column=0, columnspan=2, pady=6, sticky="w")

        # ── Panel derecho: Alternativas ──
        right = tk.Frame(body, bg=BG_COLOR)
        right.grid(row=0, column=1, sticky="nsew")

        self._seccion_editor(right, "Alternativas")
        alt_ctrl = tk.Frame(right, bg=BG_COLOR)
        alt_ctrl.pack(fill="x", pady=(0, 4))
        self._btn(alt_ctrl, "+ Agregar",  self._agregar_alternativa ).pack(side="left", padx=2)
        self._btn(alt_ctrl, "✎ Editar",   self._editar_alternativa  ).pack(side="left", padx=2)
        self._btn(alt_ctrl, "✕ Eliminar", self._eliminar_alternativa, danger=True
                  ).pack(side="left", padx=2)

        # Frame con scroll horizontal para la tabla de alternativas
        alt_tree_frame = tk.Frame(right, bg=BG_COLOR)
        alt_tree_frame.pack(fill="both", expand=True)

        self.tree_alt_scroll_y = AutoScrollbar(alt_tree_frame, orient="vertical")
        self.tree_alt_scroll_y.configure_pack(side="right", fill="y")

        self.tree_alt_scroll_x = AutoScrollbar(alt_tree_frame, orient="horizontal")
        self.tree_alt_scroll_x.configure_pack(side="bottom", fill="x")

        self.tree_alt = ttk.Treeview(
            alt_tree_frame, show="headings", height=14,
            style="Custom.Treeview",
            xscrollcommand=self.tree_alt_scroll_x.set,
            yscrollcommand=self.tree_alt_scroll_y.set
        )
        self.tree_alt_scroll_x.config(command=self.tree_alt.xview)
        self.tree_alt_scroll_y.config(command=self.tree_alt.yview)
        self.tree_alt.pack(fill="both", expand=True)

        # Aviso vacío
        self.lbl_alt_aviso = tk.Label(
            right,
            text="Agrega criterios primero para habilitar las alternativas.",
            font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_COLOR
        )
        self.lbl_alt_aviso.pack(pady=4)

        self._refrescar_tree_crit()
        self._refrescar_tree_alt()

    # ── HELPERS UI ────────────────────────────────────────

    def _btn(self, parent, text, command, primary=False, danger=False):
        if primary:
            bg, fg = ACCENT_COLOR, "white"
        elif danger:
            bg, fg = "#fff0f0", DANGER_COLOR
        else:
            bg, fg = "#ffffff", TEXT_PRIMARY
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, font=FONT_BOLD if primary else FONT_MAIN,
            relief="flat", padx=10, pady=5, cursor="hand2",
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )

    def _seccion_editor(self, parent, titulo):
        tk.Label(parent, text=titulo, font=FONT_BOLD,
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(14, 2))
        tk.Frame(parent, bg=ACCENT_COLOR, height=2).pack(fill="x", pady=(0, 8))

    # ── CRITERIOS CRUD ────────────────────────────────────

    def _refrescar_tree_crit(self):
        self.tree_crit.delete(*self.tree_crit.get_children())
        for c in self.datos_criterios:
            self.tree_crit.insert("", "end", values=(
                c["Criterio"],
                c["Importancia (1-10)"],
                c["Tipo"]
            ))

    def _agregar_criterio(self):
        dlg = DialogCriterio(self)
        self.wait_window(dlg)
        if dlg.resultado:
            # Verificar nombre duplicado
            nombres = [c["Criterio"] for c in self.datos_criterios]
            if dlg.resultado["Criterio"] in nombres:
                messagebox.showwarning("Duplicado",
                    f"Ya existe un criterio llamado '{dlg.resultado['Criterio']}'.")
                return
            self.datos_criterios.append(dlg.resultado)
            self._refrescar_tree_crit()
            self._refrescar_tree_alt()
            self.status_var.set(f"Criterio '{dlg.resultado['Criterio']}' agregado.")

    def _editar_criterio(self):
        sel = self.tree_crit.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un criterio para editar.")
            return
        idx = self.tree_crit.index(sel[0])
        dlg = DialogCriterio(self, datos_existentes=self.datos_criterios[idx])
        self.wait_window(dlg)
        if dlg.resultado:
            nombre_viejo = self.datos_criterios[idx]["Criterio"]
            nombre_nuevo = dlg.resultado["Criterio"]
            self.datos_criterios[idx] = dlg.resultado

            # Actualizar columnas en alternativas si cambió el nombre
            if nombre_viejo != nombre_nuevo:
                for alt in self.datos_alternativas:
                    for sufijo in ("_Min", "_Max"):
                        if f"{nombre_viejo}{sufijo}" in alt:
                            alt[f"{nombre_nuevo}{sufijo}"] = alt.pop(f"{nombre_viejo}{sufijo}")

            self._refrescar_tree_crit()
            self._refrescar_tree_alt()
            self.status_var.set(f"Criterio actualizado.")

    def _eliminar_criterio(self):
        sel = self.tree_crit.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un criterio para eliminar.")
            return
        idx  = self.tree_crit.index(sel[0])
        nombre = self.datos_criterios[idx]["Criterio"]
        if not messagebox.askyesno("Confirmar",
                f"¿Eliminar el criterio '{nombre}'?\n"
                "Sus columnas se eliminarán también de las alternativas."):
            return
        self.datos_criterios.pop(idx)
        # Limpiar columnas en alternativas
        for alt in self.datos_alternativas:
            alt.pop(f"{nombre}_Min", None)
            alt.pop(f"{nombre}_Max", None)
        self._refrescar_tree_crit()
        self._refrescar_tree_alt()
        self.status_var.set(f"Criterio '{nombre}' eliminado.")

    # ── ALTERNATIVAS CRUD ─────────────────────────────────

    def _refrescar_tree_alt(self):
        """Reconstruye el treeview de alternativas (columnas dinámicas)."""
        self.tree_alt.delete(*self.tree_alt.get_children())

        if not self.datos_criterios:
            self.tree_alt["columns"] = ()
            self.lbl_alt_aviso.config(
                text="Agrega criterios primero para habilitar las alternativas.",
                fg=TEXT_MUTED
            )
            return

        self.lbl_alt_aviso.config(text="", fg=BG_COLOR)

        cols = ["Alternativa"]
        for c in self.datos_criterios:
            cols += [f"{c['Criterio']}_Min", f"{c['Criterio']}_Max"]

        self.tree_alt["columns"] = cols
        for col in cols:
            row_data = [{col: a.get(col, "") for col in cols} for a in self.datos_alternativas]
            w = col_width(col, row_data, col, char_px=9, pad=20)
            self.tree_alt.heading(col, text=col)
            self.tree_alt.column(col, anchor="center",
                                 width=w, minwidth=w, stretch=False)

        for alt in self.datos_alternativas:
            self.tree_alt.insert("", "end",
                                 values=[str(alt.get(c, "")) for c in cols])

    def _agregar_alternativa(self):
        if not self.datos_criterios:
            messagebox.showwarning("Sin criterios",
                "Define al menos un criterio antes de agregar alternativas.")
            return
        dlg = DialogAlternativa(self, self.datos_criterios)
        self.wait_window(dlg)
        if dlg.resultado:
            nombres = [a["Alternativa"] for a in self.datos_alternativas]
            if dlg.resultado["Alternativa"] in nombres:
                messagebox.showwarning("Duplicado",
                    f"Ya existe una alternativa llamada '{dlg.resultado['Alternativa']}'.")
                return
            self.datos_alternativas.append(dlg.resultado)
            self._refrescar_tree_alt()
            self.status_var.set(f"Alternativa '{dlg.resultado['Alternativa']}' agregada.")

    def _editar_alternativa(self):
        sel = self.tree_alt.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona una alternativa para editar.")
            return
        idx = self.tree_alt.index(sel[0])
        dlg = DialogAlternativa(self, self.datos_criterios,
                                datos_existentes=self.datos_alternativas[idx])
        self.wait_window(dlg)
        if dlg.resultado:
            self.datos_alternativas[idx] = dlg.resultado
            self._refrescar_tree_alt()
            self.status_var.set("Alternativa actualizada.")

    def _eliminar_alternativa(self):
        sel = self.tree_alt.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona una alternativa para eliminar.")
            return
        idx    = self.tree_alt.index(sel[0])
        nombre = self.datos_alternativas[idx]["Alternativa"]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la alternativa '{nombre}'?"):
            self.datos_alternativas.pop(idx)
            self._refrescar_tree_alt()
            self.status_var.set(f"Alternativa '{nombre}' eliminada.")

    # ── CONFIGURACIÓN ─────────────────────────────────────

    def _aplicar_config(self):
        try:
            iters = int(self.ent_iter.get())
            if iters < 100:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "Iteraciones debe ser un entero ≥ 100.")
            return
        nombre = self.ent_nombre_dec.get().strip() or "Decisión"
        self.datos_config = {"Iteraciones": iters, "Nombre Decision": nombre}
        self.status_var.set("Configuración aplicada.")

    # ── GUARDAR / CARGAR EXCEL ────────────────────────────

    def _guardar_excel(self):
        """Exporta el estado actual del editor a un archivo .xlsx."""
        self._aplicar_config()

        if not self.datos_criterios:
            messagebox.showwarning("Sin datos", "Agrega al menos un criterio antes de guardar.")
            return
        if not self.datos_alternativas:
            messagebox.showwarning("Sin datos", "Agrega al menos una alternativa antes de guardar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar como Excel"
        )
        if not path:
            return

        try:
            df_alt  = pd.DataFrame(self.datos_alternativas)
            df_crit = pd.DataFrame(self.datos_criterios)
            df_conf = pd.DataFrame([
                {"Parametro": k, "Valor": v}
                for k, v in self.datos_config.items()
            ])

            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df_alt.to_excel(writer,  sheet_name="Alternativas",  index=False)
                df_crit.to_excel(writer, sheet_name="Criterios",     index=False)
                df_conf.to_excel(writer, sheet_name="Configuracion", index=False)

            self.archivo_path = path
            self.lbl_archivo.config(
                text=f"✔ {os.path.basename(path)} (guardado desde editor)",
                fg=SUCCESS_COLOR
            )
            self.status_var.set(f"Excel guardado: {path}")
            messagebox.showinfo("Guardado", f"Archivo guardado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def _recargar_desde_archivo(self):
        """Recarga el estado del editor desde el archivo Excel cargado."""
        if not self.archivo_path:
            messagebox.showwarning("Sin archivo",
                "Primero carga un archivo Excel con el botón 'Cargar Excel'.")
            return
        self._poblar_desde_archivo(self.archivo_path)

    def _cargar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return

        ok, msg = validar_excel(path)
        if not ok:
            messagebox.showerror("Archivo inválido", msg)
            return

        self.archivo_path = path
        self.lbl_archivo.config(text=f"✔ {os.path.basename(path)}", fg=SUCCESS_COLOR)
        self._poblar_desde_archivo(path)

    def _poblar_desde_archivo(self, path):
        """Lee el Excel y actualiza el estado en memoria, editor y vista previa."""
        try:
            alts, err = leer_alternativas(path)
            if err:
                messagebox.showerror("Error", err)
                return

            crits, err = leer_criterios(path)
            if err:
                messagebox.showerror("Error", err)
                return

            conf, err = leer_configuracion(path)
            # conf puede fallar en archivos sin esa hoja → no es fatal
            if err:
                conf = {"Iteraciones": 10000, "Nombre Decision": "Decisión"}

            self.datos_alternativas = alts
            self.datos_criterios    = crits
            self.datos_config       = conf

            # Refrescar editor
            self._refrescar_tree_crit()
            self._refrescar_tree_alt()
            self.ent_iter.delete(0, "end")
            self.ent_iter.insert(0, str(conf.get("Iteraciones", 10000)))
            self.ent_nombre_dec.delete(0, "end")
            self.ent_nombre_dec.insert(0, str(conf.get("Nombre Decision", "Decisión")))

            # Refrescar vista previa
            self._actualizar_preview()

            n_alt  = len(alts)
            n_crit = len(crits)
            self.status_var.set(
                f"Cargado: {os.path.basename(path)}  •  "
                f"{n_alt} alternativas  •  {n_crit} criterios"
            )
            # Navegar a Vista Previa
            self.notebook.select(self.tab_preview)

        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    # ── EJECUCIÓN DEL ANÁLISIS ────────────────────────────

    def _ejecutar(self):
        self._aplicar_config()

        if not self.datos_criterios:
            messagebox.showwarning("Sin datos", "Define criterios antes de ejecutar.")
            return
        if not self.datos_alternativas:
            messagebox.showwarning("Sin datos", "Define alternativas antes de ejecutar.")
            return
        if len(self.datos_alternativas) < 2:
            messagebox.showwarning("Pocas alternativas",
                "Necesitas al menos 2 alternativas para comparar.")
            return

        # Actualizar preview con datos actuales del editor
        self._actualizar_preview()

        self.status_var.set("Procesando modelos…")
        threading.Thread(target=self._procesar_datos, daemon=True).start()

    def _procesar_datos(self):
        try:
            alts  = copy.deepcopy(self.datos_alternativas)
            crits = copy.deepcopy(self.datos_criterios)
            conf  = copy.deepcopy(self.datos_config)

            ranking_ahp = rankear_alternativas(alts, crits)

            iteraciones = int(conf.get("Iteraciones", 10000))
            pesos_norm  = {c["Criterio"]: c["peso"]
                           for c in normalizar_pesos(crits)}
            res_mc = simular_todas(alts, crits, pesos_norm, iteraciones=iteraciones)

            self.after(0, lambda: self._render_resultados(ranking_ahp, res_mc, conf))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error de Procesamiento", str(e)))
            self.after(0, lambda: self.status_var.set("Error en el análisis."))

    # ── RENDER DASHBOARD ──────────────────────────────────

    def _render_resultados(self, ranking_ahp, res_mc, conf):
        for w in self.tab_dashboard.winfo_children():
            w.destroy()

        container = tk.Frame(self.tab_dashboard, bg=BG_COLOR)
        container.pack(fill="both", expand=True, padx=15, pady=12)

        ganador_ahp  = ranking_ahp[0]["alternativa"]
        ganador_mc   = res_mc["ganador"]
        nombre_dec   = conf.get("Nombre Decision", "la decisión actual")

        # RECOMENDACIÓN
        rec_box = tk.Frame(container, bg=SURFACE_COLOR, padx=18, pady=16,
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        rec_box.pack(fill="x", pady=(0, 18))
        tk.Label(rec_box, text="RECOMENDACIÓN FINAL", font=FONT_BOLD,
                 fg=ACCENT_COLOR, bg=SURFACE_COLOR).pack(anchor="w")
        tk.Label(rec_box,
                 text=generar_recomendacion(ganador_ahp, ganador_mc, nombre_dec),
                 font=FONT_MAIN, fg=TEXT_PRIMARY, bg=SURFACE_COLOR,
                 justify="left", wraplength=950).pack(anchor="w", pady=(8, 0))

        # TABLA RESUMEN
        tk.Label(container, text="Resumen Comparativo", font=FONT_BOLD,
                 bg=BG_COLOR, fg=TEXT_PRIMARY).pack(anchor="w", pady=(4, 4))
        df = generar_tabla_resumen(ranking_ahp, res_mc["resultados"])
        cols = list(df.columns)
        tree = ttk.Treeview(container, columns=cols, show="headings",
                            height=len(df), style="Custom.Treeview")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=160, minwidth=120, stretch=False)
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        tree.pack(fill="x", pady=(0, 16))

        # ALERTAS
        alert_box = tk.Frame(container, bg="#fff3f3", padx=14, pady=14,
                             highlightbackground="#f5c2c7", highlightthickness=1)
        alert_box.pack(fill="x")
        tk.Label(alert_box, text="ALERTAS Y RIESGOS", font=FONT_BOLD,
                 fg="#842029", bg="#fff3f3").pack(anchor="w")
        tk.Label(alert_box,
                 text=generar_advertencias(res_mc["resultados"]),
                 font=FONT_MAIN, fg="#842029", bg="#fff3f3",
                 justify="left", wraplength=950).pack(anchor="w", pady=(6, 0))

        self.status_var.set(
            f"Análisis completado  •  Mejor opción: {ganador_ahp}  •  "
            f"Ganador MC: {ganador_mc}"
        )
        self.notebook.select(self.tab_dashboard)


if __name__ == "__main__":
    app = App()
    app.mainloop()