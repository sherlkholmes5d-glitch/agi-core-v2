import os
import sys
import json
import shutil
from pathlib import Path

def create_directory_structure():
    """Создает необходимую структуру папок"""
    dirs = [
        "logs", "data", "documents/upload", "documents/processed", 
        "data/vector_index", "plugins", "output", "benchmarks", 
        "modules", "orchestrator", "monitoring", "config/backups"
    ]
    
    for d in dirs:
        path = Path(d)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Создана папка: {d}")
        else:
            print(f"⚪ Папка существует: {d}")

    # Создаем пустой лог
    log_file = Path("logs/app.log")
    if not log_file.exists():
        log_file.touch()
        print("✅ Создан файл лога: logs/app.log")

def check_dependencies():
    """Проверяет наличие критических библиотек"""
    required = ["requests", "pydantic", "chromadb", "psutil"]
    missing = []
    
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
            
    if missing:
        print(f"\n❌ Отсутствуют библиотеки: {', '.join(missing)}")
        print("Запустите: pip install -r requirements.txt")
        return False
    return True

def generate_default_config():
    """Создает дефолтный конфиг если нет"""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        # Здесь можно добавить логику копирования шаблона
        print("⚠️ Файл config/config.yaml не найден. Создайте его вручную.")
    else:
        print("✅ Конфигурация найдена.")

if __name__ == "__main__":
    print("🚀 Инициализация LM-Studio-AGI-Core...")
    create_directory_structure()
    if check_dependencies():
        generate_default_config()
        print("\n🎉 Система готова к запуску!")
    else:
        sys.exit(1)