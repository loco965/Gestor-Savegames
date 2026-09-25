# 🎮 Gestor de Partidas Guardadas (Savegames Backup)

Una aplicación ligera, automatizada y de código abierto programada en **Python** con interfaz gráfica **Tkinter** para gestionar, respaldar y restaurar las partidas guardadas de tus videojuegos favoritos de PC (Steam, Epic Games, GOG, etc.).

---

## ✨ Características Principales

*   **🔍 Escáner Automático:** Detecta al instante las carpetas de guardado en las rutas más comunes del sistema (`Documents`, `Saved Games`, `AppData Local/Roaming`, carpetas específicas de Steam/GOG y discos secundarios).
*   **🌐 Base de Datos en la Nube:** Permite actualizar de forma remota los filtros de exclusión directamente desde este repositorio de GitHub para omitir carpetas de telemetría, controladores, caché o archivos basura del sistema.
*   **💾 Respaldos Seguros:** Copia tus *savegames* mediante `Robocopy` de forma nativa en Windows.
*   **🔄 Historial de Versiones:** Si un respaldo o una restauración sobrescribe datos existentes, el programa automatiza un sistema de rotación a carpetas `.old` para evitar cualquier pérdida accidental de progreso.
*   **🛠️ Organización a tu medida:** Posibilidad de ocultar juegos detectados de la vista principal y de añadir directorios de guardado personalizados de forma manual.
*   **📦 Ejecutable Único:** Compilado en un solo archivo `.exe` independiente que no requiere instalación previa ni dependencias externas.

---

## 🚀 Guía Detallada de Uso (Paso a Paso)

### 1. Instalación y Puesta a Punto
*   **Descarga:** Ve a la sección de **Releases** (Lanzamientos) en la barra lateral derecha y descarga el archivo **`Backup SaveGames.exe`**.
*   **Ubicación:** Coloca el `.exe` donde prefieras y ejecútalo. De forma automática, el programa creará una carpeta en tu Escritorio llamada `Backup Saves`. Ahí es donde se guardarán todas tus partidas de forma organizada.
*   **Cambiar Ruta:** Si prefieres guardar tus backups en otra ubicación, haz clic en el botón **`Cambiar`** en la zona superior y elige la nueva carpeta. Puedes pulsar **`Abrir`** en cualquier momento para ver tus archivos respaldados.

### 2. Actualizar Filtros y Escanear
*   **Base de datos integrada:** El programa incluye por defecto una pequeña lista de exclusiones integrada en su código interno para poder funcionar de forma local desde el primer segundo. 
*   **Descarga recomendada (La opción óptima):** Sin embargo, **es muy importante y recomendable hacer clic primero en el botón `🔄 Actualizar Filtros GitHub`**. Al hacerlo, la app descargará la base de datos externa de este repositorio, la cual está muchísimo más completa, detallada y se mantiene actualizada constantemente con nuevos programas basura que hay que omitir.
*   **Escanear:** Tras poner al día tus filtros, haz clic en **`🔍 ESCANEAR SAVES`**. El programa revisará tu ordenador y te mostrará la lista de juegos.
*   *Indicadores visuales:* Los juegos que ya tengan una copia de seguridad hecha mostrarán la etiqueta **`[👍 Copia Ok]`** a la izquierda. Los juegos desinstalados que aún conserves en tu carpeta de backups aparecerán abajo del todo en la sección **`SOLO EN CARPETA BACKUP`**.

### 3. Respaldar y Restaurar Partidas
*   **Selección Múltiple:** Puedes seleccionar varios juegos a la vez haciendo clic sobre ellos. Si quieres agilizar el proceso, utiliza los botones **`☑️ Seleccionar Todos`** o **`🔲 Deseleccionar Todos`**.
*   **Crear Copia de Seguridad:** Con los juegos marcados en la lista, haz clic en el botón verde **`💾 Respaldar Save(s)`**. Tu partida se copiará a tu carpeta de backups de forma segura.
*   **Restaurar Partida:** Si has formateado el PC o quieres recuperar un progreso antiguo, selecciona los juegos en la lista y haz clic en el botón rojo **`🔄 Restaurar Save(s)`**. El programa devolverá los archivos exactamente a la carpeta original donde el juego los necesita.

### 4. Personalizar tu Lista (Manuales y Ocultos)
*   **Añadir un juego que no aparece:** Si tienes un juego antiguo o pirata cuya ruta de guardado no se detecta de forma automática, haz clic en **`➕ Añadir Manual`**, selecciona la carpeta donde guarda los archivos en tu PC y asígnale un nombre. Aparecerá en su propia sección de forma permanente.
*   **Limpiar la vista (Ocultar):** Si el escáner te muestra herramientas o juegos que no te interesan, selecciónalos y haz clic en **`🙈 Ocultar seleccionado(s)`**.
*   **Recuperar juegos ocultos:** Si te has equivocado al ocultar un juego, haz clic en **`👀 Gestionar Ocultos`**, marca los elementos que quieras recuperar en la ventana emergente y pulsa **`✅ Volver a mostrar seleccionado(s)`**.

---

## 🛠️ Requisitos del Sistema y Desarrollo

*   **Sistema Operativo:** Windows 10 / Windows 11 de 64 bits.
*   **Entorno:** Diseñado en Python 3 utilizando la librería gráfica nativa `Tkinter` (interfaz asíncrona mediante hilos `threading` para evitar congelamientos en la ventana al procesar archivos).

---

## 📝 Créditos y Contacto

*  Desarrollado por **nox.bat** con ayuda de Inteligencia Artificial local. 
*  Si quieres ponerte en contacto, reportar algún fallo o realizar sugerencias para futuras actualizaciones, puedes encontrarme en mi perfil de **X (Twitter):** [@_noxbat](https://x.com).
