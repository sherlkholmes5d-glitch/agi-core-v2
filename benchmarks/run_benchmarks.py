import time
import random

def run_benchmark(model_name, tokens=100):
    print(f"🏁 Запуск бенчмарка для {model_name}...")
    # Эмуляция замера
    start = time.time()
    time.sleep(random.uniform(1.0, 3.0)) # Имитация генерации
    end = time.time()
    
    tps = tokens / (end - start)
    print(f"✅ {model_name}: {tps:.2f} tokens/sec")
    return tps

if __name__ == "__main__":
    models = ["llama_3_2_3b", "deepseek_coder_v2", "qwen_35b"]
    for m in models:
        run_benchmark(m)