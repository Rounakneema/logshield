import psutil
import os

target = os.path.abspath('LogShield_IEEE_Paper_Official.pdf').lower()
found = False

for proc in psutil.process_iter(['pid', 'name']):
    try:
        for f in proc.open_files():
            if f.path.lower() == target:
                print(f"PID {proc.pid} ({proc.name()}) is holding {target}")
                found = True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if not found:
    print("No open_files found with psutil. Checking process names...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.name().lower()
            if any(k in pname for k in ['acro', 'foxit', 'pdf', 'winword']):
                print(f"Potential viewer process: PID {proc.pid} ({proc.name()})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
