# 🗡️ Hunter Assassin - 2D Stealth Game

A top-down stealth elimination game built with **Python** and **Pygame**.

## 📁 Project Structure

```
pygame_CTP/
├── main.py            → Main game loop, level progression
├── settings.py        → Constants, 5 level maps, guard configs
├── player.py          → Player class (movement, facing)
├── zombie.py          → Guard class (patrol AI, vision cone, LOS)
├── map_manager.py     → Map rendering, wall collision
├── ui.py              → Menu, HUD, level clear, win screens
├── sound_manager.py   → Sound effects (optional)
├── assets/            → Folder for sound files
└── README.md          → This file
```

## 🚀 How to Run

```bash
pip install pygame
cd D:\projects\pygame_CTP
python main.py
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| **WASD / Arrows** | Move |
| **Enter** | Start / Next Level |
| **R** | Restart |
| **ESC** | Quit |

## 🎯 How to Play

- **Sneak behind guards** and touch them to eliminate (stealth kill)
- **Stay out of vision cones** — if spotted, you're detected = game over
- **Eliminate ALL guards** on a level to advance
- **5 levels** of increasing difficulty

## ✨ Features

- Vision cone system with line-of-sight (walls block vision)
- Patrol AI — guards walk between waypoints
- Stealth kill mechanic (behind = kill, front = death)
- 5 handcrafted levels with increasing guard count/speed
- Timer tracking across all levels
