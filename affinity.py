import os
import sys
import time
import json
import requests
import threading
import winreg
import locale
from pypresence import Presence
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal, QPropertyAnimation, pyqtProperty, QTimer
from PyQt6.QtGui import QIcon, QPainter, QColor, QBrush, QPen, QPainterPath

CLIENT_ID = '1530346476440522792'
LOGO_PATH = 'logo.png' 
APP_NAME = "AffinityRPC"

# --- SISTEMA DE CONFIGURACIÓN ---
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    default = {"rpc_active": True, "privacy_mode": False, "is_dark": True, "lang": None}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                default.update(json.load(f))
    except Exception:
        pass
    return default

def save_config(config_data):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
    except Exception:
        pass

# --- IDIOMA (Actualizado para evitar el DeprecationWarning) ---
try:
    idioma_sistema = locale.getlocale()[0]
    _default_lang = "es" if idioma_sistema and idioma_sistema.startswith("es") else "en"
except:
    _default_lang = "en"

IDIOMA = _default_lang

TEXTOS = {
    "en": {
        "status_connecting": "Connecting service...",
        "status_waiting": "Waiting for document...",
        "status_paused": "Paused",
        "status_reconnecting": "Reconnecting...",
        "status_editing": "Editing: {}",
        "lbl_discord": "Discord:",
        "lbl_privacy": "Privacy:",
        "lbl_start": "Autostart:",
        "btn_exit": "Close\nProgram",
        "rpc_large": "Working in Affinity",
        "rpc_details": "Project: {}",
        "tray_pause": "Pause RPC",
        "tray_resume": "Resume RPC",
        "tray_privacy": "Privacy Mode",
        "tray_start": "Start with Windows",
        "tray_open": "Open Panel",
        "tray_close": "Close",
        "tray_msg": "Running in the background."
    },
    "es": {
        "status_connecting": "Conectando servicio...",
        "status_waiting": "Esperando documento...",
        "status_paused": "Pausado",
        "status_reconnecting": "Reconectando...",
        "status_editing": "Editando: {}",
        "lbl_discord": "Discord:",
        "lbl_privacy": "Privacidad:",
        "lbl_start": "Arrancar:",
        "btn_exit": "Cerrar\nPrograma",
        "rpc_large": "Trabajando en Affinity",
        "rpc_details": "Proyecto: {}",
        "tray_pause": "Pausar RPC",
        "tray_resume": "Reanudar RPC",
        "tray_privacy": "Modo Privacidad",
        "tray_start": "Iniciar con Windows",
        "tray_open": "Abrir Panel",
        "tray_close": "Cerrar",
        "tray_msg": "Ejecutándose en 2do plano."
    }
}

def ruta_recurso(ruta_relativa):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, ruta_relativa)

def get_app_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(__file__)

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return value == f'"{get_app_path()}" --autostart'
    except WindowsError:
        return False

def set_autostart(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if enable:
            comando = f'"{get_app_path()}" --autostart'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, comando)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except WindowsError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass

DARK_STYLE = """
    #GlassWidget { background-color: rgba(20, 20, 20, 210); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 20); }
    QLabel { color: #eeeeee; font-family: 'Segoe UI', Arial, sans-serif; }
    QPushButton { background-color: rgba(255, 255, 255, 8); border: 1px solid rgba(255, 255, 255, 15); border-radius: 10px; color: #eeeeee; padding: 6px; font-size: 13px; font-weight: 500; }
    QPushButton:hover { background-color: rgba(255, 255, 255, 15); border: 1px solid rgba(255, 255, 255, 30); }
    QPushButton:pressed { background-color: rgba(255, 255, 255, 25); }
    #TitleBtn { background-color: transparent; border: none; font-size: 14px; font-weight: normal; }
    #TitleBtn:hover { background-color: rgba(255, 255, 255, 15); border-radius: 15px; }
    #CloseBtn { background-color: transparent; border: none; font-size: 14px; font-weight: normal; }
    #CloseBtn:hover { background-color: rgba(230, 60, 60, 200); color: white; border-radius: 15px; }
"""

