import os
import string
import shutil
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import sys
import urllib.request
import ast

DESKTOP_PATH = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop').replace("\\", "/")
if not os.path.exists(DESKTOP_PATH):
    DESKTOP_PATH = os.path.expanduser("~/Desktop").replace("\\", "/")

APP_GAMESAVES_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'APP GameSaves').replace("\\", "/")
if not os.path.exists(APP_GAMESAVES_DIR):
    os.makedirs(APP_GAMESAVES_DIR, exist_ok=True)

BKP = os.path.join(DESKTOP_PATH, 'Backup Saves').replace("\\", "/")
if not os.path.exists(BKP):
    os.makedirs(BKP, exist_ok=True)
UP = os.environ.get('USERPROFILE', os.path.expanduser('~')).replace("\\", "/")
M_O = os.path.join(APP_GAMESAVES_DIR, "juegos_ocultos.txt").replace("\\", "/")
M_M = os.path.join(APP_GAMESAVES_DIR, "juegos_manuales.txt").replace("\\", "/")
M_EXC = os.path.join(APP_GAMESAVES_DIR, "exclusiones_remotas.txt").replace("\\", "/") 
URL_EXCLUSIONES_GITHUB = "https://raw.githubusercontent.com/loco965/Gestor-Savegames/refs/heads/main/exclusiones_remotas.txt"

