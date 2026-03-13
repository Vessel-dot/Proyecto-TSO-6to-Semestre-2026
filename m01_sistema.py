"""
Módulo 01 — Información del Sistema Operativo
═══════════════════════════════════════════════
Responsable: [Integrante 1]

Recopila: versión del SO, kernel, hostname, uptime, arquitectura,
          procesador y fecha/hora del sistema.
"""

import platform
import socket
import datetime
import psutil


def obtener() -> dict:
    """Devuelve un diccionario con la info básica del SO."""

    # Tiempo de encendido del sistema
    boot_timestamp = psutil.boot_time()
    boot_dt = datetime.datetime.fromtimestamp(boot_timestamp)
    ahora = datetime.datetime.now()
    uptime_delta = ahora - boot_dt

    horas, resto = divmod(int(uptime_delta.total_seconds()), 3600)
    minutos, segundos = divmod(resto, 60)
    uptime_str = f"{horas}h {minutos}m {segundos}s"

    return {
        "sistema":       platform.system(),           # Linux / Windows / Darwin
        "version_so":    platform.version(),
        "release":       platform.release(),          # Ej: 6.8.0-45-generic
        "nombre_so":     platform.platform(),         # Nombre completo
        "arquitectura":  platform.machine(),          # x86_64 / ARM64
        "procesador":    platform.processor() or platform.machine(),
        "hostname":      socket.gethostname(),
        "python_ver":    platform.python_version(),
        "boot_time":     boot_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime":        uptime_str,
        "fecha_reporte": ahora.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = obtener()
    print("\n[Módulo 01] Información del Sistema\n" + "─" * 40)
    for clave, valor in datos.items():
        print(f"  {clave:<18} : {valor}")
