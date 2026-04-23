import sys
import shutil
from pathlib import Path

def apply_preset(preset_name):
    presets_dir = Path("config/presets")
    if not presets_dir.exists():
        print("❌ Папка пресетов не найдена")
        return

    preset_file = presets_dir / f"{preset_name}.yaml"
    if not preset_file.exists():
        print(f"❌ Пресет '{preset_name}' не найден")
        print("Доступные: coding, analysis, creative, quick")
        return

    target = Path("config/active_config.yaml")
    shutil.copy(preset_file, target)
    print(f"✅ Пресет '{preset_name}' применен!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python scripts/apply_preset.py <name>")
    else:
        apply_preset(sys.argv[1])