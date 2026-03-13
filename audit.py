"""
╔══════════════════════════════════════════════════════════╗
║   Script de Auditoría y Reporte del Sistema              ║
║   Taller de Sistemas Operativos — ITZ Zacatepec 2025     ║
╚══════════════════════════════════════════════════════════╝

Uso:
    python audit.py              → genera reporte HTML
    python audit.py --preview    → muestra resumen en consola
"""

import sys
import datetime
from modules import m01_sistema, m02_usuarios, m03_procesos
from modules import m04_recursos, m05_almacenamiento, m06_red_reporte

# ── Bandera de modo ───────────────────────────────────────────────────────────
PREVIEW = "--preview" in sys.argv

def banner():
    print("\033[92m")   # verde
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Script de Auditoría y Reporte del Sistema              ║")
    print("║   Taller de Sistemas Operativos — ITZ Zacatepec 2025     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\033[0m")

def log(msg, ok=True):
    estado = "\033[92m[OK]\033[0m" if ok else "\033[91m[ERR]\033[0m"
    print(f"  {estado} {msg}")

def main():
    banner()
    print(f"  Iniciando auditoría: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    datos = {}

    # Módulo 01 — Info del SO
    log("Recopilando información del sistema operativo...")
    datos["sistema"] = m01_sistema.obtener()

    # Módulo 02 — Usuarios activos
    log("Obteniendo usuarios activos...")
    datos["usuarios"] = m02_usuarios.obtener()

    # Módulo 03 — Procesos críticos
    log("Analizando procesos en ejecución...")
    datos["procesos"] = m03_procesos.obtener()

    # Módulo 04 — Uso de recursos
    log("Midiendo uso de CPU, RAM y swap...")
    datos["recursos"] = m04_recursos.obtener()

    # Módulo 05 — Almacenamiento
    log("Revisando particiones y almacenamiento...")
    datos["almacenamiento"] = m05_almacenamiento.obtener()

    # Módulo 06 — Red y generación del reporte
    log("Detectando interfaces de red...")
    datos["red"] = m06_red_reporte.obtener_red()

    print()

    if PREVIEW:
        # Muestra resumen en consola sin generar HTML
        m06_red_reporte.preview_consola(datos)
    else:
        # Genera el reporte HTML
        log("Generando reporte HTML...")
        archivo = m06_red_reporte.generar_reporte(datos)
        print(f"\n  \033[92m✔  Reporte generado exitosamente:\033[0m  {archivo}")
        print(f"  Ábrelo en tu navegador para visualizarlo.\n")

if __name__ == "__main__":
    main()
