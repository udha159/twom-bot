#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   GAME BOT INSTALLER - All in One        ║
║   The World of Magic - Redfinger Cloud   ║
║                                          ║
║   Cara pakai di Termux:                  ║
║   curl -sL <url> | python3               ║
║   atau: python3 install.py               ║
╚══════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import textwrap
from pathlib import Path

BOT_DIR = Path.home() / "game-bot"

# ============================================================
# WARNA TERMINAL
# ============================================================
def c(text, color):
    codes = {"green": "\033[92m", "yellow": "\033[93m",
             "cyan": "\033[96m", "red": "\033[91m", "bold": "\033[1m"}
    return f"{codes.get(color,'')}{text}\033[0m"

def log(msg, color="cyan"):
    print(c(f"  {msg}", color))

def header(msg):
    print()
    print(c("═" * 46, "bold"))
    print(c(f"  {msg}", "bold"))
    print(c("═" * 46, "bold"))

# ============================================================
# ISI FILE BOT (Embed langsung di installer)
# ============================================================

CONFIG_YAML = """
device:
  screen_width: 1080
  screen_height: 1920
  action_delay: 0.4
  tap_duration: 50

bot:
  mode: farming
  duration: 0
  enable_logging: true
  log_file: ~/game-bot/logs/bot.log

macros:
  farming_loop:
    - action: tap
      x: 0.5
      y: 0.85
      delay: 1.0
      description: "Mulai Battle"

    - action: wait
      seconds: 30
      description: "Tunggu battle selesai"

    - action: tap
      x: 0.5
      y: 0.75
      delay: 0.5
      description: "Klik OK/Next"

    - action: tap
      x: 0.5
      y: 0.85
      delay: 1.0
      description: "Battle lagi"

  auto_skill:
    - action: tap
      x: 0.2
      y: 0.92
      delay: 0.1
      description: "Skill 1"
    - action: tap
      x: 0.38
      y: 0.92
      delay: 0.1
      description: "Skill 2"
    - action: tap
      x: 0.56
      y: 0.92
      delay: 0.1
      description: "Skill 3"
    - action: tap
      x: 0.74
      y: 0.92
      delay: 0.1
      description: "Skill 4"

  daily_reward:
    - action: tap
      x: 0.08
      y: 0.5
      delay: 0.5
      description: "Buka menu"
    - action: tap
      x: 0.5
      y: 0.3
      delay: 0.5
      description: "Tap Daily Reward"
    - action: tap
      x: 0.5
      y: 0.65
      delay: 0.5
      description: "Claim"
    - action: tap
      x: 0.5
      y: 0.8
      delay: 0.3
      description: "Tutup popup"
""".strip()

