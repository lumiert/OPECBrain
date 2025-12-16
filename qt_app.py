import os
import sys
import threading
import time
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QDialog, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QWidget, QHeaderView, QPushButton, QDateEdit
)
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, Signal, QObject, QDate

import keyboard

from history import load_history, save_record


class HotkeySignal(QObject):
    triggered = Signal()


class AddBarDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Novo registro")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(620)

        # Set window icon for taskbar
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'icons', 'brain.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main container with rounded corners
        container = QWidget(self)
        container.setObjectName("container")
        container_lay = QVBoxLayout(self)
        container_lay.setContentsMargins(0, 0, 0, 0)
        container_lay.addWidget(container)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Title row: input + status on same line
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Título")
        self.input.setMinimumHeight(36)
        # Force uppercase
        self.input.textChanged.connect(self._force_upper)
        # Add key-return icon inside the input on the right
        key_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'icons', 'key-return.png')
        if os.path.exists(key_icon_path):
            self.enter_action = self.input.addAction(QIcon(key_icon_path), QLineEdit.TrailingPosition)
        input_row.addWidget(self.input, 3)

        self.status = QComboBox()
        self.status.addItems(["Subiu", "Desceu", "Pronto"])
        self.status.setMinimumHeight(36)
        self.status.setMinimumWidth(130)
        input_row.addWidget(self.status, 1)
        lay.addLayout(input_row)

        help_lbl = QLabel("Enter para salvar · Esc para fechar")
        help_lbl.setAlignment(Qt.AlignCenter)
        help_lbl.setObjectName("helpLabel")
        lay.addWidget(help_lbl)

        self.input.returnPressed.connect(self._on_enter)
        self.input.setFocus()

        # Install event filter to catch Esc key
        self.input.installEventFilter(self)
        self.status.installEventFilter(self)

        # Modern grayscale dark stylesheet
        self.setStyleSheet("""
            #container {
                background-color: #1a1a1a;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #808080;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 1px solid #808080;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: url(common/icons/caret-down.png);
                width: 12px;
                height: 12px;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #e0e0e0;
                selection-background-color: #404040;
                border-radius: 8px;
            }
            #helpLabel {
                color: #808080;
                font-size: 12px;
            }
        """)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.close()
            return True
        return super().eventFilter(obj, event)

    def _force_upper(self, text):
        if text != text.upper():
            pos = self.input.cursorPosition()
            self.input.blockSignals(True)
            self.input.setText(text.upper())
            self.input.setCursorPosition(pos)
            self.input.blockSignals(False)

    def _on_enter(self):
        text = self.input.text().strip()
        if not text:
            return
        status = self.status.currentText()
        if '|' in text:
            parts = [p.strip() for p in text.split('|', 1)]
            if len(parts) == 2 and parts[1].lower() in ("subiu", "desceu", "pronto"):
                status = parts[1].capitalize()
                text = parts[0]
        save_record(text, status)
        # keep dialog open for continuous entry: clear field
        self.input.clear()
        self.input.setFocus()

    def show_centered(self):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        w = self.width()
        h = self.height()
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.move(x, y)
        self.show()


class HistoryDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Histórico")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.resize(1100, 580)

        # Set window icon for taskbar
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'icons', 'brain.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        lay = QVBoxLayout()
        self.setLayout(lay)

        # Date filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        
        filter_row.addWidget(QLabel("Data Inicial:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate())
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setMinimumHeight(32)
        filter_row.addWidget(self.date_start)
        
        filter_row.addWidget(QLabel("Data Final:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setMinimumHeight(32)
        filter_row.addWidget(self.date_end)
        
        self.btn_filter = QPushButton("Filtrar")
        self.btn_filter.setMinimumHeight(32)
        self.btn_filter.setMinimumWidth(80)
        self.btn_filter.clicked.connect(self.load)
        filter_row.addWidget(self.btn_filter)
        
        filter_row.addStretch()
        lay.addLayout(filter_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Objeto", "Subiu", "Desceu", "Pronto", "Status"])
        # Set column widths - Objeto gets more space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Objeto stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Subiu
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Desceu
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Pronto
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        self.table.setMinimumWidth(1000)
        lay.addWidget(self.table)

        # Grayscale dark theme with dark title bar
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QDateEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 6px 10px;
                padding-right: 25px;
                font-size: 13px;
            }
            QDateEdit:focus {
                border: 1px solid #808080;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border: none;
                background: transparent;
            }
            QDateEdit::down-arrow {
                image: url(common/icons/caret-down.png);
                width: 12px;
                height: 12px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #505050;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #606060;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QCalendarWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
            QCalendarWidget QToolButton {
                color: #e0e0e0;
                background-color: #2a2a2a;
                border: none;
                padding: 4px;
            }
            QCalendarWidget QMenu {
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
            QCalendarWidget QSpinBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #2a2a2a;
                color: #e0e0e0;
                selection-background-color: #404040;
                selection-color: #ffffff;
            }
            QTableWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 8px;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #333333;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Dark title bar on Windows
        self._set_dark_title_bar()

        self.load()

    def _set_dark_title_bar(self):
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = int(self.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    def _entry_in_date_range(self, entry, start_date: str, end_date: str) -> bool:
        """Check if any timestamp in the entry falls within the date range."""
        for field in ['subiu', 'desceu', 'pronto']:
            ts = entry.get(field)
            if ts:
                # Extract date part (YYYY-MM-DD) from timestamp
                entry_date = ts.split(' ')[0]
                if start_date <= entry_date <= end_date:
                    return True
        return False

    def load(self):
        data = load_history()
        
        # Get date range filter
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        
        # Filter data by date range
        filtered_data = [entry for entry in data if self._entry_in_date_range(entry, start_date, end_date)]
        
        self.table.setRowCount(len(filtered_data))
        
        # Load icons
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'icons')
        icon_subiu = QIcon(os.path.join(icon_dir, 'subiu.png'))
        icon_desceu = QIcon(os.path.join(icon_dir, 'desceu.png'))
        icon_check = QIcon(os.path.join(icon_dir, 'check.png'))
        
        for i, entry in enumerate(filtered_data):
            self.table.setItem(i, 0, QTableWidgetItem(entry.get('objeto', '')))
            
            # Subiu column with icon
            subiu_item = QTableWidgetItem(entry.get('subiu', '') or '')

            self.table.setItem(i, 1, subiu_item)
            # Desceu column with icon
            desceu_item = QTableWidgetItem(entry.get('desceu', '') or '')
            self.table.setItem(i, 2, desceu_item)
            
            # Pronto column with icon
            pronto_item = QTableWidgetItem(entry.get('pronto', '') or '')
            self.table.setItem(i, 3, pronto_item)
            
            # Status column with icon
            status = entry.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'Subiu':
                status_item.setIcon(icon_subiu)
            elif status == 'Desceu':
                status_item.setIcon(icon_desceu)
            elif status == 'Pronto':
                status_item.setIcon(icon_check)
            self.table.setItem(i, 4, status_item)


class TrayApp:
    _instance = None

    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        # Keep app running when windows are closed (tray app)
        self.app.setQuitOnLastWindowClosed(False)
        # Ensure system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("System tray not available on this system")

        # Set icon with fallback to a generated pixmap
        icon = self._load_icon()
        if icon.isNull():
            pm = QPixmap(32, 32)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)
            p.setBrush(QColor(30, 144, 255))
            p.setPen(Qt.NoPen)
            p.drawEllipse(2, 2, 28, 28)
            p.end()
            icon = QIcon(pm)

        self.tray = QSystemTrayIcon(icon)
        self.tray.setToolTip("OPEC Brain")
        self.tray.setVisible(True)
        # Left-click opens Novo registro
        self.tray.activated.connect(self._on_tray_activated)

        # Keep menu and actions as attributes to avoid GC
        self.menu = QMenu()
        self.act_hist = QAction("Histórico")
        self.act_new = QAction("Novo registro")
        self.act_quit = QAction("Sair")
        self.act_hist.triggered.connect(self.show_history)
        self.act_new.triggered.connect(self.show_addbar)
        self.act_quit.triggered.connect(self.quit)
        self.menu.addAction(self.act_hist)
        self.menu.addAction(self.act_new)
        self.menu.addSeparator()
        self.menu.addAction(self.act_quit)
        self.tray.setContextMenu(self.menu)

        self._addbar_open = False
        self._open_dialogs = []  # keep strong refs to prevent GC auto-close

        # Signal bridge for cross-thread hotkey
        self._hotkey_signal = HotkeySignal()
        self._hotkey_signal.triggered.connect(self.show_addbar)

        # Hotkey thread
        self._running = True
        self.hotkey_thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = TrayApp()
        return cls._instance

    def _load_icon(self) -> QIcon:
        try:
            icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'icons')
            for name in ('brain.png', 'note-pencil.png', 'clipboard-text.png'):
                p = os.path.join(icon_dir, name)
                if os.path.exists(p):
                    return QIcon(p)
        except Exception:
            pass
        return QIcon()  # default empty icon

    def _hotkey_loop(self):
        try:
            keyboard.add_hotkey('ctrl+0', lambda: self._hotkey_signal.triggered.emit())
            while self._running:
                time.sleep(0.2)
        except Exception:
            pass

    def show_addbar(self):
        if self._addbar_open:
            return
        self._addbar_open = True
        dlg = AddBarDialog()
        dlg.finished.connect(lambda _: self._on_dialog_finished(dlg, addbar=True))
        self._open_dialogs.append(dlg)
        dlg.show_centered()

    def _on_dialog_finished(self, dlg: QDialog, addbar: bool = False):
        try:
            if addbar:
                self._addbar_open = False
        finally:
            # remove reference
            if dlg in self._open_dialogs:
                self._open_dialogs.remove(dlg)

    def show_history(self):
        dlg = HistoryDialog()
        self._open_dialogs.append(dlg)
        dlg.finished.connect(lambda _: self._on_dialog_finished(dlg))
        dlg.show()

    def run(self):
        self.app.exec()

    def quit(self):
        try:
            self._running = False
        except Exception:
            pass
        self.tray.hide()
        self.app.quit()

    def _on_tray_activated(self, reason):
        # Trigger = left-click
        if reason == QSystemTrayIcon.Trigger:
            self.show_addbar()
