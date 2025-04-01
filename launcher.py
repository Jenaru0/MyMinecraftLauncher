import os
import subprocess
import requests
import json
import minecraft_launcher_lib
import tkinter as tk
from tkinter import messagebox

# --- Configuración ---
MC_VERSION = "1.20.1-forge-47.4.0"
FORGE_INSTALLER_URL = "https://github.com/Jenaru0/MyMinecraftLauncher/releases/download/minecraft/forge-1.20.1-47.4.0-installer.jar"
JEI_MOD_URL = "https://github.com/Jenaru0/MyMinecraftLauncher/releases/download/minecraft/jei-1.20.1-forge-15.20.0.106.jar"

# Forzar el directorio de Minecraft a la ruta correcta
mc_dir = r"C:\Users\jonna\AppData\Roaming\.minecraft"
versions_dir = os.path.join(mc_dir, "versions")
mods_dir = os.path.join(mc_dir, "mods")

# Crear el directorio mods si no existe
if not os.path.exists(mods_dir):
    os.makedirs(mods_dir)

# --- Función de Depuración ---
def debug_installed_versions():
    print("=== Versiones instaladas detectadas ===")
    if not os.path.exists(versions_dir):
        print("No se encontró el directorio 'versions' en:", versions_dir)
        return
    for folder in os.listdir(versions_dir):
        version_folder = os.path.join(versions_dir, folder)
        if os.path.isdir(version_folder):
            json_path = os.path.join(version_folder, folder + ".json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        version_id = data.get("id", "No id")
                        print("Carpeta:", folder, "-> id:", version_id)
                except Exception as e:
                    print("Error leyendo", json_path, ":", e)
            else:
                print("No se encontró JSON en", version_folder)

# Llama a la función de depuración para ver qué versiones detecta la librería.
# Revisa la salida en consola para asegurarte de que aparece la versión con id "1.20.1-forge-47.4.0".
debug_installed_versions()

# --- Función para Descargar Archivos ---
def download_file(url, dest_path):
    try:
        print(f"Descargando {url} ...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Archivo guardado en {dest_path}")
        else:
            raise Exception(f"Código de estado: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al descargar {url}: {e}")
        raise

# --- Función para Instalar Forge ---
def install_forge():
    version_dir = os.path.join(versions_dir, MC_VERSION)
    json_path = os.path.join(version_dir, f"{MC_VERSION}.json")
    if os.path.exists(json_path):
        print(f"La versión {MC_VERSION} ya está instalada.")
    else:
        print(f"Instalando Forge versión {MC_VERSION}...")
        installer_path = os.path.join(mc_dir, "forge_installer.jar")
        try:
            download_file(FORGE_INSTALLER_URL, installer_path)
        except Exception:
            return

        # Forzar el directorio de trabajo al directorio de Minecraft
        cwd = mc_dir

        # Verificar y crear un launcher_profiles.json mínimo si no existe
        profiles_path = os.path.join(mc_dir, "launcher_profiles.json")
        if not os.path.exists(profiles_path):
            print("No se encontró launcher_profiles.json, creando uno mínimo...")
            minimal_profile = {
                "profiles": {},
                "selectedProfile": "",
                "clientToken": "00000000-0000-0000-0000-000000000000",
                "authenticationDatabase": {}
            }
            with open(profiles_path, "w", encoding="utf-8") as f:
                json.dump(minimal_profile, f, indent=4)

        # Eliminar archivo extra que pueda interferir (por ejemplo, TLauncherAdditional.json)
        tal_path = os.path.join(versions_dir, MC_VERSION, "TLauncherAdditional.json")
        if os.path.exists(tal_path):
            try:
                os.remove(tal_path)
                print("Se eliminó TLauncherAdditional.json de la versión.")
            except Exception as e:
                print("No se pudo eliminar TLauncherAdditional.json:", e)

        try:
            subprocess.check_call(["java", "-jar", installer_path, "--installClient"], cwd=cwd)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error durante la instalación de Forge: {e}")
            return

        # El instalador crea la carpeta y el archivo JSON; eliminamos el instalador descargado
        os.remove(installer_path)
        print("Forge instalado correctamente.")

# --- Función para Instalar el Mod JEI ---
def install_mod():
    mod_filename = os.path.basename(JEI_MOD_URL)
    mod_dest = os.path.join(mods_dir, mod_filename)
    if os.path.exists(mod_dest):
        print(f"El mod {mod_filename} ya existe.")
    else:
        try:
            download_file(JEI_MOD_URL, mod_dest)
        except Exception:
            return

# --- Función para Lanzar el Juego ---
def launch_game(username):
    java_path = "java"  # Se asume que Java está en el PATH
    launch_options = {
        "username": username,
        "version": MC_VERSION,
        "gameDirectory": mc_dir,
        "assetsDir": os.path.join(mc_dir, "assets"),
        "resolution": {"width": 854, "height": 480}
    }
    try:
        command = minecraft_launcher_lib.command.get_minecraft_command(MC_VERSION, java_path, launch_options)
        print("Lanzando Minecraft...")
        subprocess.Popen(command)
    except Exception as e:
        messagebox.showerror("Error", f"Error al lanzar el juego: {e}")

# --- Función que se Ejecuta al Dar Clic en "Jugar" ---
def start_game():
    username = username_entry.get().strip()
    if not username:
        messagebox.showwarning("Aviso", "Por favor, ingresa tu nombre de usuario.")
        return
    install_forge()
    install_mod()
    launch_game(username)

# --- Interfaz Gráfica (tkinter) ---
root = tk.Tk()
root.title("Launcher Personalizado de Minecraft")
root.geometry("300x150")

username_label = tk.Label(root, text="Nombre de usuario:")
username_label.pack(pady=5)

username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)

play_button = tk.Button(root, text="Jugar", command=start_game)
play_button.pack(pady=10)

root.mainloop()
