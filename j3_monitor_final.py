#!/usr/bin/env python3
"""
K2 Workplace Monitor Bot

A Telegram bot that monitors K2 workplace in Tillakori cluster
and sends notifications when users login/logout.

Author: rrangesi
License: MIT
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

import requests
from flask import Flask


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class Config:
    """Application configuration"""
    # School21 API
    SCHOOL21_USERNAME: str = "rrangesi"
    SCHOOL21_PASSWORD: str = ""  # Load from .env
    
    # Monitoring settings
    CLUSTER_ID: int = 36738  # Tillakori
    TARGET_ROW: str = "k"
    TARGET_NUMBER: int = 2
    CHECK_INTERVAL: int = 60  # seconds
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Logging
    LOG_FILE: str = "k2_monitor.log"
    LOG_LEVEL: int = logging.INFO
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        config = cls()
        
        # Try to load from .env file first (for local development)
        env_vars = cls._load_env_file()
        
        # Get from environment variables (Render.com) or .env file
        config.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', env_vars.get('TELEGRAM_BOT_TOKEN', ''))
        config.TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', env_vars.get('TELEGRAM_CHAT_ID', ''))
        config.SCHOOL21_PASSWORD = os.environ.get('SCHOOL21_PASSWORD', env_vars.get('SCHOOL21_PASSWORD', ''))
        config.SCHOOL21_USERNAME = os.environ.get('SCHOOL21_USERNAME', env_vars.get('SCHOOL21_USERNAME', config.SCHOOL21_USERNAME))
        
        # Workplace configuration
        target_row = os.environ.get('TARGET_ROW', env_vars.get('TARGET_ROW', 'k'))
        config.TARGET_ROW = target_row.lower()
        
        target_number = os.environ.get('TARGET_NUMBER', env_vars.get('TARGET_NUMBER', '2'))
        config.TARGET_NUMBER = int(target_number)
        
        return config
    
    @staticmethod
    def _load_env_file() -> Dict[str, str]:
        """Load environment variables from .env file (for local development)"""
        env_vars = {}
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except FileNotFoundError:
            # .env file not found - this is normal on Render.com
            pass
        return env_vars


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure logging"""
    logger = logging.getLogger('K2Monitor')
    logger.setLevel(config.LOG_LEVEL)
    
    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(config.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# School21 API Client
# ============================================================================

class School21APIError(Exception):
    """School21 API error"""
    pass


class School21API:
    """School21 API client with automatic token refresh"""
    
    AUTH_URL = "https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token"
    BASE_URL = "https://platform.21-school.ru/services/21-school/api/v1"
    TOKEN_LIFETIME = 300  # 5 minutes
    
    def __init__(self, username: str, password: str, logger: logging.Logger):
        self.username = username
        self.password = password
        self.logger = logger
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
    
    def authenticate(self) -> bool:
        """Authenticate and obtain access token"""
        data = {
            'client_id': 's21-open-api',
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
        }
        
        try:
            response = requests.post(
                self.AUTH_URL,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            response.raise_for_status()
            
            tokens = response.json()
            self._access_token = tokens.get('access_token')
            self._token_expires_at = time.time() + self.TOKEN_LIFETIME
            
            self.logger.info("Authentication successful")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def _ensure_authenticated(self) -> None:
        """Ensure valid access token exists"""
        if not self._access_token or time.time() >= self._token_expires_at:
            if not self.authenticate():
                raise School21APIError("Failed to authenticate")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization"""
        return {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make authenticated API request"""
        self._ensure_authenticated()
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API request failed ({endpoint}): {e}")
            return None
    
    def get_cluster_map(self, cluster_id: int) -> Optional[Dict[str, Any]]:
        """Get cluster map"""
        return self._make_request(f"clusters/{cluster_id}/map?limit=250")
    
    def get_participant_info(self, login: str) -> Optional[Dict[str, Any]]:
        """Get participant information"""
        return self._make_request(f"participants/{login}")
    
    def get_participant_logtime(self, login: str) -> Optional[Any]:
        """Get participant logtime"""
        return self._make_request(f"participants/{login}/logtime")
    
    def get_participant_points(self, login: str) -> Optional[Dict[str, Any]]:
        """Get participant points"""
        return self._make_request(f"participants/{login}/points")
    
    def get_participant_coalition(self, login: str) -> Optional[Dict[str, Any]]:
        """Get participant coalition"""
        return self._make_request(f"participants/{login}/coalition")


# ============================================================================
# Telegram Bot Client
# ============================================================================

class TelegramBot:
    """Telegram bot client"""
    
    def __init__(self, bot_token: str, chat_id: str, logger: logging.Logger):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = logger
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.user_data_cache: Dict[str, Dict[str, Any]] = {}
    
    def send_message(self, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_markup:
                data['reply_markup'] = reply_markup
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def get_updates(self, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get bot updates"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to get updates: {e}")
        
        return None
    
    @staticmethod
    def create_keyboard() -> Dict[str, Any]:
        """Create reply keyboard with 'Batafsil' button"""
        return {
            'keyboard': [[{'text': 'Batafsil'}]],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }


# ============================================================================
# User Details Formatter
# ============================================================================

class UserDetailsFormatter:
    """Format user details for display"""
    
    @staticmethod
    def format_short_message(login: str, event_type: str) -> str:
        """Format short notification message"""
        if event_type == "LOGIN":
            return f"<b>Login qilindi</b>\nNick: <code>{login}</code>"
        else:
            return f"<b>Logout qilindi</b>\nNick: <code>{login}</code>"
    
    @staticmethod
    def format_detailed_message(details: Dict[str, Any]) -> str:
        """Format detailed user information"""
        msg = f"<b>Login:</b> <code>{details.get('login', 'N/A')}</code>\n"
        msg += f"<b>Vaqt:</b> {details.get('timestamp', 'N/A')}\n"
        msg += "─────────────────────────\n"
        
        msg += f"<b>Sinf:</b> {details.get('class', 'N/A')}\n"
        msg += f"<b>Level:</b> {details.get('level', 'N/A')} | <b>XP:</b> {details.get('xp', 'N/A')}\n"
        
        if details.get('coalition'):
            msg += f"<b>Tribe:</b> {details['coalition']}\n"
        
        if details.get('weekly_hours'):
            msg += f"<b>Haftalik logtime:</b> {details['weekly_hours']} soat\n"
        
        if 'prp' in details or 'coins' in details:
            msg += "─────────────────────────\n"
            msg += f"<b>PRP:</b> {details.get('prp', 0)} | <b>Coins:</b> {details.get('coins', 0)}"
        
        return msg


# ============================================================================
# User Details Fetcher
# ============================================================================

class UserDetailsFetcher:
    """Fetch and aggregate user details from API"""
    
    def __init__(self, api: School21API):
        self.api = api
    
    def fetch(self, login: str) -> Dict[str, Any]:
        """Fetch complete user details"""
        details = {
            'login': login,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Basic info
        info = self.api.get_participant_info(login)
        if info:
            details['class'] = info.get('className', 'N/A')
            details['level'] = info.get('level', 'N/A')
            details['xp'] = info.get('expValue', 'N/A')
        
        # Logtime
        logtime = self.api.get_participant_logtime(login)
        if logtime:
            details['weekly_hours'] = self._parse_logtime(logtime)
        
        # Points
        points = self.api.get_participant_points(login)
        if points:
            details['prp'] = points.get('peerReviewPoints', 0)
            details['coins'] = points.get('coins', 0)
        
        # Coalition
        coalition = self.api.get_participant_coalition(login)
        if coalition:
            details['coalition'] = coalition.get('name', 'N/A')
        
        return details
    
    @staticmethod
    def _parse_logtime(logtime: Any) -> Optional[float]:
        """Parse logtime data"""
        if isinstance(logtime, dict):
            days = logtime.get('days', [])
            if days:
                total_minutes = sum(day.get('minutes', 0) for day in days)
                return round(total_minutes / 60, 1)
        elif isinstance(logtime, (int, float)):
            return round(logtime, 1)
        return None


# ============================================================================
# Workplace Monitor
# ============================================================================

class WorkplaceMonitor:
    """Monitor specific workplace for login/logout events"""
    
    def __init__(
        self,
        api: School21API,
        telegram: TelegramBot,
        config: Config,
        logger: logging.Logger
    ):
        self.api = api
        self.telegram = telegram
        self.config = config
        self.logger = logger
        self.formatter = UserDetailsFormatter()
        self.fetcher = UserDetailsFetcher(api)
        
        self.current_user: Optional[str] = None
        self.login_time: Optional[datetime] = None
    
    def get_current_user(self) -> Optional[str]:
        """Get current user at monitored workplace"""
        cluster_map = self.api.get_cluster_map(self.config.CLUSTER_ID)
        if not cluster_map:
            return None
        
        workplaces = cluster_map.get('clusterMap', [])
        for wp in workplaces:
            if (wp.get('row') == self.config.TARGET_ROW and 
                wp.get('number') == self.config.TARGET_NUMBER):
                return wp.get('login')
        
        return None
    
    def handle_login(self, login: str) -> None:
        """Handle user login event"""
        self.logger.info(f"Login detected: {login}")
        
        # Fetch and cache user details
        details = self.fetcher.fetch(login)
        self.telegram.user_data_cache[login] = details
        
        # Send notification
        message = self.formatter.format_short_message(login, "LOGIN")
        keyboard = TelegramBot.create_keyboard()
        self.telegram.send_message(message, keyboard)
        
        # Update state
        self.current_user = login
        self.login_time = datetime.now()
    
    def handle_logout(self, login: str) -> None:
        """Handle user logout event"""
        duration = (datetime.now() - self.login_time).total_seconds() / 60
        self.logger.info(f"Logout detected: {login} (duration: {duration:.1f} min)")
        
        # Send notification
        message = self.formatter.format_short_message(login, "LOGOUT")
        message += f"\n<b>Davomiyligi:</b> {duration:.1f} daqiqa"
        self.telegram.send_message(message)
        
        # Update state
        self.current_user = None
        self.login_time = None
    
    def run(self) -> None:
        """Run monitoring loop"""
        self.logger.info("Workplace monitor started")
        self.logger.info(f"Monitoring: Cluster {self.config.CLUSTER_ID}, "
                        f"{self.config.TARGET_ROW.upper()}{self.config.TARGET_NUMBER}")
        
        # Check initial state
        current_login = self.get_current_user()
        if current_login:
            self.handle_login(current_login)
        else:
            self.logger.info("Workplace is currently empty")
        
        # Monitoring loop
        try:
            while True:
                time.sleep(self.config.CHECK_INTERVAL)
                
                new_login = self.get_current_user()
                
                # Login event
                if new_login and new_login != self.current_user:
                    self.handle_login(new_login)
                
                # Logout event
                elif not new_login and self.current_user:
                    self.handle_logout(self.current_user)
        
        except KeyboardInterrupt:
            self.logger.info("Monitor stopped by user")


# ============================================================================
# Message Handler
# ============================================================================

class MessageHandler:
    """Handle incoming Telegram messages"""
    
    def __init__(
        self,
        telegram: TelegramBot,
        monitor: WorkplaceMonitor,
        logger: logging.Logger
    ):
        self.telegram = telegram
        self.monitor = monitor
        self.logger = logger
        self.formatter = UserDetailsFormatter()
        self.fetcher = UserDetailsFetcher(monitor.api)
    
    def handle_batafsil_request(self) -> None:
        """Handle 'Batafsil' button press"""
        if not self.monitor.current_user:
            self.telegram.send_message("Hozirda bo'sh.")
            return
        
        login = self.monitor.current_user
        
        # Get details from cache or fetch new
        if login in self.telegram.user_data_cache:
            details = self.telegram.user_data_cache[login]
        else:
            details = self.fetcher.fetch(login)
        
        # Send detailed message
        message = self.formatter.format_detailed_message(details)
        self.telegram.send_message(message)
    
    def run(self) -> None:
        """Run message handling loop"""
        offset = 0
        
        while True:
            try:
                updates = self.telegram.get_updates(offset)
                
                if updates and updates.get('result'):
                    for update in updates['result']:
                        offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            message = update['message']
                            text = message.get('text', '').strip()
                            
                            if text == 'Batafsil':
                                self.handle_batafsil_request()
            
            except Exception as e:
                self.logger.error(f"Message handler error: {e}")
                time.sleep(5)


# ============================================================================
# Flask Web Server (for Render.com keep-alive)
# ============================================================================

# Flask app for health check
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    """Health check endpoint"""
    return {
        'status': 'alive',
        'bot': 'K2 Monitor',
        'timestamp': datetime.now().isoformat()
    }

@flask_app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}


def run_flask_server():
    """Run Flask server in background"""
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


# ============================================================================
# Application Entry Point
# ============================================================================

def main() -> int:
    """Application entry point"""
    # Load configuration
    config = Config.from_env()
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("="*70)
    logger.info("K2 Workplace Monitor Bot Starting")
    logger.info("="*70)
    
    # Validate configuration
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        logger.error("Telegram configuration missing in .env file")
        return 1
    
    # Initialize API client
    api = School21API(
        config.SCHOOL21_USERNAME,
        config.SCHOOL21_PASSWORD,
        logger
    )
    
    if not api.authenticate():
        logger.error("Initial authentication failed")
        return 1
    
    # Initialize Telegram bot
    telegram = TelegramBot(
        config.TELEGRAM_BOT_TOKEN,
        config.TELEGRAM_CHAT_ID,
        logger
    )
    
    # Send startup notification
    telegram.send_message("K2 Monitoring Bot ishga tushdi!")
    
    # Start Flask server in separate thread
    logger.info("Starting Flask web server...")
    flask_thread = threading.Thread(
        target=run_flask_server,
        daemon=True,
        name="FlaskServer"
    )
    flask_thread.start()
    logger.info("Flask server started")
    
    # Initialize monitor
    monitor = WorkplaceMonitor(api, telegram, config, logger)
    
    # Start message handler in separate thread
    message_handler = MessageHandler(telegram, monitor, logger)
    handler_thread = threading.Thread(
        target=message_handler.run,
        daemon=True,
        name="MessageHandler"
    )
    handler_thread.start()
    
    # Run monitor (blocking)
    monitor.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
