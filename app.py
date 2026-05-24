# ─── ADD THIS TO THE VERY TOP OF YOUR APP.PY ───
from flask import Flask, jsonify, request, render_template_string
import json, time, random
import os  # <-- Add this import so we can read Render's system port

app = Flask(__name__)

GRID_SIZE = 1000
# ... (Keep all your seed_canvas arrays and giant HTML strings exactly the same)
pixel_grid = ["#FFFFFF"] * (GRID_SIZE * GRID_SIZE)

# Seed canvas with vibrant artwork so it looks alive on load
def seed_canvas():
    # Gradient sun burst in center
    cx, cy = 500, 500
    for r in range(120, 0, -1):
        hue = int(r * 3)
        colors = ["#FF6B6B","#FF8E53","#FFC107","#FFD700","#FF6B6B","#C0392B","#E91E63"]
        col = colors[r % len(colors)]
        for angle in range(0, 360, 2):
            import math
            ax = int(cx + r * math.cos(math.radians(angle)))
            ay = int(cy + r * math.sin(math.radians(angle)))
            if 0 <= ax < GRID_SIZE and 0 <= ay < GRID_SIZE:
                pixel_grid[ay * GRID_SIZE + ax] = col

    # Blue ocean band
    for i in range(700, 800):
        for j in range(0, 1000):
            idx = i * GRID_SIZE + j
            if j % 4 < 2:
                pixel_grid[idx] = "#1565C0"
            else:
                pixel_grid[idx] = "#1E88E5"

    # Green land strip
    for i in range(800, 850):
        for j in range(0, 1000):
            idx = i * GRID_SIZE + j
            pixel_grid[idx] = "#2E7D32" if (i+j) % 3 != 0 else "#388E3C"

    # Red diagonal stripes top-left corner
    for i in range(0, 200):
        for j in range(0, 200):
            idx = i * GRID_SIZE + j
            if ((i + j) // 8) % 2 == 0:
                pixel_grid[idx] = "#B71C1C"
            else:
                pixel_grid[idx] = "#D32F2F"

    # Purple galaxy top-right
    for i in range(0, 300):
        for j in range(700, 1000):
            idx = i * GRID_SIZE + j
            dist = ((i-150)**2 + (j-850)**2) ** 0.5
            if dist < 100:
                pixel_grid[idx] = "#7B1FA2"
            elif dist < 150:
                pixel_grid[idx] = "#9C27B0"
            else:
                pixel_grid[idx] = "#4A148C"

    # Cyan checker pattern bottom-left
    for i in range(850, 1000):
        for j in range(0, 300):
            idx = i * GRID_SIZE + j
            if (i // 5 + j // 5) % 2 == 0:
                pixel_grid[idx] = "#00BCD4"
            else:
                pixel_grid[idx] = "#006064"

seed_canvas()

# In-memory leaderboard
leaderboard = [
    {"rank": 1, "username": "OLE_BP", "pixels": 18420, "value": 18420.00, "badge": "👑"},
    {"rank": 2, "username": "KATASTROPHE", "pixels": 11750, "value": 11750.00, "badge": "💎"},
    {"rank": 3, "username": "TASCHENTUCH", "pixels": 7200, "value": 7200.00, "badge": "🥇"},
    {"rank": 4, "username": "ANONYMOUS_DEV", "pixels": 3100, "value": 3100.00, "badge": "🥈"},
    {"rank": 5, "username": "PIXEL_KING_99", "pixels": 1850, "value": 1850.00, "badge": "🥉"},
    {"rank": 6, "username": "NEON_WIZARD", "pixels": 920, "value": 920.00, "badge": "⭐"},
]

@app.route('/')
def index():
    return render_template_string(HTML_FRONTEND)

@app.route('/api/grid', methods=['GET'])
def get_grid():
    return jsonify({"grid": pixel_grid, "size": GRID_SIZE})

@app.route('/api/paint', methods=['POST'])
def paint_pixel():
    data = request.json
    pixels = data.get('pixels', [])
    painted = 0
    for p in pixels:
        x, y = p.get('x'), p.get('y')
        color = p.get('color', '#FF0000')
        if x is not None and y is not None and 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            pixel_grid[y * GRID_SIZE + x] = color
            painted += 1
    return jsonify({"status": "ok", "painted": painted})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    return jsonify({"leaderboard": leaderboard})

HTML_FRONTEND = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Million Dollar Artwork</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-base: #080810;
  --bg-panel: #0e0e1a;
  --bg-card: #131320;
  --bg-hover: #1a1a2e;
  --border: #1e1e35;
  --border-bright: #2a2a4a;
  --accent: #6C63FF;
  --accent2: #FF3E6C;
  --accent3: #00D4AA;
  --accent4: #FFB800;
  --text-primary: #F0EEFF;
  --text-secondary: #9090BB;
  --text-dim: #4a4a6a;
  --glow: 0 0 20px rgba(108,99,255,0.35);
  --glow2: 0 0 20px rgba(255,62,108,0.35);
  --font-display: 'Syne', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --radius: 10px;
  --sidebar-w: 240px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; width: 100%; overflow: hidden; background: var(--bg-base); color: var(--text-primary); font-family: var(--font-display); }

/* ── LAYOUT ── */
.app-shell { display: flex; width: 100vw; height: 100vh; }

/* ── SIDEBAR ── */
.sidebar {
  width: var(--sidebar-w); min-width: var(--sidebar-w);
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 0; z-index: 50; overflow: hidden;
  animation: slideInLeft 0.5s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes slideInLeft { from { transform: translateX(-100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

.brand {
  padding: 20px 18px 16px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.brand-icon {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; flex-shrink: 0;
  box-shadow: 0 0 16px rgba(108,99,255,0.5);
  animation: pulseGlow 3s ease-in-out infinite;
}
@keyframes pulseGlow {
  0%,100% { box-shadow: 0 0 16px rgba(108,99,255,0.5); }
  50% { box-shadow: 0 0 28px rgba(108,99,255,0.85), 0 0 60px rgba(108,99,255,0.3); }
}
.brand-text { display: flex; flex-direction: column; }
.brand-name { font-size: 0.8rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.3px; line-height: 1.1; }
.brand-tagline { font-size: 0.62rem; color: var(--accent); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; font-family: var(--font-mono); }

.nav { padding: 12px 10px; display: flex; flex-direction: column; gap: 2px; flex: 1; }
.nav-item {
  display: flex; align-items: center; gap: 11px;
  padding: 11px 14px; border-radius: var(--radius);
  font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);
  cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden;
  user-select: none;
}
.nav-item::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, var(--accent), transparent);
  opacity: 0; transition: opacity 0.2s;
  border-radius: var(--radius);
}
.nav-item:hover { color: var(--text-primary); background: var(--bg-hover); }
.nav-item.active { color: var(--text-primary); background: var(--bg-hover); }
.nav-item.active::before { opacity: 0.08; }
.nav-item.active::after {
  content: ''; position: absolute; left: 0; top: 20%; bottom: 20%;
  width: 3px; background: var(--accent); border-radius: 0 3px 3px 0;
}
.nav-icon { font-size: 1rem; }

.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid var(--border);
}
.login-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: var(--radius);
  color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s; border: 1px solid var(--border);
}
.login-btn:hover { color: var(--accent); border-color: var(--accent); background: rgba(108,99,255,0.05); }

.pixel-stats {
  padding: 12px 14px; margin: 0 10px 10px;
  background: var(--bg-card); border-radius: var(--radius);
  border: 1px solid var(--border);
}
.stat-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.stat-label { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.8px; font-family: var(--font-mono); }
.stat-val { font-size: 0.8rem; font-weight: 700; color: var(--accent3); font-family: var(--font-mono); }

/* ── MAIN WORKSPACE ── */
.workspace { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }

/* ── TOP BAR ── */
.topbar {
  height: 52px; background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; gap: 12px; flex-shrink: 0;
  animation: fadeInDown 0.4s 0.2s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes fadeInDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.live-badge {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.72rem; font-weight: 700; color: var(--accent3);
  text-transform: uppercase; letter-spacing: 1.5px; font-family: var(--font-mono);
}
.live-dot {
  width: 7px; height: 7px; border-radius: 50%; background: var(--accent3);
  box-shadow: 0 0 8px var(--accent3);
  animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

.topbar-actions { display: flex; align-items: center; gap: 8px; }
.tbtn {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 14px; border-radius: 20px;
  font-size: 0.78rem; font-weight: 700;
  cursor: pointer; border: 1px solid var(--border);
  background: var(--bg-card); color: var(--text-secondary);
  transition: all 0.2s; font-family: var(--font-display);
  white-space: nowrap;
}
.tbtn:hover { border-color: var(--border-bright); color: var(--text-primary); transform: translateY(-1px); }
.tbtn.on { background: rgba(254,240,138,0.1); border-color: var(--accent4); color: var(--accent4); }
.tbtn.primary {
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  color: white; border: none;
  box-shadow: 0 4px 15px rgba(108,99,255,0.4);
}
.tbtn.primary:hover { box-shadow: 0 6px 20px rgba(108,99,255,0.6); transform: translateY(-2px); }

/* ── TICKER TAPE ── */
.ticker {
  height: 32px; background: #060612;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; overflow: hidden;
  flex-shrink: 0; position: relative;
}
.ticker::before, .ticker::after {
  content: ''; position: absolute; top: 0; bottom: 0; width: 60px; z-index: 2; pointer-events: none;
}
.ticker::before { left: 0; background: linear-gradient(90deg, #060612, transparent); }
.ticker::after { right: 0; background: linear-gradient(-90deg, #060612, transparent); }
.ticker-inner {
  display: flex; white-space: nowrap;
  animation: tickerScroll 45s linear infinite;
  will-change: transform;
}
.ticker-inner:hover { animation-play-state: paused; }
@keyframes tickerScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.tick { display: inline-flex; align-items: center; gap: 6px; padding: 0 28px; font-size: 0.7rem; font-family: var(--font-mono); color: var(--text-dim); }
.tick-user { color: var(--accent2); font-weight: 700; }
.tick-coord { color: var(--accent3); }
.tick-sep { color: var(--text-dim); }

/* ── VIEWS ── */
.view { flex: 1; display: none; position: relative; overflow: hidden; }
.view.active { display: flex; }

/* ── CANVAS VIEWPORT ── */
#liveCanvasView {
  background: #e8e8e8;
  align-items: center; justify-content: center;
  overflow: hidden;
}

/* ── TOOL PALETTE ── */
.palette {
  position: absolute; top: 16px; left: 16px;
  background: rgba(255,255,255,0.97); backdrop-filter: blur(12px);
  border: 1px solid #d8d8d8; border-radius: 12px;
  padding: 10px 14px; display: flex; align-items: center; gap: 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  z-index: 20;
  animation: fadeInDown 0.5s 0.4s cubic-bezier(0.22,1,0.36,1) both;
}

.mode-toggle {
  display: flex; background: #f0f0f0; border-radius: 8px;
  padding: 3px; border: 1px solid #ddd; gap: 2px;
}
.mbt {
  border: none; padding: 6px 12px; border-radius: 6px;
  font-size: 0.75rem; font-weight: 700; cursor: pointer;
  background: none; color: #666; transition: all 0.18s;
  font-family: var(--font-display);
}
.mbt.on { background: #2563eb; color: white; box-shadow: 0 2px 8px rgba(37,99,235,0.35); }

.palette-divider { width: 1px; height: 28px; background: #e0e0e0; }

.palette-label { font-size: 0.65rem; color: #888; text-transform: uppercase; letter-spacing: 1px; font-family: var(--font-mono); }

.color-swatch-row { display: flex; gap: 5px; align-items: center; }
.preset-color {
  width: 20px; height: 20px; border-radius: 4px; cursor: pointer; border: 2px solid transparent;
  transition: all 0.15s; flex-shrink: 0;
}
.preset-color:hover, .preset-color.sel { border-color: white; transform: scale(1.2); }

input[type="color"]#colorPicker {
  width: 30px; height: 30px; border: none; background: none;
  border-radius: 6px; cursor: pointer; padding: 0;
  outline: 2px solid #ddd; outline-offset: 2px;
  transition: outline-color 0.2s;
}
input[type="color"]#colorPicker:hover { outline-color: #2563eb; }

.brush-row { display: flex; align-items: center; gap: 8px; }
.brush-row input[type="range"] {
  width: 70px; accent-color: #2563eb; cursor: pointer; height: 4px;
}
.brush-val {
  font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700;
  color: #2563eb; min-width: 20px; text-align: center;
}

.coord-display {
  font-family: var(--font-mono); font-size: 0.72rem;
  color: #2563eb; min-width: 110px;
  padding-left: 10px; border-left: 1px solid #ddd;
}

/* ── CANVAS WRAPPER ── */
.canvas-frame {
  position: absolute; inset: 0;
  overflow: hidden;
  animation: popIn 0.5s 0.2s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes popIn { from { opacity: 0; } to { opacity: 1; } }

#pixelCanvas {
  display: block;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  background: #ffffff;
  position: absolute; top: 0; left: 0;
}

/* ── LOADING OVERLAY ── */
.canvas-loader {
  position: absolute; inset: 0;
  background: rgba(255,255,255,0.95);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px;
  z-index: 100;
  transition: opacity 0.5s;
}
.canvas-loader.hidden { opacity: 0; pointer-events: none; }
.loader-ring {
  width: 48px; height: 48px; border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loader-text { font-family: var(--font-mono); font-size: 0.75rem; color: #888; letter-spacing: 2px; }
.loader-pct { font-family: var(--font-mono); font-size: 1.4rem; font-weight: 700; color: #2563eb; }

/* ── ZOOM CAPSULE ── */
.zoom-panel {
  position: absolute; right: 20px; bottom: 24px;
  background: rgba(255,255,255,0.95); backdrop-filter: blur(12px);
  border: 1px solid #d0d0d0; border-radius: 14px;
  display: flex; flex-direction: column; align-items: center;
  padding: 10px 0; gap: 8px; width: 44px; z-index: 20;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  animation: fadeInUp 0.5s 0.5s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes fadeInUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.zbtn {
  width: 28px; height: 28px; border-radius: 7px; border: 1px solid #e0e0e0;
  background: #f5f5f5; color: #444;
  font-size: 1.1rem; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.zbtn:hover { background: #2563eb; color: white; border-color: #2563eb; }
.zoom-track { height: 120px; display: flex; align-items: center; justify-content: center; }
.zoom-track input[type=range] {
  writing-mode: vertical-lr; direction: rtl;
  appearance: slider-vertical;
  width: 4px; height: 100%; accent-color: #2563eb; cursor: pointer;
}
.zoom-label { font-family: var(--font-mono); font-size: 0.6rem; color: #888; font-weight: 600; }

/* ── MINIMAP ── */
.minimap {
  position: absolute; left: 20px; bottom: 24px;
  width: 160px; height: 160px;
  background: #fff;
  border: 1.5px solid #bbb; border-radius: 6px;
  overflow: hidden; z-index: 20; cursor: crosshair;
  box-shadow: 0 4px 18px rgba(0,0,0,0.18);
  animation: fadeInUp 0.5s 0.6s cubic-bezier(0.22,1,0.36,1) both;
}
.minimap-title {
  position: absolute; top: 0; left: 0; right: 0;
  padding: 3px 8px; font-size: 0.58rem;
  font-family: var(--font-mono); color: #555;
  background: rgba(255,255,255,0.9); z-index: 2;
  text-transform: uppercase; letter-spacing: 1px;
  border-bottom: 1px solid #e0e0e0;
}
#miniMapCanvas { width: 100%; height: 100%; display: block; }
.mm-fov {
  position: absolute; border: 2px solid #2563eb;
  background: rgba(37,99,235,0.08); pointer-events: none; box-sizing: border-box;
  box-shadow: 0 0 4px rgba(37,99,235,0.4);
  transition: all 0.05s linear;
}

/* ── LEADERBOARD VIEW ── */
#leaderboardView { padding: 40px; overflow-y: auto; }
.page-header { margin-bottom: 32px; animation: fadeInDown 0.5s both; }
.page-header h2 { font-size: 2rem; font-weight: 800; color: var(--text-primary); }
.page-header p { color: var(--text-secondary); margin-top: 6px; font-size: 0.9rem; }

.lb-table { width: 100%; border-collapse: collapse; }
.lb-table thead tr { border-bottom: 1px solid var(--border-bright); }
.lb-table th {
  padding: 12px 16px; text-align: left; font-size: 0.68rem;
  color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-family: var(--font-mono);
}
.lb-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); }
.lb-row { transition: background 0.15s; animation: rowIn 0.4s both; }
.lb-row:hover { background: var(--bg-hover); }
@keyframes rowIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
.lb-row:nth-child(1) { animation-delay: 0.05s; }
.lb-row:nth-child(2) { animation-delay: 0.1s; }
.lb-row:nth-child(3) { animation-delay: 0.15s; }
.lb-row:nth-child(4) { animation-delay: 0.2s; }
.lb-row:nth-child(5) { animation-delay: 0.25s; }

.rank-num { font-weight: 800; color: var(--text-primary); font-family: var(--font-mono); }
.rank-1 { color: var(--accent4); }
.rank-2 { color: #C0C0C0; }
.rank-3 { color: #CD7F32; }
.user-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 34px; height: 34px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
  background: var(--bg-base); border: 1px solid var(--border);
}
.uname { font-weight: 700; font-size: 0.9rem; color: var(--text-primary); }
.px-val { font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-secondary); }
.money-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(0,212,170,0.12); border: 1px solid rgba(0,212,170,0.3);
  color: var(--accent3); padding: 4px 10px; border-radius: 20px;
  font-family: var(--font-mono); font-size: 0.82rem; font-weight: 700;
}
.progress-bar-bg { height: 4px; background: var(--bg-base); border-radius: 4px; width: 120px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 4px; transition: width 1s cubic-bezier(0.22,1,0.36,1); }

/* ── PROFILE VIEW ── */
#profileView { padding: 40px; overflow-y: auto; }
.profile-card {
  max-width: 420px; margin: 60px auto; text-align: center;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 48px 36px;
  animation: popIn 0.5s both;
}
.profile-icon { font-size: 3rem; margin-bottom: 16px; }
.profile-card h3 { font-size: 1.3rem; font-weight: 800; margin-bottom: 8px; }
.profile-card p { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; }
.profile-btn {
  margin-top: 24px; display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 24px; border-radius: 30px;
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  color: white; font-weight: 700; cursor: pointer; border: none;
  font-family: var(--font-display); font-size: 0.9rem;
  box-shadow: 0 4px 20px rgba(108,99,255,0.4);
  transition: all 0.2s;
}
.profile-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(108,99,255,0.5); }

/* ── TOAST NOTIFICATIONS ── */
.toast-stack { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column-reverse; gap: 8px; pointer-events: none; }
.toast {
  background: var(--bg-card); border: 1px solid var(--border-bright);
  padding: 10px 20px; border-radius: 30px;
  font-size: 0.78rem; font-family: var(--font-mono); color: var(--text-primary);
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  animation: toastIn 0.3s cubic-bezier(0.22,1,0.36,1) both;
  white-space: nowrap;
}
@keyframes toastIn { from { opacity: 0; transform: translateY(16px) scale(0.9); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes toastOut { to { opacity: 0; transform: translateY(-8px) scale(0.95); } }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
</style>
</head>
<body>
<div class="app-shell">

  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">🎨</div>
      <div class="brand-text">
        <div class="brand-name">Million Dollar<br>Artwork</div>
        <div class="brand-tagline">1,000,000 Pixels</div>
      </div>
    </div>

    <nav class="nav">
      <div class="nav-item active" data-view="liveCanvasView">
        <span class="nav-icon">🖼</span> Live Canvas
      </div>
      <div class="nav-item" data-view="leaderboardView">
        <span class="nav-icon">🏆</span> Leaderboard
      </div>
      <div class="nav-item" data-view="profileView">
        <span class="nav-icon">👤</span> My Profile
      </div>
    </nav>

    <div class="pixel-stats">
      <div class="stat-row"><span class="stat-label">Total Pixels</span><span class="stat-val" id="statTotal">1,000,000</span></div>
      <div class="stat-row"><span class="stat-label">Painted</span><span class="stat-val" id="statPainted">0</span></div>
      <div class="stat-row"><span class="stat-label">Available</span><span class="stat-val" id="statFree">0</span></div>
    </div>

    <div class="sidebar-footer">
      <div class="login-btn">🔓 Login / Register</div>
    </div>
  </aside>

  <main class="workspace">

    <header class="topbar">
      <div class="live-badge">
        <div class="live-dot"></div>
        LIVE · Updated Now
      </div>
      <div class="topbar-actions">
        <button class="tbtn" id="highlightBtn">💡 Show Available</button>
        <button class="tbtn" id="resetViewBtn">⊡ Reset View</button>
        <button class="tbtn primary">⚡ Buy Pixels</button>
      </div>
    </header>

    <div class="ticker">
      <div class="ticker-inner" id="tickerInner">
        <span class="tick">⚡ <span class="tick-user">OLE_BP</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(500, 375)</span></span>
        <span class="tick">⚡ <span class="tick-user">KATASTROPHE</span> <span class="tick-sep">CLAIMED</span> <span class="tick-coord">(492, 381)</span></span>
        <span class="tick">⚡ <span class="tick-user">TASCHENTUCH</span> <span class="tick-sep">BOUGHT</span> <span class="tick-coord">(512, 360)</span></span>
        <span class="tick">⚡ <span class="tick-user">PIXEL_KING</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(820, 144)</span></span>
        <span class="tick">⚡ <span class="tick-user">NEON_WIZARD</span> <span class="tick-sep">CLAIMED</span> <span class="tick-coord">(33, 901)</span></span>
        <span class="tick">⚡ <span class="tick-user">ANONYMOUS_DEV</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(777, 222)</span></span>
        <span class="tick">⚡ <span class="tick-user">OLE_BP</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(500, 375)</span></span>
        <span class="tick">⚡ <span class="tick-user">KATASTROPHE</span> <span class="tick-sep">CLAIMED</span> <span class="tick-coord">(492, 381)</span></span>
        <span class="tick">⚡ <span class="tick-user">TASCHENTUCH</span> <span class="tick-sep">BOUGHT</span> <span class="tick-coord">(512, 360)</span></span>
        <span class="tick">⚡ <span class="tick-user">PIXEL_KING</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(820, 144)</span></span>
        <span class="tick">⚡ <span class="tick-user">NEON_WIZARD</span> <span class="tick-sep">CLAIMED</span> <span class="tick-coord">(33, 901)</span></span>
        <span class="tick">⚡ <span class="tick-user">ANONYMOUS_DEV</span> <span class="tick-sep">PAINTED</span> <span class="tick-coord">(777, 222)</span></span>
      </div>
    </div>

    <div class="view active" id="liveCanvasView">

      <div class="palette">
        <div class="mode-toggle">
          <button class="mbt on" id="modePaint">✏️ Paint</button>
          <button class="mbt" id="modePan">✋ Move</button>
        </div>
        <div class="palette-divider"></div>
        <div style="display:flex;flex-direction:column;gap:4px">
          <div class="palette-label">Color</div>
          <div class="color-swatch-row">
            <div class="preset-color sel" style="background:#EF4444" data-color="#EF4444"></div>
            <div class="preset-color" style="background:#F97316" data-color="#F97316"></div>
            <div class="preset-color" style="background:#EAB308" data-color="#EAB308"></div>
            <div class="preset-color" style="background:#22C55E" data-color="#22C55E"></div>
            <div class="preset-color" style="background:#3B82F6" data-color="#3B82F6"></div>
            <div class="preset-color" style="background:#A855F7" data-color="#A855F7"></div>
            <div class="preset-color" style="background:#EC4899" data-color="#EC4899"></div>
            <div class="preset-color" style="background:#0f0f0f" data-color="#0f0f0f"></div>
            <div class="preset-color" style="background:#FFFFFF;border:1px solid #333" data-color="#FFFFFF"></div>
            <input type="color" id="colorPicker" value="#EF4444" title="Custom color">
          </div>
        </div>
        <div class="palette-divider"></div>
        <div style="display:flex;flex-direction:column;gap:4px">
          <div class="palette-label">Brush <span class="brush-val" id="brushVal">1</span>px</div>
          <div class="brush-row">
            <input type="range" id="brushSize" min="1" max="9" step="2" value="1">
          </div>
        </div>
        <div class="palette-divider"></div>
        <div class="coord-display" id="coordHUD">X: —, Y: —</div>
      </div>

      <div class="canvas-frame" id="canvasFrame">
        <canvas id="pixelCanvas"></canvas>
        <div class="canvas-loader" id="canvasLoader">
          <div class="loader-ring"></div>
          <div class="loader-pct" id="loadPct">0%</div>
          <div class="loader-text">LOADING CANVAS</div>
        </div>
      </div>

      <div class="zoom-panel">
        <button class="zbtn" id="zoomIn" title="Zoom in">+</button>
        <div class="zoom-track">
          <input type="range" id="zoomRange" min="0.3" max="40" step="0.1" value="0.7">
        </div>
        <button class="zbtn" id="zoomOut" title="Zoom out">−</button>
        <div class="zoom-label" id="zoomLabel">1×</div>
      </div>

      <div class="minimap" id="minimapEl">
        <div class="minimap-title">RADAR MAP</div>
        <canvas id="miniMapCanvas" width="150" height="150"></canvas>
        <div class="mm-fov" id="mmFov"></div>
      </div>

    </div><div class="view" id="leaderboardView" style="flex-direction:column;">
      <div style="padding:40px;overflow-y:auto;flex:1">
        <div class="page-header">
          <h2>🏆 Global Leaderboard</h2>
          <p>Rankings by total pixels claimed and ecosystem value contributed.</p>
        </div>
        <table class="lb-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Artist</th>
              <th>Pixels</th>
              <th>Value ($)</th>
              <th>Share</th>
            </tr>
          </thead>
          <tbody id="lbBody"></tbody>
        </table>
      </div>
    </div>

    <div class="view" id="profileView" style="align-items:center;justify-content:center;">
      <div class="profile-card">
        <div class="profile-icon">🎨</div>
        <h3>Your Artist Profile</h3>
        <p>Sign in to track your pixel ownership, canvas coordinates, and ecosystem value contribution in real time.</p>
        <button class="profile-btn">🔓 Login / Register</button>
      </div>
    </div>

  </main>
</div>

<div class="toast-stack" id="toastStack"></div>

<script>
// ═══════════════════════════════════════════════════════════
//  CONSTANTS & STATE
// ═══════════════════════════════════════════════════════════
const GRID = 1000;
const MINIMAP_SIZE = 150;

const canvas  = document.getElementById('pixelCanvas');
const ctx     = canvas.getContext('2d', { alpha: false });
const mmCvs   = document.getElementById('miniMapCanvas');
const mmCtx   = mmCvs.getContext('2d');
const mmFov   = document.getElementById('mmFov');
const mmEl    = document.getElementById('minimapEl');
const loader  = document.getElementById('canvasLoader');
const loadPct = document.getElementById('loadPct');
const frame   = document.getElementById('canvasFrame');

let pixelData   = new Array(GRID * GRID).fill('#ffffff');
let mmDirty     = true;
let mmBuffer    = null;

const cam = { x: 500, y: 500, zoom: 0.7 };
let mode        = 'paint';
let drawing     = false;
let panning     = false;
let lastX = 0, lastY = 0;
let highlightOn = false;
let rafId       = null;
let needsRender = true;
let lastPaint   = null; // throttle

// Off-screen canvas for full 1000×1000 render
const offscreen = document.createElement('canvas');
offscreen.width = GRID; offscreen.height = GRID;
const offCtx = offscreen.getContext('2d', { alpha: false });
let offDirty = true; // entire offscreen needs rebuild

// ═══════════════════════════════════════════════════════════
//  LAYOUT — make canvas fill available space
// ═══════════════════════════════════════════════════════════
function layout() {
  const sidebar = document.querySelector('.sidebar').offsetWidth;
  const topbar  = document.querySelector('.topbar').offsetHeight;
  const ticker  = document.querySelector('.ticker').offsetHeight;
  const availW  = window.innerWidth  - sidebar;
  const availH  = window.innerHeight - topbar - ticker;
  canvas.width  = availW;
  canvas.height = availH;
  // frame is position:absolute inset:0, size is auto
  frame.style.width  = availW + 'px';
  frame.style.height = availH + 'px';
  const minZ = Math.min(availW, availH) / GRID;
  if (cam.zoom < minZ) cam.zoom = minZ;
  needsRender = true;
}

// ═══════════════════════════════════════════════════════════
//  GRID FETCH
// ═══════════════════════════════════════════════════════════
async function fetchGrid() {
  try {
    const res  = await fetch('/api/grid');
    const data = await res.json();
    pixelData = data.grid;
    offDirty  = true;
    mmDirty   = true;
    updateStats();
    needsRender = true;
    loader.classList.add('hidden');
    showToast('✅ Canvas loaded — 1,000,000 pixels ready');
  } catch(e) {
    loadPct.textContent = 'ERR';
    showToast('❌ Failed to load canvas');
  }
}

// Simulate loading progress while fetching
let fakePct = 0;
const pctTimer = setInterval(() => {
  fakePct = Math.min(95, fakePct + Math.random() * 18);
  loadPct.textContent = Math.floor(fakePct) + '%';
}, 200);
fetchGrid().then(() => { clearInterval(pctTimer); loadPct.textContent = '100%'; });

// ═══════════════════════════════════════════════════════════
//  OFF-SCREEN CANVAS (full 1000×1000 pixel buffer)
//  Rebuilt only when pixels change, then GPU-scaled to viewport
// ═══════════════════════════════════════════════════════════
function rebuildOffscreen() {
  const imgData = offCtx.createImageData(GRID, GRID);
  const d = imgData.data;
  for (let i = 0; i < GRID * GRID; i++) {
    let col = pixelData[i] || '#ffffff';
    if (highlightOn && (col === '#FFFFFF' || col === '#ffffff' || col === '#0f0f0f')) col = '#FEF08A';
    const r = parseInt(col.slice(1,3),16);
    const g = parseInt(col.slice(3,5),16);
    const b = parseInt(col.slice(5,7),16);
    const base = i * 4;
    d[base]   = r;
    d[base+1] = g;
    d[base+2] = b;
    d[base+3] = 255;
  }
  offCtx.putImageData(imgData, 0, 0);
  offDirty = false;
}

// ═══════════════════════════════════════════════════════════
//  MAIN RENDER LOOP (rAF driven)
// ═══════════════════════════════════════════════════════════
function renderLoop() {
  rafId = requestAnimationFrame(renderLoop);
  if (!needsRender) return;
  needsRender = false;

  if (offDirty) rebuildOffscreen();

  const cw = canvas.width, ch = canvas.height;
  const z  = cam.zoom;

  // How many grid pixels fit in the canvas at this zoom
  const viewW = cw / z;
  const viewH = ch / z;

  // Source rect in grid coords
  let sx = cam.x - viewW / 2;
  let sy = cam.y - viewH / 2;

  // Clamp so we never show outside [0, GRID]
  sx = Math.max(0, Math.min(GRID - viewW, sx));
  sy = Math.max(0, Math.min(GRID - viewH, sy));

  // Fill background (checkerboard pattern outside grid bounds, white inside)
  ctx.fillStyle = '#d0d0d0';
  ctx.fillRect(0, 0, cw, ch);

  // Draw the relevant slice of the offscreen canvas scaled up
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(offscreen,
    sx, sy, viewW, viewH,       // source: slice of grid
    0, 0, cw, ch                // dest: full canvas
  );

  // Grid overlay when zoomed in enough (≥4×)
  if (z >= 4) {
    const pxSize = cw / viewW;   // pixels per grid cell on screen
    ctx.strokeStyle = 'rgba(0,0,0,0.1)';
    ctx.lineWidth = 0.5;

    const startX = Math.floor(sx);
    const startY = Math.floor(sy);
    const endX   = Math.ceil(sx + viewW);
    const endY   = Math.ceil(sy + viewH);

    ctx.beginPath();
    for (let gx = startX; gx <= endX; gx++) {
      const px = (gx - sx) * pxSize;
      ctx.moveTo(px, 0); ctx.lineTo(px, ch);
    }
    for (let gy = startY; gy <= endY; gy++) {
      const py = (gy - sy) * pxSize;
      ctx.moveTo(0, py); ctx.lineTo(cw, py);
    }
    ctx.stroke();
  }

  updateMinimap();
}

// ═══════════════════════════════════════════════════════════
//  MINIMAP
// ═══════════════════════════════════════════════════════════
function updateMinimap() {
  if (mmDirty) {
    // Build minimap image
    if (!mmBuffer) mmBuffer = mmCtx.createImageData(MINIMAP_SIZE, MINIMAP_SIZE);
    const d = mmBuffer.data;
    for (let my = 0; my < MINIMAP_SIZE; my++) {
      for (let mx = 0; mx < MINIMAP_SIZE; mx++) {
        const gx = Math.floor(mx * (GRID / MINIMAP_SIZE));
        const gy = Math.floor(my * (GRID / MINIMAP_SIZE));
        const col = pixelData[gy * GRID + gx] || '#ffffff';
        const r = parseInt(col.slice(1,3),16);
        const g = parseInt(col.slice(3,5),16);
        const b = parseInt(col.slice(5,7),16);
        const base = (my * MINIMAP_SIZE + mx) * 4;
        d[base]=r; d[base+1]=g; d[base+2]=b; d[base+3]=255;
      }
    }
    mmCtx.putImageData(mmBuffer, 0, 0);
    mmDirty = false;
  }

  // Update FOV box
  const cw = canvas.width, ch = canvas.height;
  const z  = cam.zoom;
  const viewW = cw / z;
  const viewH = ch / z;
  let sx = cam.x - viewW / 2;
  let sy = cam.y - viewH / 2;
  sx = Math.max(0, Math.min(GRID - viewW, sx));
  sy = Math.max(0, Math.min(GRID - viewH, sy));

  const scale = MINIMAP_SIZE / GRID;
  const fovX  = sx  * scale;
  const fovY  = sy  * scale;
  const fovW  = Math.min(MINIMAP_SIZE, viewW * scale);
  const fovH  = Math.min(MINIMAP_SIZE, viewH * scale);

  mmFov.style.left   = fovX + 'px';
  mmFov.style.top    = (fovY + 18) + 'px'; // offset for title bar
  mmFov.style.width  = fovW + 'px';
  mmFov.style.height = fovH + 'px';
}

// ═══════════════════════════════════════════════════════════
//  COORDINATE HELPERS
// ═══════════════════════════════════════════════════════════
function screenToGrid(clientX, clientY) {
  const rect  = canvas.getBoundingClientRect();
  const cw    = canvas.width, ch = canvas.height;
  const z     = cam.zoom;
  const viewW = cw / z, viewH = ch / z;
  let sx = cam.x - viewW / 2;
  let sy = cam.y - viewH / 2;
  sx = Math.max(0, Math.min(GRID - viewW, sx));
  sy = Math.max(0, Math.min(GRID - viewH, sy));

  const rx = (clientX - rect.left) / rect.width;
  const ry = (clientY - rect.top)  / rect.height;
  const gx = Math.floor(sx + rx * viewW);
  const gy = Math.floor(sy + ry * viewH);
  if (gx < 0 || gx >= GRID || gy < 0 || gy >= GRID) return null;
  return { x: gx, y: gy };
}

// ═══════════════════════════════════════════════════════════
//  PAINT
// ═══════════════════════════════════════════════════════════
const pendingBatch = [];
let sendTimer = null;

function flushBatch() {
  if (!pendingBatch.length) return;
  const payload = [...pendingBatch];
  pendingBatch.length = 0;
  fetch('/api/paint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pixels: payload })
  });
}

function doPaint(clientX, clientY) {
  const g = screenToGrid(clientX, clientY);
  if (!g) return;

  // Throttle: skip if same cell as last
  const key = g.x + ',' + g.y;
  if (key === lastPaint) return;
  lastPaint = key;

  const size    = parseInt(document.getElementById('brushSize').value);
  const radius  = Math.floor(size / 2);
  const color   = document.getElementById('colorPicker').value;

  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      const px = g.x + dx, py = g.y + dy;
      if (px < 0 || px >= GRID || py < 0 || py >= GRID) continue;
      const idx = py * GRID + px;
      if (pixelData[idx] === color) continue; // skip same color
      pixelData[idx] = color;
      pendingBatch.push({ x: px, y: py, color });
    }
  }

  offDirty  = true;
  mmDirty   = true;
  needsRender = true;

  // Debounce server flush
  clearTimeout(sendTimer);
  sendTimer = setTimeout(flushBatch, 120);

  // Ticker update
  addTickerEvent(g.x, g.y);
}

// ═══════════════════════════════════════════════════════════
//  STATS
// ═══════════════════════════════════════════════════════════
function updateStats() {
  let painted = 0;
  for (let i = 0; i < pixelData.length; i++) {
    if (pixelData[i] !== '#0f0f0f' && pixelData[i] !== '#FFFFFF' && pixelData[i] !== '#ffffff') painted++;
  }
  const free = GRID * GRID - painted;
  document.getElementById('statPainted').textContent = painted.toLocaleString();
  document.getElementById('statFree').textContent    = free.toLocaleString();
}

// ═══════════════════════════════════════════════════════════
//  ZOOM
// ═══════════════════════════════════════════════════════════
const zoomRange = document.getElementById('zoomRange');
const zoomLabel = document.getElementById('zoomLabel');

function setZoom(val, pivotX, pivotY) {
  const oldZ = cam.zoom;
  const minZ = Math.min(canvas.width, canvas.height) / GRID;
  cam.zoom = Math.max(minZ * 0.5, Math.min(40, val));
  zoomRange.value = cam.zoom;
  zoomLabel.textContent = cam.zoom.toFixed(1).replace('.0','') + '×';

  // Zoom toward cursor pivot
  if (pivotX !== undefined) {
    const rect  = canvas.getBoundingClientRect();
    const cw    = canvas.width, ch = canvas.height;
    const rx    = (pivotX - rect.left) / rect.width  - 0.5;
    const ry    = (pivotY - rect.top)  / rect.height - 0.5;
    const dz    = cam.zoom - oldZ;
    const shift = (cw / oldZ) * dz;
    cam.x += rx * shift;
    cam.y += ry * shift;
    clampCamera();
  }
  needsRender = true;
}

function clampCamera() {
  const cw  = canvas.width, ch  = canvas.height;
  const z   = cam.zoom;
  const hw  = (cw / z) / 2;
  const hh  = (ch / z) / 2;
  cam.x = Math.max(hw, Math.min(GRID - hw, cam.x));
  cam.y = Math.max(hh, Math.min(GRID - hh, cam.y));
}

zoomRange.addEventListener('input', e => setZoom(parseFloat(e.target.value)));
document.getElementById('zoomIn').addEventListener('click',  () => setZoom(cam.zoom * 1.4));
document.getElementById('zoomOut').addEventListener('click', () => setZoom(cam.zoom / 1.4));
document.getElementById('resetViewBtn').addEventListener('click', () => {
  cam.x = 500; cam.y = 500;
  const minZ = Math.min(canvas.width, canvas.height) / GRID;
  setZoom(minZ);
  showToast('🔄 View reset to center');
});

// ═══════════════════════════════════════════════════════════
//  CANVAS EVENTS
// ═══════════════════════════════════════════════════════════
canvas.addEventListener('mousedown', e => {
  if (e.button !== 0) return;
  if (mode === 'paint') { drawing = true; lastPaint = null; doPaint(e.clientX, e.clientY); }
  else { panning = true; lastX = e.clientX; lastY = e.clientY; canvas.style.cursor = 'grabbing'; }
});
canvas.addEventListener('mousemove', e => {
  const g = screenToGrid(e.clientX, e.clientY);
  document.getElementById('coordHUD').textContent = g ? `X: ${g.x}, Y: ${g.y}` : 'X: —, Y: —';

  if (mode === 'paint' && drawing) doPaint(e.clientX, e.clientY);
  if (mode === 'pan'   && panning) {
    const rect  = canvas.getBoundingClientRect();
    const z     = cam.zoom;
    const cw    = canvas.width;
    const dx    = (e.clientX - lastX) / (rect.width  / cw) / z;
    const dy    = (e.clientY - lastY) / (rect.height / cw) / z;
    cam.x  -= dx; cam.y -= dy;
    clampCamera();
    lastX = e.clientX; lastY = e.clientY;
    needsRender = true;
  }
});
window.addEventListener('mouseup', () => {
  drawing = panning = false;
  lastPaint = null;
  canvas.style.cursor = mode === 'pan' ? 'grab' : 'crosshair';
  flushBatch();
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.12 : 0.89;
  setZoom(cam.zoom * factor, e.clientX, e.clientY);
}, { passive: false });

// Touch support
canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  const t = e.touches[0];
  if (mode === 'paint') { drawing = true; lastPaint = null; doPaint(t.clientX, t.clientY); }
  else { panning = true; lastX = t.clientX; lastY = t.clientY; }
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  const t = e.touches[0];
  if (mode === 'paint' && drawing) doPaint(t.clientX, t.clientY);
  if (mode === 'pan'   && panning) {
    const rect = canvas.getBoundingClientRect();
    cam.x -= (t.clientX - lastX) / (rect.width / canvas.width) / cam.zoom;
    cam.y -= (t.clientY - lastY) / (rect.height / canvas.height) / cam.zoom;
    clampCamera(); lastX = t.clientX; lastY = t.clientY; needsRender = true;
  }
}, { passive: false });
canvas.addEventListener('touchend', () => { drawing = panning = false; flushBatch(); });

// ═══════════════════════════════════════════════════════════
//  MINIMAP CLICK = TELEPORT
// ═══════════════════════════════════════════════════════════
mmEl.addEventListener('click', e => {
  const rect = mmEl.getBoundingClientRect();
  const mx   = e.clientX - rect.left;
  const my   = e.clientY - rect.top - 18; // offset for title
  cam.x = Math.floor((mx / MINIMAP_SIZE) * GRID);
  cam.y = Math.floor((my / MINIMAP_SIZE) * GRID);
  clampCamera();
  needsRender = true;
  showToast(`📍 Teleported to (${cam.x}, ${cam.y})`);
});

// ═══════════════════════════════════════════════════════════
//  MODE BUTTONS
// ═══════════════════════════════════════════════════════════
document.getElementById('modePaint').addEventListener('click', () => {
  mode = 'paint';
  document.getElementById('modePaint').classList.add('on');
  document.getElementById('modePan').classList.remove('on');
  canvas.style.cursor = 'crosshair';
});
document.getElementById('modePan').addEventListener('click', () => {
  mode = 'pan';
  document.getElementById('modePan').classList.add('on');
  document.getElementById('modePaint').classList.remove('on');
  canvas.style.cursor = 'grab';
});

// ═══════════════════════════════════════════════════════════
//  COLOR PRESETS
// ═══════════════════════════════════════════════════════════
const picker = document.getElementById('colorPicker');
document.querySelectorAll('.preset-color').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.preset-color').forEach(x => x.classList.remove('sel'));
    el.classList.add('sel');
    picker.value = el.dataset.color;
  });
});
picker.addEventListener('input', () => {
  document.querySelectorAll('.preset-color').forEach(x => x.classList.remove('sel'));
});

// ═══════════════════════════════════════════════════════════
//  BRUSH SIZE DISPLAY
// ═══════════════════════════════════════════════════════════
document.getElementById('brushSize').addEventListener('input', e => {
  document.getElementById('brushVal').textContent = e.target.value;
});

// ═══════════════════════════════════════════════════════════
//  HIGHLIGHT TOGGLE
// ═══════════════════════════════════════════════════════════
document.getElementById('highlightBtn').addEventListener('click', () => {
  highlightOn = !highlightOn;
  document.getElementById('highlightBtn').classList.toggle('on', highlightOn);
  offDirty = true; mmDirty = true; needsRender = true;
  showToast(highlightOn ? '💡 Available pixels highlighted' : '💡 Highlight off');
});

// ═══════════════════════════════════════════════════════════
//  NAV TABS
// ═══════════════════════════════════════════════════════════
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    item.classList.add('active');
    document.getElementById(item.dataset.view).classList.add('active');
    if (item.dataset.view === 'leaderboardView') loadLeaderboard();
  });
});

