import os
import sys
import subprocess
import time

VENV_DIR = ".venv"
REQUIREMENTS_FILE = "requirements.txt"
MAIN_SCRIPT = os.path.join("app", "main.py")
DASHBOARD_SCRIPT = os.path.join("app", "dashboard.py")

def get_venv_python():
    """Zwraca ścieżkę do pliku wykonywalnego Python wewnątrz wirtualnego środowiska."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")

def setup_venv():
    """Sprawdza czy .venv istnieje, jeśli nie - tworzy je i instaluje zależności."""
    if not os.path.exists(VENV_DIR):
        print(f"Tworzenie środowiska wirtualnego w '{VENV_DIR}'...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
        print("Środowisko wirtualne zostało utworzone.")
        
        venv_python = get_venv_python()
        
        if os.path.exists(REQUIREMENTS_FILE):
            print("Instalowanie zależności z requirements.txt...")
            subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            subprocess.run([venv_python, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True)
            print("Zależności zostały zainstalowane.")
        else:
            print(f"Ostrzeżenie: Nie znaleziono pliku {REQUIREMENTS_FILE}.")
    else:
        print(f"Środowisko wirtualne '{VENV_DIR}' już istnieje.")

def run_apps():
    """Uruchamia main.py oraz dashboard.py w odpowiedniej kolejności."""
    venv_python = get_venv_python()
    processes = []

    try:
        print(f"Uruchamianie {MAIN_SCRIPT}...")
        main_proc = subprocess.Popen([venv_python, MAIN_SCRIPT])
        processes.append(main_proc)
        
        time.sleep(2)

        print(f"Uruchamianie dashboardu Streamlit ({DASHBOARD_SCRIPT})...")
        dashboard_proc = subprocess.Popen([venv_python, "-m", "streamlit", "run", DASHBOARD_SCRIPT])
        processes.append(dashboard_proc)

        print("Aplikacje działają. Naciśnij Ctrl+C, aby zatrzymać.")
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nZatrzymywanie aplikacji...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("Aplikacje zostały zatrzymane.")

if __name__ == "__main__":
    setup_venv()
    run_apps()