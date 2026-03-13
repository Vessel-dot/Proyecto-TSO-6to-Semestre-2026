"""
Módulo 06 — Red & Generación del Reporte HTML
═══════════════════════════════════════════════
Responsable: [Integrante 6]

Recopila: interfaces de red activas, IPs, MAC addresses, bytes enviados/recibidos.
Genera: reporte completo en formato HTML con toda la info del sistema.
"""

import psutil
import socket
import datetime
import os


# ── RED ───────────────────────────────────────────────────────────────────────

def bytes_a_legible(n_bytes: int) -> str:
    for unidad in ("GB", "MB", "KB", "B"):
        divisor = {"GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}[unidad]
        if n_bytes >= divisor:
            return f"{n_bytes / divisor:.2f} {unidad}"
    return "0 B"


def obtener_red() -> dict:
    """Devuelve información de interfaces de red activas."""
    interfaces = []

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io    = psutil.net_io_counters(pernic=True)

    for nombre, direcciones in addrs.items():
        ipv4 = mac = "N/A"
        for addr in direcciones:
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == psutil.AF_LINK:
                mac = addr.address

        activa = stats[nombre].isup if nombre in stats else False
        velocidad = f"{stats[nombre].speed} Mbps" if nombre in stats and stats[nombre].speed > 0 else "N/A"

        bytes_env = bytes_rec = 0
        if nombre in io:
            bytes_env = io[nombre].bytes_sent
            bytes_rec = io[nombre].bytes_recv

        # Solo incluir interfaces con IP o MAC
        if ipv4 != "N/A" or mac != "N/A":
            interfaces.append({
                "nombre":     nombre,
                "ipv4":       ipv4,
                "mac":        mac,
                "activa":     activa,
                "velocidad":  velocidad,
                "enviados":   bytes_a_legible(bytes_env),
                "recibidos":  bytes_a_legible(bytes_rec),
            })

    return {
        "interfaces":       interfaces,
        "total_interfaces": len(interfaces),
        "activas":          sum(1 for i in interfaces if i["activa"]),
    }


# ── PREVIEW EN CONSOLA ────────────────────────────────────────────────────────

def preview_consola(datos: dict):
    """Imprime un resumen del sistema en consola (modo --preview)."""
    G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; B = "\033[94m"; X = "\033[0m"

    s = datos.get("sistema", {})
    r = datos.get("recursos", {})
    a = datos.get("almacenamiento", {})
    red = datos.get("red", {})

    print(f"\n{G}{'─'*55}{X}")
    print(f"  {B}RESUMEN DEL SISTEMA — {s.get('fecha_reporte','')}{X}")
    print(f"{'─'*55}{X}")
    print(f"  SO         : {s.get('nombre_so','N/A')}")
    print(f"  Hostname   : {s.get('hostname','N/A')}")
    print(f"  Uptime     : {s.get('uptime','N/A')}")
    print(f"\n  CPU        : {r.get('cpu_barra','N/A')}")
    print(f"  RAM        : {r.get('ram_barra','N/A')}  ({r.get('ram_usada','?')} / {r.get('ram_total','?')})")
    print(f"  Swap       : {r.get('swap_barra','N/A')}")
    print(f"\n  Procesos   : {datos.get('procesos',{}).get('total_procesos','N/A')}")
    print(f"  Usuarios   : {datos.get('usuarios',{}).get('total_sesiones','0')} sesión(es) activa(s)")

    partic = a.get("particiones", [])
    if partic:
        print(f"\n  Disco:")
        for p in partic:
            simbolo = {"normal": G+"✔", "advertencia": Y+"⚠", "critico": R+"✘"}[p["alerta"]]
            print(f"    {simbolo}{X}  {p['punto_montaje']:<18} {p['usado_%']:>5}%  ({p['usado']} / {p['total']})")

    ifaces = red.get("interfaces", [])
    if ifaces:
        print(f"\n  Red ({red.get('activas',0)} activa(s)):")
        for i in ifaces[:4]:
            estado = f"{G}activa{X}" if i["activa"] else f"{R}inactiva{X}"
            print(f"    · {i['nombre']:<12}  IP: {i['ipv4']:<16}  {estado}")

    print(f"\n{G}{'─'*55}{X}\n")


# ── GENERADOR HTML ────────────────────────────────────────────────────────────

def _color_alerta(nivel: str) -> str:
    return {"normal": "#10B981", "advertencia": "#F59E0B", "critico": "#EF4444"}.get(nivel, "#64748B")

def _barra_html(porcentaje: float, color: str = "#10B981") -> str:
    return f"""
    <div class="barra-contenedor">
      <div class="barra-relleno" style="width:{min(porcentaje,100):.1f}%;background:{color};">
        <span class="barra-label">{porcentaje:.1f}%</span>
      </div>
    </div>"""

def _color_cpu(p):
    if p >= 80: return "#EF4444"
    if p >= 50: return "#F59E0B"
    return "#10B981"


def generar_reporte(datos: dict) -> str:
    """Genera el archivo HTML del reporte y devuelve su ruta."""

    s  = datos.get("sistema", {})
    u  = datos.get("usuarios", {})
    p  = datos.get("procesos", {})
    r  = datos.get("recursos", {})
    a  = datos.get("almacenamiento", {})
    n  = datos.get("red", {})

    # ── Sección: Info del SO ─────────────────────────────────────────────
    filas_so = ""
    campos_so = [
        ("Sistema", s.get("sistema","")),
        ("Versión / Release", s.get("release","")),
        ("Plataforma completa", s.get("nombre_so","")),
        ("Arquitectura", s.get("arquitectura","")),
        ("Procesador", s.get("procesador","")),
        ("Hostname", s.get("hostname","")),
        ("Python", s.get("python_ver","")),
        ("Último inicio", s.get("boot_time","")),
        ("Uptime", s.get("uptime","")),
    ]
    for k, v in campos_so:
        filas_so += f"<tr><td class='td-key'>{k}</td><td>{v}</td></tr>"

    # ── Sección: Usuarios ────────────────────────────────────────────────
    filas_sesiones = ""
    for ses in u.get("sesiones_activas", []):
        if "error" in ses:
            filas_sesiones += f"<tr><td colspan='4'>{ses['error']}</td></tr>"
        else:
            filas_sesiones += f"""<tr>
              <td>{ses.get('usuario','')}</td><td>{ses.get('terminal','')}</td>
              <td>{ses.get('host','')}</td><td>{ses.get('inicio','')}</td></tr>"""
    if not filas_sesiones:
        filas_sesiones = "<tr><td colspan='4'>No hay sesiones activas detectadas</td></tr>"

    filas_usr_sis = ""
    for usr in u.get("usuarios_sistema", [])[:15]:
        if "info" in usr:
            filas_usr_sis += f"<tr><td colspan='4'>{usr['info']}</td></tr>"
        else:
            filas_usr_sis += f"""<tr>
              <td>{usr.get('nombre','')}</td><td>{usr.get('uid','')}</td>
              <td>{usr.get('shell','')}</td><td>{usr.get('home','')}</td></tr>"""

    # ── Sección: Procesos ────────────────────────────────────────────────
    estados_html = "".join(
        f"<span class='badge' style='background:#1E293B;border:1px solid #334155'>"
        f"{est}: <b>{cnt}</b></span> "
        for est, cnt in p.get("estados", {}).items()
    )

    filas_cpu_proc = ""
    for proc in p.get("top_cpu", []):
        color = _color_cpu(proc["cpu_%"])
        filas_cpu_proc += f"""<tr>
          <td>{proc['pid']}</td><td>{proc['nombre']}</td><td>{proc['usuario']}</td>
          <td><span style='color:{color};font-weight:bold'>{proc['cpu_%']}%</span></td>
          <td>{proc['ram_%']}%</td><td>{proc['ram_mb']} MB</td><td>{proc['hilos']}</td></tr>"""

    filas_ram_proc = ""
    for proc in p.get("top_ram", []):
        color = _color_cpu(proc["ram_%"])
        filas_ram_proc += f"""<tr>
          <td>{proc['pid']}</td><td>{proc['nombre']}</td><td>{proc['usuario']}</td>
          <td>{proc['cpu_%']}%</td>
          <td><span style='color:{color};font-weight:bold'>{proc['ram_%']}%</span></td>
          <td>{proc['ram_mb']} MB</td><td>{proc['hilos']}</td></tr>"""

    # ── Sección: Recursos ────────────────────────────────────────────────
    color_cpu_bar = _color_cpu(r.get("cpu_total_%", 0))
    color_ram_bar = _color_cpu(r.get("ram_%", 0))
    color_swap_bar = _color_cpu(r.get("swap_%", 0)) if r.get("swap_disponible") else "#64748B"

    nucleos_html = ""
    for i, pct in enumerate(r.get("cpu_por_nucleo", [])):
        c = _color_cpu(pct)
        nucleos_html += f"""
        <div class="nucleo-card">
          <div class="nucleo-label">Núcleo {i}</div>
          {_barra_html(pct, c)}
        </div>"""

    # ── Sección: Almacenamiento ───────────────────────────────────────────
    filas_disco = ""
    for part in a.get("particiones", []):
        color_a = _color_alerta(part["alerta"])
        icono   = {"normal": "✔", "advertencia": "⚠", "critico": "✘"}[part["alerta"]]
        filas_disco += f"""<tr>
          <td><span style='color:{color_a};font-size:1.1em'>{icono}</span></td>
          <td><code>{part['dispositivo']}</code></td>
          <td>{part['punto_montaje']}</td>
          <td>{part['sistema_arch']}</td>
          <td>{_barra_html(part['usado_%'], color_a)}</td>
          <td>{part['usado']}</td><td>{part['libre']}</td><td>{part['total']}</td></tr>"""

    # ── Sección: Red ─────────────────────────────────────────────────────
    filas_red = ""
    for iface in n.get("interfaces", []):
        est_color = "#10B981" if iface["activa"] else "#EF4444"
        est_txt   = "Activa" if iface["activa"] else "Inactiva"
        filas_red += f"""<tr>
          <td>{iface['nombre']}</td>
          <td><code>{iface['ipv4']}</code></td>
          <td><code style='font-size:0.8em'>{iface['mac']}</code></td>
          <td><span style='color:{est_color};font-weight:bold'>{est_txt}</span></td>
          <td>{iface['velocidad']}</td>
          <td>↑ {iface['enviados']}</td>
          <td>↓ {iface['recibidos']}</td></tr>"""

    # ── HTML completo ─────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte del Sistema — {s.get('hostname','')}</title>
<style>
  :root {{
    --bg:      #0F172A;
    --card:    #1E293B;
    --card2:   #162032;
    --border:  #334155;
    --green:   #10B981;
    --green2:  #34D399;
    --blue:    #3B82F6;
    --purple:  #8B5CF6;
    --orange:  #F59E0B;
    --red:     #EF4444;
    --white:   #F1F5F9;
    --muted:   #94A3B8;
    --text:    #E2E8F0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif;
         font-size: 14px; line-height: 1.6; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px; }}

  /* Header */
  .header {{ background: var(--card); border-bottom: 3px solid var(--green);
             padding: 24px 32px; margin-bottom: 28px; border-radius: 8px; }}
  .header-top {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }}
  .header h1 {{ font-size: 1.6em; color: var(--white); }}
  .header h1 span {{ color: var(--green2); font-family: Consolas, monospace; }}
  .header-meta {{ font-size: 0.85em; color: var(--muted); margin-top: 6px; }}
  .badge-so {{ background: #064E3B; color: var(--green2); border: 1px solid var(--green);
               padding: 4px 12px; border-radius: 20px; font-size: 0.82em; font-weight: bold; }}

  /* Cards de resumen */
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                   gap: 14px; margin-bottom: 28px; }}
  .summary-card {{ background: var(--card); border: 1px solid var(--border);
                   border-radius: 8px; padding: 16px; border-top: 3px solid var(--green); }}
  .summary-card .valor {{ font-size: 2em; font-weight: bold; color: var(--white); }}
  .summary-card .label {{ color: var(--muted); font-size: 0.82em; margin-top: 2px; }}

  /* Secciones */
  .seccion {{ background: var(--card); border: 1px solid var(--border);
              border-radius: 8px; margin-bottom: 24px; overflow: hidden; }}
  .seccion-header {{ background: var(--card2); padding: 14px 20px;
                     border-bottom: 1px solid var(--border);
                     display: flex; align-items: center; gap: 10px; }}
  .seccion-header h2 {{ font-size: 1em; color: var(--white); }}
  .num-badge {{ background: var(--green); color: #000; font-weight: bold;
                border-radius: 4px; padding: 2px 8px; font-size: 0.82em; }}
  .seccion-body {{ padding: 20px; }}

  /* Tablas */
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
  th {{ background: #0F172A; color: var(--muted); font-weight: 600;
        padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #1A2840; vertical-align: middle; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(255,255,255,0.02); }}
  .td-key {{ color: var(--muted); width: 200px; }}
  code {{ background: #0F172A; padding: 2px 6px; border-radius: 4px;
          font-family: Consolas, monospace; font-size: 0.88em; color: var(--green2); }}

  /* Barras de progreso */
  .barra-contenedor {{ background: #0F172A; border-radius: 6px; height: 18px;
                       overflow: hidden; position: relative; min-width: 120px; }}
  .barra-relleno {{ height: 100%; border-radius: 6px; transition: width 0.3s;
                    display: flex; align-items: center; justify-content: flex-end;
                    padding-right: 6px; min-width: 30px; }}
  .barra-label {{ color: #000; font-weight: bold; font-size: 0.78em; white-space: nowrap; }}

  /* Grid de núcleos */
  .nucleos-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }}
  .nucleo-card {{ background: var(--card2); border: 1px solid var(--border);
                  border-radius: 6px; padding: 10px 12px; }}
  .nucleo-label {{ font-size: 0.8em; color: var(--muted); margin-bottom: 6px; }}

  /* Badges */
  .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px;
            font-size: 0.82em; margin: 2px; }}

  /* Footer */
  .footer {{ text-align: center; color: var(--muted); font-size: 0.82em;
             margin-top: 32px; padding: 16px; border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">

  <!-- HEADER -->
  <div class="header">
    <div class="header-top">
      <div>
        <h1>Reporte de Auditoría — <span>{s.get('hostname','sistema')}</span></h1>
        <div class="header-meta">
          Generado el {s.get('fecha_reporte','')} &nbsp;·&nbsp;
          Uptime: {s.get('uptime','')} &nbsp;·&nbsp;
          Python {s.get('python_ver','')}
        </div>
      </div>
      <span class="badge-so">{s.get('sistema','')} {s.get('release','')}</span>
    </div>
  </div>

  <!-- RESUMEN RÁPIDO -->
  <div class="summary-grid">
    <div class="summary-card" style="border-top-color:#10B981">
      <div class="valor">{r.get('cpu_total_%',0):.0f}%</div>
      <div class="label">CPU en uso</div>
    </div>
    <div class="summary-card" style="border-top-color:#3B82F6">
      <div class="valor">{r.get('ram_%',0):.0f}%</div>
      <div class="label">RAM en uso ({r.get('ram_usada','?')} / {r.get('ram_total','?')})</div>
    </div>
    <div class="summary-card" style="border-top-color:#8B5CF6">
      <div class="valor">{p.get('total_procesos',0)}</div>
      <div class="label">Procesos activos</div>
    </div>
    <div class="summary-card" style="border-top-color:#F59E0B">
      <div class="valor">{u.get('total_sesiones',0)}</div>
      <div class="label">Sesiones activas</div>
    </div>
    <div class="summary-card" style="border-top-color:#06B6D4">
      <div class="valor">{n.get('activas',0)}</div>
      <div class="label">Interfaces de red activas</div>
    </div>
    <div class="summary-card" style="border-top-color:#EC4899">
      <div class="valor">{len(a.get('criticas',[]))+len(a.get('advertencias',[]))}</div>
      <div class="label">Alertas de almacenamiento</div>
    </div>
  </div>

  <!-- 01: SISTEMA -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge">01</span>
      <h2>Información del Sistema Operativo</h2>
    </div>
    <div class="seccion-body">
      <table><tbody>{filas_so}</tbody></table>
    </div>
  </div>

  <!-- 02: USUARIOS -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge" style="background:#3B82F6">02</span>
      <h2>Usuarios del Sistema</h2>
    </div>
    <div class="seccion-body">
      <h3 style="color:var(--muted);font-size:0.85em;margin-bottom:10px">SESIONES ACTIVAS</h3>
      <table>
        <thead><tr><th>Usuario</th><th>Terminal</th><th>Host</th><th>Inicio de sesión</th></tr></thead>
        <tbody>{filas_sesiones}</tbody>
      </table>
      <h3 style="color:var(--muted);font-size:0.85em;margin:18px 0 10px">USUARIOS DEL SISTEMA</h3>
      <table>
        <thead><tr><th>Nombre</th><th>UID</th><th>Shell</th><th>Home</th></tr></thead>
        <tbody>{filas_usr_sis}</tbody>
      </table>
    </div>
  </div>

  <!-- 03: PROCESOS -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge" style="background:#8B5CF6">03</span>
      <h2>Procesos Críticos &nbsp;
        <span style="color:var(--muted);font-weight:normal;font-size:0.9em">
          Total: {p.get('total_procesos',0)}
        </span>
      </h2>
    </div>
    <div class="seccion-body">
      <div style="margin-bottom:14px">{estados_html}</div>
      <h3 style="color:var(--muted);font-size:0.85em;margin-bottom:10px">TOP 10 — MAYOR USO DE CPU</h3>
      <table>
        <thead><tr><th>PID</th><th>Nombre</th><th>Usuario</th><th>CPU%</th><th>RAM%</th><th>RAM</th><th>Hilos</th></tr></thead>
        <tbody>{filas_cpu_proc}</tbody>
      </table>
      <h3 style="color:var(--muted);font-size:0.85em;margin:18px 0 10px">TOP 10 — MAYOR USO DE RAM</h3>
      <table>
        <thead><tr><th>PID</th><th>Nombre</th><th>Usuario</th><th>CPU%</th><th>RAM%</th><th>RAM</th><th>Hilos</th></tr></thead>
        <tbody>{filas_ram_proc}</tbody>
      </table>
    </div>
  </div>

  <!-- 04: RECURSOS -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge" style="background:#F59E0B;color:#000">04</span>
      <h2>Uso de Recursos — CPU, RAM y Swap</h2>
    </div>
    <div class="seccion-body">
      <table style="margin-bottom:20px"><tbody>
        <tr><td class="td-key">CPU Total</td><td>{_barra_html(r.get('cpu_total_%',0), color_cpu_bar)}</td></tr>
        <tr><td class="td-key">Núcleos</td><td>{r.get('cpu_nucleos_fisicos','?')} físicos / {r.get('cpu_nucleos_logicos','?')} lógicos</td></tr>
        <tr><td class="td-key">Frecuencia</td><td>{r.get('cpu_freq_actual','N/A')} (máx {r.get('cpu_freq_max','N/A')})</td></tr>
        <tr><td class="td-key">Temperatura</td><td>{r.get('cpu_temperatura','N/A')}</td></tr>
        <tr><td class="td-key">RAM en uso</td><td>{_barra_html(r.get('ram_%',0), color_ram_bar)}</td></tr>
        <tr><td class="td-key">RAM</td><td>{r.get('ram_usada','?')} usada / {r.get('ram_total','?')} total ({r.get('ram_libre','?')} libre)</td></tr>
        <tr><td class="td-key">Swap en uso</td><td>{_barra_html(r.get('swap_%',0), color_swap_bar)}</td></tr>
        <tr><td class="td-key">Swap</td><td>{r.get('swap_usada','?')} usada / {r.get('swap_total','?')} total</td></tr>
      </tbody></table>
      <h3 style="color:var(--muted);font-size:0.85em;margin-bottom:12px">CARGA POR NÚCLEO</h3>
      <div class="nucleos-grid">{nucleos_html}</div>
    </div>
  </div>

  <!-- 05: ALMACENAMIENTO -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge" style="background:#EC4899">05</span>
      <h2>Almacenamiento</h2>
    </div>
    <div class="seccion-body">
      <table>
        <thead><tr><th></th><th>Dispositivo</th><th>Montaje</th><th>Sistema</th>
                   <th>Uso</th><th>Usado</th><th>Libre</th><th>Total</th></tr></thead>
        <tbody>{filas_disco}</tbody>
      </table>
    </div>
  </div>

  <!-- 06: RED -->
  <div class="seccion">
    <div class="seccion-header">
      <span class="num-badge" style="background:#06B6D4;color:#000">06</span>
      <h2>Interfaces de Red</h2>
    </div>
    <div class="seccion-body">
      <table>
        <thead><tr><th>Interfaz</th><th>IPv4</th><th>MAC</th><th>Estado</th>
                   <th>Velocidad</th><th>Enviados</th><th>Recibidos</th></tr></thead>
        <tbody>{filas_red}</tbody>
      </table>
    </div>
  </div>

  <div class="footer">
    Reporte generado por <strong>audit.py</strong> &nbsp;·&nbsp;
    Taller de Sistemas Operativos &nbsp;·&nbsp;
    ITZ Zacatepec 2025
  </div>

</div>
</body>
</html>"""

    # Guardar archivo
    nombre_archivo = f"reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)

    return ruta


# ── Prueba independiente ──────────────────────────────────────────────────────
if __name__ == "__main__":
    datos_red = obtener_red()
    print("\n[Módulo 06] Red\n" + "─" * 40)
    for i in datos_red["interfaces"]:
        estado = "activa" if i["activa"] else "inactiva"
        print(f"  {i['nombre']:<12} IP: {i['ipv4']:<16} MAC: {i['mac']}  [{estado}]")
