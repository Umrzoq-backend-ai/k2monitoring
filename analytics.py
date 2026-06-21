#!/usr/bin/env python3
"""
School21 Advanced Analytics Tool v2.0

Professional analytics dashboard with:
- Color-coded terminal output
- Interactive menu system
- Data export (JSON/TXT)
- Progress indicators
- Smart error handling & retry logic
- Session caching
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from functools import wraps


# ============================================================================
# ANSI Colors (no external dependency needed)
# ============================================================================

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # Foreground
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

    # Background
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'


    @staticmethod
    def colored(text, color):
        return f"{color}{text}{Colors.RESET}"

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✅ {text}{Colors.RESET}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}❌ {text}{Colors.RESET}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}"

    @staticmethod
    def info_text(text):
        return f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}"


# ============================================================================
# Configuration
# ============================================================================

CONFIG = {
    'auth_url': "https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token",
    'base_url': "https://platform.21-school.ru/services/21-school/api/v1",
    'username': "rrangesi",
    'password': "",
    'timeout': 15,
    'max_retries': 3,
    'retry_delay': 2,
    'cluster_id': 36738,
}


# ============================================================================
# Environment & Config Loader
# ============================================================================

def load_env():
    """Load environment variables from .env file"""
    env_files = ['.env', '../.env', os.path.expanduser('~/.env')]
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ.setdefault(key.strip(), value.strip())
            except (IOError, OSError):
                continue
            break

    CONFIG['password'] = os.environ.get('SCHOOL21_PASSWORD', '')
    if not CONFIG['password']:
        print(Colors.error("SCHOOL21_PASSWORD topilmadi! .env faylni tekshiring."))
        sys.exit(1)


# ============================================================================
# API Client with Retry & Caching
# ============================================================================

class APIClient:
    """Smart API client with retry logic, caching, and token management"""

    def __init__(self):
        self.token = None
        self.token_expires = None
        self.session = requests.Session()
        self.cache = {}
        self.stats = {'requests': 0, 'cached': 0, 'errors': 0}

    def authenticate(self):
        """Authenticate and get access token with retry"""
        for attempt in range(CONFIG['max_retries']):
            try:
                data = {
                    'client_id': 's21-open-api',
                    'username': CONFIG['username'],
                    'password': CONFIG['password'],
                    'grant_type': 'password'
                }
                resp = self.session.post(
                    CONFIG['auth_url'], data=data, timeout=CONFIG['timeout']
                )
                resp.raise_for_status()
                token_data = resp.json()
                self.token = token_data.get('access_token')
                # Token odatda 5 daqiqa amal qiladi
                expires_in = token_data.get('expires_in', 300)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 30)
                return True
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 401:
                    print(Colors.error("Login yoki parol noto'g'ri!"))
                    sys.exit(1)
                if attempt < CONFIG['max_retries'] - 1:
                    time.sleep(CONFIG['retry_delay'])
            except requests.exceptions.ConnectionError:
                if attempt < CONFIG['max_retries'] - 1:
                    print(Colors.warning(f"Ulanish xatosi, qayta urinish... ({attempt + 1})"))
                    time.sleep(CONFIG['retry_delay'])
            except Exception as e:
                if attempt < CONFIG['max_retries'] - 1:
                    time.sleep(CONFIG['retry_delay'])

        print(Colors.error("Autentifikatsiya bajarilmadi!"))
        sys.exit(1)

    def _ensure_token(self):
        """Token muddati o'tganligini tekshirish va yangilash"""
        if not self.token or (self.token_expires and datetime.now() >= self.token_expires):
            self.authenticate()

    def get(self, endpoint, use_cache=True):
        """GET request with caching and retry"""
        self._ensure_token()

        # Cache check
        if use_cache and endpoint in self.cache:
            self.stats['cached'] += 1
            return self.cache[endpoint]

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        for attempt in range(CONFIG['max_retries']):
            try:
                self.stats['requests'] += 1
                resp = self.session.get(
                    f"{CONFIG['base_url']}/{endpoint}",
                    headers=headers,
                    timeout=CONFIG['timeout']
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if use_cache:
                        self.cache[endpoint] = data
                    return data
                elif resp.status_code == 401:
                    # Token expired — refresh
                    self.authenticate()
                    headers['Authorization'] = f'Bearer {self.token}'
                    continue
                elif resp.status_code == 404:
                    return None
                else:
                    self.stats['errors'] += 1
                    if attempt < CONFIG['max_retries'] - 1:
                        time.sleep(CONFIG['retry_delay'])
            except requests.exceptions.Timeout:
                self.stats['errors'] += 1
                if attempt < CONFIG['max_retries'] - 1:
                    time.sleep(CONFIG['retry_delay'])
            except Exception:
                self.stats['errors'] += 1
                return None

        return None


# ============================================================================
# Display Engine
# ============================================================================

class Display:
    """Advanced terminal display engine"""

    @staticmethod
    def banner():
        """Show application banner"""
        print(f"""
{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ███████╗ ██████╗██╗  ██╗ ██████╗  ██████╗ ██╗          ║
    ║     ██╔════╝██╔════╝██║  ██║██╔═══██╗██╔═══██╗██║          ║
    ║     ███████╗██║     ███████║██║   ██║██║   ██║██║          ║
    ║     ╚════██║██║     ██╔══██║██║   ██║██║   ██║██║          ║
    ║     ███████║╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████╗    ║
    ║     ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝    ║
    ║                                                              ║
    ║          📊 Advanced Analytics Dashboard v2.0               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}""")
        print(f"    {Colors.GRAY}⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  "
              f"👤 {CONFIG['username']}{Colors.RESET}\n")

    @staticmethod
    def header(title, icon="📋"):
        """Section header with gradient effect"""
        width = 60
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'━' * width}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}  {icon} {title.upper()}{Colors.RESET}")
        print(f"{Colors.BLUE}{'━' * width}{Colors.RESET}")

    @staticmethod
    def subheader(title):
        print(f"\n  {Colors.CYAN}▸ {title}{Colors.RESET}")

    @staticmethod
    def kv(key, value, color=None):
        """Key-value pair display"""
        val_color = color or Colors.WHITE
        print(f"    {Colors.GRAY}{key:<22}{Colors.RESET} {val_color}{value}{Colors.RESET}")

    @staticmethod
    def table_header(*columns):
        """Print table header"""
        fmt = "    "
        sep = "    "
        for col, width in columns:
            fmt += f"{Colors.BOLD}{col:<{width}}{Colors.RESET} "
            sep += f"{'─' * width} "
        print(fmt)
        print(f"{Colors.GRAY}{sep}{Colors.RESET}")

    @staticmethod
    def separator():
        print(f"    {Colors.GRAY}{'─' * 50}{Colors.RESET}")

    @staticmethod
    def progress_bar(current, total, width=30, label=""):
        """Visual progress bar"""
        if total == 0:
            pct = 0
        else:
            pct = min(current / total, 1.0)
        filled = int(width * pct)
        bar = '█' * filled + '░' * (width - filled)
        pct_str = f"{pct*100:.0f}%"
        color = Colors.GREEN if pct >= 0.7 else Colors.YELLOW if pct >= 0.4 else Colors.RED
        print(f"    {label:<15} {color}{bar}{Colors.RESET} {pct_str}")

    @staticmethod
    def status_badge(status):
        """Colored status badge"""
        status_colors = {
            'completed': Colors.GREEN,
            'active': Colors.BLUE,
            'in_progress': Colors.YELLOW,
            'available': Colors.CYAN,
            'failed': Colors.RED,
            'locked': Colors.GRAY,
        }
        color = status_colors.get(status.lower(), Colors.WHITE) if isinstance(status, str) else Colors.WHITE
        return f"{color}{status}{Colors.RESET}"