class GestorPartidasLocal:
    def abrir_carpeta_backups(self):
        if not os.path.exists(self.dest):
            os.makedirs(self.dest, exist_ok=True)
        os.startfile(os.path.normpath(self.dest))

    def cambiar_carpeta(self):
        r = fd.askdirectory(initialdir=self.dest)
        if r:
            self.dest = r
            self.lbl_r.config(text=f"Guardando en: {self.dest}")

    def centrar_ventana(self, ventana, ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def ejecutar_en_hilo(self, funcion):
        hilo = threading.Thread(target=funcion, daemon=True)
        hilo.start()

    def abrir_link_donar(self):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def abrir_link_contacto(self):
        webbrowser.open("https://x.com/_noxbat")

    def seleccionar_todo_el_listado(self):
        self.box.selection_clear(0, tk.END)
        for i in range(self.box.size()):
            texto = self.box.get(i)
            if not texto.startswith("---") and texto != "":
                self.box.selection_set(i)

    def deseleccionar_todo_el_listado(self):
        self.box.selection_clear(0, tk.END)

    def get_sel_list(self):
        try:
            selección = self.box.curselection()
            if selección:
                elementos_validos = []
                for idx in selección:
                    texto_item = self.box.get(idx)
                    if not texto_item.startswith("---") and texto_item != "":
                        elementos_validos.append(texto_item)
                return elementos_validos
        except Exception:
            pass
        return []

    def limpiar_nombre_juego(self, texto_fila):
        res = texto_fila.replace("[👍 Copia Ok] ", "")
        res = res.replace("[Solo en Backup] ", "")
        res = res.strip()
        if " (" in res:
            partes = res.split(" (")
            res = " (".join(partes[:-1])
        return res.strip()

    def r_path(self, orig, nombre_juego_limpio):
        so = orig if os.path.isabs(orig) else os.path.join(UP, orig).replace("\\", "/")
        ultimo_directorio = os.path.basename(so)
        
        if ultimo_directorio.lower() == nombre_juego_limpio.lower():
            sub = nombre_juego_limpio
        else:
            sub = os.path.join(nombre_juego_limpio, ultimo_directorio)
            
        return os.path.join(self.dest, sub).replace("\\", "/"), so

    def check_bkp(self, folder):
        return folder.lower().strip() in self.backups_existentes

    def run_cmd(self, o, d):
        if os.path.isdir(o):
            os.makedirs(d, exist_ok=True)
            os.system(f'robocopy "{o}" "{d}" /E /R:1 /W:1 /NFL /NDL /NJH /NJS')
        elif os.path.isfile(o):
            os.makedirs(os.path.dirname(d), exist_ok=True)
            dir_o, file_o = os.path.split(o)
            dir_d = d if os.path.isdir(d) else os.path.dirname(d)
            os.system(f'robocopy "{dir_o}" "{dir_d}" "{file_o}" /R:1 /W:1 /NFL /NDL /NJH /NJS')

    def rotar_a_old(self, dst_actual):
        if os.path.exists(dst_actual):
            rel = os.path.relpath(dst_actual, self.dest)
            contador = 1
            while True:
                nombre_old = "old" if contador == 1 else f"old{contador}"
                camino_old = os.path.join(self.dest, nombre_old, rel).replace("\\", "/")
                if not os.path.exists(camino_old):
                    break
                contador += 1
            os.makedirs(os.path.dirname(camino_old), exist_ok=True)
            try:
                shutil.move(dst_actual, camino_old)
            except Exception:
                pass

    def rotar_original_en_pc(self, ruta_original_pc):
        if os.path.exists(ruta_original_pc):
            contador = 1
            while True:
                sufijo = "_old" if contador == 1 else f"_old{contador}"
                nueva_ruta_old = ruta_original_pc.rstrip("/") + sufijo
                if not os.path.exists(nueva_ruta_old):
                    break
                contador += 1
            try:
                shutil.move(ruta_original_pc, nueva_ruta_old)
            except Exception:
                pass

    def mostrar_submenu_ocultos(self):
        if not self.ocultos:
            mb.showinfo("Ocultos", "No tienes ningún elemento en la lista de ocultos actualmente.")
            return
        ventana_ocultos = tk.Toplevel(self.root)
        ventana_ocultos.title("Elementos Ocultados")
        ventana_ocultos.geometry("380x450")
        self.centrar_ventana(ventana_ocultos, 380, 450)
        ventana_ocultos.configure(bg="#2c3e50")
        ventana_ocultos.grab_set() 
        tk.Label(ventana_ocultos, text="Lista de Elementos Ocultados", font=("Arial", 12, "bold"), fg="#1abc9c", bg="#2c3e50").pack(pady=10)
        box_ocultos = tk.Listbox(ventana_ocultos, font=("Arial", 11), bg="#34495e", fg="white", selectbackground="#1abc9c", bd=0, highlightthickness=0, selectmode="multiple")
        box_ocultos.pack(padx=15, pady=5, fill="both", expand=True)
        for item in sorted(list(self.ocultos)):
            box_ocultos.insert(tk.END, item)

        def restaurar_elementos_multiples():
            selección = box_ocultos.curselection()
            if not selección:
                mb.showwarning("Atención", "Selecciona uno o varios elementos de la lista para restaurarlos.", parent=ventana_ocultos)
                return
            elementos_a_quitar = [box_ocultos.get(idx) for idx in selección]
            if mb.askyesno("Restaurar", f"¿Quieres volver a mostrar los {len(elementos_a_quitar)} elementos seleccionados en el escáner principal?", parent=ventana_ocultos):
                for nombre_item in elementos_a_quitar:
                    if nombre_item in self.ocultos:
                        self.ocultos.remove(nombre_item)
                self.save_data(M_O, self.ocultos)
                box_ocultos.delete(0, tk.END)
                for item in sorted(list(self.ocultos)):
                    box_ocultos.insert(tk.END, item)
                self.scan()
                if not self.ocultos:
                    ventana_ocultos.destroy()

        tk.Button(ventana_ocultos, text="✅ Volver a mostrar seleccionado(s)", command=restaurar_elementos_multiples, bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), bd=0, pady=8, cursor="hand2").pack(fill="x", padx=15, pady=15)

    def hide(self):
        lista_seleccionados = self.get_sel_list()
        if lista_seleccionados:
            if mb.askyesno("Ocultar", f"¿Quieres ocultar los {len(lista_seleccionados)} elementos seleccionados de la vista?"):
                for tag_juego in lista_seleccionados:
                    nombre_limpio = self.limpiar_nombre_juego(tag_juego)
                    self.ocultos.add(nombre_limpio)
                self.save_data(M_O, self.ocultos)
                self.scan()

    def añadir_carpeta_manual(self):
        ruta_seleccionada = fd.askdirectory(title="Selecciona la carpeta donde están las partidas guardadas")
        if not ruta_seleccionada:
            return
        nombre_juego = sd.askstring("Nombre del Juego", "¿Qué nombre quieres darle a este juego en la lista?")
        if not nombre_juego or not nombre_juego.strip():
            mb.showwarning("Atención", "Debes asignar un nombre válido para identificar la carpeta.")
            return
        nombre_juego = nombre_juego.strip()
        self.manuales[nombre_juego] = ruta_seleccionada.replace("\\", "/")
        lineas_a_guardar = [f"{k}|||{v}" for k, v in self.manuales.items()]
        self.save_data(M_M, lineas_a_guardar)
        mb.showinfo("Éxito", f"¡Se ha añadido '{nombre_juego}' correctamente! El sistema volverá a escanear.")
        self.scan()

    def quitar_carpeta_manual(self):
        lista_seleccionados = self.get_sel_list()
        if not lista_seleccionados:
            mb.showwarning("Atención", "Por favor, selecciona uno o varios elementos manuales de la lista para quitarlos.")
            return
        manuales_a_eliminar = []
        for tag_seleccionado in lista_seleccionados:
            nombre_limpio = self.limpiar_nombre_juego(tag_seleccionado)
            if nombre_limpio in self.manuales:
                manuales_a_eliminar.append(nombre_limpio)
        if not manuales_a_eliminar:
            mb.showwarning("Atención", "Ninguno de los elementos seleccionados pertenece a la lista de carpetas manuales.")
            return
        if mb.askyesno("Quitar Manual", f"¿Quieres quitar los {len(manuales_a_eliminar)} juegos manuales seleccionados de la lista?\n(Esto NO borrará tus partidas guardadas del disco)."):
            for juego in manuales_a_eliminar:
                if juego in self.manuales:
                    del self.manuales[juego]
            lineas_a_guardar = [f"{k}|||{v}" for k, v in self.manuales.items()]
            self.save_data(M_M, lineas_a_guardar)
            self.scan()

    def load_manuales(self, path):
        if not os.path.exists(path):
            return {}
        dict_manuales = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for linea in f:
                     if "|||" in linea:
                        partes = linea.strip().split("|||")
                     if len(partes) == 2:
                            dict_manuales[partes[0]] = partes[1]
            return dict_manuales
        except Exception:
             return {}

    def get_folder_size_str(self, path):
        if not os.path.exists(path):
            return "No Encontrada"
        total_size = 0
        try:
            if os.path.isdir(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            total_size += os.path.getsize(fp)
            else:
                total_size = os.path.getsize(path)
        except Exception:
            return "Error Tam."
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.2f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.2f} TB"

    def op(self, mode):
        lista_seleccionados = self.get_sel_list()
        if not lista_seleccionados:
            mb.showwarning("Atención", "Por favor, selecciona uno o varios elementos de la lista haciendo clic sobre ellos.")
            return
        c = 0
        for tag_seleccionado in lista_seleccionados:
            if tag_seleccionado in self.juegos:
                orig = self.juegos[tag_seleccionado]
                nombre_limpio = self.limpiar_nombre_juego(tag_seleccionado)
                dst, _ = self.r_path(orig, nombre_limpio)
                if mode == 1:
                    if os.path.exists(orig):
                        self.rotar_a_old(dst)
                        self.run_cmd(orig, dst)
                        c += 1
                elif mode == 2:
                    if os.path.exists(dst):
                        self.rotar_original_en_pc(orig)
                        self.run_cmd(dst, orig)
                        c += 1
        self.root.after(0, self.scan)
        accion_str = "respaldaron" if mode == 1 else "restauraron"
        mb.showinfo("Éxito", f"¡Operación completada! Se {accion_str} {c} partidas marcadas.")

    def indexar_backups_en_disco(self):
        self.backups_existentes.clear()
        if os.path.exists(self.dest) and os.path.isdir(self.dest):
            try:
                for elemento in os.listdir(self.dest):
                    if os.path.isdir(os.path.join(self.dest, elemento)) and elemento.lower().strip() not in ["old", "old2", "old3"]:
                        self.backups_existentes.add(elemento.lower().strip())
            except Exception:
                pass

    def load_ocultos(self, path):
        if not os.path.exists(path):
            return set()
        try:
            with open(path, "r", encoding="utf-8") as f:
                return set([linea.strip() for linea in f if linea.strip()])
        except Exception:
            return set()

    def save_data(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                for item in sorted(list(data)):
                    f.write(f"{item}\n")
        except Exception:
            pass

    def actualizar_exclusiones_desde_github(self):
        """Descarga el txt de GitHub (en formato texto plano) y guarda las exclusiones."""
        try:
            self.btn_scan.config(state="disabled", text="⏳ ACTUALIZANDO...")

            # Descargar el contenido del archivo remoto
            respuesta = urllib.request.urlopen(URL_EXCLUSIONES_GITHUB, timeout=10)
            contenido_raw = respuesta.read().decode('utf-8')

            # Procesar el texto línea por línea
            nuevos_filtros = []
            for linea in contenido_raw.splitlines():
                linea_limpia = linea.strip().lower()
                # Ignorar líneas vacías o comentarios
                if linea_limpia and not linea_limpia.startswith("#"):
                    nuevos_filtros.append(linea_limpia)

            # Verificar si ya existe el archivo local y eliminarlo
            exclusiones_path = os.path.join(BKP, "exclusiones_remotas.txt")
            if os.path.exists(exclusiones_path):
                os.remove(exclusiones_path)

            if nuevos_filtros:
                with open(M_EXC, "w", encoding="utf-8") as f:
                    for filtro in sorted(list(set(nuevos_filtros))):
                        f.write(f"{filtro}\n")

                self.root.after(0, lambda: mb.showinfo("Éxito", "¡Lista de exclusiones actualizada correctamente desde GitHub!"))
                self.root.after(0, self.scan)
            else:
                raise ValueError("No se encontraron elementos válidos en el archivo remoto.")

        except Exception as e:
            self.root.after(0, lambda: mb.showerror("Error", f"No se pudieron actualizar las exclusiones.\nDetalle: {e}"))
        finally:
            self.root.after(0, lambda: self.btn_scan.config(state="normal", text="🔍 ESCANEAR SAVES"))

    def scan(self):
        self.root.after(0, lambda: self.btn_scan.config(state="disabled", text="⏳ ESCANEANDO..."))
        self.juegos.clear()
        self.root.after(0, lambda: self.box.delete(0, tk.END))
        self.indexar_backups_en_disco()
        
        # Filtros de exclusion siempre en minuscula
        exclusiones_sistema = [
            "microsoft", "temp", "packages", "cache", "adobe", "google", "nvidia", 
            "discord", "spotify", "battle.net", "origin", "comms", "itunes", "vlc",
            "skype", "telegram", "audacity", "gimp", "obs-studio", "curseforge",
            "amd", "ati", "intel", "realtek", "historial", "3dmark", "anydesk",
            "mi música", "mis imágenes", "mis vídeos", "mi musica", "mis imagenes", "mis videos",
            "plantillas", "custom office templates", "archivos temporales", "oc_ocat", "ocat",
            "battleye", "bittorrent", "cef", "comgr", "connecteddevices", "crashdumps", 
            "crashreport", "datos de programa", "dbg", "discovery", "drivebeyond", 
            "elevateddiagnostics", "epicgames", "faceit", "futuremark", "g1r", 
            "gamequest", "gpu3d", "install4j", "isolatedstorage", "jdownloader", 
            "openshell", "peerdist", "pigeonsimulator", "pip", "programs", "publishers", 
            "python", "razer", "redengine", "riot games", "steam", "logs", "telemetry",
            "winrar", "utorrent", "stremio", "libreoffice", "riot client", "easyanticheat",
            "freac", "jam software", "maxon", "netease", "rapidcrc", "ts3client", 
            "userbenchmark", "zaap", "ankama launcher", "goldberg eos emu",
            "setup", "speech", "teamspeak", "truckersmp", "ul", "unrealengine",
            "uv", "virtualstore", "vivox", "vs revo group",
            "0tr0s", "frameview", "bionic", "github desktop", "lm studio", "bravesoftware", "mod.io",
            "placeholdertilelogofolder", "lm-studio-updater", "githubdesktop"
        ]

        if os.path.exists(M_EXC):
            try:
                with open(M_EXC, "r", encoding="utf-8") as f:
                    filtros_archivo = [linea.strip().lower() for linea in f if linea.strip()]
                    if filtros_archivo:
                        exclusiones_sistema = filtros_archivo
            except Exception:
                pass
        
        bloques_origen = [
            {"titulo": "--- 📄 DOCUMENTOS ---", "ruta": os.path.join(UP, "Documents")},
            {"titulo": "--- 📦 JUEGOS (MY GAMES) ---", "ruta": os.path.join(UP, "Documents/My Games")},
            {"titulo": "--- 🎮 PARTIDAS GUARDADAS (SAVED GAMES) ---", "ruta": os.path.join(UP, "Saved Games")},
            {"titulo": "--- 📁 APPDATA LOCAL ---", "ruta": os.path.join(UP, "AppData/Local")},
            {"titulo": "--- ⚙️ APPDATA ROAMING ---", "ruta": os.path.join(UP, "AppData/Roaming")}
        ]

        # Lógica para escanear de forma dinámica otros discos duros
        letras_discos = [f"{letra}:/" for letra in string.ascii_uppercase if os.path.exists(f"{letra}:/")]
        for disco in letras_discos:
            if disco.upper().startswith("C"):
                continue
            for variante in ["Documentos", "Documents"]:
                ruta_alternativa = os.path.join(disco, variante).replace("\\", "/")
                if os.path.exists(ruta_alternativa) and os.path.isdir(ruta_alternativa):
                    bloques_origen.append({
                        "titulo": f"--- 📄 DOCUMENTOS ({disco.strip('/')}) ---", 
                        "ruta": ruta_alternativa
                    })
                    ruta_my_games_alt = os.path.join(ruta_alternativa, "My Games").replace("\\", "/")
                    if os.path.exists(ruta_my_games_alt) and os.path.isdir(ruta_my_games_alt):
                        bloques_origen.append({
                            "titulo": f"--- 📦 JUEGOS MY GAMES ({disco.strip('/')}) ---", 
                            "ruta": ruta_my_games_alt
                        })

        juegos_encontrados_global = set()
        total_items_detectados = 0

        if self.manuales:
            self.box.insert(tk.END, "")
            self.box.insert(tk.END, "--- ➕ CARPETAS AÑADIDAS MANUALMENTE ---")
            for nombre_manual, ruta_manual in sorted(self.manuales.items()):
                if nombre_manual in self.ocultos:
                    continue
                juegos_encontrados_global.add(nombre_manual)
                ind = "[👍 Copia Ok] " if self.check_bkp(nombre_manual) else "               "
                tam_str = self.get_folder_size_str(ruta_manual)
                nv = f"{ind}{nombre_manual} ({tam_str})"
                self.juegos[nv] = ruta_manual
                self.box.insert(tk.END, nv)
                total_items_detectados += 1

        for Schuyler in bloques_origen:
            ruta_raiz = Schuyler["ruta"]
            if os.path.exists(ruta_raiz) and os.path.isdir(ruta_raiz):
                try:
                    elementos_carpeta = []
                    for elemento in os.listdir(ruta_raiz):
                        ruta_completa = os.path.join(ruta_raiz, elemento).replace("\\", "/")
                        if os.path.isdir(ruta_completa):
                            nombre_bajo = elemento.lower()
                            if elemento.startswith(".") or elemento in self.ocultos:
                                continue
                            if "--- 📄 DOCUMENTOS" in Schuyler["titulo"] and nombre_bajo == "my games":
                                continue
                            es_basura = False
                            for exc in exclusiones_sistema:
                                if exc in nombre_bajo:
                                    es_basura = True
                                    break
                            if es_basura:
                                continue
                            if elemento not in juegos_encontrados_global:
                                elementos_carpeta.append(elemento)
                    if elementos_carpeta:
                        elementos_carpeta.sort(key=lambda s: s.lower())
                        self.box.insert(tk.END, "")
                        self.box.insert(tk.END, Schuyler["titulo"])
                        for el in elementos_carpeta:
                            juegos_encontrados_global.add(el)
                            ind = "[👍 Copia Ok] " if self.check_bkp(el) else "               "
                            r_c = os.path.join(ruta_raiz, el).replace("\\", "/")
                            tam_str = self.get_folder_size_str(r_c)
                            nv = f"{ind}{el} ({tam_str})"
                            self.juegos[nv] = r_c
                            self.box.insert(tk.END, nv)
                            total_items_detectados += 1
                except Exception:
                    continue

        lista_solo_backup = []
        for juego_bkp in list(self.backups_existentes):
            if juego_bkp not in [x.lower() for x in juegos_encontrados_global] and juego_bkp not in [x.lower() for x in self.ocultos]:
                nombre_visual = juego_bkp
                ruta_antigua_bkp = os.path.join(self.dest, juego_bkp)
                if os.path.exists(ruta_antigua_bkp):
                    try:
                        nombre_visual = os.listdir(self.dest)[list(self.backups_existentes).index(juego_bkp)]
                    except Exception:
                        pass
                lista_solo_backup.append(nombre_visual)
        if lista_solo_backup:
            lista_solo_backup.sort(key=lambda s: s.lower())
            self.box.insert(tk.END, "")
            self.box.insert(tk.END, "--- 💾 SOLO EN CARPETA BACKUP (DESINSTALADOS) ---")
            for bkp_item in lista_solo_backup:
                r_c = os.path.join(self.dest, bkp_item).replace("\\", "/")
                tam_str = self.get_folder_size_str(r_c)
                nv = f"[👍 Copia Ok] [Solo en Backup] {bkp_item} ({tam_str})"
                self.juegos[nv] = os.path.join(UP, f"Documents/{bkp_item}").replace("\\", "/")
                self.box.insert(tk.END, nv)
                total_items_detectados += 1
        self.lbl_i.config(text=f"Partidas detectadas ({total_items_detectados}):", fg="#1abc9c" if total_items_detectados else "white")
        self.btn_scan.config(state="normal", text="🔍 ESCANEAR SAVES")

    def __init__(self, root):
        self.root = root
        root.title("Gestor de partidas guardadas by nox.bat")
        root.geometry("640x790")
        root.configure(bg="#2c3e50")
        self.centrar_ventana(root, 640, 790)
        self.dest = BKP
        self.juegos = {} 
        self.backups_existentes = set() 
        self.ocultos = self.load_ocultos(M_O)
        self.manuales = self.load_manuales(M_M)
        tk.Label(root, text="Gestor de partidas guardadas", font=("Arial", 16, "bold"), fg="#1abc9c", bg="#2c3e50").pack(pady=12)
        f_db = tk.Frame(root, bg="#2c3e50")
        f_db.pack(pady=2, fill="x", padx=20)
        self.lbl_db_status = tk.Label(f_db, text="Base de datos: Modo Local", fg="#2ecc71", bg="#2c3e50", font=("Arial", 9, "italic"))
        self.lbl_db_status.pack(side="left")
        tk.Button(f_db, text="🔄 Actualizar Filtros GitHub", 
                  command=lambda: self.ejecutar_en_hilo(self.actualizar_exclusiones_desde_github), 
                  bg="#34495e", fg="#1abc9c", font=("Arial", 8, "bold"), bd=0, cursor="hand2", padx=5).pack(side="right")
        f_r = tk.Frame(root, bg="#34495e", bd=1, relief="solid")
        f_r.pack(pady=5, fill="x", padx=20, ipady=5)
        self.lbl_r = tk.Label(f_r, text=f" Guardando en: {self.dest}", fg="#bdc3c7", bg="#34495e", font=("Arial", 9), wraplength=420, justify="left")
        self.lbl_r.pack(side="left", fill="x", expand=True, padx=5)
        f_r_btns = tk.Frame(f_r, bg="#34495e")
        f_r_btns.pack(side="right", padx=5)
        tk.Button(f_r_btns, text="Abrir", command=self.abrir_carpeta_backups, bg="#3498db", fg="white", font=("Arial", 8, "bold"), bd=0, cursor="hand2", padx=8, pady=2).pack(side="top", pady=2)
        tk.Button(f_r_btns, text="Cambiar", command=self.cambiar_carpeta, bg="#1abc9c", fg="white", font=("Arial", 8, "bold"), bd=0, cursor="hand2", padx=8, pady=2).pack(side="top", pady=2)
        f_s = tk.Frame(root, bg="#2c3e50")
        f_s.pack(pady=8, fill="x", padx=20)
        self.lbl_i = tk.Label(f_s, text="Partidas detectadas (0):", font=("Arial", 11, "bold"), fg="white", bg="#2c3e50")
        self.lbl_i.pack(side="left")
        f_s_btns = tk.Frame(f_s, bg="#2c3e50")
        f_s_btns.pack(side="right")
        tk.Button(f_s_btns, text="➕ Añadir Manual", command=self.añadir_carpeta_manual, bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), bd=0, padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
        tk.Button(f_s_btns, text="➖ Quitar Manual", command=self.quitar_carpeta_manual, bg="#e67e22", fg="white", font=("Arial", 9, "bold"), bd=0, padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
        self.btn_scan = tk.Button(f_s_btns, text="🔍 ESCANEAR SAVES", command=lambda: self.ejecutar_en_hilo(self.scan), bg="#3498db", fg="white", font=("Arial", 9, "bold"), bd=0, padx=8, pady=4, cursor="hand2")
        self.btn_scan.pack(side="left", padx=2)
        self.box = tk.Listbox(root, font=("Arial", 11), bg="#34495e", fg="white", selectbackground="#1abc9c", bd=0, highlightthickness=0, activestyle="none", selectmode="multiple")
        self.box.pack(pady=5, padx=20, fill="both", expand=True)
        f_v = tk.Frame(root, bg="#2c3e50")
        f_v.pack(pady=4, fill="x", padx=20)
        tk.Button(f_v, text="🙈 Ocultar seleccionado(s)", font=("Arial", 9, "bold"), bg="#2c3e50", fg="#e67e22", bd=0, activebackground="#2c3e50", activeforeground="#d35400", cursor="hand2", command=self.hide).pack(side="left", fill="x", expand=True)
        tk.Button(f_v, text="👀 Gestionar Ocultos", font=("Arial", 9, "bold"), bg="#2c3e50", fg="#3498db", bd=0, activebackground="#2c3e50", activeforeground="#2980b9", cursor="hand2", command=self.mostrar_submenu_ocultos).pack(side="right", fill="x", expand=True)
        f_m = tk.Frame(root, bg="#2c3e50")
        f_m.pack(pady=4, fill="x", padx=20)
        f_m.columnconfigure(0, weight=1, uniform="grupo_botones")
        f_m.columnconfigure(1, weight=1, uniform="grupo_botones")
        btn_sel = tk.Button(f_m, text="☑️ Seleccionar Todos", font=("Arial", 10, "bold"), bg="#9b59b6", fg="white", bd=0, relief="flat", pady=8, cursor="hand2", command=self.seleccionar_todo_el_listado)
        btn_sel.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        btn_desel = tk.Button(f_m, text="🔲 Deseleccionar Todos", font=("Arial", 10, "bold"), bg="#95a5a6", fg="black", bd=0, relief="flat", pady=8, cursor="hand2", command=self.deseleccionar_todo_el_listado)
        btn_desel.grid(row=0, column=1, sticky="ew", padx=(3, 0))
        f_b = tk.Frame(root, bg="#2c3e50")
        f_b.pack(pady=4, fill="x", padx=20)
        f_b.columnconfigure(0, weight=1, uniform="grupo_botones")
        f_b.columnconfigure(1, weight=1, uniform="grupo_botones")
        btn_resp = tk.Button(f_b, text="💾 Respaldar Save(s)", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white", bd=0, relief="flat", pady=8, cursor="hand2", command=lambda: self.ejecutar_en_hilo(lambda: self.op(1)))
        btn_resp.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        btn_rest = tk.Button(f_b, text="🔄 Restaurar Save(s)", font=("Arial", 11, "bold"), bg="#e74c3c", fg="white", bd=0, relief="flat", pady=8, cursor="hand2", command=lambda: self.ejecutar_en_hilo(lambda: self.op(2)))
        btn_rest.grid(row=0, column=1, sticky="ew", padx=(3, 0))
        f_inf = tk.Frame(root, bg="#2c3e50")
        f_inf.pack(pady=15, fill="x", padx=20)
        tk.Button(f_inf, text="🎁 Donar", command=self.abrir_link_donar, bg="#e67e22", fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, pady=6, cursor="hand2").pack(side="left")
        tk.Button(f_inf, text="➡️ X (Twitter)", command=self.abrir_link_contacto, bg="#d35400", fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, pady=6, cursor="hand2").pack(side="left", padx=10)
        tk.Button(f_inf, text="🚪 Salir", command=root.quit, bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, pady=6, cursor="hand2").pack(side="right")
        tk.Label(f_inf, text="by nox.bat", font=("Arial", 11, "bold", "italic"), fg="#bdc3c7", bg="#2c3e50").pack(pady=4)
        self.ejecutar_en_hilo(self.indexar_backups_en_disco)

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorPartidasLocal(root)
    root.mainloop()
