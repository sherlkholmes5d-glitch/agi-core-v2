import os
import shutil
from pathlib import Path

def cleanup():
    print("🧹 Экстренная очистка...")
    dirs_to_clean = ["logs", "data/temp", "__pycache__"]
    for d in dirs_to_clean:
        p = Path(d)
        if p.exists():
            for f in p.glob("*"):
                if f.is_file():
                    try: f.unlink()
                    except: pass
    print("✅ Очистка завершена. Попробуйте перезапустить ядро.")

if __name__ == "__main__":
    cleanup()