# ============================================================================
# Analytics Modules
# ============================================================================

class Analytics:
    """All analytics sections"""

    def __init__(self, client: APIClient):
        self.client = client
        self.login = CONFIG['username']
        self.collected_data = {}

    def participant_info(self):
        """Foydalanuvchi profili"""
        Display.header("PROFIL MA'LUMOTLARI", "👤")

        data = self.client.get(f"participants/{self.login}")
        if not data:
            print(f"    {Colors.warning('Ma`lumot olinmadi')}")
            return

        self.collected_data['participant'] = data

        Display.kv("Login", data.get('login', 'N/A'), Colors.GREEN)
        Display.kv("Class", data.get('className', 'N/A'), Colors.CYAN)
        Display.kv("Parallel", data.get('parallelName', 'N/A'))
        Display.kv("Campus", data.get('campusName', 'N/A'))
        Display.kv("Status", data.get('status', 'N/A'),
                   Colors.GREEN if data.get('status') == 'Active' else Colors.YELLOW)
        Display.kv("Email", data.get('email', 'N/A'))

        # Level & XP with progress bar
        level = data.get('level', 0)
        xp = data.get('expValue', 0)
        xp_next = data.get('expToNextLevel', 1)

        Display.subheader("Level & XP")
        Display.kv("Level", f"⭐ {level}", Colors.YELLOW)
        Display.kv("XP", f"{xp:,}", Colors.GREEN)
        if xp_next:
            Display.progress_bar(xp, xp + xp_next, label="Keyingi level")

    def logtime(self):
        """Logtime statistikasi"""
        Display.header("LOGTIME", "⏱️")

        data = self.client.get(f"participants/{self.login}/logtime")
        if not data:
            print(f"    {Colors.warning('Logtime olinmadi')}")
            return

        self.collected_data['logtime'] = data

        days = []
        if isinstance(data, dict):
            days = data.get('days', [])
        elif isinstance(data, list):
            days = data

        if days:
            Display.table_header(("Kun", 12), ("Soat", 8), ("Grafik", 20))
            total_minutes = 0
            max_minutes = max((d.get('minutes', 0) for d in days[-7:] if isinstance(d, dict)), default=1)

            for day in days[-7:]:
                if isinstance(day, dict):
                    date = day.get('date', 'N/A')
                    minutes = day.get('minutes', 0)
                    total_minutes += minutes
                    hours = round(minutes / 60, 1)
                    # Mini bar
                    bar_len = int((minutes / max(max_minutes, 1)) * 15)
                    bar = f"{Colors.GREEN}{'▓' * bar_len}{'░' * (15 - bar_len)}{Colors.RESET}"
                    print(f"    {date:<12} {hours:<8} {bar}")

            Display.separator()
            total_hours = round(total_minutes / 60, 1)
            avg_hours = round(total_hours / max(len(days[-7:]), 1), 1)
            Display.kv("Jami (7 kun)", f"{total_hours} soat", Colors.GREEN)
            Display.kv("O'rtacha/kun", f"{avg_hours} soat", Colors.CYAN)
        else:
            Display.kv("Logtime (raw)", str(data)[:100])

    def points(self):
        """Ballar tizimi"""
        Display.header("BALLAR", "💰")

        data = self.client.get(f"participants/{self.login}/points")
        if not data:
            print(f"    {Colors.warning('Ballar olinmadi')}")
            return

        self.collected_data['points'] = data

        prp = data.get('peerReviewPoints', 0)
        coins = data.get('coins', 0)
        crp = data.get('codeReviewPoints', 0)

        Display.kv("Peer Review Points", f"🔄 {prp}", Colors.MAGENTA)
        Display.kv("Coins", f"🪙 {coins}", Colors.YELLOW)
        Display.kv("Code Review Points", f"📝 {crp}", Colors.CYAN)

        # Qo'shimcha fieldlar
        known_keys = {'peerReviewPoints', 'coins', 'codeReviewPoints'}
        for key, val in data.items():
            if key not in known_keys:
                Display.kv(key, val)

    def coalition(self):
        """Coalition/Tribe"""
        Display.header("COALITION", "🏛️")

        data = self.client.get(f"participants/{self.login}/coalition")
        if not data:
            print(f"    {Colors.warning('Coalition olinmadi')}")
            return

        self.collected_data['coalition'] = data

        Display.kv("Nomi", data.get('name', 'N/A'), Colors.BOLD)
        Display.kv("Score", f"⚡ {data.get('score', 'N/A')}", Colors.YELLOW)
        Display.kv("Rang", data.get('color', 'N/A'))

        known_keys = {'name', 'score', 'color'}
        for key, val in data.items():
            if key not in known_keys:
                Display.kv(key, val)

    def projects(self):
        """Loyihalar ro'yxati"""
        Display.header("LOYIHALAR", "📁")

        data = self.client.get(f"participants/{self.login}/projects")
        if not data:
            print(f"    {Colors.warning('Loyihalar olinmadi')}")
            return

        self.collected_data['projects'] = data

        if not isinstance(data, list):
            Display.kv("Projects (raw)", str(data)[:200])
            return

        # Statistika
        completed = [p for p in data if isinstance(p, dict) and p.get('status', '').lower() in ('completed', 'finished')]
        in_progress = [p for p in data if isinstance(p, dict) and p.get('status', '').lower() in ('in_progress', 'active')]

        Display.subheader("Statistika")
        Display.kv("Jami", len(data))
        Display.kv("Tugatilgan", f"{len(completed)} ✅", Colors.GREEN)
        Display.kv("Jarayonda", f"{len(in_progress)} 🔄", Colors.YELLOW)

        # Table
        Display.subheader("Loyihalar ro'yxati")
        Display.table_header(("Loyiha", 28), ("Status", 14), ("Baho", 6))

        for project in data:
            if isinstance(project, dict):
                name = project.get('name', project.get('projectName', 'N/A'))[:27]
                status = project.get('status', 'N/A')
                grade = project.get('finalMark', project.get('mark', '-'))
                status_display = Display.status_badge(status)
                grade_color = Colors.GREEN if isinstance(grade, (int, float)) and grade >= 80 else Colors.YELLOW
                grade_str = f"{grade_color}{grade}{Colors.RESET}" if grade != '-' else Colors.GRAY + '-' + Colors.RESET
                print(f"    {name:<28} {status_display:<26} {grade_str}")

        Display.separator()
        if completed:
            grades = [p.get('finalMark', 0) for p in completed if isinstance(p.get('finalMark'), (int, float))]
            if grades:
                avg_grade = sum(grades) / len(grades)
                Display.kv("O'rtacha baho", f"{avg_grade:.1f}", Colors.GREEN)

    def skills(self):
        """Skills analitikasi"""
        Display.header("SKILLS", "🎯")

        data = self.client.get(f"participants/{self.login}/skills")
        if not data:
            print(f"    {Colors.warning('Skills olinmadi')}")
            return

        self.collected_data['skills'] = data

        skills_list = data.get('skills', data) if isinstance(data, dict) else data
        if not isinstance(skills_list, list):
            Display.kv("Skills (raw)", str(data)[:200])
            return

        # Sort by points
        sorted_skills = sorted(
            skills_list,
            key=lambda x: x.get('points', 0) if isinstance(x, dict) else 0,
            reverse=True
        )

        max_points = max((s.get('points', 0) for s in sorted_skills if isinstance(s, dict)), default=1)

        Display.table_header(("Skill", 28), ("Points", 8), ("Grafik", 22))

        for skill in sorted_skills:
            if isinstance(skill, dict):
                name = skill.get('name', 'N/A')[:27]
                points = skill.get('points', 0)
                # Color-coded progress bar
                pct = points / max(max_points, 1)
                bar_len = int(pct * 18)
                if pct >= 0.7:
                    bar_color = Colors.GREEN
                elif pct >= 0.4:
                    bar_color = Colors.YELLOW
                else:
                    bar_color = Colors.RED
                bar = f"{bar_color}{'█' * bar_len}{'░' * (18 - bar_len)}{Colors.RESET}"
                print(f"    {name:<28} {points:<8} {bar}")

        Display.separator()
        Display.kv("Jami skills", len(skills_list), Colors.CYAN)
        total_pts = sum(s.get('points', 0) for s in skills_list if isinstance(s, dict))
        Display.kv("Jami points", f"{total_pts:,}", Colors.GREEN)

    def achievements(self):
        """Yutuqlar"""
        Display.header("ACHIEVEMENTS", "🏆")

        data = self.client.get(f"participants/{self.login}/achievements")
        if not data:
            print(f"    {Colors.warning('Achievements olinmadi')}")
            return

        self.collected_data['achievements'] = data

        if isinstance(data, list):
            for ach in data:
                if isinstance(ach, dict):
                    name = ach.get('name', ach.get('title', 'N/A'))
                    desc = ach.get('description', '')[:50]
                    print(f"    {Colors.YELLOW}🥇 {name}{Colors.RESET}")
                    if desc:
                        print(f"       {Colors.GRAY}{desc}{Colors.RESET}")
                else:
                    print(f"    🥇 {ach}")
            Display.separator()
            Display.kv("Jami achievements", len(data), Colors.YELLOW)
        else:
            Display.kv("Achievements (raw)", str(data)[:200])

    def feedbacks(self):
        """Feedbacklar"""
        Display.header("FEEDBACKS", "💬")

        data = self.client.get(f"participants/{self.login}/feedbacks")
        if not data:
            print(f"    {Colors.warning('Feedbacks olinmadi')}")
            return

        self.collected_data['feedbacks'] = data

        if isinstance(data, list):
            for fb in data[:10]:
                if isinstance(fb, dict):
                    reviewer = fb.get('reviewer', fb.get('from', 'Anonim'))
                    comment = fb.get('comment', fb.get('text', ''))[:70]
                    rating = fb.get('rating', '')
                    stars = '⭐' * int(rating) if isinstance(rating, (int, float)) else ''
                    print(f"    {Colors.CYAN}💬 {reviewer}{Colors.RESET} {stars}")
                    if comment:
                        print(f"       {Colors.GRAY}\"{comment}\"{Colors.RESET}")
                    print()
            Display.separator()
            Display.kv("Jami feedbacklar", len(data), Colors.CYAN)
        else:
            Display.kv("Feedbacks (raw)", str(data)[:200])

    def cluster_map(self):
        """Klaster xaritasi"""
        Display.header("CLUSTER MAP (Tillakori)", "🖥️")

        data = self.client.get(f"clusters/{CONFIG['cluster_id']}/map")
        if not data:
            print(f"    {Colors.warning('Cluster map olinmadi')}")
            return

        self.collected_data['cluster'] = data

        workplaces = data.get('clusterMap', data if isinstance(data, list) else [])
        occupied = [wp for wp in workplaces if isinstance(wp, dict) and wp.get('login')]
        empty_count = len(workplaces) - len(occupied)
        total = len(workplaces)

        # Visual occupancy
        Display.subheader("Bandlik holati")
        Display.progress_bar(len(occupied), total, label="Band/Jami")
        print()
        Display.kv("Jami kompyuterlar", total)
        Display.kv("Band", f"{len(occupied)} 🔴", Colors.RED)
        Display.kv("Bo'sh", f"{empty_count} 🟢", Colors.GREEN)

        if occupied:
            Display.subheader("Hozir klasterda")
            Display.table_header(("Joy", 8), ("Login", 20), ("Vaqt", 12))
            for wp in sorted(occupied, key=lambda x: (x.get('row', ''), x.get('number', 0))):
                row = wp.get('row', '?').upper()
                num = wp.get('number', '?')
                login = wp.get('login', 'N/A')
                since = wp.get('since', '')
                if since:
                    try:
                        dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                        since = dt.strftime('%H:%M')
                    except (ValueError, TypeError):
                        since = str(since)[:10]
                place = f"{row}{num}"
                print(f"    {Colors.YELLOW}{place:<8}{Colors.RESET} "
                      f"{Colors.WHITE}{login:<20}{Colors.RESET} {Colors.GRAY}{since}{Colors.RESET}")

    def campuses(self):
        """Kampuslar"""
        Display.header("CAMPUSES", "🏫")

        data = self.client.get("campuses")
        if not data:
            print(f"    {Colors.warning('Campuses olinmadi')}")
            return

        self.collected_data['campuses'] = data

        campuses_list = data.get('campuses', data) if isinstance(data, dict) else data
        if isinstance(campuses_list, list):
            Display.table_header(("#", 4), ("Qisqa nomi", 25), ("To'liq nomi", 30))
            for i, campus in enumerate(campuses_list, 1):
                if isinstance(campus, dict):
                    short = campus.get('shortName', campus.get('name', 'N/A'))[:24]
                    full = campus.get('fullName', '')[:29]
                    print(f"    {i:<4} {Colors.CYAN}{short:<25}{Colors.RESET} {full}")
            Display.separator()
            Display.kv("Jami kampuslar", len(campuses_list))
        else:
            Display.kv("Campuses (raw)", str(data)[:300])

    def coalitions(self):
        """Coalitionlar reytingi"""
        Display.header("COALITIONS RATING", "⚔️")

        data = self.client.get("coalitions")
        if not data:
            print(f"    {Colors.warning('Coalitions olinmadi')}")
            return

        self.collected_data['coalitions'] = data

        if isinstance(data, list):
            # Sort by score
            sorted_coals = sorted(data, key=lambda x: x.get('score', 0) if isinstance(x, dict) else 0, reverse=True)
            max_score = max((c.get('score', 0) for c in sorted_coals if isinstance(c, dict)), default=1)

            medals = ['🥇', '🥈', '🥉', '  ']
            Display.table_header(("", 4), ("Nomi", 20), ("Score", 10), ("Rating", 20))

            for i, coal in enumerate(sorted_coals):
                if isinstance(coal, dict):
                    medal = medals[i] if i < 3 else '  '
                    name = coal.get('name', 'N/A')[:19]
                    score = coal.get('score', 0)
                    # Mini bar
                    bar_len = int((score / max(max_score, 1)) * 15)
                    bar = f"{Colors.GREEN}{'▓' * bar_len}{'░' * (15 - bar_len)}{Colors.RESET}"
                    print(f"    {medal:<4} {name:<20} {score:<10} {bar}")
        else:
            Display.kv("Coalitions (raw)", str(data)[:300])

    def events(self):
        """Eventlar"""
        Display.header("EVENTS", "📅")

        data = self.client.get("events")
        if not data:
            print(f"    {Colors.warning('Events olinmadi')}")
            return

        self.collected_data['events'] = data

        if isinstance(data, list):
            now = datetime.now()
            upcoming = []
            past = []

            for event in data:
                if isinstance(event, dict):
                    date_str = event.get('date', event.get('startDate', ''))
                    try:
                        event_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        if event_date.replace(tzinfo=None) >= now:
                            upcoming.append(event)
                        else:
                            past.append(event)
                    except (ValueError, TypeError):
                        upcoming.append(event)

            if upcoming:
                Display.subheader(f"Kelgusi eventlar ({len(upcoming)})")
                for event in upcoming[:8]:
                    name = event.get('name', event.get('title', 'N/A'))[:40]
                    date = event.get('date', event.get('startDate', 'N/A'))[:16]
                    print(f"    {Colors.GREEN}📌 {name}{Colors.RESET}")
                    print(f"       {Colors.GRAY}📆 {date}{Colors.RESET}")

            if past:
                Display.subheader(f"O'tgan eventlar ({len(past)})")
                for event in past[:5]:
                    name = event.get('name', event.get('title', 'N/A'))[:40]
                    date = event.get('date', event.get('startDate', 'N/A'))[:16]
                    print(f"    {Colors.GRAY}📌 {name} — {date}{Colors.RESET}")

            Display.separator()
            Display.kv("Jami eventlar", len(data))
        else:
            Display.kv("Events (raw)", str(data)[:300])

    def notifications(self):
        """Bildirishnomalar"""
        Display.header("NOTIFICATIONS", "🔔")

        data = self.client.get("notifications")
        if not data:
            print(f"    {Colors.warning('Notifications olinmadi')}")
            return

        self.collected_data['notifications'] = data

        if isinstance(data, list):
            for notif in data[:8]:
                if isinstance(notif, dict):
                    text = notif.get('text', notif.get('message', 'N/A'))[:70]
                    date = notif.get('date', notif.get('createdAt', ''))[:16]
                    is_read = notif.get('isRead', notif.get('read', True))
                    icon = '📩' if not is_read else '📧'
                    color = Colors.WHITE if not is_read else Colors.GRAY
                    print(f"    {color}{icon} {text}{Colors.RESET}")
                    if date:
                        print(f"       {Colors.GRAY}{date}{Colors.RESET}")
            Display.separator()
            Display.kv("Jami", len(data))
            unread = sum(1 for n in data if isinstance(n, dict) and not n.get('isRead', n.get('read', True)))
            if unread:
                Display.kv("O'qilmagan", f"{unread} 🔴", Colors.RED)
        else:
            Display.kv("Notifications (raw)", str(data)[:300])


