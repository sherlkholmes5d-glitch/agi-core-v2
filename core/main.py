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
        :root {
            --bg-primary: #1e1e2e;
            --bg-secondary: #313244;
            --bg-tertiary: #45475a;
            --text-primary: #cdd6f4;
            --text-secondary: #a6adc8;
            --accent-blue: #89b4fa;
            --accent-green: #a6e3a1;
            --accent-red: #f38ba8;
            --accent-yellow: #f9e2af;
            --accent-orange: #fab387;
            --accent-purple: #cba6f7;
        }
        
        body { 
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; 
            background: var(--bg-primary); 
            color: var(--text-primary); 
            margin: 0; 
            padding: 20px; 
        }
        
        .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 20px; 
            padding-bottom: 15px;
            border-bottom: 2px solid var(--bg-tertiary);
        }
        
        .status-badge { 
            background: var(--accent-green); 
            color: var(--bg-primary); 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-weight: bold; 
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        
        .grid { 
            display: grid; 
            grid-template-columns: 280px 1fr 350px; 
            gap: 20px; 
            height: calc(100vh - 120px); 
        }
        
        .panel { 
            background: var(--bg-secondary); 
            border-radius: 12px; 
            padding: 20px; 
            overflow-y: auto; 
            border: 1px solid var(--bg-tertiary);
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        
        /* Blueprint-style Plugin Cards */
        .plugin-card { 
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, #585b70 100%);
            padding: 15px; 
            margin-bottom: 12px; 
            border-radius: 8px; 
            cursor: grab; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            border-left: 4px solid var(--accent-blue);
            position: relative;
            overflow: hidden;
        }
        
        .plugin-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 30%, rgba(137, 180, 250, 0.1) 50%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .plugin-card:hover::before {
            opacity: 1;
        }
        
        .plugin-card:hover { 
            transform: translateY(-3px) scale(1.02); 
            background: linear-gradient(135deg, #585b70 0%, #6c7086 100%);
            box-shadow: 0 8px 16px rgba(137, 180, 250, 0.2);
            border-left-color: var(--accent-green);
        }
        
        .plugin-card.dragging { 
            opacity: 0.6; 
            cursor: grabbing; 
            transform: rotate(3deg) scale(1.05);
        }
        
        .plugin-card .plugin-icon {
            font-size: 1.5em;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        .plugin-card .plugin-name {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .plugin-card .plugin-type {
            font-size: 0.8em;
            color: var(--text-secondary);
            margin-top: 4px;
        }
        
        /* Workspace Drop Zone */
        .drop-zone { 
            border: 3px dashed var(--bg-tertiary); 
            background: linear-gradient(135deg, #181825 0%, #1e1e2e 100%);
            min-height: 300px; 
            border-radius: 12px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            flex-direction: column; 
            padding: 30px; 
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .drop-zone::after {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 2px solid transparent;
            border-radius: 10px;
            transition: all 0.3s;
            pointer-events: none;
        }
        
        .drop-zone.dragover { 
            border-color: var(--accent-green); 
            background: linear-gradient(135deg, #1e2e20 0%, #181825 100%);
            transform: scale(1.02);
            box-shadow: 0 0 30px rgba(166, 227, 161, 0.2);
        }
        
        .drop-zone.dragover::after {
            border-color: var(--accent-green);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        /* Activated Plugin in Workspace */
        .workspace-plugin { 
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, #585b70 100%);
            padding: 16px; 
            margin: 10px; 
            border-radius: 10px; 
            cursor: pointer; 
            border-left: 5px solid var(--accent-blue);
            animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .workspace-plugin:hover { 
            background: linear-gradient(135deg, #585b70 0%, #6c7086 100%);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(137, 180, 250, 0.3);
        }
        
        .workspace-plugin .delete-btn { 
            position: absolute; 
            top: 8px; 
            right: 8px; 
            background: var(--accent-red); 
            color: var(--bg-primary); 
            border: none; 
            width: 24px; 
            height: 24px; 
            border-radius: 50%; 
            cursor: pointer; 
            font-weight: bold; 
            font-size: 16px; 
            line-height: 1; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            opacity: 0; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .workspace-plugin:hover .delete-btn { 
            opacity: 1; 
            transform: scale(1.1);
        }
        
        .workspace-plugin .delete-btn:hover { 
            background: #eba0ac; 
            transform: scale(1.2) rotate(90deg);
        }
        
        @keyframes slideIn { 
            from { 
                opacity: 0; 
                transform: translateX(-30px) scale(0.9); 
            } 
            to { 
                opacity: 1; 
                transform: translateX(0) scale(1); 
            } 
        }
        
        /* Enhanced Logs with Grouping */
        .log-group {
            margin-bottom: 15px;
            border: 1px solid var(--bg-tertiary);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .log-group-header {
            background: var(--bg-tertiary);
            padding: 10px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            transition: background 0.2s;
        }
        
        .log-group-header:hover {
            background: #585b70;
        }
        
        .log-group-content {
            max-height: 300px;
            overflow-y: auto;
            background: #181825;
        }
        
        .log-entry { 
            font-family: 'Consolas', 'Courier New', monospace; 
            font-size: 0.85em; 
            border-bottom: 1px solid var(--bg-tertiary); 
            padding: 8px 15px; 
            display: flex;
            align-items: flex-start;
        }
        
        .log-entry:last-child {
            border-bottom: none;
        }
        
        .log-entry .log-time {
            color: var(--text-secondary);
            margin-right: 10px;
            white-space: nowrap;
        }
        
        .log-entry .log-message {
            flex: 1;
        }
        
        .log-entry.info { color: var(--accent-blue); }
        .log-entry.warn { color: var(--accent-orange); background: rgba(250, 179, 135, 0.05); }
        .log-entry.error { color: var(--accent-red); background: rgba(243, 139, 168, 0.05); }
        .log-entry.success { color: var(--accent-green); background: rgba(166, 227, 161, 0.05); }
        
        .agent-active { color: var(--accent-green); font-weight: bold; }
        
        h2 { 
            margin-top: 0; 
            color: var(--accent-yellow); 
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metrics { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 12px; 
            margin-top: 20px; 
        }
        
        .metric-box { 
            background: linear-gradient(135deg, #181825 0%, #1e1e2e 100%);
            padding: 15px; 
            border-radius: 10px; 
            text-align: center;
            border: 1px solid var(--bg-tertiary);
            transition: transform 0.3s;
        }
        
        .metric-box:hover {
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }
        
        .metric-val { 
            font-size: 1.6em; 
            font-weight: bold; 
            color: var(--accent-purple);
            font-family: 'Consolas', monospace;
        }
        
        .metric-label {
            font-size: 0.85em;
            color: var(--text-secondary);
            margin-top: 5px;
        }
        
        .model-badge { 
            display: inline-block; 
            background: var(--accent-blue); 
            color: var(--bg-primary); 
            padding: 6px 12px; 
            border-radius: 6px; 
            font-size: 0.85em; 
            margin: 4px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .model-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(137, 180, 250, 0.4);
        }
        
        .btn { 
            background: linear-gradient(135deg, var(--accent-blue) 0%, #b4befe 100%);
            color: var(--bg-primary); 
            border: none; 
            padding: 10px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold; 
            margin: 5px;
            transition: all 0.3s;
            font-size: 0.9em;
        }
        
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(137, 180, 250, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-danger { 
            background: linear-gradient(135deg, var(--accent-red) 0%, #eba0ac 100%);
        }
        
        .btn-danger:hover { 
            box-shadow: 0 4px 12px rgba(243, 139, 168, 0.4);
        }
        
        /* Calendar Widget */
        .calendar-widget {
            margin-top: 20px;
            background: #181825;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid var(--bg-tertiary);
        }
        
        .calendar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-weight: 600;
            color: var(--accent-yellow);
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            text-align: center;
        }
        
        .calendar-day-name {
            font-size: 0.8em;
            color: var(--text-secondary);
            padding: 5px;
        }
        
        .calendar-day {
            padding: 8px;
            border-radius: 6px;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .calendar-day:hover {
            background: var(--bg-tertiary);
        }
        
        .calendar-day.today {
            background: var(--accent-blue);
            color: var(--bg-primary);
            font-weight: bold;
        }
        
        .calendar-day.has-event {
            border: 2px solid var(--accent-green);
        }
        
        /* Enhanced Task Graph */
        .graph-container {
            margin-top: 20px;
            background: #181825;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid var(--bg-tertiary);
            height: 250px;
        }
        
        .graph-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .graph-stats {
            display: flex;
            gap: 15px;
            font-size: 0.85em;
            color: var(--text-secondary);
        }
        
        .stat-value {
            color: var(--accent-green);
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 LM Studio AGI-Core <span style="font-size:0.6em; color:#9399b2;">| Visual Router (Blueprint Edition)</span></h1>
        <div id="connection-status" class="status-badge">⏳ Checking...</div>
    </div>

    <div class="grid">
        <!-- Панель плагинов -->
        <div class="panel">
            <h2>🧩 Plugins Library</h2>
            <div id="plugin-list">
                <div class="plugin-card" draggable="true" data-id="gdd_architect" data-type="generator">
                    <span class="plugin-icon">📝</span>
                    <span class="plugin-name">GDD Architect</span>
                    <div class="plugin-type">Game Design Document Generator</div>
                </div>
                <div class="plugin-card" draggable="true" data-id="vision_bridge" data-type="processor">
                    <span class="plugin-icon">👁️</span>
                    <span class="plugin-name">Vision Bridge</span>
                    <div class="plugin-type">Image Processing & Analysis</div>
                </div>
                <div class="plugin-card" draggable="true" data-id="internet_agent" data-type="agent">
                    <span class="plugin-icon">🌐</span>
                    <span class="plugin-name">Internet Agent</span>
                    <div class="plugin-type">Web Search & Data Collection</div>
                </div>
                <div class="plugin-card" draggable="true" data-id="auto_hotkey" data-type="automation">
                    <span class="plugin-icon">🎮</span>
                    <span class="plugin-name">AutoHotkey</span>
                    <div class="plugin-type">System Automation</div>
                </div>
                <div class="plugin-card" draggable="true" data-id="social_publisher" data-type="publisher">
                    <span class="plugin-icon">📢</span>
                    <span class="plugin-name">Social Publisher</span>
                    <div class="plugin-type">Content Distribution</div>
                </div>
                <div class="plugin-card" draggable="true" data-id="self_learning" data-type="learning">
                    <span class="plugin-icon">🧠</span>
                    <span class="plugin-name">Self Learning</span>
                    <div class="plugin-type">Adaptive Learning Module</div>
                </div>
            </div>

            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-val" id="vram-val">N/A</div>
                    <div class="metric-label">VRAM Used</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val" id="model-val" style="font-size: 0.8em;">None</div>
                    <div class="metric-label">Active Model</div>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <button class="btn" onclick="testConnection()">🔌 Test LM Studio</button>
                <button class="btn btn-danger" onclick="unloadModels()">🗑 Unload All</button>
            </div>
            
            <div class="calendar-widget">
                <div class="calendar-header">
                    <span id="calendar-month"></span>
                    <div>
                        <button class="btn" style="padding: 4px 8px; font-size: 0.8em;" onclick="prevMonth()">◀</button>
                        <button class="btn" style="padding: 4px 8px; font-size: 0.8em;" onclick="nextMonth()">▶</button>
                    </div>
                </div>
                <div class="calendar-grid" id="calendar-grid"></div>
            </div>
        </div>

        <!-- Рабочая область -->
        <div class="panel">
            <h2>⚡ Active Workspace</h2>
            <div id="workspace" class="drop-zone">
                <p style="color: #6c7086; text-align: center;">
                    <span style="font-size: 2em;">🎯</span><br>
                    Drag plugins here to activate<br>
                    <small>Click activated plugin to send test request<br>Double-click to deactivate</small>
                </p>
            </div>
            
            <div class="graph-container">
                <div class="graph-header">
                    <h3 style="margin: 0;">📊 Live Task Graph</h3>
                    <div class="graph-stats">
                        <span>Tasks: <span class="stat-value" id="task-count">0</span></span>
                        <span>Active: <span class="stat-value" id="active-count">0</span></span>
                    </div>
                </div>
                <canvas id="graphCanvas" width="100%" height="180" style="background:#1e1e2e; border-radius:8px;"></canvas>
            </div>
            
            <div style="margin-top: 20px;">
                <h3>📦 Loaded Models</h3>
                <div id="loaded-models" style="min-height: 40px; padding: 10px; background: #181825; border-radius: 8px;"></div>
            </div>
        </div>

        <!-- Логи -->
        <div class="panel">
            <h2>📜 System Logs</h2>
            <div id="log-container"></div>
        </div>
    </div>

    <script>
        // ============================================
        // CALENDAR WIDGET
        // ============================================
        let currentCalendarDate = new Date();
        
        function renderCalendar() {
            const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
            const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
            
            const year = currentCalendarDate.getFullYear();
            const month = currentCalendarDate.getMonth();
            
            document.getElementById('calendar-month').innerText = `${monthNames[month]} ${year}`;
            
            const grid = document.getElementById('calendar-grid');
            grid.innerHTML = '';
            
            // Дни недели
            dayNames.forEach(day => {
                const div = document.createElement('div');
                div.className = 'calendar-day-name';
                div.innerText = day;
                grid.appendChild(div);
            });
            
            // Первый день месяца
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const today = new Date();
            
            // Корректировка для понедельника (0 = Пн)
            let startDay = firstDay.getDay() - 1;
            if (startDay < 0) startDay = 6;
            
            // Пустые ячейки до первого дня
            for (let i = 0; i < startDay; i++) {
                const div = document.createElement('div');
                grid.appendChild(div);
            }
            
            // Дни месяца
            for (let day = 1; day <= lastDay.getDate(); day++) {
                const div = document.createElement('div');
                div.className = 'calendar-day';
                div.innerText = day;
                
                // Сегодняшний день
                if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                    div.classList.add('today');
                }
                
                // Пример событий (можно расширить)
                if (day % 7 === 0) {
                    div.classList.add('has-event');
                    div.title = 'Запланированная задача';
                }
                
                grid.appendChild(div);
            }
        }
        
        function prevMonth() {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() - 1);
            renderCalendar();
        }
        
        function nextMonth() {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() + 1);
            renderCalendar();
        }
        
        // ============================================
        // DRAG AND DROP LOGIC (Blueprint Style)
        // ============================================
        const draggables = document.querySelectorAll('.plugin-card');
        const dropZone = document.getElementById('workspace');
        let activePlugins = new Map(); // Используем Map для хранения данных о плагинах
        
        draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', (e) => {
                draggable.classList.add('dragging');
                const pluginData = {
                    id: draggable.dataset.id,
                    name: draggable.querySelector('.plugin-name').innerText,
                    type: draggable.dataset.type,
                    icon: draggable.querySelector('.plugin-icon').innerText
                };
                e.dataTransfer.setData('text/plain', JSON.stringify(pluginData));
                e.dataTransfer.effectAllowed = 'copy';
                
                // Визуальный эффект перетаскивания
                setTimeout(() => {
                    draggable.style.opacity = '0.5';
                }, 0);
            });
        
            draggable.addEventListener('dragend', () => {
                draggable.classList.remove('dragging');
                draggable.style.opacity = '1';
            });
        });
        
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', e => {
            // Проверяем, что уходим именно из drop-zone, а не внутрь неё
            if (!dropZone.contains(e.relatedTarget)) {
                dropZone.classList.remove('dragover');
            }
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
                    addLog('❌ Error parsing plugin data', 'error');
                }
            }
        });
        
        function addPluginToWorkspace(pluginData) {
            if (activePlugins.has(pluginData.id)) {
                addLog(`⚠️ Plugin "${pluginData.name}" already active!`, 'warn');
                // Анимация уже активного плагина
                const existingPlugin = document.querySelector(`.workspace-plugin[data-id="${pluginData.id}"]`);
                if (existingPlugin) {
                    existingPlugin.style.animation = 'none';
                    existingPlugin.offsetHeight; /* trigger reflow */
                    existingPlugin.style.animation = 'pulse 0.5s ease';
                }
                return;
            }
        
            const pluginEl = document.createElement('div');
            pluginEl.className = 'workspace-plugin';
            pluginEl.dataset.id = pluginData.id;
            pluginEl.innerHTML = `
                <button class="delete-btn" title="Remove plugin">×</button>
                <span style="font-size: 1.3em;">${pluginData.icon || '🔌'}</span>
                <strong style="margin-left: 8px;">${pluginData.name}</strong><br>
                <small style="color: #89b4fa; margin-left: 36px;">Type: ${pluginData.type}</small><br>
                <small style="color: #a6e3a1; margin-left: 36px;">● Active</small>
            `;
        
            // Обработчик кнопки удаления - ИСПРАВЛЕНО
            const deleteBtn = pluginEl.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Предотвращаем срабатывание клика по самому плагину
                e.preventDefault(); // Предотвращаем любые другие действия
                
                const pluginName = pluginData.name;
                if(confirm(`Remove "${pluginName}" from workspace?`)) {
                    // Анимация перед удалением
                    pluginEl.style.transition = 'all 0.3s ease';
                    pluginEl.style.transform = 'scale(0.8) translateX(100px)';
                    pluginEl.style.opacity = '0';
                    
                    setTimeout(() => {
                        pluginEl.remove();
                        activePlugins.delete(pluginData.id);
                        addLog(`🗑️ Plugin removed: ${pluginName}`, 'info');
                        updateGraphStats();
                        updateStatus(false);
                    }, 300);
                }
            });
        
            // Клик по плагину - тестовый запрос
            pluginEl.addEventListener('click', (e) => {
                // Игнорируем клик если это был клик по кнопке удаления
                if (e.target.classList.contains('delete-btn')) return;
                sendPluginTestRequest(pluginData.id, pluginData.name);
            });
            
            // Двойной клик - деактивация
            pluginEl.addEventListener('dblclick', (e) => {
                if (e.target.classList.contains('delete-btn')) return;
                deleteBtn.click();
            });
        
            dropZone.appendChild(pluginEl);
            activePlugins.set(pluginData.id, pluginData);
            addLog(`✅ Plugin activated: ${pluginData.name}`, 'success');
            updateGraphStats();
            updateStatus();
        }
        
        function sendPluginTestRequest(pluginId, pluginName) {
            addLog(`📤 Sending test request to ${pluginName}...`, 'info');
        
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
                    addLog(`✅ Plugin ${pluginName} responded successfully`, 'success');
                    if (data.message) {
                        addLog(`📝 Response: ${JSON.stringify(data.message).substring(0, 200)}`, 'info');
                    }
                } else {
                    addLog(`❌ Plugin ${pluginName} error: ${data.error}`, 'error');
                }
            })
            .catch(err => {
                addLog(`❌ Error calling plugin: ${err.message}`, 'error');
            });
        }
        
        // ============================================
        // ENHANCED LOGGING WITH GROUPING
        // ============================================
        let logGroups = {};
        let currentLogDate = null;
        
        function addLog(msg, type='info') {
            const container = document.getElementById('log-container');
            const now = new Date();
            const dateKey = now.toLocaleDateString();
            const timeStr = now.toLocaleTimeString();
            
            // Создаем новую группу для нового дня
            if (currentLogDate !== dateKey) {
                currentLogDate = dateKey;
                
                const groupHeader = document.createElement('div');
                groupHeader.className = 'log-group-header';
                groupHeader.innerHTML = `<span>📅 ${dateKey}</span><span>▼</span>`;
                groupHeader.onclick = function() {
                    const content = this.nextElementSibling;
                    content.style.maxHeight = content.style.maxHeight === '0px' ? '300px' : '0px';
                    this.querySelector('span:last-child').innerText = content.style.maxHeight === '0px' ? '▶' : '▼';
                };
                
                const groupContent = document.createElement('div');
                groupContent.className = 'log-group-content';
                
                container.insertBefore(groupHeader, container.firstChild);
                container.insertBefore(groupContent, groupHeader.nextSibling);
            }
            
            // Получаем последнюю группу
            const lastGroup = container.querySelector('.log-group-content:last-child');
            if (!lastGroup) return;
            
            const div = document.createElement('div');
            div.className = `log-entry ${type}`;
            div.innerHTML = `
                <span class="log-time">${timeStr}</span>
                <span class="log-message">${msg}</span>
            `;
            
            lastGroup.insertBefore(div, lastGroup.firstChild);
            
            // Автопрокрутка к новому сообщению
            lastGroup.scrollTop = 0;
            
            // Ограничиваем количество записей в группе
            while (lastGroup.children.length > 150) {
                lastGroup.removeChild(lastGroup.lastChild);
            }
        }
        
        // ============================================
        // STATUS POLLING - Оптимизировано: проверка раз в 60 секунд
        // ============================================
        let lastCheck = 0;
        async function updateStatus(force = false) {
            const now = Date.now();
            // Проверяем статус LM Studio только раз в минуту, если не форсировано
            if (!force && now - lastCheck < 60000) {
                return;
            }
            
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                lastCheck = now;
        
                const statusEl = document.getElementById('connection-status');
                if (data.lmstudio_connected) {
                    statusEl.innerText = "✅ LM Studio Connected";
                    statusEl.style.background = "var(--accent-green)";
                } else {
                    statusEl.innerText = "⚠️ LM Studio Offline";
                    statusEl.style.background = "var(--accent-orange)";
                }
        
                document.getElementById('vram-val').innerText = data.vram_usage || "N/A";
                
                const modelVal = document.getElementById('model-val');
                modelVal.innerText = data.active_model || "None";
                if (data.active_model && data.active_model !== "None") {
                    modelVal.style.color = "var(--accent-green)";
                } else {
                    modelVal.style.color = "var(--accent-purple)";
                }
        
                // Обновляем список загруженных моделей
                const modelsContainer = document.getElementById('loaded-models');
                if (data.loaded_models && data.loaded_models.length > 0) {
                    modelsContainer.innerHTML = data.loaded_models.map(m =>
                        `<span class="model-badge">📦 ${m}</span>`
                    ).join('');
                } else {
                    modelsContainer.innerHTML = '<small style="color: #6c7086;">No models loaded in LM Studio</small>';
                }
        
                if (!data.lmstudio_connected && force) {
                    addLog("⚠️ Warning: LM Studio not connected!", "warn");
                }
            } catch (e) {
                if (force) {
                    addLog(`❌ Status check error: ${e.message}`, 'error');
                }
            }
        }
        
        // ============================================
        // TEST CONNECTION
        // ============================================
        async function testConnection() {
            addLog('🔌 Testing LM Studio connection...', 'info');
            try {
                await updateStatus(true);
                const res = await fetch('/api/status');
                const data = await res.json();
                
                if (data.lmstudio_connected) {
                    addLog('✅ Successfully connected to LM Studio!', 'success');
                    
                    // Получаем список моделей напрямую из LM Studio
                    try {
                        const modelsRes = await fetch('http://127.0.0.1:1234/v1/models');
                        const modelsData = await modelsRes.json();
                        
                        if (modelsData.data && modelsData.data.length > 0) {
                            const modelNames = modelsData.data.map(m => m.id);
                            addLog(`📦 Available models in LM Studio: ${modelNames.length}`, 'info');
                            modelNames.slice(0, 5).forEach(name => {
                                addLog(`   • ${name}`, 'info');
                            });
                            if (modelNames.length > 5) {
                                addLog(`   ... and ${modelNames.length - 5} more`, 'info');
                            }
                        }
                    } catch (e) {
                        addLog('ℹ️ Could not fetch model list', 'warn');
                    }
                    
                    if (data.loaded_models && data.loaded_models.length > 0) {
                        addLog(`📦 Currently loaded: ${data.loaded_models.join(', ')}`, 'info');
                    } else {
                        addLog('ℹ️ No models currently loaded in memory', 'info');
                    }
                } else {
                    addLog('⚠️ LM Studio is not running or unreachable', 'warn');
                    addLog('💡 Please start LM Studio server on port 1234', 'warn');
                }
            } catch (e) {
                addLog(`❌ Connection test failed: ${e.message}`, 'error');
            }
        }
        
        // ============================================
        // UNLOAD MODELS
        // ============================================
        async function unloadModels() {
            if(!confirm('Unload all models from LM Studio memory?')) return;
        
            addLog('🗑️ Unloading all models...', 'info');
            try {
                const res = await fetch('/api/unload-models', { method: 'POST' });
                const data = await res.json();
                
                if (data.success) {
                    addLog('✅ All models unloaded successfully', 'success');
                    await updateStatus(true);
                } else {
                    addLog(`❌ Error: ${data.error}`, 'error');
                }
            } catch (e) {
                addLog(`❌ Unload error: ${e.message}`, 'error');
            }
        }
        
        // ============================================
        // GRAPH STATS & ANIMATION
        // ============================================
        function updateGraphStats() {
            const count = activePlugins.size;
            document.getElementById('task-count').innerText = count;
            document.getElementById('active-count').innerText = count;
        }
        
        const canvas = document.getElementById('graphCanvas');
        const ctx = canvas.getContext('2d');
        
        // Устанавливаем правильный размер canvas
        function resizeCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width - 30;
            canvas.height = 180;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        let offset = 0;
        let nodes = [];
        
        // Создаем узлы для графа
        function initNodes() {
            nodes = [];
            const nodeCount = 8;
            for (let i = 0; i < nodeCount; i++) {
                nodes.push({
                    x: (canvas.width / (nodeCount + 1)) * (i + 1),
                    y: canvas.height / 2 + (Math.random() - 0.5) * 40,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5
                });
            }
        }
        initNodes();
        
        function drawGraph() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Рисуем связи
            ctx.strokeStyle = 'rgba(137, 180, 250, 0.3)';
            ctx.lineWidth = 1;
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[i].x - nodes[j].x;
                    const dy = nodes[i].y - nodes[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 100) {
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.stroke();
                    }
                }
            }
            
            // Рисуем волны
            ctx.strokeStyle = '#89b4fa';
            ctx.lineWidth = 2;
            ctx.beginPath();
            for(let i = 0; i <= canvas.width; i += 5) {
                const y = canvas.height / 2 + Math.sin((i + offset) / 30) * 30 + 
                          Math.sin((i + offset * 1.5) / 50) * 15;
                if (i === 0) {
                    ctx.moveTo(i, y);
                } else {
                    ctx.lineTo(i, y);
                }
            }
            ctx.stroke();
            
            // Рисуем узлы
            nodes.forEach(node => {
                node.x += node.vx;
                node.y += node.vy;
                
                // Отталкивание от границ
                if (node.x < 20 || node.x > canvas.width - 20) node.vx *= -1;
                if (node.y < 20 || node.y > canvas.height - 20) node.vy *= -1;
                
                // Свечение
                const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, 12);
                gradient.addColorStop(0, 'rgba(137, 180, 250, 0.8)');
                gradient.addColorStop(1, 'rgba(137, 180, 250, 0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(node.x, node.y, 12, 0, Math.PI * 2);
                ctx.fill();
                
                // Ядро узла
                ctx.fillStyle = '#89b4fa';
                ctx.beginPath();
                ctx.arc(node.x, node.y, 4, 0, Math.PI * 2);
                ctx.fill();
            });
            
            offset += 1.5;
            requestAnimationFrame(drawGraph);
        }
        drawGraph();
        
        // ============================================
        // INITIALIZATION
        // ============================================
        // Рендерим календарь
        renderCalendar();
        
        // Обновляем статус при загрузке
        updateStatus(true);
        
        // Периодическое обновление (UI каждые 5 сек, реальный запрос раз в минуту)
        setInterval(() => {
            updateStatus(false);
        }, 5000);
        
        addLog('🚀 Visual Router initialized', 'success');
        addLog('📅 Calendar ready', 'info');
        addLog('🎯 Drag plugins to workspace to activate', 'info');
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
                    try:
                        self.wfile.write(json.dumps(status).encode())
                    except (ConnectionAbortedError, BrokenPipeError):
                        # Игнорируем ошибки разорванного соединения при закрытии браузера
                        pass
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
                elif self.path == '/api/unload-models':
                    # Обработка запроса на выгрузку всех моделей
                    self.handle_unload_models()
                    return
                return super().do_POST()

            def handle_unload_models(self):
                """Выгружает все модели через оркестратор"""
                try:
                    if self.server.core.orchestrator:
                        self.server.core.orchestrator.unload_all()
                        response = {
                            "success": True,
                            "message": "All models unloaded successfully"
                        }
                        logger.info("✅ All models unloaded via API")
                    else:
                        response = {
                            "success": False,
                            "error": "Orchestrator not initialized"
                        }
                        logger.warning("⚠️ Cannot unload models: orchestrator not available")
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    try:
                        self.wfile.write(json.dumps(response).encode())
                    except (ConnectionAbortedError, BrokenPipeError):
                        pass
                except Exception as e:
                    logger.error(f"❌ Error unloading models: {e}")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    try:
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                    except (ConnectionAbortedError, BrokenPipeError):
                        pass

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
