# 3D Subway Runner Game

A 3D endless runner game built with Python and OpenGL, inspired by the classic Subway Surfers gameplay. Navigate through an infinite cityscape while avoiding obstacles and collecting power-ups!

## 🎮 Game Features

### Core Gameplay
- **Endless Runner**: Infinite road with dynamic obstacles and power-ups
- **3D Graphics**: Full 3D environment with perspective rendering
- **Progressive Difficulty**: Speed increases every 10 seconds (2.0 → 8.0 max speed)
- **Score System**: Points awarded for distance traveled and power-ups collected

### Player Mechanics
- **Movement**: Left/Right arrow keys for lane switching
- **Jumping**: 'J' key for jumping over low obstacles
- **Physics**: Realistic gravity and jumping mechanics
- **Lives System**: Start with 3 lives, gain more through silver power-ups

### Obstacle Types
1. **🔴 Low Obstacles (Red)**: Must be jumped over using 'J' key
2. **🔵 Tall Obstacles (Blue)**: Must be avoided by moving left/right
3. **💎 Power-ups**: Collectible items with special effects

### Power-up System
- **🟢 Green Power-ups**: +20 score points
- **🟡 Yellow Power-ups**: +1 ammunition (max 5 bullets)
- **⚪ Silver Power-ups**: +1 extra life

### Game Controls
- **Arrow Keys**: Move player left/right
- **J Key**: Jump over low obstacles
- **Space Bar**: Pause/Resume game
- **R Key**: Restart game (when game over) or reset camera
- **P Key**: Alternative pause key

### Camera Controls
- **W/S**: Move camera forward/backward
- **A/D**: Move camera left/right  
- **Q/E**: Move camera up/down

## 🛠️ Technical Features

### Graphics & Rendering
- **OpenGL 3D Rendering**: Full 3D graphics with depth testing
- **Perspective Projection**: Realistic 3D perspective view
- **Dynamic Lighting**: Colored obstacles and environment
- **Infinite Scrolling**: Seamless world movement system

### Game Systems
- **Time-based Speed Progression**: Automatic difficulty scaling
- **Collision Detection**: Precise 3D collision system
- **State Management**: Proper game state handling (playing, paused, game over)
- **Dynamic Obstacle Spawning**: Intelligent obstacle generation

### Visual Elements
- **3D Player Model**: Detailed character with head, body, arms, and legs
- **Road System**: Dynamic road with white lane markings
- **Border Boundaries**: Cyan wireframe borders defining play area
- **Obstacle Variety**: Different colored and sized 3D obstacles

## 📋 Requirements


## How to Play
Start the Game: Run Project.py to begin
Control Your Character:
Use Left/Right arrows to dodge obstacles
Press J to jump over red obstacles
Collect colorful power-ups for bonuses
Avoid Obstacles:
Red blocks: Jump over them
Blue blocks: Move left or right to avoid
Collect Power-ups:
Green: Instant score boost (+20 points)
Yellow: Ammunition for future features
Silver: Extra life for extended gameplay
Survive: The game gets faster every 10 seconds - how long can you last?


🏆 Scoring System
Distance: Points earned continuously based on speed
Green Power-ups: +20 points each
Speed Bonus: Higher speeds = faster scoring
Survival: Longer survival = higher scores


⚙️ Game Mechanics
Speed Progression
Starting Speed: 2.0 units/second
Speed Increase: +0.5 every 10 seconds
Maximum Speed: 8.0 units/second (reached after 2 minutes)
Difficulty Scaling: More obstacles spawn at higher speeds




