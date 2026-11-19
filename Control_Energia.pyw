import ctypes
from ctypes import wintypes
import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox


CREATE_NO_WINDOW = 0x08000000
ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFREQUENCY = 0x00400000
DM_BITSPERPEL = 0x00040000
CDS_UPDATEREGISTRY = 0x00000001
DISP_CHANGE_SUCCESSFUL = 0

PROCESSOR = "54533251-82be-4824-96c1-47b60b740d00"
TURBO = "be337238-0d82-4146-a960-4f3749d470c7"
CPMINCORES = "0cc5b647-c1df-4637-891a-dec35c318583"
CPMAXCORES = "ea062031-0e34-4ff1-9b6d-eb1059334028"
EPP = "36687f9e-e3a5-4dbf-b1dc-15eb381c6863"
USB = "2a737441-1930-4402-8d77-b2bebba308a3"
USB_SUSPEND = "48e6b7a6-50f5-4782-a5d4-53bb8f07e226"

# Punto medio para juegos (League of Legends): parte de la base del perfil
# "normal" y solo limita la CPU. Ajusta estos cuatro valores a gusto.
GAMING_CPU_MIN = "5"    # CPU minima (%)
GAMING_CPU_MAX = "25"   # CPU maxima (%) — mitad entre el 5% de ahorro extremo y el 100% de normal
GAMING_TURBO = "0"      # Turbo apagado: menos calor y sin picos de consumo
GAMING_EPP = "30"       # EPP equilibrado/respuesta: sube rapido dentro del limite, sin tirones


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", wintypes.LONG),
        ("dmPositionY", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def relaunch_as_admin():
    # UAC launches can start in System32 and argv[0] may be relative, so pass
    # the absolute script path and keep the current working directory.
    script_path = os.path.abspath(sys.argv[0])
    params = subprocess.list2cmdline([script_path] + sys.argv[1:])
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, os.getcwd(), 1)
    if result <= 32:
        messagebox.showerror("Permiso requerido", "No se pudo iniciar la aplicación como administrador.")


def set_refresh_rate(eco):
    user32 = ctypes.windll.user32
    current = DEVMODEW()
    current.dmSize = ctypes.sizeof(DEVMODEW)
    if not user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(current)):
        raise RuntimeError("Windows no pudo leer la configuración actual del monitor principal.")

    supported = {current.dmDisplayFrequency} if current.dmDisplayFrequency else set()
    index = 0
    while True:
        mode = DEVMODEW()
        mode.dmSize = ctypes.sizeof(DEVMODEW)
        if not user32.EnumDisplaySettingsW(None, index, ctypes.byref(mode)):
            break
        if (mode.dmPelsWidth == current.dmPelsWidth and
                mode.dmPelsHeight == current.dmPelsHeight and
                mode.dmBitsPerPel == current.dmBitsPerPel and
                mode.dmDisplayFrequency):
            supported.add(mode.dmDisplayFrequency)
        index += 1
    if not supported:
        supported = {current.dmDisplayFrequency or 60}

    if eco:
        # Lowest supported refresh at or above 60 Hz. Some modern panels have
        # no exact 60 Hz mode, so fall back to their lowest available one.
        candidates = sorted(hz for hz in supported if hz >= 60)
        target_hz = candidates[0] if candidates else min(supported)
    else:
        target_hz = max(supported)

    if current.dmDisplayFrequency == target_hz:
        return "La pantalla ya estaba a {} Hz.".format(target_hz)

    # Pass the current mode back with only frequency changed; retain resolution, color depth, etc.
    current.dmDisplayFrequency = target_hz
    current.dmFields = DM_DISPLAYFREQUENCY | DM_PELSWIDTH | DM_PELSHEIGHT | DM_BITSPERPEL
    result = user32.ChangeDisplaySettingsW(ctypes.byref(current), CDS_UPDATEREGISTRY)
    if result != DISP_CHANGE_SUCCESSFUL:
        raise RuntimeError("Windows rechazó el cambio de frecuencia (código {}).".format(result))
    return "Frecuencia de pantalla cambiada a {} Hz.".format(target_hz)


