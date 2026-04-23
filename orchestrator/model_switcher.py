# orchestrator/model_switcher.py
import requests
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("AGICore.Orchestrator")

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
        self.models_config = self.config.get('models', {})

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
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Получает конфигурацию модели из YAML"""
        return self.models_config.get(model_name, {})

    def load_model(self, model_name: str) -> bool:
        """Ленивая загрузка модели через LM Studio API"""
        logger.info(f"🔄 Loading model: {model_name}...")
        
        # Проверяем, есть ли модель в конфиге
        model_cfg = self.get_model_config(model_name)
        model_path = model_cfg.get('path', model_name)
        
        try:
            # Вызываем LM Studio API для загрузки модели
            endpoint = f"{self.lmstudio_url}/v1/models/load"
            payload = {
                "model": model_path,
                "context_length": model_cfg.get('context_length', 32768),
                "gpu_offload": model_cfg.get('gpu_offload', 100),
            }
            
            resp = requests.post(endpoint, json=payload, timeout=30)
            if resp.status_code == 200:
                logger.info(f"✅ Model {model_name} loaded successfully via API")
                self.loaded_models[model_name] = True
                self.active_model = model_name
                return True
            else:
                logger.warning(f"⚠️ LM Studio API returned {resp.status_code}, trying alternative method...")
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ LM Studio not reachable at {self.lmstudio_url}, using fallback mode")
        except Exception as e:
            logger.error(f"❌ Error loading model {model_name}: {e}")
        
        # Fallback: эмуляция для тестирования без LM Studio
        logger.info(f"📝 Using fallback mode for {model_name}")
        self.loaded_models[model_name] = True
        self.active_model = model_name
        return True

    def unload_all(self):
        """Выгружает все модели из памяти"""
        logger.info("🗑 Unloading all models...")
        try:
            endpoint = f"{self.lmstudio_url}/v1/models/unload"
            requests.post(endpoint, timeout=10)
        except:
            pass
        self.loaded_models.clear()
        self.active_model = None

    def send_request(self, prompt: str, model_name: Optional[str] = None, 
                     system_prompt: str = "", temperature: Optional[float] = None,
                     max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Отправляет запрос к модели через LM Studio API
        
        Args:
            prompt: Пользовательский запрос
            model_name: Имя модели (если None, используется active_model)
            system_prompt: Системный промпт
            temperature: Температура генерации
            max_tokens: Максимум токенов в ответе
            
        Returns:
            Dict с ответом от модели
        """
        if not model_name:
            model_name = self.active_model
        
        if not model_name:
            # Выбираем модель по умолчанию
            model_name = self.get_model_for_task("quick")
        
        model_cfg = self.get_model_config(model_name)
        
        # Используем параметры из конфига, если не переданы явно
        if temperature is None:
            temperature = model_cfg.get('temperature', 0.7)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_cfg.get('path', model_name),
            "messages": messages,
            "temperature": temperature,
            "top_p": model_cfg.get('top_p', 0.9),
            "max_tokens": max_tokens,
            "stream": False
        }
        
        logger.info(f"📤 Sending request to {model_name}...")
        
        try:
            endpoint = f"{self.lmstudio_url}/v1/chat/completions"
            resp = requests.post(endpoint, json=payload, timeout=60)
            
            if resp.status_code == 200:
                result = resp.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.info(f"✅ Received response from {model_name}")
                return {
                    "success": True,
                    "content": content,
                    "model": model_name,
                    "usage": result.get('usage', {}),
                    "raw_response": result
                }
            else:
                error_msg = f"LM Studio API error: {resp.status_code} - {resp.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "model": model_name
                }
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to LM Studio at {self.lmstudio_url}: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "model": model_name,
                "fallback_content": f"[Fallback Mode] Request would be sent to {model_name}. Prompt: {prompt[:100]}..."
            }
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "model": model_name
            }

    def get_status(self) -> Dict[str, Any]:
        """Получает статус оркестратора"""
        # Пытаемся получить реальную информацию от LM Studio
        vram_usage = "N/A"
        try:
            resp = requests.get(f"{self.lmstudio_url}/v1/system/info", timeout=5)
            if resp.status_code == 200:
                info = resp.json()
                vram_usage = info.get('gpu', {}).get('vram_used', 'N/A')
        except:
            pass
        
        return {
            "active_model": self.active_model,
            "loaded_count": len(self.loaded_models),
            "models": list(self.loaded_models.keys()),
            "vram_usage": vram_usage,
            "lmstudio_url": self.lmstudio_url
        }