# ============================================================================
# Export Engine
# ============================================================================

class Exporter:
    """Ma'lumotlarni export qilish"""

    @staticmethod
    def to_json(data, filename=None):
        """Export to JSON"""
        if not filename:
            filename = f"analytics_{CONFIG['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(Colors.success(f"JSON saqlandi: {filename}"))
            return filename
        except IOError as e:
            print(Colors.error(f"JSON saqlashda xatolik: {e}"))
            return None

    @staticmethod
    def to_txt(data, filename=None):
        """Export to TXT summary"""
        if not filename:
            filename = f"analytics_{CONFIG['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"School21 Analytics Report\n")
                f.write(f"User: {CONFIG['username']}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'=' * 50}\n\n")

                for section, section_data in data.items():
                    f.write(f"\n{'─' * 40}\n")
                    f.write(f"{section.upper()}\n")
                    f.write(f"{'─' * 40}\n")
                    if isinstance(section_data, dict):
                        for k, v in section_data.items():
                            f.write(f"  {k}: {v}\n")
                    elif isinstance(section_data, list):
                        f.write(f"  Items: {len(section_data)}\n")
                        for item in section_data[:20]:
                            if isinstance(item, dict):
                                name = item.get('name', item.get('title', str(item)[:50]))
                                f.write(f"  - {name}\n")
                    else:
                        f.write(f"  {section_data}\n")

            print(Colors.success(f"TXT saqlandi: {filename}"))
            return filename
        except IOError as e:
            print(Colors.error(f"TXT saqlashda xatolik: {e}"))
            return None


