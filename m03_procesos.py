"""
Módulo 03 — Procesos Críticos
═══════════════════════════════════════════════
Responsable: [Integrante 3]

Recopila: top 10 procesos por CPU, top 10 por RAM,
          total de procesos y estados del sistema.
"""

import psutil


def obtener() -> dict:
    """Devuelve los procesos más demandantes del sistema."""

    procesos_raw = []

    # LIGERO — solo lo esencial
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            # Ignorar procesos sin nombre o del kernel
            if not info["name"]:
                continue
            procesos_raw.append({
                "pid":    info["pid"],
                "nombre": info["name"],
                "usuario": "N/A",
                "estado":  "N/A",
                "cpu_%":   round(info["cpu_percent"] or 0, 2),
                "ram_%":   round(info["memory_percent"] or 0, 2),
                "ram_mb":  0,
                "hilos":   0,
})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Hacer una segunda pasada para obtener CPU% real (requiere dos lecturas)
    # La primera llamada a cpu_percent() devuelve 0 siempre; la segunda es real.
    #psutil.cpu_percent(interval=0.3)
    #for proc in psutil.process_iter(["pid", "cpu_percent"]):
    #    try:
    #       for p in procesos_raw:
    #            if p["pid"] == proc.pid:
    #                p["cpu_%"] = round(proc.cpu_percent() or 0, 2)
    #    except (psutil.NoSuchProcess, psutil.AccessDenied):
    #        continue

    # Conteo de estados
    estados = {}
    for p in procesos_raw:
        est = p["estado"]
        estados[est] = estados.get(est, 0) + 1

    # Cambiar de [:10] a [:5]
    top_cpu = sorted(procesos_raw, key=lambda x: x["cpu_%"], reverse=True)[:5]
    top_ram = sorted(procesos_raw, key=lambda x: x["ram_%"], reverse=True)[:5]

    return {
        "total_procesos": len(procesos_raw),
        "estados":        estados,
        "top_cpu":        top_cpu,
        "top_ram":        top_ram,
    }


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos = obtener()
    print("\n[Módulo 03] Procesos Críticos\n" + "─" * 40)
    print(f"  Total de procesos: {datos['total_procesos']}")
    print(f"  Estados: {datos['estados']}")
    print("\n  Top 5 por CPU:")
    for p in datos["top_cpu"][:5]:
        print(f"    [{p['pid']:>5}] {p['nombre']:<25} CPU: {p['cpu_%']:>5}%  RAM: {p['ram_%']:>5}%")
    print("\n  Top 5 por RAM:")
    for p in datos["top_ram"][:5]:
        print(f"    [{p['pid']:>5}] {p['nombre']:<25} RAM: {p['ram_%']:>5}%  ({p['ram_mb']} MB)")
