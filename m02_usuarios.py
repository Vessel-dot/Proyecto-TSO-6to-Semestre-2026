"""
Módulo 02 — Usuarios Activos
═══════════════════════════════════════════════
Responsable: [Integrante 2]

Recopila: usuarios del sistema, sesiones activas, UID, terminal
          y hora de inicio de sesión.
"""

import psutil
import datetime
import subprocess
import platform


def obtener() -> dict:
    """Devuelve info de usuarios del sistema y sesiones activas."""

    # Sesiones activas (usuarios con sesión iniciada)
    sesiones = []
    try:
        for u in psutil.users():
            inicio = datetime.datetime.fromtimestamp(u.started)
            sesiones.append({
                "usuario":  u.name,
                "terminal": u.terminal or "N/A",
                "host":     u.host or "local",
                "inicio":   inicio.strftime("%Y-%m-%d %H:%M"),
            })
    except Exception as e:
        sesiones = [{"error": str(e)}]

    # Lista de usuarios del sistema (solo Linux/macOS)
    usuarios_sistema = []
    if platform.system() in ("Linux", "Darwin"):
        try:
            with open("/etc/passwd", "r") as f:
                for linea in f:
                    partes = linea.strip().split(":")
                    if len(partes) >= 7:
                        nombre = partes[0]
                        uid    = int(partes[2])
                        shell  = partes[6]
                        # Solo usuarios con shell real (no daemons)
                        if uid >= 1000 and shell not in ("/usr/sbin/nologin", "/bin/false", "/sbin/nologin"):
                            usuarios_sistema.append({
                                "nombre": nombre,
                                "uid":    uid,
                                "shell":  shell,
                                "home":   partes[5],
                            })
        except PermissionError:
            usuarios_sistema = [{"info": "Sin permisos para leer /etc/passwd"}]
        except FileNotFoundError:
            usuarios_sistema = [{"info": "/etc/passwd no disponible en este SO"}]
    else:
        # Windows: obtener usuario actual
        try:
            import os
            usuarios_sistema = [{"nombre": os.environ.get("USERNAME", "N/A"), "uid": "N/A", "shell": "cmd/powershell", "home": os.environ.get("USERPROFILE", "N/A")}]
        except Exception:
            usuarios_sistema = []

    return {
        "sesiones_activas":   sesiones,
        "total_sesiones":     len(sesiones),
        "usuarios_sistema":   usuarios_sistema,
        "total_usuarios":     len(usuarios_sistema),
    }


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = obtener()
    print("\n[Módulo 02] Usuarios del Sistema\n" + "─" * 40)
    print(f"  Sesiones activas: {datos['total_sesiones']}")
    for s in datos["sesiones_activas"]:
        print(f"    · {s}")
    print(f"\n  Usuarios del sistema: {datos['total_usuarios']}")
    for u in datos["usuarios_sistema"]:
        print(f"    · {u}")
