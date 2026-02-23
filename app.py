import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# Importación módulos existentes
from excel_reader import leer_alternativas, leer_criterios, leer_configuracion, validar_excel
from ahp_wsm import rankear_alternativas, normalizar_pesos
from montecarlo import simular_todas
from recomendacion import generar_recomendacion, generar_razones, generar_advertencias, generar_tabla_resumen

# --- CONFIGURACIÓN ESTÉTICA PLANA ---
BG_COLOR      = "#ffffff"  # Fondo blanco puro
SURFACE_COLOR = "#f8f9fa"  # Gris muy claro para secciones
BORDER_COLOR  = "#dee2e6"  # Bordes sutiles
TEXT_PRIMARY  = "#212529"  # Texto casi negro
TEXT_MUTED    = "#6c757d"  # Texto gris para detalles
ACCENT_COLOR  = "#0d6efd"  # Azul institucional (Bootstrap style)
SUCCESS_COLOR = "#198754"  # Verde plano para éxitos

FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI Bold", 10)
FONT_TITLE  = ("Segoe UI Semibold", 16)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Decision Analyzer — Professional Edition")
        self.geometry("1100x750")
        self.configure(bg=BG_COLOR)
        
        self.archivo_path = None
        self._build_ui()

    def _build_ui(self):
        # --- HEADER ---
        header = tk.Frame(self, bg=BG_COLOR, pady=20, padx=30)
        header.pack(fill="x")
        
        tk.Label(header, text="Analizador de Decisiones", font=FONT_TITLE, 
                 fg=TEXT_PRIMARY, bg=BG_COLOR).pack(side="left")
        
        # --- TOOLBAR ---
        toolbar = tk.Frame(self, bg=SURFACE_COLOR, pady=10, padx=30, 
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        toolbar.pack(fill="x")
        
        self.btn_cargar = self._create_button(toolbar, "Cargar Excel", self._cargar_archivo)
        self.btn_cargar.pack(side="left", padx=5)
        
        self.lbl_archivo = tk.Label(toolbar, text="No se ha seleccionado archivo", 
                                    font=FONT_MAIN, fg=TEXT_MUTED, bg=SURFACE_COLOR)
        self.lbl_archivo.pack(side="left", padx=15)
        
        self.btn_ejecutar = self._create_button(toolbar, "▶ Ejecutar Análisis", self._ejecutar, primary=True)
        self.btn_ejecutar.pack(side="right", padx=5)

        # --- CONTENIDO PRINCIPAL (Notebook) ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE_COLOR, padding=[20, 8], font=FONT_MAIN)
        style.map("TNotebook.Tab", background=[("selected", BG_COLOR)], foreground=[("selected", ACCENT_COLOR)])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Tabs
        self.tab_dashboard = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_dashboard, text="Dashboard de Resultados")
        
        # Mensaje inicial en el dashboard
        self.msg_espera = tk.Label(self.tab_dashboard, text="Cargue un archivo y presione 'Ejecutar' para ver los resultados.",
                                   font=FONT_MAIN, fg=TEXT_MUTED, bg=BG_COLOR, pady=100)
        self.msg_espera.pack()

        # --- STATUS BAR ---
        self.status_var = tk.StringVar(value="Listo")
        status_bar = tk.Label(self, textvariable=self.status_var, bg=SURFACE_COLOR, 
                              fg=TEXT_MUTED, anchor="w", padx=10, pady=5, 
                              highlightbackground=BORDER_COLOR, highlightthickness=1)
        status_bar.pack(fill="x", side="bottom")

    def _create_button(self, parent, text, command, primary=False):
        bg = ACCENT_COLOR if primary else "#ffffff"
        fg = "#ffffff" if primary else TEXT_PRIMARY
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, 
                        font=FONT_BOLD, relief="flat", padx=15, pady=6, 
                        cursor="hand2", highlightbackground=BORDER_COLOR, highlightthickness=1 if not primary else 0)
        return btn

    def _cargar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.archivo_path = path
            self.lbl_archivo.config(text=f"✔ {os.path.basename(path)}", fg=SUCCESS_COLOR)
            self.status_var.set(f"Archivo cargado: {path}")

    def _ejecutar(self):
        if not self.archivo_path:
            messagebox.showwarning("Atención", "Por favor, cargue un archivo Excel primero.")
            return
        
        self.status_var.set("Procesando modelos...")
        threading.Thread(target=self._procesar_datos, daemon=True).start()

    def _procesar_datos(self):
        try:
            # 1. Uso de excel_reader
            ok, msg = validar_excel(self.archivo_path)
            if not ok: raise Exception(msg)

            alts, _ = leer_alternativas(self.archivo_path)
            crits, _ = leer_criterios(self.archivo_path)
            conf, _ = leer_configuracion(self.archivo_path)

            # 2. Uso de ahp_wsm
            ranking_ahp = rankear_alternativas(alts, crits)
            
            # 3. Uso de montecarlo
            iteraciones = int(conf.get("Iteraciones", 10000))
            pesos_norm = {c['Criterio']: c['peso'] for c in normalizar_pesos(crits)}
            res_mc = simular_todas(alts, crits, pesos_norm, iteraciones=iteraciones)

            # Actualizar Interfaz
            self.after(0, lambda: self._render_resultados(ranking_ahp, res_mc, conf))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error de Procesamiento", str(e)))
            self.status_var.set("Error en el análisis.")

    def _render_resultados(self, ranking_ahp, res_mc, conf):
        # Limpiar dashboard
        for w in self.tab_dashboard.winfo_children(): w.destroy()
        
        container = tk.Frame(self.tab_dashboard, bg=BG_COLOR)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # SECCIÓN SUPERIOR: RECOMENDACIÓN (Uso de recomendacion.py)
        ganador_ahp = ranking_ahp[0]['alternativa']
        ganador_mc = res_mc['ganador']
        nombre_dec = conf.get("Nombre Decision", "la selección actual")
        
        rec_text = generar_recomendacion(ganador_ahp, ganador_mc, nombre_dec)
        
        rec_box = tk.Frame(container, bg=SURFACE_COLOR, padx=20, pady=20, 
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
        rec_box.pack(fill="x", pady=(0, 20))
        
        tk.Label(rec_box, text="RECOMENDACIÓN FINAL", font=FONT_BOLD, fg=ACCENT_COLOR, bg=SURFACE_COLOR).pack(anchor="w")
        tk.Label(rec_box, text=rec_text, font=FONT_MAIN, fg=TEXT_PRIMARY, bg=SURFACE_COLOR, 
                 justify="left", wraplength=900).pack(anchor="w", pady=(10, 0))

        # SECCIÓN MEDIA: TABLA RESUMEN (Uso de recomendacion.py)
        tk.Label(container, text="Resumen Comparativo", font=FONT_BOLD, bg=BG_COLOR).pack(anchor="w", pady=(10, 5))
        
        df_resumen = generar_tabla_resumen(ranking_ahp, res_mc['resultados'])
        
        # Frame para la tabla
        table_frame = tk.Frame(container, bg=BG_COLOR)
        table_frame.pack(fill="x")
        
        columns = list(df_resumen.columns)
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=len(df_resumen))
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
            
        for _, row in df_resumen.iterrows():
            tree.insert("", "end", values=list(row))
            
        tree.pack(fill="x")

        # SECCIÓN INFERIOR: ALERTAS (Uso de recomendacion.py)
        alert_box = tk.Frame(container, bg="#fff3f3", padx=15, pady=15, 
                             highlightbackground="#f5c2c7", highlightthickness=1)
        alert_box.pack(fill="x", pady=20)
        
        alertas = generar_advertencias(res_mc['resultados'])
        tk.Label(alert_box, text="ALERTAS Y RIESGOS", font=FONT_BOLD, fg="#842029", bg="#fff3f3").pack(anchor="w")
        tk.Label(alert_box, text=alertas, font=FONT_MAIN, fg="#842029", bg="#fff3f3", 
                 justify="left", wraplength=900).pack(anchor="w", pady=(5, 0))

        self.status_var.set("Análisis completado exitosamente.")

if __name__ == "__main__":
    app = App()
    app.mainloop()