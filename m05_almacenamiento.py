"""
Módulo 05 — Almacenamiento (Disco)
═══════════════════════════════════════════════
Responsable: [Integrante 5]

Recopila: particiones montadas, espacio total/usado/libre por partición,
          sistema de archivos, alertas de umbral (>80% = advertencia, >90% = crítico).
"""

import psutil


# Umbrales de alerta
UMBRAL_ADVERTENCIA = 80   # %
UMBRAL_CRITICO     = 90   # %


def bytes_a_legible(n_bytes: int) -> str:
    for unidad in ("TB", "GB", "MB", "KB", "B"):
        divisor = {"TB": 1024**4, "GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}[unidad]
        if n_bytes >= divisor:
            return f"{n_bytes / divisor:.2f} {unidad}"
    return "0 B"


def nivel_alerta(porcentaje: float) -> str:
    if porcentaje >= UMBRAL_CRITICO:
        return "critico"
    elif porcentaje >= UMBRAL_ADVERTENCIA:
        return "advertencia"
    return "normal"


def obtener() -> dict:
    """Devuelve info de todas las particiones montadas del sistema."""

    particiones = []

    for particion in psutil.disk_partitions(all=False):
        # Saltar particiones sin punto de montaje o de solo lectura (ej. CDs)
        if not particion.mountpoint:
            continue
        try:
            uso = psutil.disk_usage(particion.mountpoint)
        except PermissionError:
            continue
        except OSError:
            continue

        porcentaje = round(uso.percent, 1)

        particiones.append({
            "dispositivo":  particion.device,
            "punto_montaje":particion.mountpoint,
            "sistema_arch": particion.fstype or "desconocido",
            "total":        bytes_a_legible(uso.total),
            "usado":        bytes_a_legible(uso.used),
            "libre":        bytes_a_legible(uso.free),
            "usado_%":      porcentaje,
            "alerta":       nivel_alerta(porcentaje),
            "total_bytes":  uso.total,
            "usado_bytes":  uso.used,
        })

    # Estadísticas de E/S de disco (si están disponibles)
    io_stats = {}
    try:
        io = psutil.disk_io_counters()
        if io:
            io_stats = {
                "lecturas":      io.read_count,
                "escrituras":    io.write_count,
                "bytes_leidos":  bytes_a_legible(io.read_bytes),
                "bytes_escritos":bytes_a_legible(io.write_bytes),
            }
    except (AttributeError, Exception):
        io_stats = {"info": "Estadísticas de I/O no disponibles"}

    # Resumen de alertas
    criticas    = [p for p in particiones if p["alerta"] == "critico"]
    advertencias = [p for p in particiones if p["alerta"] == "advertencia"]

    return {
        "particiones":    particiones,
        "total_partic":   len(particiones),
        "criticas":       criticas,
        "advertencias":   advertencias,
        "io":             io_stats,
    }


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = obtener()
    print("\n[Módulo 05] Almacenamiento\n" + "─" * 40)
    for p in datos["particiones"]:
        alerta_str = {"normal": "✔", "advertencia": "⚠", "critico": "✘"}[p["alerta"]]
        print(f"  {alerta_str} {p['punto_montaje']:<20} {p['usado_']:>5}%  "
              f"{p['usado']} / {p['total']}  [{p['sistema_arch']}]")
    if datos["criticas"]:
        print(f"\n  ⚠  CRITICO: {len(datos['criticas'])} partición(es) sobre {UMBRAL_CRITICO}%")
    print(f"\n  I/O: {datos['io']}")
