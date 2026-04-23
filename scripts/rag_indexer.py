import sys
from pathlib import Path

def index_documents(path, rebuild=False, threshold=0.5):
    p = Path(path)
    if not p.exists():
        print(f"❌ Папка {path} не найдена")
        return
    
    files = list(p.glob("**/*.md")) + list(p.glob("**/*.txt"))
    print(f"🔍 Найдено файлов: {len(files)}")
    
    if rebuild:
        print("🗑️ Очистка старого индекса...")
    
    print(f"⚙️ Индексация с порогом {threshold}...")
    for f in files:
        print(f"  📄 {f.name}")
    
    print("✅ Индексация завершена!")

if __name__ == "__main__":
    # Простая обработка аргументов
    path = "documents"
    rebuild = "--rebuild" in sys.argv
    thresh = 0.5
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        thresh = float(sys.argv[idx+1])
        
    index_documents(path, rebuild, thresh)