def run_command(args, timeout=20):
    try:
        result = subprocess.run(
            args,
            shell=False,
            creationflags=CREATE_NO_WINDOW,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return False, "No se encontró el comando: {}".format(args[0])
    except subprocess.TimeoutExpired:
        return False, "El comando superó el límite de {} segundos: {}".format(timeout, " ".join(args))
    detail = (result.stderr or result.stdout or "").strip()
    return result.returncode == 0, detail or ("Correcto" if result.returncode == 0 else "código {}".format(result.returncode))


def powercfg(*args):
    return run_command(["powercfg"] + list(args))


def gpu_reset_commands():
    # Let the NVIDIA driver pick clocks dynamically, which is the factory
    # behavior. Fixed MHz values are model/driver dependent and can be
    # rejected or force inefficient states, so only the reset commands are used.
    if shutil.which("nvidia-smi") is None:
        # No NVIDIA GPU present: skip silently instead of reporting a failure.
        return []
    return [
        (["nvidia-smi", "-rgc"], "GPU: reloj de núcleo en control automático (predeterminado)"),
        (["nvidia-smi", "-rmc"], "GPU: reloj de memoria en control automático (predeterminado)"),
    ]


def build_commands(profile):
    """Both profiles apply instantly; Windows does not need a restart.
    Every value is written for both AC (plugged in) and DC (battery) so the
    same behavior applies on laptops."""
    def both(scheme, group, setting, value, label):
        return [
            (["/setacvalueindex", scheme, group, setting, value], label),
            (["/setdcvalueindex", scheme, group, setting, value], label + " (batería)"),
        ]

    if profile == "normal":
        commands = [
            (["/restoredefaultschemes"], "Planes de energía: restaurados a los valores de fábrica de Windows"),
            (["/setactive", "SCHEME_BALANCED"], "Plan activo: Equilibrado (predeterminado de Windows)"),
        ]
        # Write the post-reset values to the Balanced scheme explicitly instead
        # of SCHEME_CURRENT, so policy latency or a stale cache can never make
        # them land on another plan. Windows left USB, PCIe and disk power
        # saving on by default, so the Normal profile removes those savings.
        for group, setting, value, label in (
            (USB, USB_SUSPEND, "0", "Suspensión selectiva USB: desactivada"),
            ("SUB_PCIEXPRESS", "ASPM", "0", "PCI Express: ahorro desactivado"),
            ("SUB_DISK", "DISKIDLE", "0", "Apagado de discos: desactivado"),
        ):
            commands.extend(both("SCHEME_BALANCED", group, setting, value, label))
        # Re-activate so the kernel reloads the modified subgroup indexes.
        commands.append((["/setactive", "SCHEME_BALANCED"], "Plan de energía: aplicado"))
        return commands, gpu_reset_commands()

    if profile == "ultra":
        commands = []
        for group, setting, value, label in (
            (PROCESSOR, TURBO, "0", "Turbo Boost: desactivado"),
            (PROCESSOR, CPMINCORES, "25", "Núcleos activos: 25% (el resto en reposo)"),
            (PROCESSOR, CPMAXCORES, "25", "Núcleos activos máximo: 25%"),
            ("SUB_PROCESSOR", "PROCTHROTTLEMIN", "5", "CPU mínima: 5%"),
            ("SUB_PROCESSOR", "PROCTHROTTLEMAX", "5", "CPU máxima: 5%"),
            (PROCESSOR, EPP, "100", "EPP: ahorro máximo"),
            ("SUB_PCIEXPRESS", "ASPM", "2", "PCI Express: ahorro máximo"),
            (USB, USB_SUSPEND, "1", "Suspensión selectiva USB: activada"),
            ("SUB_DISK", "DISKIDLE", "60", "Apagado de discos: 60 s"),
            ("SUB_VIDEO", "VIDEOIDLE", "60", "Apagado de pantalla: 1 min"),
        ):
            commands.extend(both("SCHEME_CURRENT", group, setting, value, label))
        commands.append((["/setactive", "SCHEME_CURRENT"], "Plan de energía: aplicado"))
        return commands, gpu_reset_commands()

    if profile == "gaming":
        # Punto medio: misma base limpia que "normal" (sin ahorros de USB, PCIe
        # ni discos, para evitar tirones) mas una tapa suave de CPU al ~25%.
        # No se tocan los nucleos activos ni la GPU: esta queda en relojes
        # automaticos, sin overclock ni limite forzado.
        commands = [
            (["/restoredefaultschemes"], "Planes de energía: restaurados a los valores de fábrica de Windows"),
            (["/setactive", "SCHEME_BALANCED"], "Plan activo: Equilibrado (predeterminado de Windows)"),
        ]
        for group, setting, value, label in (
            (USB, USB_SUSPEND, "0", "Suspensión selectiva USB: desactivada"),
            ("SUB_PCIEXPRESS", "ASPM", "0", "PCI Express: ahorro desactivado"),
            ("SUB_DISK", "DISKIDLE", "0", "Apagado de discos: desactivado"),
        ):
            commands.extend(both("SCHEME_BALANCED", group, setting, value, label))
        for group, setting, value, label in (
            (PROCESSOR, TURBO, GAMING_TURBO, "Turbo Boost: desactivado (menos calor)"),
            ("SUB_PROCESSOR", "PROCTHROTTLEMIN", GAMING_CPU_MIN, "CPU mínima: {}%".format(GAMING_CPU_MIN)),
            ("SUB_PROCESSOR", "PROCTHROTTLEMAX", GAMING_CPU_MAX, "CPU máxima: {}% (punto medio para juegos)".format(GAMING_CPU_MAX)),
            (PROCESSOR, EPP, GAMING_EPP, "EPP: equilibrado/respuesta (sin tirones)"),
        ):
            commands.extend(both("SCHEME_BALANCED", group, setting, value, label))
        commands.append((["/setactive", "SCHEME_BALANCED"], "Plan de energía: aplicado"))
        return commands, gpu_reset_commands()

    raise ValueError("Perfil desconocido: {}".format(profile))


class EnergyApp:
    BG = "#111318"
    PANEL = "#1a1d24"
    MUTED = "#9aa3b2"
    TEXT = "#f3f4f6"

    def __init__(self, root):
        self.root = root
        root.title("Control de energía")
        root.geometry("540x480")
        root.minsize(480, 390)
        root.configure(bg=self.BG)

        tk.Label(root, text="CONTROL DE ENERGÍA", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=26, pady=(24, 2))
        tk.Label(root, text="Normal, punto medio para juegos y ahorro extremo · sin reinicio",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=27, pady=(0, 16))

        panel = tk.Frame(root, bg=self.PANEL, padx=18, pady=16)
        panel.pack(fill="x", padx=22)
        self.status = tk.Label(panel, text="Elegí un perfil para aplicar los ajustes", bg=self.PANEL,
                               fg=self.TEXT, font=("Segoe UI", 10, "bold"), anchor="w")
        self.status.pack(fill="x")
        self.details = tk.Label(panel, text="La aplicación no monitorea sensores ni ejecuta tareas en segundo plano.",
                                bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9), anchor="w", justify="left", wraplength=440)
        self.details.pack(fill="x", pady=(6, 0))

        self.normal_button = self.make_button(root, "Normal · todo por defecto de Windows", "#1d4ed8", "#2563eb",
                                              lambda: self.apply_profile("normal"))
        self.gaming_button = self.make_button(root, "Juegos · LoL · punto medio (CPU ~25%)", "#b45309", "#d97706",
                                              lambda: self.apply_profile("gaming"))
        self.ultra_button = self.make_button(root, "Ahorro extremo · consumo mínimo", "#166534", "#15803d",
                                             lambda: self.apply_profile("ultra"))
        self.buttons = [self.normal_button, self.gaming_button, self.ultra_button]
        for button in self.buttons:
            button.pack(fill="x", padx=22, pady=6, ipady=8)
        tk.Label(root,
                 text="Los cambios se aplican al instante; no hace falta reiniciar. Normal restablece los planes a valores de fábrica, activa Equilibrado y quita los ahorros de USB, PCI Express y discos (nada se limita). Juegos · LoL usa esa misma base y solo limita la CPU al ~25% (mitad entre el 5% de ahorro extremo y el 100% de normal): menos calor, sin tirones, monitor a su frecuencia máxima y GPU en relojes automáticos (sin overclock ni límite forzado). Ahorro extremo limita la CPU al 5%, activa al máximo el ahorro de USB y PCIe, apaga discos y pantalla pronto y pone el monitor a 60 Hz: el PC queda lento pero estable. Los valores se aplican con y sin batería.",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8), wraplength=490,
                 justify="left").pack(anchor="w", padx=26, pady=(10, 0))

    @staticmethod
    def make_button(root, label, color, active, command):
        return tk.Button(root, text=label, command=command, bg=color, fg="white", activebackground=active,
                         activeforeground="white", font=("Segoe UI", 10, "bold"), relief="flat",
                         bd=0, cursor="hand2")

    def apply_profile(self, profile):
        for button in self.buttons:
            button.configure(state="disabled")
        self.status.configure(text="Aplicando perfil…", fg="#fbbf24")
        self.details.configure(text="Ejecutando los comandos. Puede tardar unos segundos.")
        self.root.update_idletasks()

        def worker():
            # Run every blocking call off the Tk thread so the window never
            # freezes while powercfg or nvidia-smi work.
            failures = []
            try:
                power_commands, gpu_commands = build_commands(profile)
                for args, description in power_commands + gpu_commands:
                    ok, detail = (powercfg(*args) if args and args[0].startswith("/") else run_command(args, timeout=60))
                    if not ok:
                        failures.append("{} — {}".format(description, detail))
            except Exception as exc:
                failures.append("Error interno — {}".format(exc))
            try:
                display_result = set_refresh_rate(profile == "ultra")
            except Exception as exc:
                failures.append("Frecuencia de pantalla — {}".format(exc))
                display_result = "No se pudo cambiar la frecuencia de pantalla."
            self.root.after(0, lambda: self.finish_apply(profile, failures, display_result))

        threading.Thread(target=worker, daemon=True).start()

    def finish_apply(self, profile, failures, display_result):
        for button in self.buttons:
            button.configure(state="normal")
        if failures:
            self.status.configure(text="Perfil aplicado con ajustes pendientes", fg="#fbbf24")
            summary = "\n".join("• " + item for item in failures[:5])
            if len(failures) > 5:
                summary += "\n• y {} error(es) más".format(len(failures) - 5)
            self.details.configure(text=display_result + "\n" + summary)
            messagebox.showwarning("Aplicación parcial", "Algunos ajustes no se pudieron aplicar:\n\n" + "\n".join(failures), parent=self.root)
        else:
            names = {"ultra": "AHORRO EXTREMO", "normal": "NORMAL · POR DEFECTO",
                     "gaming": "JUEGOS · LOL · PUNTO MEDIO"}
            colors = {"ultra": "#4ade80", "normal": "#60a5fa", "gaming": "#fbbf24"}
            self.status.configure(text="Perfil {} aplicado".format(names[profile]), fg=colors[profile])
            self.details.configure(text=display_result + " Todos los comandos finalizaron correctamente.")


def main():
    if os.name != "nt":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Windows requerido", "Esta aplicación funciona únicamente en Windows 10/11.")
        return
    root = tk.Tk()
    if not is_admin():
        root.withdraw()
        relaunch_as_admin()
        root.destroy()
        return
    EnergyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
