import sys
import platform
import importlib

def diagnose():
    print("🔍 Диагностика системы...")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    libs = ["requests", "pydantic", "chromadb", "yaml"]
    for lib in libs:
        try:
            if lib == "yaml": importlib.import_module("yaml")
            else: importlib.import_module(lib)
            print(f"✅ {lib}: OK")
        except ImportError:
            print(f"❌ {lib}: MISSING")

if __name__ == "__main__":
    diagnose()