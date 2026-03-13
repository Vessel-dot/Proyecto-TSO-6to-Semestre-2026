# 🖥️ Script de Auditoría y Reporte del Sistema

> Proyecto Final — Taller de Sistemas Operativos  
> Instituto Tecnológico de Zacatepec · 2025

Script en Python que realiza una auditoría completa del sistema operativo en tiempo real y genera automáticamente un reporte visual en formato HTML. Diseñado con arquitectura modular para trabajo en equipo.

---

## 📋 ¿Qué hace?

Al ejecutarse, el script recopila la siguiente información del sistema:

- 🖥️ **Sistema Operativo** — versión, kernel, hostname y uptime
- 👤 **Usuarios** — sesiones activas y usuarios del sistema
- ⚙️ **Procesos** — top 10 por consumo de CPU y RAM
- 📊 **Recursos** — uso de CPU por núcleo, RAM y swap
- 💾 **Almacenamiento** — uso por partición con alertas automáticas
- 🌐 **Red** — interfaces activas, IPs y tráfico

Todo se consolida en un archivo `.html` que puedes abrir directamente en el navegador sin instalar nada extra.

---

## 📁 Estructura del proyecto

```
audit_project/
├── audit.py                    ← Punto de entrada principal
└── modules/
    ├── __init__.py
    ├── m01_sistema.py           → Info del SO
    ├── m02_usuarios.py          → Usuarios activos
    ├── m03_procesos.py          → Procesos críticos
    ├── m04_recursos.py          → CPU, RAM y swap
    ├── m05_almacenamiento.py    → Disco y particiones
    └── m06_red_reporte.py       → Red + generador HTML
```

---

## ⚙️ Requisitos

- Python 3.8 o superior
- pip

---

## 🚀 Instalación

**1. Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/audit-so.git
cd audit-so
```

**2. Instala la única dependencia:**
```bash
pip install psutil
```

---

## ▶️ Uso

```bash
# Generar el reporte HTML completo
python audit.py

# Ver resumen rápido en la terminal
python audit.py --preview
```

El reporte se guarda como `reporte_YYYYMMDD_HHMMSS.html` en la carpeta del proyecto. Ábrelo con doble clic en cualquier navegador.

---

## 🧩 Probar un módulo individualmente

Cada módulo puede ejecutarse de forma independiente:

```bash
python modules/m01_sistema.py
python modules/m02_usuarios.py
python modules/m03_procesos.py
python modules/m04_recursos.py
python modules/m05_almacenamiento.py
python modules/m06_red_reporte.py
```

---

## 🛠️ Compatibilidad

| Sistema Operativo | Funcional |
|-------------------|-----------|
| Windows 10/11     | ✅ |
| Ubuntu / Debian   | ✅ |
| macOS             | ✅ |

---

## 👥 Equipo

| Módulo | Integrante |
|--------|------------|
| m01 — Info del SO | [Nombre] |
| m02 — Usuarios | [Nombre] |
| m03 — Procesos | [Nombre] |
| m04 — Recursos | [Nombre] |
| m05 — Almacenamiento | [Nombre] |
| m06 — Red & Reporte | [Nombre] |

---

> Taller de Sistemas Operativos · ITZ Zacatepec · 2025