// ═══════════════════════════════════════════════════════════
//  LEADERBOARD
// ═══════════════════════════════════════════════════════════
async function loadLeaderboard() {
  const res  = await fetch('/api/leaderboard');
  const data = await res.json();
  const tbody = document.getElementById('lbBody');
  const max = data.leaderboard[0]?.pixels || 1;
  tbody.innerHTML = data.leaderboard.map((u,i) => `
    <tr class="lb-row">
      <td><span class="rank-num rank-${i+1}">${u.badge} #${u.rank}</span></td>
      <td><div class="user-cell"><div class="avatar">${u.badge}</div><div class="uname">${u.username}</div></div></td>
      <td><span class="px-val">${u.pixels.toLocaleString()} px</span></td>
      <td><span class="money-chip">$${u.value.toLocaleString('en-US',{minimumFractionDigits:2})}</span></td>
      <td><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${Math.round(u.pixels/max*100)}%"></div></div></td>
    </tr>
  `).join('');
}

// ═══════════════════════════════════════════════════════════
//  TOAST SYSTEM
// ═══════════════════════════════════════════════════════════
function showToast(msg) {
  const stack = document.getElementById('toastStack');
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  stack.appendChild(t);
  setTimeout(() => {
    t.style.animation = 'toastOut 0.3s forwards';
    setTimeout(() => t.remove(), 300);
  }, 2800);
}

// ═══════════════════════════════════════════════════════════
//  LIVE TICKER INJECTION
// ═══════════════════════════════════════════════════════════
const users = ['OLE_BP','KATASTROPHE','PIXEL_KING','NEON_WIZARD','ART_MAXIMUS','TASCHENTUCH'];
const verbs = ['PAINTED','CLAIMED','BOUGHT','STYLED'];
function addTickerEvent(x, y) {
  const u = users[Math.floor(Math.random()*users.length)];
  const v = verbs[Math.floor(Math.random()*verbs.length)];
  const inner = document.getElementById('tickerInner');
  const span = document.createElement('span');
  span.className = 'tick';
  span.innerHTML = `⚡ <span class="tick-user">${u}</span> <span class="tick-sep">${v}</span> <span class="tick-coord">(${x}, ${y})</span>`;
  inner.appendChild(span.cloneNode(true));
  inner.appendChild(span);
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
window.addEventListener('resize', () => { layout(); needsRender = true; });
layout();
clampCamera();
renderLoop();
</script>
</body>
</html>"""

if __name__ == '__main__':
    # Grab the precise dynamic port assigned by Render, falling back to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
