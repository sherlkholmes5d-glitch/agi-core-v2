# core/main.py
import asyncio
import logging
import os
import sys
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import json
import yaml

# Импорт наших модулей
try:
    from orchestrator.model_switcher import ModelOrchestrator
except ImportError:
    print("⚠️ Warning: Could not import ModelOrchestrator. Running in safe mode.")
    ModelOrchestrator = None

# Настройка путей
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
LOGS_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "static" # Папка для HTML/JS

# Создаем папки если нет
LOGS_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AGICore")

class AGICore:
    def __init__(self):
        logger.info("🚀 Initializing AGI Core...")
        
        # Загрузка конфига
        if not CONFIG_PATH.exists():
            logger.error(f"❌ Config file not found at {CONFIG_PATH}")
            logger.info("💡 Run 'python scripts/init_config.py' first!")
            sys.exit(1)
            
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        logger.info(f"✅ Configuration loaded from {CONFIG_PATH}")
        
        # Инициализация оркестратора (исправленная версия)
        if ModelOrchestrator:
            try:
                # Передаем ПУТЬ, а не dict
                self.orchestrator = ModelOrchestrator(str(CONFIG_PATH))
                logger.info("🤖 Orchestrator initialized")
            except Exception as e:
                logger.error(f"❌ Orchestrator failed: {e}")
                self.orchestrator = None
        else:
            self.orchestrator = None
            
        self.is_running = True
        self.active_agents = []
        self.task_log = []

    def check_lm_studio(self):
        """Проверка подключения к LM Studio"""
        import requests
        url = self.config.get('server', {}).get('url', 'http://127.0.0.1:1234')
        try:
            resp = requests.get(f"{url}/v1/models", timeout=2)
            if resp.status_code == 200:
                logger.info(f"✅ LM Studio connected at {url}")
                return True
        except:
            pass
        logger.warning(f"⚠️ LM Studio not detected at {url}. Please start LM Studio Server.")
        return False

    def generate_html(self):
        """Генерирует HTML для Visual Router"""
        html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>LM Studio AGI-Core | Visual Router</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .status-badge { background: #a6e3a1; color: #1e1e2e; padding: 5px 10px; border-radius: 12px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: 250px 1fr 300px; gap: 20px; height: calc(100vh - 100px); }
        .panel { background: #313244; border-radius: 12px; padding: 15px; overflow-y: auto; border: 1px solid #45475a; }
        .plugin-card { background: #45475a; padding: 10px; margin-bottom: 10px; border-radius: 8px; cursor: grab; transition: transform 0.2s; }
        .plugin-card:hover { transform: translateY(-2px); background: #585b70; }
        .drop-zone { border: 2px dashed #89b4fa; background: #181825; min-height: 200px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
        .drop-zone.dragover { border-color: #a6e3a1; background: #1e2e20; }
        .log-entry { font-family: monospace; font-size: 0.9em; border-bottom: 1px solid #45475a; padding: 5px 0; }
        .log-entry.info { color: #89b4fa; }
        .log-entry.warn { color: #fab387; }
        .agent-active { color: #a6e3a1; font-weight: bold; }
        h2 { margin-top: 0; color: #f9e2af; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
        .metric-box { background: #181825; padding: 10px; border-radius: 8px; text-align: center; }
        .metric-val { font-size: 1.5em; font-weight: bold; color: #cba6f7; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 LM Studio AGI-Core <span style="font-size:0.6em; color:#9399b2;">Visual Router</span></h1>
        <div id="connection-status" class="status-badge">Checking...</div>
    </div>

    <div class="grid">
        <!-- Панель плагинов -->
        <div class="panel">
            <h2>🧩 Plugins (Drag & Drop)</h2>
            <div id="plugin-list">
                <div class="plugin-card" draggable="true" data-id="gdd_architect">📝 GDD Architect</div>
                <div class="plugin-card" draggable="true" data-id="vision_bridge">👁️ Vision Bridge</div>
                <div class="plugin-card" draggable="true" data-id="internet_agent">🌐 Internet Agent</div>
                <div class="plugin-card" draggable="true" data-id="auto_hotkey">🎮 AutoHotkey</div>
                <div class="plugin-card" draggable="true" data-id="social_publisher">📢 Social Publisher</div>
                <div class="plugin-card" draggable="true" data-id="self_learning">🧠 Self Learning</div>
            </div>
            
            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-val" id="vram-val">0%</div>
                    <div>VRAM Used</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val" id="model-val">None</div>
                    <div>Active Model</div>
                </div>
            </div>
        </div>

        <!-- Рабочая область -->
        <div class="panel">
            <h2>⚡ Active Workspace</h2>
            <div id="workspace" class="drop-zone">
                <p>Drag plugins here to activate</p>
            </div>
            <div style="margin-top: 20px;">
                <h3>📊 Live Task Graph</h3>
                <canvas id="graphCanvas" width="100%" height="200" style="background:#181825; border-radius:8px;"></canvas>
            </div>
        </div>

        <!-- Логи -->
        <div class="panel">
            <h2>📜 System Logs</h2>
            <div id="log-container"></div>
        </div>
    </div>

    <script>
        // Drag and Drop Logic
        const draggables = document.querySelectorAll('.plugin-card');
        const dropZone = document.getElementById('workspace');

        draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', () => {
                draggable.classList.add('dragging');
            });
            draggable.addEventListener('dragend', () => {
                draggable.classList.remove('dragging');
            });
        });

        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const draggable = document.querySelector('.dragging');
            if (draggable) {
                const clone = draggable.cloneNode(true);
                clone.classList.remove('dragging');
                clone.style.cursor = 'default';
                clone.addEventListener('click', () => {
                    if(confirm(`Deactivate ${clone.innerText}?`)) {
                        clone.remove();
                        updateStatus();
                    }
                });
                dropZone.appendChild(clone);
                
                // Add log entry
                addLog(`Plugin activated: ${clone.innerText}`, 'info');
                updateStatus();
            }
        });

        // Logging
        function addLog(msg, type='info') {
            const container = document.getElementById('log-container');
            const div = document.createElement('div');
            div.className = `log-entry ${type}`;
            div.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
            container.prepend(div);
            if (container.children.length > 50) container.lastChild.remove();
        }

        // Status Polling
        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                
                document.getElementById('connection-status').innerText = data.lmstudio_connected ? "✅ LM Studio Connected" : "⚠️ LM Studio Offline";
                document.getElementById('connection-status').style.background = data.lmstudio_connected ? "#a6e3a1" : "#fab387";
                
                document.getElementById('vram-val').innerText = data.vram_usage || "N/A";
                document.getElementById('model-val').innerText = data.active_model || "None";
                
                if (!data.lmstudio_connected) {
                    addLog("Warning: LM Studio not connected!", "warn");
                }
            } catch (e) {
                console.error(e);
            }
        }

        setInterval(updateStatus, 2000);
        updateStatus();
        
        // Fake Graph Animation
        const canvas = document.getElementById('graphCanvas');
        const ctx = canvas.getContext('2d');
        let offset = 0;
        function drawGraph() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#89b4fa';
            ctx.lineWidth = 2;
            ctx.beginPath();
            for(let i=0; i<canvas.width; i+=10) {
                ctx.lineTo(i, 50 + Math.sin((i+offset)/20)*20);
            }
            ctx.stroke();
            offset += 2;
            requestAnimationFrame(drawGraph);
        }
        drawGraph();
    </script>
</body>
</html>
        """
        return html_content

    def start_web_server(self):
        """Запускает локальный веб-сервер для интерфейса"""
        
        # Сохраняем HTML в статическую папку
        html_path = STATIC_DIR / "index.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_html())
            
        class RequestHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(STATIC_DIR), **kwargs)
            
            def do_GET(self):
                if self.path == '/':
                    self.path = '/index.html'
                elif self.path == '/api/status':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    status = {
                        "lmstudio_connected": self.server.core.check_lm_studio(),
                        "active_model": self.server.core.orchestrator.active_model if self.server.core.orchestrator else "None",
                        "vram_usage": "12.4 GB" if self.server.core.orchestrator else "N/A", # Эмуляция
                        "agents": self.server.core.active_agents
                    }
                    self.wfile.write(json.dumps(status).encode())
                    return
                return super().do_GET()

        server_address = ('127.0.0.1', 8080)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.core = self # Передаем ссылку на ядро
        
        url = "http://localhost:8080"
        logger.info(f"🌐 Visual Router available at {url}")
        webbrowser.open(url)
        
        # Запуск в отдельном потоке
        thread = Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

    def run_simulation_loop(self):
        """Основной цикл (теперь фоновый)"""
        logger.info("🔄 Entering background task loop...")
        while self.is_running:
            # Здесь должна быть реальная логика ожидания задач
            # Пока просто спим, чтобы не грузить CPU
            asyncio.run(asyncio.sleep(5))

def main():
    try:
        core = AGICore()
        core.check_lm_studio()
        core.start_web_server()
        
        logger.info("✅ System Ready. Interface opened in browser.")
        logger.info("Press Ctrl+C to stop.")
        
        # Запускаем цикл в фоне, не блокируя ввод полностью, но держа процесс живым
        core.run_simulation_loop()
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
        if hasattr(core, 'is_running'):
            core.is_running = False
    except Exception as e:
        logger.error(f"💥 Critical Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()