# ============================================================================
# Interactive Menu
# ============================================================================

class Menu:
    """Interactive menu system"""

    SECTIONS = [
        ('1', 'Profil', 'participant_info'),
        ('2', 'Logtime', 'logtime'),
        ('3', 'Ballar', 'points'),
        ('4', 'Coalition', 'coalition'),
        ('5', 'Loyihalar', 'projects'),
        ('6', 'Skills', 'skills'),
        ('7', 'Achievements', 'achievements'),
        ('8', 'Feedbacks', 'feedbacks'),
        ('9', 'Cluster Map', 'cluster_map'),
        ('10', 'Campuses', 'campuses'),
        ('11', 'Coalitions Rating', 'coalitions'),
        ('12', 'Events', 'events'),
        ('13', 'Notifications', 'notifications'),
    ]

    @staticmethod
    def show():
        """Show interactive menu"""
        print(f"\n{Colors.BOLD}  ╔══════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}  ║         📋 MENU                      ║{Colors.RESET}")
        print(f"{Colors.BOLD}  ╠══════════════════════════════════════╣{Colors.RESET}")

        for num, name, _ in Menu.SECTIONS:
            print(f"{Colors.BOLD}  ║  {Colors.CYAN}{num:>2}{Colors.RESET}{Colors.BOLD}. {name:<31}║{Colors.RESET}")

        print(f"{Colors.BOLD}  ╠══════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.BOLD}  ║  {Colors.GREEN} a{Colors.RESET}{Colors.BOLD}. Hammasi                       ║{Colors.RESET}")
        print(f"{Colors.BOLD}  ║  {Colors.YELLOW} e{Colors.RESET}{Colors.BOLD}. Export (JSON)                  ║{Colors.RESET}")
        print(f"{Colors.BOLD}  ║  {Colors.YELLOW} t{Colors.RESET}{Colors.BOLD}. Export (TXT)                   ║{Colors.RESET}")
        print(f"{Colors.BOLD}  ║  {Colors.RED} q{Colors.RESET}{Colors.BOLD}. Chiqish                        ║{Colors.RESET}")
        print(f"{Colors.BOLD}  ╚══════════════════════════════════════╝{Colors.RESET}")

    @staticmethod
    def get_choice():
        """Get user choice"""
        try:
            return input(f"\n  {Colors.CYAN}▸ Tanlang:{Colors.RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 'q'


# ============================================================================
# Main Application
# ============================================================================

def run_all(analytics):
    """Barcha bo'limlarni ishga tushirish"""
    sections = [
        analytics.participant_info,
        analytics.logtime,
        analytics.points,
        analytics.coalition,
        analytics.projects,
        analytics.skills,
        analytics.achievements,
        analytics.feedbacks,
        analytics.cluster_map,
        analytics.campuses,
        analytics.coalitions,
        analytics.events,
        analytics.notifications,
    ]

    total = len(sections)
    for i, section in enumerate(sections, 1):
        try:
            section()
        except Exception as e:
            print(Colors.error(f"Xatolik: {e}"))
        # Progress
        print(f"\n    {Colors.GRAY}[{i}/{total}] ━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")


def main():
    """Main entry point"""
    load_env()

    # Parse command line args
    args = sys.argv[1:]
    interactive_mode = '--interactive' in args or '-i' in args
    run_all_mode = '--all' in args or '-a' in args or not args

    # Initialize
    Display.banner()

    # Authenticate
    print(f"  {Colors.YELLOW}🔐 Autentifikatsiya...{Colors.RESET}")
    client = APIClient()
    client.authenticate()
    print(f"  {Colors.success('Token olindi!')}")

    analytics = Analytics(client)

    if interactive_mode:
        # Interactive mode
        while True:
            Menu.show()
            choice = Menu.get_choice()

            if choice == 'q':
                print(f"\n  {Colors.success('Ko`rishguncha! 👋')}\n")
                break
            elif choice == 'a':
                run_all(analytics)
            elif choice == 'e':
                if analytics.collected_data:
                    Exporter.to_json(analytics.collected_data)
                else:
                    print(Colors.warning("Avval ma'lumot yig'ing (a tanlang)"))
            elif choice == 't':
                if analytics.collected_data:
                    Exporter.to_txt(analytics.collected_data)
                else:
                    print(Colors.warning("Avval ma'lumot yig'ing (a tanlang)"))
            else:
                # Run specific section
                found = False
                for num, name, method_name in Menu.SECTIONS:
                    if choice == num:
                        method = getattr(analytics, method_name, None)
                        if method:
                            try:
                                method()
                            except Exception as e:
                                print(Colors.error(f"Xatolik: {e}"))
                        found = True
                        break
                if not found:
                    print(Colors.warning("Noto'g'ri tanlov!"))
    else:
        # Run all sections
        run_all(analytics)

        # Export option
        if '--export-json' in args:
            Exporter.to_json(analytics.collected_data)
        if '--export-txt' in args:
            Exporter.to_txt(analytics.collected_data)

    # Footer stats
    print(f"\n{'━' * 60}")
    print(f"  {Colors.BOLD}📊 Session statistikasi:{Colors.RESET}")
    Display.kv("API so'rovlar", client.stats['requests'])
    Display.kv("Keshdan", client.stats['cached'])
    Display.kv("Xatoliklar", client.stats['errors'],
               Colors.RED if client.stats['errors'] > 0 else Colors.GREEN)
    Display.kv("Bo'limlar", len(analytics.collected_data))
    print(f"{'━' * 60}\n")


if __name__ == "__main__":
    main()