LIGHT_STYLE = """
    #GlassWidget { background-color: rgba(245, 245, 245, 210); border-radius: 16px; border: 1px solid rgba(0, 0, 0, 15); }
    QLabel { color: #333333; font-family: 'Segoe UI', Arial, sans-serif; }
    QPushButton { background-color: rgba(0, 0, 0, 5); border: 1px solid rgba(0, 0, 0, 15); border-radius: 10px; color: #333333; padding: 6px; font-size: 13px; font-weight: 500;}
    QPushButton:hover { background-color: rgba(0, 0, 0, 12); border: 1px solid rgba(0, 0, 0, 30); }
    QPushButton:pressed { background-color: rgba(0, 0, 0, 20); }
    #TitleBtn { background-color: transparent; border: none; color: #333333; font-size: 14px; font-weight: normal; }
    #TitleBtn:hover { background-color: rgba(0, 0, 0, 10); border-radius: 15px; }
    #CloseBtn { background-color: transparent; border: none; color: #333333; font-size: 14px; font-weight: normal; }
    #CloseBtn:hover { background-color: rgba(230, 60, 60, 200); color: white; border-radius: 15px; }
"""

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(55, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._position = 27
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(200) 
        self.stateChanged.connect(self.setup_animation)
        self.setChecked(True)

    def hitButton(self, pos):
        return self.rect().contains(pos)

    @pyqtProperty(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(27) 
        else:
            self.animation.setEndValue(4)  
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isChecked():
            painter.setPen(Qt.PenStyle.NoPen)
            if self.isEnabled():
                painter.setBrush(QBrush(QColor("#000000")))
            else:
                painter.setBrush(QBrush(QColor("#555555")))
            painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.drawEllipse(int(self._position), 3, 24, 24)
        else:
            if self.isEnabled():
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.setBrush(QBrush(QColor("#ffffff")))
            else:
                painter.setPen(QPen(QColor("#888888"), 2))
                painter.setBrush(QBrush(QColor("#dddddd")))
            painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 14, 14)
            painter.setPen(Qt.PenStyle.NoPen)
            
            if self.isEnabled():
                painter.setBrush(QBrush(QColor("#000000")))
            else:
                painter.setBrush(QBrush(QColor("#888888")))
            painter.drawEllipse(int(self._position), 3, 24, 24)
        painter.end()

class ThemeButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("TitleBtn")
        self.is_dark = True
        
    def toggle(self):
        self.is_dark = not self.is_dark
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event) 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.is_dark:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#eeeeee"))
            path = QPainterPath()
            path.addEllipse(7, 7, 16, 16)
            bite = QPainterPath()
            bite.addEllipse(11, 4, 14, 14)
            crescent = path.subtracted(bite)
            painter.drawPath(crescent)
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#333333"))
            painter.drawEllipse(9, 9, 12, 12)
            painter.setPen(QPen(QColor("#333333"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(15, 3, 15, 6)   
            painter.drawLine(15, 24, 15, 27) 
            painter.drawLine(3, 15, 6, 15)   
            painter.drawLine(24, 15, 27, 15) 
            painter.drawLine(7, 7, 9, 9)     
            painter.drawLine(21, 21, 23, 23) 
            painter.drawLine(7, 23, 9, 21)   
            painter.drawLine(23, 7, 21, 9)   
        painter.end()

class AffinityMCP:
    def __init__(self):
        self.session = requests.Session()
        self.endpoint = None
        self.responses = {}
        self.is_connected = False
        self.msg_id = 1

    def _listen_sse(self, sse_response):
        try:
            for line in sse_response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]
                        if data_str.startswith("http") or data_str.startswith("/"):
                            if data_str.startswith("/"): data_str = "http://localhost:6767" + data_str
                            self.endpoint = data_str
                        else:
                            try:
                                msg = json.loads(data_str)
                                if "id" in msg: self.responses[msg["id"]] = msg
                            except json.JSONDecodeError:
                                pass
        except Exception:
            self.is_connected = False

    def _llamar_herramienta(self, nombre, argumentos):
        req_id = self.msg_id
        self.msg_id += 1
        payload = {"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": nombre, "arguments": argumentos}}
        try:
            self.session.post(self.endpoint, json=payload, timeout=2)
            start = time.time()
            while time.time() - start < 2:
                if req_id in self.responses:
                    return self.responses.pop(req_id)
                time.sleep(0.05)
        except Exception:
            pass
        return None

    def conectar_y_saludar(self):
        try:
            sse = self.session.get("http://localhost:6767/sse", stream=True, timeout=2)
            threading.Thread(target=self._listen_sse, args=(sse,), daemon=True).start()
            
            for _ in range(10):
                if self.endpoint: break
                time.sleep(0.1)
                
            if not self.endpoint: return False
                
            req_init = {"jsonrpc": "2.0", "id": self.msg_id, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "DiscordRPC", "version": "1.0"}}}
            self.session.post(self.endpoint, json=req_init)
            
            start = time.time()
            while time.time() - start < 2:
                if self.msg_id in self.responses: break
                time.sleep(0.05)
            self.msg_id += 1
            
            req_ready = {"jsonrpc": "2.0", "method": "notifications/initialized"}
            self.session.post(self.endpoint, json=req_ready)
            
            self._llamar_herramienta("read_sdk_documentation_topic", {"filename": "preamble"})
            self._llamar_herramienta("read_sdk_documentation_topic", {"filename": "document.js"})
            self._llamar_herramienta("read_sdk_documentation_topic", {"filename": "application.js"})
            
            self.is_connected = True
            return True
        except requests.exceptions.RequestException:
            return False

    def obtener_proyecto(self):
        if not self.is_connected:
            if not self.conectar_y_saludar(): return None
        js_code = """
        try {
            const docModule = require('/document'); const appModule = require('/application');
            let currentDoc = null;
            if (docModule && docModule.Document && docModule.Document.current) currentDoc = docModule.Document.current;
            else if (appModule && appModule.app && appModule.app.documents && appModule.app.documents.current) currentDoc = appModule.app.documents.current;
            if (currentDoc) console.log('TITULO:' + currentDoc.title); else console.log('VACIO');
        } catch(e) { console.log('ERROR_JS'); }
        """
        res = self._llamar_herramienta("execute_script", {"script": js_code})
        
        if res and "result" in res:
            content = res["result"].get("content", [])
            if content:
                texto = content[0].get("text", "").strip()
                if "TITULO:" in texto: return texto.split("TITULO:")[1].strip().split(".af")[0]
                elif "preamble" in texto.lower() or "not yet been read" in texto.lower(): self.is_connected = False
        elif res and "error":
            if res["error"].get("code") == -32600: self.is_connected = False
        return None

