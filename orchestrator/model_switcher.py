# orchestrator/model_switcher.py
import requests
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ModelOrchestrator:
    def __init__(self, config_source):
        """
        Принимает либо путь к файлу (str), либо готовый dict конфига.
        """
        if isinstance(config_source, dict):
            self.config = config_source
            self.config_path = "config/config.yaml" # Для логирования
        else:
            self.config_path = config_source
            self.config = self._load_config()
        
        self.active_model = None
        self.loaded_models = {}
        self.lmstudio_url = self.config.get('server', {}).get('url', 'http://127.0.0.1:1234')

    def _load_config(self) -> Dict[str, Any]:
        if not Path(self.config_path).exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_model_for_task(self, task_type: str) -> str:
        """Выбирает модель на основе типа задачи"""
        routing = self.config.get('orchestrator', {}).get('task_routing', {})
        model_name = routing.get(task_type, routing.get('default', 'llama_3_2_3b'))
        
        if model_name not in self.loaded_models:
            self.load_model(model_name)
            
        return model_name

    def load_model(self, model_name: str):
        """Ленивая загрузка модели через LM Studio API"""
        print(f"🔄 Loading model: {model_name}...")
        
        # В реальной реализации здесь будет вызов API LM Studio для загрузки
        # Сейчас просто эмулируем
        self.loaded_models[model_name] = True
        self.active_model = model_name
        print(f"✅ Model {model_name} loaded successfully.")

    def unload_all(self):
        """Выгружает все модели из памяти"""
        print("🗑 Unloading all models...")
        self.loaded_models.clear()
        self.active_model = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_model": self.active_model,
            "loaded_count": len(self.loaded_models),
            "models": list(self.loaded_models.keys())
        }