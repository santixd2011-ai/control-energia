# Control de Energía

Utilidad de Windows que permite gestionar el plan de energía y la frecuencia de actualización de la pantalla desde una interfaz gráfica sencilla.

## Perfiles

| Perfil | Qué hace |
|---|---|
| **Normal** | Restaura los planes a valores de fábrica, activa Equilibrado y desactiva los ahorros de USB, PCIe y discos. Nada se limita. |
| **Juegos · LoL (punto medio)** | Misma base que Normal, pero con la **CPU limitada al ~25%** (mínimo 5%, Turbo apagado, EPP equilibrado). Menos calor y sin tirones; la GPU queda en relojes automáticos (sin overclock ni límite forzado) y el monitor usa su frecuencia máxima. Pensado para jugar League of Legends sin que el PC se dispare de consumo. |
| **Ahorro extremo** | CPU al 5%, ahorro máximo de USB y PCIe, discos y pantalla se apagan pronto y monitor a 60 Hz. El PC queda lento pero estable. |

Los valores del punto medio se ajustan con las constantes `GAMING_CPU_MIN`, `GAMING_CPU_MAX`, `GAMING_TURBO` y `GAMING_EPP` al inicio de `Control_Energia.pyw`. Todos los perfiles se aplican al instante, con y sin batería, y no requieren reinicio. La app solo ejecuta comandos de energía una vez: no monitorea sensores ni consume CPU/GPU en segundo plano.

## Descarga rápida (no necesitas instalar Python)

| Archivo | Para quién |
|---|---|
| [`releases/Control_Energia_x64.exe`](releases/Control_Energia_x64.exe) | Windows **10/11 de 64 bits** (la mayoría de los PCs) |
| [`releases/Control_Energia_x86.exe`](releases/Control_Energia_x86.exe) | Windows **10/11 de 32 bits** (PCs antiguos) |

**Cómo elegir:** en Windows, ve a *Configuración → Sistema → Acerca de → Tipo de sistema*. Si dice «Sistema operativo de 64 bits», usa `_x64.exe`.

- Descarga el `.exe` y haz doble clic. **No requiere Python ni dependencias**.
- Aparecerá la ventana de **Control de Cuentas de Usuario (UAC)**: pulsa «Sí». La app necesita permisos de administrador para cambiar el plan de energía.
- Algunos antivirus pueden mostrar una alerta por tratarse de un ejecutable sin firma digital (compilado con PyInstaller). Es un falso positivo conocido; el código fuente está disponible aquí para revisarlo.

## Ejecutar desde el código fuente

```powershell
python Control_Energia.pyw
```

Generar el ejecutable:

```powershell
pyinstaller --noconfirm --onefile --windowed Control_Energia.pyw
```

## Requisitos

- Windows 10 u 11 (Python 3.15 solo es compatible con Windows 10 en adelante, según la documentación oficial).
- Permisos de administrador (la propia app solicita la elevación UAC).
- Para ejecutar el `.pyw`: Python 3.x. Para el `.exe`: nada.

## Compatibilidad analizada

| Aspecto | Resultado |
|---|---|
| Dependencias externas | Ninguna: solo biblioteca estándar de Python |
| Python embebido | Sí, incluido dentro del `.exe` |
| Arquitecturas | x64 y x86 (no ARM64) |
| Windows 7 / 8.1 | No compatibles con Python 3.15 |
| Archivos externos requeridos | Ninguno |
| Elevación de permisos | Automática vía UAC |

## Aviso

Esta herramienta modifica ajustes de energía del sistema. Revisa el código antes de ejecutarla y guarda tu configuración original.
