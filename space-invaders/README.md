# 👾 Vics Invaders — Space Invaders

A retro-style Space Invaders clone built with HTML5 Canvas. Zero dependencies — just open and play!

## 🚀 How to Launch

### Option 1 — Double-click
Just open `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).

### Option 2 — Command line
```bash
# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

### Option 3 — VS Code Live Server
1. Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension
2. Right-click `index.html` → **Open with Live Server**

## 🎮 How to Play

### Controls

| Key | Action |
|-----|--------|
| `←` `→` or `A` `D` | Move ship left / right |
| `Space` | Fire |
| `P` | Pause / Resume |

### Objective

Destroy all alien invaders before they reach the bottom of the screen. Survive as many waves as possible and rack up a high score!

### Enemies

| Enemy | Color | Points |
|-------|-------|--------|
| Top row | 🔴 Red | 40 pts |
| Middle rows | 🟠 Orange | 20 pts |
| Bottom rows | 🟢 Green | 10 pts |

### Scoring & Combos

- Kill enemies quickly in succession to build a **combo multiplier** (up to 5x!)
- Combo resets after ~1 second of no kills
- Example: A green enemy (10 pts) at 5x combo = **50 points**

### Power-ups

Power-ups drop randomly (5% chance) when you destroy an enemy:

| Power-up | Symbol | Effect |
|----------|--------|--------|
| **Rapid Fire** | 🟡 `R` | Triple fire rate for 5 seconds |
| **Shield** | 🔵 `S` | Invulnerability for 3 seconds |
| **Extra Life** | 🔴 `+` | +1 life (max 5) |

### Waves

- Each wave adds more enemies and increases their speed and fire rate
- After clearing all enemies, the next wave begins immediately
- Enemy rows increase every 3 waves (up to 5 rows)
- Enemy columns increase every 2 waves (up to 11 columns)

### Tips

- 🎯 Focus on building combos for maximum score
- 🛡️ Grab power-ups when they drop — they're rare!
- ⚡ Rapid Fire is devastating — save it for dense formations
- 🎮 Enemies speed up as fewer remain — clear them fast
- 🏆 High scores are saved in your browser automatically

## 📁 Files

```
space-invaders/
├── README.md       ← You're here
└── index.html      ← The entire game (single file, no dependencies)
```

## 🛠 Tech

- **HTML5 Canvas** for rendering
- **Vanilla JavaScript** — no frameworks, no build step
- **localStorage** for high score persistence
- Pixel art sprites drawn programmatically
- 60 FPS game loop via `requestAnimationFrame`

## 📸 Features

- Pixel-art aliens with walk animations
- Particle explosions on enemy kills
- Screen shake on impacts
- Scrolling starfield background
- Combo scoring with on-screen multiplier
- 3 types of power-ups
- Progressive wave difficulty
- Pause/resume support
- Persistent high score

---

**Part of [Vics Agent](../README.md) — Coding your day away by Vics**