BOT_PY = '''
import os, sys, time, subprocess, logging, signal, yaml
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    def cprint(msg, color="white"):
        c = {"green": Fore.GREEN, "red": Fore.RED,
             "yellow": Fore.YELLOW, "cyan": Fore.CYAN}
        print(f"{c.get(color, Style.RESET_ALL)}{msg}{Style.RESET_ALL}")
except ImportError:
    def cprint(msg, color="white"): print(msg)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path("~/game-bot/logs/bot.log").expanduser(), mode="a")
    ]
)
logger = logging.getLogger("Bot")

class Controller:
    def __init__(self, w, h):
        self.w, self.h = w, h

    def tap(self, xr, yr, delay=0.3):
        x, y = int(xr * self.w), int(yr * self.h)
        subprocess.run(f"input tap {x} {y}", shell=True, capture_output=True)
        logger.debug(f"TAP ({x},{y})")
        time.sleep(delay)

    def swipe(self, x1r, y1r, x2r, y2r, ms=300, delay=0.3):
        x1,y1 = int(x1r*self.w), int(y1r*self.h)
        x2,y2 = int(x2r*self.w), int(y2r*self.h)
        subprocess.run(f"input swipe {x1} {y1} {x2} {y2} {ms}", shell=True, capture_output=True)
        time.sleep(delay)

    def screenshot(self, path="/sdcard/bot_screen.png"):
        subprocess.run(f"screencap -p {path}", shell=True, capture_output=True)
        return path

    def key(self, code):
        subprocess.run(f"input keyevent {code}", shell=True, capture_output=True)

class Bot:
    def __init__(self, cfg_path="~/game-bot/config.yaml"):
        with open(Path(cfg_path).expanduser()) as f:
            self.cfg = yaml.safe_load(f)
        d = self.cfg.get("device", {})
        self.ctrl = Controller(d.get("screen_width", 1080), d.get("screen_height", 1920))
        self.running = True
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

    def _stop(self, *_):
        cprint("\\n[!] Bot dihentikan.", "yellow")
        self.running = False
        sys.exit(0)

    def run_macro(self, name, actions):
        cprint(f"  ▶ Makro: {name}", "cyan")
        for step in actions:
            if not self.running: break
            act = step.get("action", "")
            desc = step.get("description", act)
            delay = step.get("delay", 0.3)
            cprint(f"    → {desc}", "cyan")
            if act == "tap":
                self.ctrl.tap(step["x"], step["y"], delay)
            elif act == "swipe":
                self.ctrl.swipe(step["x1"],step["y1"],step["x2"],step["y2"],
                                step.get("duration_ms",300), delay)
            elif act == "wait":
                secs = step.get("seconds", 1)
                cprint(f"    ⏳ Tunggu {secs}s...", "yellow")
                for _ in range(int(secs * 10)):
                    if not self.running: break
                    time.sleep(0.1)
            elif act == "key":
                self.ctrl.key(step.get("keycode", 4))
                time.sleep(delay)

    def run(self, macro_name=None):
        mode = self.cfg.get("bot", {}).get("mode", "farming")
        macros = self.cfg.get("macros", {})
        target = macro_name or (mode + "_loop")
        if target not in macros:
            target = list(macros.keys())[0]
        duration = self.cfg.get("bot", {}).get("duration", 0)

        cprint(f"""
╔══════════════════════════════════════╗
║    GAME BOT - The World of Magic     ║
║  Mode  : {mode:<26} ║
║  Makro : {target:<26} ║
║  [Ctrl+C untuk berhenti]             ║
╚══════════════════════════════════════╝
""", "green")

        start = time.time()
        loop = 0
        while self.running:
            loop += 1
            elapsed = (time.time() - start) / 60
            cprint(f"\\n[Loop #{loop}] Waktu: {elapsed:.1f} menit", "yellow")
            self.run_macro(target, macros[target])
            if duration > 0 and elapsed >= duration:
                cprint("\\n[✓] Selesai!", "green")
                break
            time.sleep(0.5)

def show_menu():
    cprint("""
╔════════════════════════════════╗
║   GAME BOT - Menu             ║
╠════════════════════════════════╣
║  1. Jalankan bot farming       ║
║  2. Jalankan makro tertentu    ║
║  3. Test tap koordinat         ║
║  4. Ambil screenshot           ║
║  5. Lihat semua makro          ║
║  6. Keluar                     ║
╚════════════════════════════════╝
""", "cyan")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro", default=None)
    ap.add_argument("--test-tap", nargs=2, type=float, metavar=("X","Y"))
    args = ap.parse_args()

    bot = Bot()

    if args.test_tap:
        x, y = args.test_tap
        cprint(f"Test tap ({x}, {y})...", "yellow")
        bot.ctrl.tap(x, y)
        cprint("Done!", "green")
    elif args.macro:
        bot.run(args.macro)
    else:
        show_menu()
        ch = input("Pilih [1-6]: ").strip()
        macros = bot.cfg.get("macros", {})
        if ch == "1":
            bot.run()
        elif ch == "2":
            ml = list(macros.keys())
            for i, n in enumerate(ml, 1):
                cprint(f"  {i}. {n}", "cyan")
            idx = int(input("Nomor makro: ")) - 1
            bot.run(ml[idx])
        elif ch == "3":
            x = float(input("X (0.0-1.0): "))
            y = float(input("Y (0.0-1.0): "))
            bot.ctrl.tap(x, y)
            cprint("Tap dikirim!", "green")
        elif ch == "4":
            path = bot.ctrl.screenshot()
            cprint(f"Screenshot: {path}", "green")
        elif ch == "5":
            for n, acts in macros.items():
                cprint(f"  • {n} ({len(acts)} aksi)", "cyan")
        else:
            sys.exit(0)
'''.strip()

