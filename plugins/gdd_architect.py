"""
GDD Architect Plugin - Game Design Document Generator
Generates comprehensive game design documents with all aspects of game development
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class GDDArchitectPlugin:
    """Plugin for creating full-featured Game Design Documents"""
    
    def __init__(self, core):
        self.core = core
        self.name = "gdd_architect"
        self.version = "1.0.0"
        self.description = "Generates comprehensive GDDs with mechanics, balance, lore, and more"
        self.output_dir = Path("output/gdd")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_gdd(self, concept: str, style: str = "detailed") -> Dict[str, Any]:
        """
        Generate a complete Game Design Document
        
        Args:
            concept: Game concept description
            style: Output style (detailed, concise, pitch)
        
        Returns:
            Dictionary with all GDD sections
        """
        gdd_structure = {
            "title": self._extract_title(concept),
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "sections": {
                "overview": await self._generate_overview(concept, style),
                "gameplay": await self._generate_gameplay(concept, style),
                "mechanics": await self._generate_mechanics(concept, style),
                "story_lore": await self._generate_story(concept, style),
                "characters": await self._generate_characters(concept, style),
                "world_design": await self._generate_world(concept, style),
                "economy": await self._generate_economy(concept, style),
                "progression": await self._generate_progression(concept, style),
                "art_style": await self._generate_art_style(concept, style),
                "audio": await self._generate_audio(concept, style),
                "monetization": await self._generate_monetization(concept, style),
                "technical": await self._generate_technical(concept, style),
                "roadmap": await self._generate_roadmap(concept, style)
            }
        }
        
        # Export to multiple formats
        await self._export_gdd(gdd_structure)
        
        return gdd_structure
    
    async def _generate_overview(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate game overview section"""
        # TODO: Use LLM to generate overview
        return {
            "high_concept": f"{concept} - A revolutionary gaming experience",
            "genre": ["RPG", "Action", "Adventure"],
            "target_audience": "18-35, fans of deep narratives and complex systems",
            "platforms": ["PC", "PlayStation 5", "Xbox Series X"],
            "unique_selling_points": [
                "Deep branching narrative with real consequences",
                "Innovative crafting system with procedural generation",
                "Living world that evolves based on player actions"
            ]
        }
    
    async def _generate_gameplay(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate gameplay mechanics section"""
        return {
            "core_loop": "Explore -> Combat -> Loot -> Craft -> Upgrade -> Repeat",
            "perspective": "Third-person with optional first-person mode",
            "controls": "Standard WASD + Mouse with full controller support",
            "difficulty_modes": ["Story", "Normal", "Hard", "Nightmare"],
            "multiplayer": {
                "supported": True,
                "modes": ["Co-op (2-4 players)", "PvP Arena"],
                "features": ["Drop-in/Drop-out", "Cross-platform play"]
            }
        }
    
    async def _generate_mechanics(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate detailed mechanics section"""
        return {
            "combat_system": {
                "type": "Real-time with tactical pause",
                "features": ["Combo system", "Environmental interactions", "Weak point targeting"],
                "weapons": ["Melee", "Ranged", "Magic/Tech"],
                "defense": ["Dodging", "Blocking", "Parrying", "Cover system"]
            },
            "crafting_system": {
                "type": "Blueprint-based with experimentation",
                "resources": ["Common", "Rare", "Legendary", "Unique"],
                "stations": ["Forge", "Workbench", "Alchemy Lab", "Enchantment Table"],
                "special_features": ["Item fusion", "Quality tiers", "Procedural modifiers"]
            },
            "skill_system": {
                "type": "Hybrid (Skill trees + Perk system)",
                "trees": ["Combat", "Crafting", "Social", "Exploration"],
                "respec": "Available at certain checkpoints with cost"
            }
        }
    
    async def _generate_story(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate story and lore section"""
        return {
            "premise": "In a world transformed by catastrophic events, you must...",
            "themes": ["Survival", "Redemption", "Choice and Consequence", "Power vs Responsibility"],
            "narrative_structure": "Non-linear with multiple endings",
            "key_characters": [
                {"name": "Protagonist", "role": "Player character", "arc": "From survivor to leader"},
                {"name": "Mentor", "role": "Guide", "arc": "Secret antagonist"},
                {"name": "Rival", "role": "Antagonist/Foil", "arc": "Tragic villain"}
            ],
            "world_history": "Thousands of years ago, the Great Calamity...",
            "factions": [
                {"name": "The Order", "alignment": "Lawful Good", "goal": "Restore ancient order"},
                {"name": "Free Traders", "alignment": "Neutral", "goal": "Profit above all"},
                {"name": "The Corrupted", "alignment": "Chaotic Evil", "goal": "Accelerate the decay"}
            ]
        }
    
    async def _generate_characters(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate character design section"""
        return {
            "protagonist_customization": {
                "appearance": ["Gender", "Face", "Hair", "Body type", "Tattoos/Scars"],
                "background": ["Origin story", "Starting stats", "Unique abilities"],
                "voice": ["Male", "Female", "Non-binary options"]
            },
            "npc_design_principles": [
                "Each NPC has daily routines and schedules",
                "Relationships evolve based on player actions",
                "Memorable visual silhouettes",
                "Distinct voice acting and dialogue styles"
            ],
            "enemy_types": [
                {"category": "Humanoid", "examples": ["Bandits", "Soldiers", "Cultists"]},
                {"category": "Creatures", "examples": ["Beasts", "Monsters", "Mutants"]},
                {"category": "Mechanical", "examples": ["Constructs", "Drones", "Tanks"]},
                {"category": "Supernatural", "examples": ["Spirits", "Demons", "Undead"]}
            ]
        }
    
    async def _generate_world(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate world design section"""
        return {
            "world_structure": "Open world with distinct regions",
            "regions": [
                {
                    "name": "Starting Zone",
                    "theme": "Post-apocalyptic settlement",
                    "level_range": "1-10",
                    "key_locations": ["Home Base", "Training Grounds", "Market"]
                },
                {
                    "name": "The Wastelands",
                    "theme": "Desolate desert with ruins",
                    "level_range": "10-25",
                    "key_locations": ["Ancient City", "Oasis", "Bandit Camp"]
                },
                {
                    "name": "Neo-City",
                    "theme": "Cyberpunk metropolis",
                    "level_range": "25-40",
                    "key_locations": ["Corporate Plaza", "Underground", "Sky District"]
                }
            ],
            "environmental_features": [
                "Dynamic weather system",
                "Day/night cycle affecting spawns and events",
                "Destructible environments",
                "Hidden areas and secrets"
            ]
        }
    
    async def _generate_economy(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate economy and balance section"""
        return {
            "currencies": [
                {"name": "Credits", "type": "Primary", "sources": ["Quests", "Loot", "Trading"]},
                {"name": "Rare Materials", "type": "Crafting", "sources": ["Mining", "Dismantling"]},
                {"name": "Reputation Points", "type": "Social", "sources": ["Faction quests", "Helping NPCs"]}
            ],
            "pricing_strategy": "Dynamic pricing based on supply/demand",
            "inflation_control": ["Sinks: Repair costs, Housing taxes, Luxury items"],
            "trade_systems": ["Player-to-player marketplace", "Auction house", "Direct trading"]
        }
    
    async def _generate_progression(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate progression systems section"""
        return {
            "level_cap": 50,
            "experience_sources": ["Quests", "Combat", "Exploration", "Crafting", "Discovery"],
            "reward_schedules": {
                "early_game": "Frequent rewards to establish engagement",
                "mid_game": "Meaningful choices in build direction",
                "end_game": "Prestige systems and cosmetic rewards"
            },
            "endgame_content": [
                "Raids and dungeons",
                "PvP ranked seasons",
                "New Game+ with increased difficulty",
                "Seasonal events and limited-time content"
            ]
        }
    
    async def _generate_art_style(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate art direction section"""
        return {
            "visual_style": "Stylized realism with vibrant colors",
            "reference_games": ["Cyberpunk 2077", "The Witcher 3", "Borderlands 3"],
            "color_palette": "Neon accents against dark backgrounds",
            "character_design": "Distinctive silhouettes with customizable elements",
            "environment_design": "Mix of high-tech and decay",
            "ui_ux": "Minimalist HUD with diegetic elements",
            "accessibility": [
                "Colorblind modes",
                "Scalable UI",
                "Subtitle customization",
                "Motor accessibility options"
            ]
        }
    
    async def _generate_audio(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate audio design section"""
        return {
            "music_style": "Orchestral with electronic elements",
            "dynamic_music": "Adaptive soundtrack that responds to gameplay",
            "sound_effects": [
                "Weapon sounds with positional audio",
                "Environmental ambience with regional variations",
                "UI sounds that match cyberpunk aesthetic"
            ],
            "voice_acting": {
                "coverage": "Full voice acting for main quest and major NPCs",
                "languages": ["English", "Spanish", "French", "German", "Japanese", "Russian"],
                "lip_sync": "Automated with manual polish for key scenes"
            }
        }
    
    async def _generate_monetization(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate monetization strategy (if applicable)"""
        return {
            "business_model": "Premium game with optional DLC",
            "dlc_plans": [
                {"type": "Story Expansion", "timing": "6 months post-launch"},
                {"type": "Cosmetic Pack", "timing": "3 months post-launch"}
            ],
            "microtransactions": "Cosmetics only, no pay-to-win",
            "season_pass": "Optional, includes all story DLCs at discount"
        }
    
    async def _generate_technical(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate technical requirements section"""
        return {
            "engine": "Unreal Engine 5 / Godot 4 / Unity DOTS",
            "target_platforms": {
                "PC": {
                    "minimum": {
                        "OS": "Windows 10 64-bit",
                        "CPU": "Intel i5-8400 / AMD Ryzen 5 2600",
                        "GPU": "NVIDIA GTX 1060 6GB / AMD RX 580",
                        "RAM": "16 GB",
                        "storage": "70 GB SSD"
                    },
                    "recommended": {
                        "OS": "Windows 11 64-bit",
                        "CPU": "Intel i7-12700K / AMD Ryzen 7 5800X",
                        "GPU": "NVIDIA RTX 3070 Ti / AMD RX 6800 XT",
                        "RAM": "32 GB",
                        "storage": "70 GB NVMe SSD"
                    }
                }
            },
            "online_features": ["Cloud saves", "Achievements", "Leaderboards"],
            "anti_cheat": "Server-side validation for multiplayer"
        }
    
    async def _generate_roadmap(self, concept: str, style: str) -> Dict[str, Any]:
        """Generate development roadmap section"""
        return {
            "development_phases": [
                {
                    "phase": "Pre-Production",
                    "duration": "3 months",
                    "milestones": ["Concept finalization", "Prototype", "Art bible"]
                },
                {
                    "phase": "Production",
                    "duration": "18 months",
                    "milestones": ["Vertical slice", "Alpha", "Beta"]
                },
                {
                    "phase": "Polish",
                    "duration": "6 months",
                    "milestones": ["Bug fixing", "Optimization", "Localization"]
                },
                {
                    "phase": "Launch",
                    "duration": "Ongoing",
                    "milestones": ["Release", "Post-launch support", "DLC development"]
                }
            ],
            "team_requirements": {
                "core_team": "15-25 people",
                "roles": ["Designers", "Programmers", "Artists", "Writers", "QA"]
            }
        }
    
    def _extract_title(self, concept: str) -> str:
        """Extract or generate title from concept"""
        # Simple extraction - first few words capitalized
        words = concept.split()[:4]
        return ' '.join(words).title() + ": The Game"
    
    async def _export_gdd(self, gdd: Dict[str, Any]):
        """Export GDD to multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"GDD_{gdd['title'].replace(' ', '_')}_{timestamp}"
        
        # Export as JSON
        json_path = self.output_dir / f"{base_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(gdd, f, indent=2, ensure_ascii=False)
        
        # Export as Markdown
        md_path = self.output_dir / f"{base_name}.md"
        markdown_content = self._convert_to_markdown(gdd)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Export as Obsidian Canvas
        canvas_path = self.output_dir / f"{base_name}.canvas"
        canvas_content = self._convert_to_canvas(gdd)
        with open(canvas_path, 'w', encoding='utf-8') as f:
            f.write(canvas_content)
        
        print(f"✅ GDD exported to: {self.output_dir}")
        print(f"   - {json_path.name}")
        print(f"   - {md_path.name}")
        print(f"   - {canvas_path.name}")
    
    def _convert_to_markdown(self, gdd: Dict[str, Any]) -> str:
        """Convert GDD to formatted Markdown"""
        md = f"# {gdd['title']}\n\n"
        md += f"**Version:** {gdd['version']}  \n"
        md += f"**Created:** {gdd['created_at']}  \n\n"
        md += "---\n\n"
        
        for section_name, section_content in gdd['sections'].items():
            md += f"## {section_name.replace('_', ' ').title()}\n\n"
            
            if isinstance(section_content, dict):
                for key, value in section_content.items():
                    md += f"### {key.replace('_', ' ').title()}\n"
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                md += f"- **{item.get('name', 'Item')}:** {json.dumps(item, ensure_ascii=False)}\n"
                            else:
                                md += f"- {item}\n"
                    elif isinstance(value, dict):
                        md += f"```json\n{json.dumps(value, indent=2)}\n```\n"
                    else:
                        md += f"{value}\n"
                    md += "\n"
            
            md += "---\n\n"
        
        return md
    
    def _convert_to_canvas(self, gdd: Dict[str, Any]) -> str:
        """Convert GDD to Obsidian Canvas format"""
        # Simplified canvas structure
        canvas = {
            "nodes": [],
            "edges": []
        }
        
        # Add main title node
        canvas["nodes"].append({
            "id": "main",
            "x": 0,
            "y": 0,
            "width": 400,
            "height": 100,
            "type": "text",
            "text": f"# {gdd['title']}"
        })
        
        # Add section nodes
        y_offset = 150
        for i, (section_name, section_content) in enumerate(gdd['sections'].items()):
            canvas["nodes"].append({
                "id": f"section_{i}",
                "x": 0,
                "y": y_offset + (i * 200),
                "width": 350,
                "height": 150,
                "type": "text",
                "text": f"## {section_name.replace('_', ' ').title()}\n\n{json.dumps(section_content, indent=2)[:200]}..."
            })
            
            # Connect to main
            canvas["edges"].append({
                "fromNode": "main",
                "toNode": f"section_{i}"
            })
        
        return json.dumps(canvas, indent=2)
    
    async def execute(self, task: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main execution method for the plugin"""
        print(f"🎮 GDD Architect: Processing '{task}'...")
        
        concept = params.get("concept", task) if params else task
        style = params.get("style", "detailed") if params else "detailed"
        
        result = await self.generate_gdd(concept, style)
        
        return {
            "status": "success",
            "message": f"GDD generated: {result['title']}",
            "data": result,
            "exports": list(self.output_dir.glob(f"GDD_{result['title'].replace(' ', '_')}_*"))
        }
