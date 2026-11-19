# Control de Energía

Utilidad de Windows que permite gestionar el plan de energía y la frecuencia de actualización de la pantalla desde una interfaz gráfica sencilla.

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