CALIBRATE_PY = '''
import subprocess, sys
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def get_size():
    out = run("wm size").stdout
    for line in out.split("\\n"):
        if "size:" in line.lower():
            try:
                w, h = line.split(":")[-1].strip().split("x")
                return int(w), int(h)
            except: pass
    return 1080, 1920

def c(t, col):
    cols = {"g": "\\033[92m", "y": "\\033[93m", "c": "\\033[96m"}
    return f"{cols.get(col,'')} {t}\\033[0m"

w, h = get_size()
print(c(f"\\n Layar: {w} x {h}", "g"))
print(c(" config.yaml => screen_width: " + str(w), "y"))
print(c(" config.yaml => screen_height: " + str(h) + "\\n", "y"))

while True:
    print("1. Screenshot  2. Pixel→Rasio  3. Rasio→Pixel  4. Test Tap  5. Keluar")
    ch = input("Pilih: ").strip()
    if ch == "1":
        run("screencap -p /sdcard/calib.png")
        print(c(" Tersimpan di /sdcard/calib.png", "g"))
    elif ch == "2":
        px, py = int(input(f" X pixel (0-{w}): ")), int(input(f" Y pixel (0-{h}): "))
        print(c(f" x: {px/w:.4f}  y: {py/h:.4f}", "g"))
    elif ch == "3":
        rx, ry = float(input(" X rasio: ")), float(input(" Y rasio: "))
        print(c(f" Pixel: ({int(rx*w)}, {int(ry*h)})", "g"))
    elif ch == "4":
        rx, ry = float(input(" X rasio: ")), float(input(" Y rasio: "))
        run(f"input tap {int(rx*w)} {int(ry*h)}")
        print(c(" Tap dikirim!", "g"))
    elif ch == "5":
        break
'''.strip()

TMUX_SH = """#!/data/data/com.termux/files/usr/bin/bash
# Jalankan bot di background dengan tmux
# Bot tetap jalan walau Termux ditutup

SESSION="gamebot"

if tmux has-session -t $SESSION 2>/dev/null; then
    echo "Bot sudah berjalan! Reconnect dengan:"
    echo "  tmux attach -t $SESSION"
else
    tmux new-session -d -s $SESSION "python ~/game-bot/bot.py; read"
    echo "Bot dimulai di background!"
    echo "Lihat bot: tmux attach -t $SESSION"
    echo "Stop bot : tmux kill-session -t $SESSION"
fi
""".strip()

# ============================================================
# FUNGSI INSTALL
# ============================================================

def run_cmd(cmd, desc=""):
    if desc:
        log(desc)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        log(f"  warn: {result.stderr.strip()[:100]}", "yellow")
    return result.returncode == 0

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    log(f"✓ {path.name}", "green")

def main():
    header("GAME BOT INSTALLER - The World of Magic")
    print(c("  Menyiapkan semua yang dibutuhkan...", "cyan"))

    # 1. Update pkg
    header("1/5 — Update Termux")
    run_cmd("pkg update -y -o Dpkg::Options::='--force-confdef'", "Update package list...")

    # 2. Install dependensi sistem
    header("2/5 — Install Paket Sistem")
    packages = ["python", "python-pip", "git", "tmux", "nano"]
    for pkg in packages:
        run_cmd(f"pkg install -y {pkg}", f"Install {pkg}...")

    # 3. Install Python libraries
    header("3/5 — Install Python Libraries")
    pip_packages = ["pyyaml", "colorama", "numpy"]
    for pkg in pip_packages:
        run_cmd(f"pip install -q {pkg}", f"Install {pkg}...")

    # 4. Buat folder & tulis file
    header("4/5 — Membuat File Bot")
    BOT_DIR.mkdir(parents=True, exist_ok=True)
    (BOT_DIR / "logs").mkdir(exist_ok=True)
    (BOT_DIR / "screenshots").mkdir(exist_ok=True)
    (BOT_DIR / "templates").mkdir(exist_ok=True)

    write_file(BOT_DIR / "config.yaml", CONFIG_YAML)
    write_file(BOT_DIR / "bot.py", BOT_PY)
    write_file(BOT_DIR / "calibrate.py", CALIBRATE_PY)
    write_file(BOT_DIR / "start.sh", TMUX_SH)

    # Chmod
    run_cmd(f"chmod +x {BOT_DIR}/start.sh")

    # 5. Selesai
    header("5/5 — Instalasi Selesai! ✅")
    print(c(f"""
  ╔════════════════════════════════════════╗
  ║  Cara pakai:                          ║
  ║                                       ║
  ║  1. Kalibrasi koordinat:              ║
  ║     python ~/game-bot/calibrate.py    ║
  ║                                       ║
  ║  2. Edit konfigurasi:                 ║
  ║     nano ~/game-bot/config.yaml       ║
  ║                                       ║
  ║  3. Jalankan bot:                     ║
  ║     python ~/game-bot/bot.py          ║
  ║                                       ║
  ║  4. Jalankan di background (tmux):    ║
  ║     bash ~/game-bot/start.sh          ║
  ╚════════════════════════════════════════╝
""", "green"))

if __name__ == "__main__":
    main()
