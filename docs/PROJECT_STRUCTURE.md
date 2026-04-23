# 🚀 LM Studio AGI-Core - Project Structure

## Directory Overview

```
lmstudio-agi-core/
├── README.md                 # Main documentation (you are here)
├── requirements.txt          # Python dependencies
├── config/
│   └── config.yaml          # Main configuration file
├── core/
│   └── main.py              # Main entry point and orchestrator
├── agents/
│   ├── __init__.py
│   ├── base_agent.py        # Base agent class
│   ├── coding_agent.py      # Code generation specialist
│   ├── research_agent.py    # Web research and analysis
│   └── creative_agent.py    # Creative writing and marketing
├── plugins/
│   ├── __init__.py
│   ├── gdd_architect.py     # Game Design Document generator
│   ├── vision_bridge.py     # Image/video analysis
│   ├── internet_agent.py    # Web browsing with visualization
│   ├── auto_hotkey.py       # Input emulation module
│   ├── social_publisher.py  # Auto-posting to social media
│   └── self_learning.py     # RLHF and fine-tuning pipeline
├── scripts/
│   ├── init_config.py       # Initial setup script
│   ├── apply_preset.py      # Apply task-specific presets
│   ├── run_benchmarks.py    # Model benchmarking
│   └── context_optimizer.py # Adaptive context length optimizer
├── docs/
│   ├── architecture.md      # Detailed architecture docs
│   ├── api_reference.md     # API documentation
│   └── plugin_guide.md      # Plugin development guide
├── logs/
│   └── app.log              # Application logs
├── data/
│   ├── vector_index/        # ChromaDB vector store
│   ├── models/              # Cached model files
│   └── long_term_memory.db  # SQLite long-term memory
└── output/
    ├── reports/             # Generated reports (Markdown, PDF)
    ├── canvas/              # Obsidian Canvas files
    └── gdd/                 # Generated Game Design Documents
```

## Key Components

### 🔹 Core (`core/main.py`)
Main orchestration engine that:
- Loads configuration
- Manages model switching
- Coordinates agents and plugins
- Handles task decomposition and execution
- Records interactions for self-learning

### 🔹 Configuration (`config/config.yaml`)
Centralized configuration for:
- Model profiles (Llama, DeepSeek, Qwen, Mixtral, LLaVA)
- Memory management (VRAM/RAM limits, KV cache)
- RAG settings (ChromaDB + SQLite)
- Orchestrator strategy and task routing
- Plugin management
- Monitoring and features

### 🔹 Plugins System
Modular plugin architecture with hot-reload support:

**Available Plugins:**
- `gdd_architect` - Complete GDD generation
- `vision_bridge` - Image/video analysis via LLaVA
- `internet_agent` - Safe web browsing with step visualization
- `auto_hotkey` - Mouse/keyboard emulation for games and automation
- `social_publisher` - Automated content posting
- `self_learning` - Continuous improvement via RLHF

**Plugin Interface:**
```python
class BasePlugin:
    async def execute(self, task: str, params: dict) -> dict
    async def initialize(self) -> bool
    async def shutdown(self) -> bool
```

### 🔹 RAG v2 System
Two-tier memory architecture:
- **Fast Layer**: ChromaDB for vector similarity search
- **Deep Layer**: SQLite with graph relationships for structured knowledge
- **Features**: Context injection, memory summarization, semantic retrieval

### 🔹 Visual Router
Real-time monitoring dashboard showing:
- Active agents and their status
- Data flow between components
- Resource usage (VRAM/RAM/CPU)
- Task queue and progress
- Live interaction logs

### 🔹 Operating Modes
- **Normal Mode**: Full functionality with all models
- **Black Mode**: Minimal resource usage with small models only
- **Visual Mode**: Enhanced monitoring and debugging

## Quick Start Commands

```bash
# Initialize the project
python scripts/init_config.py

# Run the core system
python core/main.py

# Apply a specific preset
python scripts/apply_preset.py coding

# Run benchmarks
python scripts/run_benchmarks.py --all

# Generate a GDD
python -c "from plugins.gdd_architect import GDDArchitectPlugin; import asyncio; asyncio.run(GDDArchitectPlugin(None).execute('Cyberpunk RPG with crafting'))"
```

## Development Workflow

1. **Clone and Setup**
   ```bash
   git clone <repo-url>
   cd lmstudio-agi-core
   pip install -r requirements.txt
   ```

2. **Configure**
   Edit `config/config.yaml` for your hardware

3. **Start LM Studio Server**
   ```bash
   lmstudio serve --port 1234
   ```

4. **Run AGI-Core**
   ```bash
   python core/main.py
   ```

5. **Develop Plugins**
   - Create new plugin in `plugins/` directory
   - Implement `BasePlugin` interface
   - Add to `config.yaml` enabled plugins list
   - Hot-reload or restart to activate

## Architecture Principles

- **Modularity**: Every feature is a plugin
- **Locality First**: All processing happens on your machine
- **SSoT (Single Source of Truth)**: Deterministic prompting over external randomness
- **Lightweight**: Rust-based orchestrator for performance
- **Observable**: Full visibility into agent actions
- **Extensible**: Easy to add new models, tools, and capabilities

## License

MIT License - Use freely, modify, and contribute back!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

**Built with ❤️ by the AGI-Core Team**
