"""
Módulo 04 — Uso de Recursos (CPU, RAM, Swap)
═══════════════════════════════════════════════
Responsable: [Integrante 4]

Recopila: uso actual de CPU por núcleo, frecuencia, temperatura (si aplica),
          uso de RAM total/usada/libre y estadísticas de swap.
"""

import psutil


def barra_ascii(porcentaje: float, ancho: int = 20) -> str:
    """Genera una barra de progreso ASCII. Ej: [████████░░░░] 40%"""
    relleno = int((porcentaje / 100) * ancho)
    barra = "█" * relleno + "░" * (ancho - relleno)
    return f"[{barra}] {porcentaje:.1f}%"


def bytes_a_legible(n_bytes: int) -> str:
    """Convierte bytes a formato legible: GB, MB, KB."""
    for unidad in ("GB", "MB", "KB", "B"):
        divisor = {"GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}[unidad]
        if n_bytes >= divisor:
            return f"{n_bytes / divisor:.2f} {unidad}"
    return f"{n_bytes} B"


def obtener() -> dict:
    """Devuelve métricas completas de CPU, RAM y Swap."""

    # ── CPU ───────────────────────────────────────────────────────────────────
    cpu_total = psutil.cpu_percent(interval=0.5)
    cpu_por_nucleo = psutil.cpu_percent(interval=0.5, percpu=True)
    cpu_conteo_fisico = psutil.cpu_count(logical=False) or 1
    cpu_conteo_logico = psutil.cpu_count(logical=True) or 1

    try:
        freq = psutil.cpu_freq()
        cpu_freq_actual = f"{freq.current:.0f} MHz" if freq else "N/A"
        cpu_freq_max    = f"{freq.max:.0f} MHz" if freq and freq.max else "N/A"
    except Exception:
        cpu_freq_actual = cpu_freq_max = "N/A"

    # Temperatura (no disponible en todos los sistemas)
    cpu_temp = "N/A"
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for nombre, entradas in temps.items():
                if entradas:
                    cpu_temp = f"{entradas[0].current:.1f} °C"
                    break
    except (AttributeError, Exception):
        pass

    # ── RAM ───────────────────────────────────────────────────────────────────
    ram = psutil.virtual_memory()

    # ── Swap ──────────────────────────────────────────────────────────────────
    swap = psutil.swap_memory()

    return {
        # CPU
        "cpu_total_%":        round(cpu_total, 1),
        "cpu_barra":          barra_ascii(cpu_total),
        "cpu_por_nucleo":     [round(p, 1) for p in cpu_por_nucleo],
        "cpu_nucleos_fisicos":cpu_conteo_fisico,
        "cpu_nucleos_logicos":cpu_conteo_logico,
        "cpu_freq_actual":    cpu_freq_actual,
        "cpu_freq_max":       cpu_freq_max,
        "cpu_temperatura":    cpu_temp,

        # RAM
        "ram_total":          bytes_a_legible(ram.total),
        "ram_usada":          bytes_a_legible(ram.used),
        "ram_libre":          bytes_a_legible(ram.available),
        "ram_%":              round(ram.percent, 1),
        "ram_barra":          barra_ascii(ram.percent),
        "ram_total_bytes":    ram.total,
        "ram_usada_bytes":    ram.used,

        # Swap
        "swap_total":         bytes_a_legible(swap.total),
        "swap_usada":         bytes_a_legible(swap.used),
        "swap_%":             round(swap.percent, 1),
        "swap_barra":         barra_ascii(swap.percent),
        "swap_disponible":    swap.total > 0,
    }


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = obtener()
    print("\n[Módulo 04] Uso de Recursos\n" + "─" * 40)
    print(f"  CPU Total    : {datos['cpu_barra']}")
    print(f"  Núcleos      : {datos['cpu_nucleos_fisicos']} físicos / {datos['cpu_nucleos_logicos']} lógicos")
    print(f"  Frecuencia   : {datos['cpu_freq_actual']} (máx {datos['cpu_freq_max']})")
    print(f"  Temperatura  : {datos['cpu_temperatura']}")
    print(f"\n  RAM          : {datos['ram_barra']}")
    print(f"  RAM usada    : {datos['ram_usada']} / {datos['ram_total']}")
    print(f"\n  Swap         : {datos['swap_barra']}")
    print(f"  Swap usada   : {datos['swap_usada']} / {datos['swap_total']}")
    print(f"\n  CPU por núcleo:")
    for i, p in enumerate(datos["cpu_por_nucleo"]):
        print(f"    Núcleo {i:<2}  : {barra_ascii(p, 15)}")