class RPCWorker(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.is_active = True
        self.privacy_mode = False  
        self.last_project = None   
        self.last_rpc_state = None  
        self.affinity = AffinityMCP()
        self.rpc = None
        self.start_time = int(time.time())
        self.wake_event = threading.Event()

    def run(self):
        while self.is_running:
            if self.is_active:
                if self.rpc is None:
                    try:
                        self.rpc = Presence(CLIENT_ID)
                        self.rpc.connect()
                        self.last_rpc_state = None 
                    except Exception:
                        self.rpc = None

                if self.rpc:
                    proyecto = self.affinity.obtener_proyecto()
                    if proyecto and self.is_active: 
                        
                        current_state = (proyecto, self.privacy_mode)
                        
                        if self.privacy_mode:
                            self.status_signal.emit(TEXTOS[IDIOMA]["status_editing"].format("***"))
                        else:
                            self.status_signal.emit(TEXTOS[IDIOMA]["status_editing"].format(proyecto))
                            
                        if current_state != self.last_rpc_state:
                            if self.last_project != proyecto:
                                self.start_time = int(time.time())
                                self.last_project = proyecto
                            
                            try:
                                if self.privacy_mode:
                                    self.rpc.update(
                                        large_image="logo_affinity", 
                                        large_text=TEXTOS[IDIOMA]["rpc_large"], 
                                        start=self.start_time
                                    )
                                else:
                                    self.rpc.update(
                                        details=TEXTOS[IDIOMA]["rpc_details"].format(proyecto), 
                                        large_image="logo_affinity", 
                                        large_text=TEXTOS[IDIOMA]["rpc_large"], 
                                        start=self.start_time
                                    )
                                self.last_rpc_state = current_state
                            except Exception:
                                self.rpc = None
                    else:
                        if self.last_project is not None:
                            self.last_project = None
                            self.last_rpc_state = None
                            if self.is_active:
                                self.status_signal.emit(TEXTOS[IDIOMA]["status_waiting"])
                            try:
                                self.rpc.clear()
                            except:
                                pass
            else:
                if self.last_project is not None or self.last_rpc_state is not None:
                    self.status_signal.emit(TEXTOS[IDIOMA]["status_paused"])
                    self.last_project = None
                    self.last_rpc_state = None
                    if self.rpc:
                        try:
                            self.rpc.clear()
                        except:
                            pass
            
            self.wake_event.wait(10)
            self.wake_event.clear()

    def stop(self):
        self.is_running = False
        self.wake_event.set() 
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except:
                pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.config = load_config()
        
        global IDIOMA
        if self.config["lang"]:
            IDIOMA = self.config["lang"]

        self.worker = RPCWorker()
        self.worker.is_active = self.config["rpc_active"]
        self.worker.privacy_mode = self.config.get("privacy_mode", False)
        self.worker.status_signal.connect(self.actualizar_estado)
        self.worker.start()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(360, 270)
        self.setWindowIcon(QIcon(ruta_recurso(LOGO_PATH)))

        self.central_widget = QWidget()
        self.central_widget.setObjectName("GlassWidget")
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(15, 12, 15, 18)

        # --- BARRA DE TÍTULO ---
        title_bar = QHBoxLayout()
        title_bar.setSpacing(8)
        
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QIcon(ruta_recurso(LOGO_PATH)).pixmap(20, 20))
        title_bar.addWidget(self.logo_label)

        title_label = QLabel(APP_NAME)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; letter-spacing: 0.5px;")
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        self.btn_lang = QPushButton("ES" if IDIOMA == "es" else "EN")
        self.btn_lang.setObjectName("TitleBtn")
        self.btn_lang.setFixedSize(30, 30)
        self.btn_lang.clicked.connect(self.toggle_language)
        
        self.btn_theme = ThemeButton()
        self.btn_theme.is_dark = self.config["is_dark"]
        if self.btn_theme.is_dark:
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
            
        self.btn_theme.clicked.connect(self.toggle_theme)

        btn_min = QPushButton("━")
        btn_min.setObjectName("TitleBtn")
        btn_min.setFixedSize(30, 30)
        btn_min.clicked.connect(self.showMinimized)
        
        btn_close = QPushButton("✕")
        btn_close.setObjectName("CloseBtn")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.ocultar_a_bandeja)

        title_bar.addWidget(self.btn_lang)
        title_bar.addWidget(self.btn_theme)
        title_bar.addWidget(btn_min)
        title_bar.addWidget(btn_close)
        
        layout.addLayout(title_bar)
        layout.addSpacing(15)

        # --- ESTADO CENTRAL ---
        self.status_label = QLabel(TEXTOS[IDIOMA]["status_connecting"])
        self.status_label.setStyleSheet("font-size: 13px; opacity: 0.8;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addStretch()

        # --- BOTONES PRINCIPALES ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        switches_layout = QVBoxLayout()
        switches_layout.setSpacing(10)
        
        # Switch RPC
        switch_rpc_container = QHBoxLayout()
        self.lbl_switch_rpc = QLabel(TEXTOS[IDIOMA]["lbl_discord"])
        self.lbl_switch_rpc.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.btn_toggle_rpc = ToggleSwitch()
        self.btn_toggle_rpc.setChecked(self.worker.is_active)
        self.btn_toggle_rpc.clicked.connect(self.toggle_rpc)
        switch_rpc_container.addWidget(self.lbl_switch_rpc)
        switch_rpc_container.addWidget(self.btn_toggle_rpc)
        switch_rpc_container.addStretch()
        
        # Switch Privacidad CON COOLDOWN
        switch_privacy_container = QHBoxLayout()
        self.lbl_switch_privacy = QLabel(TEXTOS[IDIOMA]["lbl_privacy"])
        self.lbl_switch_privacy.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.btn_toggle_privacy = ToggleSwitch()
        self.btn_toggle_privacy.setChecked(self.worker.privacy_mode)
        self.btn_toggle_privacy.clicked.connect(self.toggle_privacy)
        
        self.lbl_privacy_cd = QLabel("")
        self.lbl_privacy_cd.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        self.lbl_privacy_cd.hide() 

        switch_privacy_container.addWidget(self.lbl_switch_privacy)
        switch_privacy_container.addWidget(self.btn_toggle_privacy)
        switch_privacy_container.addWidget(self.lbl_privacy_cd)
        switch_privacy_container.addStretch()

        # Switch Autostart
        switch_start_container = QHBoxLayout()
        self.lbl_switch_start = QLabel(TEXTOS[IDIOMA]["lbl_start"])
        self.lbl_switch_start.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.btn_toggle_start = ToggleSwitch()
        self.btn_toggle_start.setChecked(is_autostart_enabled())
        self.btn_toggle_start.clicked.connect(self.toggle_autostart)
        switch_start_container.addWidget(self.lbl_switch_start)
        switch_start_container.addWidget(self.btn_toggle_start)
        switch_start_container.addStretch()
        
        switches_layout.addLayout(switch_rpc_container)
        switches_layout.addLayout(switch_privacy_container)
        switches_layout.addLayout(switch_start_container)

        self.btn_exit = QPushButton(TEXTOS[IDIOMA]["btn_exit"])
        self.btn_exit.setFixedHeight(60) 
        self.btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_exit.clicked.connect(self.cerrar_aplicacion)

        action_layout.addLayout(switches_layout)
        action_layout.addWidget(self.btn_exit)
        layout.addLayout(action_layout)

        self.old_pos = self.pos()

        # --- TIMER PARA EL COOLDOWN ---
        self.cooldown_seconds = 0
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.timeout.connect(self.update_cooldown)

        # --- BANDEJA DEL SISTEMA ---
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(ruta_recurso(LOGO_PATH)))
        
        tray_menu = QMenu()
        self.tray_toggle_action = tray_menu.addAction(TEXTOS[IDIOMA]["tray_pause"])
        self.tray_toggle_action.triggered.connect(self.tray_toggle_click)
        
        self.tray_privacy_action = tray_menu.addAction(TEXTOS[IDIOMA]["tray_privacy"])
        self.tray_privacy_action.setCheckable(True)
        self.tray_privacy_action.setChecked(self.worker.privacy_mode)
        self.tray_privacy_action.triggered.connect(self.tray_privacy_click)
        
        self.tray_startup_action = tray_menu.addAction(TEXTOS[IDIOMA]["tray_start"])
        self.tray_startup_action.setCheckable(True)
        self.tray_startup_action.setChecked(self.btn_toggle_start.isChecked())
        self.tray_startup_action.triggered.connect(self.tray_startup_click)
        
        tray_menu.addSeparator()
        self.tray_open_action = tray_menu.addAction(TEXTOS[IDIOMA]["tray_open"])
        self.tray_open_action.triggered.connect(self.showNormal)
        
        self.tray_close_action = tray_menu.addAction(TEXTOS[IDIOMA]["tray_close"])
        self.tray_close_action.triggered.connect(self.cerrar_aplicacion)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_click)
        self.tray_icon.show()

    # --- LOGICA DEL COOLDOWN ---
    def iniciar_cooldown(self):
        self.cooldown_seconds = 15
        self.btn_toggle_privacy.setEnabled(False) 
        self.tray_privacy_action.setEnabled(False) 
        self.lbl_privacy_cd.setText(f"({self.cooldown_seconds}s)")
        self.lbl_privacy_cd.show()
        self.cooldown_timer.start(1000) 

    def update_cooldown(self):
        self.cooldown_seconds -= 1
        if self.cooldown_seconds > 0:
            self.lbl_privacy_cd.setText(f"({self.cooldown_seconds}s)")
        else:
            self.cooldown_timer.stop()
            self.btn_toggle_privacy.setEnabled(True) 
            self.tray_privacy_action.setEnabled(True) 
            self.lbl_privacy_cd.hide() 

    # --- FUNCIONES DE GUARDADO ---
    def guardar_config_actual(self):
        self.config["rpc_active"] = self.worker.is_active
        self.config["privacy_mode"] = self.worker.privacy_mode
        self.config["is_dark"] = self.btn_theme.is_dark
        self.config["lang"] = IDIOMA
        save_config(self.config)

    # --- FUNCIONES DE VENTANA ---
    def actualizar_estado(self, texto):
        self.status_label.setText(texto)

    def toggle_theme(self):
        self.btn_theme.toggle()
        if self.btn_theme.is_dark:
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
        self.guardar_config_actual()

    def toggle_language(self):
        global IDIOMA
        IDIOMA = "en" if IDIOMA == "es" else "es"
        
        self.btn_lang.setText("ES" if IDIOMA == "es" else "EN")
        
        self.lbl_switch_rpc.setText(TEXTOS[IDIOMA]["lbl_discord"])
        self.lbl_switch_privacy.setText(TEXTOS[IDIOMA]["lbl_privacy"])
        self.lbl_switch_start.setText(TEXTOS[IDIOMA]["lbl_start"])
        self.btn_exit.setText(TEXTOS[IDIOMA]["btn_exit"])
        
        self.tray_privacy_action.setText(TEXTOS[IDIOMA]["tray_privacy"])
        self.tray_startup_action.setText(TEXTOS[IDIOMA]["tray_start"])
        self.tray_open_action.setText(TEXTOS[IDIOMA]["tray_open"])
        self.tray_close_action.setText(TEXTOS[IDIOMA]["tray_close"])
        
        if self.worker.is_active:
            self.tray_toggle_action.setText(TEXTOS[IDIOMA]["tray_pause"])
            if self.status_label.text() in [TEXTOS["es"]["status_waiting"], TEXTOS["en"]["status_waiting"]]:
                self.status_label.setText(TEXTOS[IDIOMA]["status_waiting"])
        else:
            self.tray_toggle_action.setText(TEXTOS[IDIOMA]["tray_resume"])
            self.status_label.setText(TEXTOS[IDIOMA]["status_paused"])
            
        self.worker.wake_event.set()
        self.guardar_config_actual()

    def toggle_rpc(self, checked):
        self.worker.is_active = checked
        if checked:
            self.tray_toggle_action.setText(TEXTOS[IDIOMA]["tray_pause"])
            self.status_label.setText(TEXTOS[IDIOMA]["status_reconnecting"])
        else:
            self.tray_toggle_action.setText(TEXTOS[IDIOMA]["tray_resume"])
            self.status_label.setText(TEXTOS[IDIOMA]["status_paused"])
        self.worker.wake_event.set()
        self.guardar_config_actual()

    def toggle_privacy(self, checked):
        self.worker.privacy_mode = checked
        self.tray_privacy_action.setChecked(checked) 
        self.worker.wake_event.set()
        self.guardar_config_actual()
        self.iniciar_cooldown() 

    def toggle_autostart(self, checked):
        set_autostart(checked)
        self.tray_startup_action.setChecked(checked)

    def tray_toggle_click(self):
        nuevo_estado = not self.btn_toggle_rpc.isChecked()
        self.btn_toggle_rpc.setChecked(nuevo_estado)
        self.toggle_rpc(nuevo_estado)
        
    def tray_privacy_click(self, checked):
        self.btn_toggle_privacy.setChecked(checked) 
        self.toggle_privacy(checked)
        
    def tray_startup_click(self, checked):
        self.btn_toggle_start.setChecked(checked)
        set_autostart(checked)

    def ocultar_a_bandeja(self):
        self.hide()
        self.tray_icon.showMessage(APP_NAME, TEXTOS[IDIOMA]["tray_msg"], QSystemTrayIcon.MessageIcon.NoIcon, 1500)

    def tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def cerrar_aplicacion(self):
        self.tray_icon.hide()
        self.worker.stop()
        self.worker.wait()
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    window = MainWindow()
    
    if "--autostart" in sys.argv:
        window.hide()
    else:
        window.show()
        
    sys.exit(app.exec())
