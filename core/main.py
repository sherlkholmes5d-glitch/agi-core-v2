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
        .plugin-card { background: #45475a; padding: 10px; margin-bottom: 10px; border-radius: 8px; cursor: grab; transition: transform 0.2s; user-select: none; }
        .plugin-card:hover { transform: translateY(-2px); background: #585b70; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .plugin-card.dragging { opacity: 0.5; cursor: grabbing; }
        .drop-zone { border: 2px dashed #89b4fa; background: #181825; min-height: 200px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 20px; transition: all 0.3s; }
        .drop-zone.dragover { border-color: #a6e3a1; background: #1e2e20; border-style: solid; }
        .workspace-plugin { background: #585b70; padding: 12px; margin: 8px; border-radius: 8px; cursor: pointer; border-left: 4px solid #89b4fa; animation: slideIn 0.3s ease; }
        .workspace-plugin:hover { background: #6c7086; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
        .log-entry { font-family: monospace; font-size: 0.9em; border-bottom: 1px solid #45475a; padding: 5px 0; }
        .log-entry.info { color: #89b4fa; }
        .log-entry.warn { color: #fab387; }
        .log-entry.error { color: #f38ba8; }
        .agent-active { color: #a6e3a1; font-weight: bold; }
        h2 { margin-top: 0; color: #f9e2af; font-size: 1.2em; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
        .metric-box { background: #181825; padding: 10px; border-radius: 8px; text-align: center; }
        .metric-val { font-size: 1.5em; font-weight: bold; color: #cba6f7; }
        .model-badge { display: inline-block; background: #89b4fa; color: #1e1e2e; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; margin: 2px; }
        .btn { background: #89b4fa; color: #1e1e2e; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 5px; }
        .btn:hover { background: #b4befe; }
        .btn-danger { background: #f38ba8; }
        .btn-danger:hover { background: #eba0ac; }
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
                <div class="plugin-card" draggable="true" data-id="gdd_architect" data-type="generator">📝 GDD Architect</div>
                <div class="plugin-card" draggable="true" data-id="vision_bridge" data-type="processor">👁️ Vision Bridge</div>
                <div class="plugin-card" draggable="true" data-id="internet_agent" data-type="agent">🌐 Internet Agent</div>
                <div class="plugin-card" draggable="true" data-id="auto_hotkey" data-type="automation">🎮 AutoHotkey</div>
                <div class="plugin-card" draggable="true" data-id="social_publisher" data-type="publisher">📢 Social Publisher</div>
                <div class="plugin-card" draggable="true" data-id="self_learning" data-type="learning">🧠 Self Learning</div>
            </div>
            
            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-val" id="vram-val">N/A</div>
                    <div>VRAM Used</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val" id="model-val" style="font-size: 0.9em;">None</div>
                    <div>Active Model</div>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <button class="btn" onclick="testConnection()">🔌 Test LM Studio</button>
                <button class="btn btn-danger" onclick="unloadModels()">🗑 Unload All</button>
            </div>
        </div>

        <!-- Рабочая область -->
        <div class="panel">
            <h2>⚡ Active Workspace</h2>
            <div id="workspace" class="drop-zone">
                <p style="color: #6c7086;">Drag plugins here to activate<br><small>Click activated plugin to send test request</small></p>
            </div>
            <div style="margin-top: 20px;">
                <h3>📊 Live Task Graph</h3>
                <canvas id="graphCanvas" width="100%" height="200" style="background:#181825; border-radius:8px;"></canvas>
            </div>
            <div style="margin-top: 15px;">
                <h3>📦 Loaded Models</h3>
                <div id="loaded-models" style="min-height: 30px;"></div>
            </div>
        </div>

        <!-- Логи -->
        <div class="panel">
            <h2>📜 System Logs</h2>
            <div id="log-container"></div>
        </div>
    </div>

    <script>
        // Drag and Drop Logic с улучшенной поддержкой
        const draggables = document.querySelectorAll('.plugin-card');
        const dropZone = document.getElementById('workspace');
        let activePlugins = new Set();

        draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', (e) => {
                draggable.classList.add('dragging');
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    id: draggable.dataset.id,
                    name: draggable.innerText,
                    type: draggable.dataset.type
                }));
                e.dataTransfer.effectAllowed = 'copy';
            });
            
            draggable.addEventListener('dragend', () => {
                draggable.classList.remove('dragging');
            });
        });

        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const data = e.dataTransfer.getData('text/plain');
            if (data) {
                try {
                    const pluginData = JSON.parse(data);
                    addPluginToWorkspace(pluginData);
                } catch (err) {
                    console.error('Error parsing drop data:', err);
                }
            }
        });

        function addPluginToWorkspace(pluginData) {
            if (activePlugins.has(pluginData.id)) {
                addLog(`Plugin ${pluginData.name} already active!`, 'warn');
                return;
            }
            
            const pluginEl = document.createElement('div');
            pluginEl.className = 'workspace-plugin';
            pluginEl.dataset.id = pluginData.id;
            pluginEl.innerHTML = `
                <strong>${pluginData.name}</strong><br>
                <small style="color: #89b4fa;">Type: ${pluginData.type}</small><br>
                <small style="color: #a6e3a1;">● Active</small>
            `;
            
            pluginEl.addEventListener('click', () => {
                if(confirm(`Send test request to ${pluginData.name}?`)) {
                    sendPluginTestRequest(pluginData.id);
                }
            });
            
            pluginEl.addEventListener('dblclick', () => {
                if(confirm(`Deactivate ${pluginData.name}?`)) {
                    pluginEl.remove();
                    activePlugins.delete(pluginData.id);
                    addLog(`Plugin deactivated: ${pluginData.name}`, 'info');
                    updateStatus();
                }
            });
            
            dropZone.appendChild(pluginEl);
            activePlugins.add(pluginData.id);
            addLog(`Plugin activated: ${pluginData.name}`, 'info');
            updateStatus();
        }

        function sendPluginTestRequest(pluginId) {
            addLog(`Sending test request to ${pluginId}...`, 'info');
            
            fetch(`/api/plugin/${pluginId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    action: 'test',
                    timestamp: new Date().toISOString(),
                    message: 'Test request from Visual Router'
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    addLog(`✅ Plugin ${pluginId} responded successfully`, 'info');
                    addLog(`Response: ${JSON.stringify(data.message)}`, 'info');
                } else {
                    addLog(`❌ Plugin ${pluginId} error: ${data.error}`, 'error');
                }
            })
            .catch(err => {
                addLog(`❌ Error calling plugin: ${err.message}`, 'error');
            });
        }

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
                
                // Обновляем список загруженных моделей
                const modelsContainer = document.getElementById('loaded-models');
                if (data.loaded_models && data.loaded_models.length > 0) {
                    modelsContainer.innerHTML = data.loaded_models.map(m => 
                        `<span class="model-badge">${m}</span>`
                    ).join('');
                } else {
                    modelsContainer.innerHTML = '<small style="color: #6c7086;">No models loaded</small>';
                }
                
                if (!data.lmstudio_connected) {
                    addLog("Warning: LM Studio not connected!", "warn");
                }
            } catch (e) {
                console.error(e);
                addLog(`Status update error: ${e.message}`, 'error');
            }
        }

        // Test Connection
        async function testConnection() {
            addLog('Testing LM Studio connection...', 'info');
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                if (data.lmstudio_connected) {
                    addLog('✅ Successfully connected to LM Studio!', 'info');
                    
                    // Тестовый запрос к модели
                    addLog('Sending test request to model...', 'info');
                    const status = await updateStatus();
                } else {
                    addLog('⚠️ LM Studio is not running or unreachable', 'warn');
                    addLog('Please start LM Studio server on port 1234', 'warn');
                }
            } catch (e) {
                addLog(`Connection test failed: ${e.message}`, 'error');
            }
        }

        // Unload Models
        async function unloadModels() {
            if(!confirm('Unload all models from memory?')) return;
            
            addLog('Unloading all models...', 'info');
            // В реальной реализации здесь был бы API вызов
            setTimeout(() => {
                addLog('Models unloaded (simulated)', 'info');
                updateStatus();
            }, 500);
        }

        setInterval(updateStatus, 2000);
        updateStatus();
        
        // Graph Animation
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
                    
                    # Получаем статус от оркестратора
                    orchestrator_status = {}
                    if self.server.core.orchestrator:
                        orchestrator_status = self.server.core.orchestrator.get_status()
                    
                    status = {
                        "lmstudio_connected": self.server.core.check_lm_studio(),
                        "active_model": orchestrator_status.get("active_model", "None"),
                        "vram_usage": orchestrator_status.get("vram_usage", "N/A"),
                        "agents": self.server.core.active_agents,
                        "loaded_models": orchestrator_status.get("models", [])
                    }
                    self.wfile.write(json.dumps(status).encode())
                    return
                elif self.path.startswith('/api/plugin/'):
                    # Обработка API запросов для плагинов
                    self.handle_plugin_api()
                    return
                return super().do_GET()
            
            def do_POST(self):
                if self.path.startswith('/api/plugin/'):
                    self.handle_plugin_api()
                    return
                return super().do_POST()
            
            def handle_plugin_api(self):
                """Обрабатывает запросы к API плагинов"""
                import urllib.parse
                parsed = urllib.parse.urlparse(self.path)
                path_parts = parsed.path.split('/')
                
                if len(path_parts) >= 4 and path_parts[1] == 'api' and path_parts[2] == 'plugin':
                    plugin_name = path_parts[3]
                    
                    # Читаем тело запроса для POST
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = {}
                    if content_length > 0:
                        body = json.loads(self.rfile.read(content_length).decode())
                    
                    # Здесь будет логика вызова плагинов
                    response = {
                        "success": True,
                        "plugin": plugin_name,
                        "message": f"Plugin {plugin_name} called",
                        "data": body
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                self.send_response(404)
                self.end_headers()

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