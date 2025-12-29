import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QLabel, QFrame, QSplitter, QScrollArea, QLineEdit,
    QInputDialog, QProgressBar, QStatusBar, QGraphicsOpacityEffect,
    QComboBox, QRadioButton, QButtonGroup, QDialog, QDialogButtonBox,
    QCheckBox
)
from PySide6.QtCore import Qt, QSize, QBuffer, QIODevice, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PySide6.QtGui import QIcon, QAction, QPixmap, QImage, QMouseEvent, QDragEnterEvent, QDropEvent, QKeySequence, QShortcut, QFont, QFontDatabase
from scripts.pdf_engine import PDFEngine

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# Enhanced modern stylesheet with gradients and animations
STYLESHEET = """
QMainWindow {
    background-color: #0A0A0B;
}
QFrame#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1A1A1D, stop:1 #121214);
    border-right: 1px solid #2A2A2F;
}
QPushButton#SidebarBtn {
    background-color: transparent;
    color: #9CA3AF;
    border: none;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    border-radius: 8px;
    margin: 2px 0;
}
QPushButton#SidebarBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #2A2A2F, stop:1 #323237);
    color: #FFFFFF;
}
QPushButton#SidebarBtn:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3B82F6, stop:1 #2563EB);
    color: #FFFFFF;
    font-weight: bold;
}
QWidget#Workspace {
    background-color: #0A0A0B;
}
QLabel#Title {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: bold;
    padding: 10px 0;
}
QLabel#Subtitle {
    color: #6B7280;
    font-size: 12px;
}
QStatusBar {
    background-color: #161618;
    color: #9CA3AF;
    border-top: 1px solid #2A2A2F;
}
QProgressBar {
    border: 1px solid #2A2A2F;
    border-radius: 4px;
    background-color: #161618;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3B82F6, stop:1 #2563EB);
    border-radius: 3px;
}
"""

class RecentFilesManager:
    """Manages recent files list with persistence."""
    
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.recent_files = []
        self.load()
    
    def load(self):
        """Load recent files from config."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.recent_files = config.get('recent_files', [])
        except Exception as e:
            print(f"Error loading config: {e}")
            self.recent_files = []
    
    def save(self):
        """Save recent files to config."""
        try:
            config = {'recent_files': self.recent_files}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def add_file(self, filepath):
        """Add a file to recent files list."""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:self.max_files]
        self.save()
    
    def get_recent_files(self):
        """Get list of recent files that still exist."""
        return [f for f in self.recent_files if os.path.exists(f)]

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)
        
        # Title with icon
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        self.title = QLabel("📄 PDF Master")
        self.title.setObjectName("Title")
        title_layout.addWidget(self.title)
        
        self.subtitle = QLabel("Professional PDF Tools")
        self.subtitle.setObjectName("Subtitle")
        title_layout.addWidget(self.subtitle)
        
        layout.addWidget(title_container)
        layout.addSpacing(24)
        
        # Navigation buttons with icons
        self.btn_view = QPushButton("📖  Document Viewer")
        self.btn_view.setCheckable(True)
        self.btn_view.setChecked(True)
        self.btn_view.setObjectName("SidebarBtn")
        self.btn_view.setToolTip("View and annotate PDF documents (Ctrl+1)")
        layout.addWidget(self.btn_view)
        
        self.btn_merge = QPushButton("🔀  Merge PDFs")
        self.btn_merge.setCheckable(True)
        self.btn_merge.setObjectName("SidebarBtn")
        self.btn_merge.setToolTip("Combine multiple PDFs into one (Ctrl+2)")
        layout.addWidget(self.btn_merge)
        
        self.btn_split = QPushButton("✂️  Split PDF")
        self.btn_split.setCheckable(True)
        self.btn_split.setObjectName("SidebarBtn")
        self.btn_split.setToolTip("Split PDF into separate pages (Ctrl+3)")
        layout.addWidget(self.btn_split)
        
        self.btn_tools = QPushButton("🛠️  PDF Tools")
        self.btn_tools.setCheckable(True)
        self.btn_tools.setObjectName("SidebarBtn")
        self.btn_tools.setToolTip("Compress, convert, and organize (Ctrl+4)")
        layout.addWidget(self.btn_tools)
        
        layout.addStretch()
        
        # Settings button
        self.btn_settings = QPushButton("⚙️  Settings")
        self.btn_settings.setObjectName("SidebarBtn")
        self.btn_settings.setToolTip("Application settings")
        layout.addWidget(self.btn_settings)

class PDFViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar with enhanced styling
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(60)
        self.toolbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border-bottom: 1px solid #2A2A2F;
            }
            QPushButton {
                background-color: #27272A;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3F3F46, stop:1 #27272A);
            }
            QPushButton:pressed {
                background-color: #18181B;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #DC2626, stop:1 #B91C1C);
            }
        """)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(16, 8, 16, 8)
        
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.page_label = QLabel("Page: 0 / 0")
        self.page_label.setStyleSheet("color: white; margin: 0 12px; font-weight: bold;")
        
        self.btn_zoom_in = QPushButton("🔍+")
        self.btn_zoom_out = QPushButton("🔍-")
        self.btn_fit = QPushButton("⬜ Fit")
        
        # Annotation Toggle
        self.btn_annotate = QPushButton("✏️ Annotate")
        self.btn_annotate.setCheckable(True)
        
        for btn in [self.btn_prev, self.btn_next, self.btn_zoom_in, self.btn_zoom_out, self.btn_fit]:
            btn.setFixedSize(40, 40)
            btn.setToolTip(btn.text())
        
        self.btn_annotate.setFixedSize(100, 40)
        self.btn_annotate.setToolTip("Click to add text annotations")
        
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_annotate)
        toolbar_layout.addWidget(self.btn_fit)
        toolbar_layout.addWidget(self.btn_zoom_out)
        toolbar_layout.addWidget(self.btn_zoom_in)
        
        self.layout.addWidget(self.toolbar)
        
        # Scroll Area for PDF
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: #0A0A0B;")
        
        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("background-color: #0F0F10; padding: 20px;")
        self.scroll_area.setWidget(self.content_label)
        
        self.layout.addWidget(self.scroll_area)
        
        # State
        self.current_path = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 2.0
        
        # Connections
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_fit.clicked.connect(self.fit_to_window)
        
        # Enable mouse tracking for annotation
        self.content_label.mousePressEvent = self.handle_click

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.load_pdf(pdf_files[0])

    def load_pdf(self, path):
        self.current_path = path
        self.total_pages = PDFEngine.get_page_count(path)
        self.current_page = 0
        self.display_page()

    def display_page(self):
        if not self.current_path:
            return
            
        img_data = PDFEngine.render_page(self.current_path, self.current_page, self.zoom_level)
        image = QImage.fromData(img_data)
        pixmap = QPixmap.fromImage(image)
        self.content_label.setPixmap(pixmap)
        self.page_label.setText(f"Page: {self.current_page + 1} / {self.total_pages}")

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def zoom_in(self):
        self.zoom_level += 0.5
        self.display_page()

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.5
            self.display_page()
    
    def fit_to_window(self):
        self.zoom_level = 1.5
        self.display_page()
            
    def handle_click(self, event: QMouseEvent):
        if not self.current_path or not self.btn_annotate.isChecked():
            return

        # Use position() instead of deprecated pos()
        pos = event.position()
        x = pos.x()
        y = pos.y()
        
        pdf_x = x / self.zoom_level
        pdf_y = y / self.zoom_level
        
        text, ok = QInputDialog.getText(self, "Add Annotation", "Enter text to add:")
        if ok and text:
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Annotated PDF", "", "PDF Files (*.pdf)")
            if output_path:
                PDFEngine.add_text_annotation(self.current_path, self.current_page, text, pdf_x, pdf_y, output_path)
                QMessageBox.information(self, "✅ Success", f"Annotation added successfully!\nSaved to: {output_path}")
                self.load_pdf(output_path)
                self.btn_annotate.setChecked(False)

class MergeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # Main scroll area for vertical scrollability
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(24, 24, 24, 24)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        self.title = QLabel("🔀 Merge PDF Documents")
        self.title.setObjectName("Title")
        header_layout.addWidget(self.title)
        
        self.subtitle = QLabel("Drag and drop PDF files or click 'Add Files' to combine multiple PDFs")
        self.subtitle.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        header_layout.addWidget(self.subtitle)
        
        self.layout.addWidget(header)
        self.layout.addSpacing(16)
        
        # File list with enhanced styling
        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        self.file_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 2px dashed #3F3F46;
                color: white;
                border-radius: 12px;
                padding: 16px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
                margin: 4px 0;
            }
            QListWidget::item:hover {
                background-color: #27272A;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3B82F6, stop:1 #2563EB);
            }
        """)
        self.layout.addWidget(self.file_list)
        
        # Buttons with enhanced styling
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_add = QPushButton("➕ Add Files")
        self.btn_clear = QPushButton("🗑️ Clear All")
        self.btn_merge = QPushButton("🔀 Merge & Save")
        
        for btn in [self.btn_add, self.btn_clear, self.btn_merge]:
            btn.setFixedHeight(44)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                }
            """)
            
        self.btn_add.setStyleSheet(self.btn_add.styleSheet() + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #374151, stop:1 #27272A);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4B5563, stop:1 #374151);
            }
        """)
        self.btn_clear.setStyleSheet(self.btn_clear.styleSheet() + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #991B1B, stop:1 #7F1D1D);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #B91C1C, stop:1 #991B1B);
            }
        """)
        self.btn_merge.setStyleSheet(self.btn_merge.styleSheet() + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #60A5FA, stop:1 #3B82F6);
            }
        """)
        
        self.btn_add.setToolTip("Add PDF files to merge (Ctrl+O)")
        self.btn_clear.setToolTip("Remove all files from the list")
        self.btn_merge.setToolTip("Merge all PDFs into one file (Ctrl+M)")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_merge)
        self.layout.addLayout(btn_layout)
        
        self.btn_add.clicked.connect(self.add_files)
        self.btn_clear.clicked.connect(self.clear_with_confirmation)
        self.btn_merge.clicked.connect(self.merge_files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.file_list.addItems(pdf_files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.file_list.addItems(files)
    
    def clear_with_confirmation(self):
        if self.file_list.count() > 0:
            reply = QMessageBox.question(self, "Confirm Clear", 
                                        "Are you sure you want to remove all files from the list?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.file_list.clear()

    def merge_files(self):
        if self.file_list.count() < 2:
            QMessageBox.warning(self, "⚠️ Insufficient Files", 
                              "Please add at least 2 PDF files to merge.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if output_path:
            paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            if PDFEngine.merge_pdfs(paths, output_path):
                QMessageBox.information(self, "✅ Success", 
                                      f"Successfully merged {len(paths)} PDFs!\n\nSaved to:\n{output_path}")

class SplitWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # Main scroll area for vertical scrollability
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(24, 24, 24, 24)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        self.title = QLabel("✂️ Split PDF Document")
        self.title.setObjectName("Title")
        header_layout.addWidget(self.title)
        
        self.subtitle = QLabel("Split a PDF into individual pages or extract specific pages")
        self.subtitle.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        header_layout.addWidget(self.subtitle)
        
        self.layout.addWidget(header)
        self.layout.addSpacing(24)
        
        # Drop zone card
        self.drop_zone = QFrame()
        self.drop_zone.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 2px dashed #3F3F46;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)
        
        drop_icon = QLabel("📄")
        drop_icon.setStyleSheet("font-size: 48px;")
        drop_icon.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_icon)
        
        drop_text = QLabel("Drag & Drop PDF Here\nor")
        drop_text.setStyleSheet("color: #9CA3AF; font-size: 14px; margin: 12px 0;")
        drop_text.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_text)
        
        self.btn_select = QPushButton("📂 Select PDF File")
        self.btn_select.setFixedSize(160, 44)
        self.btn_select.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #374151, stop:1 #27272A);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4B5563, stop:1 #374151);
            }
        """)
        drop_layout.addWidget(self.btn_select, 0, Qt.AlignCenter)
        
        self.layout.addWidget(self.drop_zone)
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("""
            color: #6B7280;
            padding: 16px;
            background-color: #161618;
            border-radius: 8px;
            margin-top: 16px;
        """)
        self.file_path_label.setWordWrap(True)
        self.layout.addWidget(self.file_path_label)
        
        self.layout.addStretch()
        
        # Split button
        self.btn_split = QPushButton("✂️ Split into Pages")
        self.btn_split.setFixedHeight(50)
        self.btn_split.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                padding: 16px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #60A5FA, stop:1 #3B82F6);
            }
            QPushButton:disabled {
                background-color: #27272A;
                color: #6B7280;
            }
        """)
        self.btn_split.setEnabled(False)
        self.btn_split.setToolTip("Select a PDF file first")
        self.layout.addWidget(self.btn_split)
        
        self.current_path = None
        self.btn_select.clicked.connect(self.select_file)
        self.btn_split.clicked.connect(self.split_file)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.current_path = pdf_files[0]
            self.file_path_label.setText(f"📄 {self.current_path}")
            self.file_path_label.setStyleSheet(self.file_path_label.styleSheet().replace("#6B7280", "#10B981"))
            self.btn_split.setEnabled(True)
            self.btn_split.setToolTip("Split this PDF into individual pages")

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self.current_path = path
            self.file_path_label.setText(f"📄 {path}")
            self.file_path_label.setStyleSheet(self.file_path_label.styleSheet().replace("#6B7280", "#10B981"))
            self.btn_split.setEnabled(True)
            self.btn_split.setToolTip("Split this PDF into individual pages")

    def split_file(self):
        if not self.current_path:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            if PDFEngine.split_pdf(self.current_path, output_dir):
                page_count = PDFEngine.get_page_count(self.current_path)
                QMessageBox.information(self, "✅ Success", 
                                      f"PDF successfully split into {page_count} pages!\n\nSaved to:\n{output_dir}")

class MetadataDialog(QDialog):
    """Dialog to display PDF metadata information."""
    
    def __init__(self, pdf_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Properties")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0A0A0B;
            }
            QLabel {
                color: #E5E7EB;
                font-size: 13px;
                padding: 6px 0;
            }
            QLabel#PropertyLabel {
                color: #9CA3AF;
                font-weight: bold;
            }
            QLabel#ValueLabel {
                color: #FFFFFF;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("ℹ️ PDF Document Information")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding-bottom: 8px;")
        layout.addWidget(title)
        
        # Info container
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)
        
        # Add metadata fields
        fields = [
            ("📄 Pages", str(pdf_info.get('pages', 'N/A'))),
            ("📝 Title", pdf_info.get('title', 'N/A')),
            ("✍️ Author", pdf_info.get('author', 'N/A')),
            ("📋 Subject", pdf_info.get('subject', 'N/A')),
            ("🛠️ Creator", pdf_info.get('creator', 'N/A')),
            ("🏭 Producer", pdf_info.get('producer', 'N/A')),
            ("📅 Created", pdf_info.get('creation_date', 'N/A')),
            ("🔄 Modified", pdf_info.get('modification_date', 'N/A')),
            ("🔒 Encrypted", "Yes" if pdf_info.get('encrypted', False) else "No"),
        ]
        
        for label_text, value_text in fields:
            row = QHBoxLayout()
            row.setSpacing(12)
            
            label = QLabel(label_text)
            label.setObjectName("PropertyLabel")
            label.setMinimumWidth(120)
            row.addWidget(label)
            
            value = QLabel(str(value_text))
            value.setObjectName("ValueLabel")
            value.setWordWrap(True)
            row.addWidget(value, 1)
            
            info_layout.addLayout(row)
        
        layout.addWidget(info_frame)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #374151, stop:1 #27272A);
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4B5563, stop:1 #374151);
            }
        """)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class ToolsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main scroll area for vertical scrollability
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(24, 24, 24, 24)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        self.title = QLabel("🛠️ PDF Tools & Utilities")
        self.title.setObjectName("Title")
        header_layout.addWidget(self.title)
        
        self.subtitle = QLabel("Optimize, convert, and organize your PDF documents")
        self.subtitle.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        header_layout.addWidget(self.subtitle)
        
        self.layout.addWidget(header)
        self.layout.addSpacing(20)
        
        # Compression Section
        self.comp_card = self.create_tool_card(
            "🗜️ Compress PDF",
            "Reduce file size while maintaining quality",
            "#3B82F6",
            "Compress Selected File"
        )
        self.btn_compress = self.comp_card.findChild(QPushButton)
        self.layout.addWidget(self.comp_card)
        self.layout.addSpacing(16)
        
        # Image Conversion Section
        self.img_card = self.create_tool_card(
            "🖼️ PDF to Images",
            "Convert pages into high-quality JPG/PNG images",
            "#10B981",
            "Convert to Images"
        )
        self.btn_convert = self.img_card.findChild(QPushButton)
        self.layout.addWidget(self.img_card)
        self.layout.addSpacing(16)
        
        # Watermark Section
        self.watermark_card = QFrame()
        self.watermark_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        watermark_layout = QVBoxLayout(self.watermark_card)
        
        watermark_title = QLabel("💧 Add Watermark")
        watermark_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        watermark_layout.addWidget(watermark_title)
        
        watermark_desc = QLabel("Add custom text watermark to all pages")
        watermark_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        watermark_layout.addWidget(watermark_desc)
        
        self.watermark_input = QLineEdit()
        self.watermark_input.setPlaceholderText("Enter watermark text (e.g., CONFIDENTIAL)")
        self.watermark_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 6px;
                background-color: #27272A;
                color: white;
                border: 1px solid #3F3F46;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #8B5CF6;
            }
        """)
        watermark_layout.addWidget(self.watermark_input)
        
        self.btn_watermark = QPushButton("💧 Apply Watermark")
        self.btn_watermark.setFixedHeight(44)
        self.btn_watermark.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #8B5CF6, stop:1 #7C3AED);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #A78BFA, stop:1 #8B5CF6);
            }
        """)
        watermark_layout.addWidget(self.btn_watermark)
        self.layout.addWidget(self.watermark_card)
        self.layout.addSpacing(16)
        
        # Security Section (Encryption/Decryption)
        self.security_card = QFrame()
        self.security_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        security_layout = QVBoxLayout(self.security_card)
        
        security_title = QLabel("🔒 PDF Security")
        security_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        security_layout.addWidget(security_title)
        
        security_desc = QLabel("Protect or unlock PDFs with password encryption")
        security_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        security_layout.addWidget(security_desc)
        
        # Encryption subsection
        encrypt_label = QLabel("🔒 Encrypt PDF")
        encrypt_label.setStyleSheet("color: #10B981; font-size: 13px; font-weight: bold; margin-top: 8px;")
        security_layout.addWidget(encrypt_label)
        
        self.encrypt_password = QLineEdit()
        self.encrypt_password.setPlaceholderText("Enter password for encryption")
        self.encrypt_password.setEchoMode(QLineEdit.Password)
        self.encrypt_password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                background-color: #27272A;
                color: white;
                border: 1px solid #3F3F46;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #10B981;
            }
        """)
        security_layout.addWidget(self.encrypt_password)
        
        self.btn_encrypt = QPushButton("🔒 Encrypt PDF")
        self.btn_encrypt.setFixedHeight(40)
        self.btn_encrypt.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #10B981, stop:1 #059669);
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                margin-top: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #34D399, stop:1 #10B981);
            }
        """)
        security_layout.addWidget(self.btn_encrypt)
        
        # Decryption subsection
        decrypt_label = QLabel("🔓 Decrypt PDF")
        decrypt_label.setStyleSheet("color: #F59E0B; font-size: 13px; font-weight: bold; margin-top: 16px;")
        security_layout.addWidget(decrypt_label)
        
        self.decrypt_password = QLineEdit()
        self.decrypt_password.setPlaceholderText("Enter password to unlock")
        self.decrypt_password.setEchoMode(QLineEdit.Password)
        self.decrypt_password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                background-color: #27272A;
                color: white;
                border: 1px solid #3F3F46;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #F59E0B;
            }
        """)
        security_layout.addWidget(self.decrypt_password)
        
        self.btn_decrypt = QPushButton("🔓 Decrypt PDF")
        self.btn_decrypt.setFixedHeight(40)
        self.btn_decrypt.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #F59E0B, stop:1 #D97706);
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                margin-top: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #FBBF24, stop:1 #F59E0B);
            }
        """)
        security_layout.addWidget(self.btn_decrypt)
        self.layout.addWidget(self.security_card)
        self.layout.addSpacing(16)
        
        # Page Rotation Section
        self.rotation_card = QFrame()
        self.rotation_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        rotation_layout = QVBoxLayout(self.rotation_card)
        
        rotation_title = QLabel("🔄 Rotate Pages")
        rotation_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        rotation_layout.addWidget(rotation_title)
        
        rotation_desc = QLabel("Rotate specific pages or entire document")
        rotation_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        rotation_layout.addWidget(rotation_desc)
        
        # Rotation angle selector
        angle_label = QLabel("Rotation Angle:")
        angle_label.setStyleSheet("color: #E5E7EB; font-size: 13px; margin-top: 4px;")
        rotation_layout.addWidget(angle_label)
        
        self.rotation_angle = QComboBox()
        self.rotation_angle.addItems(["90° Clockwise", "180°", "270° Clockwise"])
        self.rotation_angle.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border-radius: 6px;
                background-color: #27272A;
                color: white;
                border: 1px solid #3F3F46;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #EC4899;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #27272A;
                color: white;
                selection-background-color: #EC4899;
                border: 1px solid #3F3F46;
            }
        """)
        rotation_layout.addWidget(self.rotation_angle)
        
        # All pages checkbox
        self.rotate_all_pages = QCheckBox("Rotate all pages")
        self.rotate_all_pages.setChecked(True)
        self.rotate_all_pages.setStyleSheet("""
            QCheckBox {
                color: #E5E7EB;
                font-size: 13px;
                margin-top: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #3F3F46;
                background-color: #27272A;
            }
            QCheckBox::indicator:checked {
                background-color: #EC4899;
                border-color: #EC4899;
            }
        """)
        rotation_layout.addWidget(self.rotate_all_pages)
        
        self.btn_rotate = QPushButton("🔄 Rotate Pages")
        self.btn_rotate.setFixedHeight(44)
        self.btn_rotate.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #EC4899, stop:1 #DB2777);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #F472B6, stop:1 #EC4899);
            }
        """)
        rotation_layout.addWidget(self.btn_rotate)
        self.layout.addWidget(self.rotation_card)
        self.layout.addSpacing(16)
        
        # Text Extraction Section
        self.extract_card = QFrame()
        self.extract_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        extract_layout = QVBoxLayout(self.extract_card)
        
        extract_title = QLabel("📝 Extract Text")
        extract_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        extract_layout.addWidget(extract_title)
        
        extract_desc = QLabel("Extract text content and save to .txt file")
        extract_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        extract_layout.addWidget(extract_desc)
        
        self.btn_extract = QPushButton("📝 Extract to TXT")
        self.btn_extract.setFixedHeight(44)
        self.btn_extract.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #06B6D4, stop:1 #0891B2);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #22D3EE, stop:1 #06B6D4);
            }
        """)
        extract_layout.addWidget(self.btn_extract)
        self.layout.addWidget(self.extract_card)
        self.layout.addSpacing(16)
        
        # Metadata Viewer Section
        self.metadata_card = QFrame()
        self.metadata_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        metadata_layout = QVBoxLayout(self.metadata_card)
        
        metadata_title = QLabel("ℹ️ PDF Information")
        metadata_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        metadata_layout.addWidget(metadata_title)
        
        metadata_desc = QLabel("View document properties and metadata")
        metadata_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        metadata_layout.addWidget(metadata_desc)
        
        self.btn_metadata = QPushButton("ℹ️ View PDF Info")
        self.btn_metadata.setFixedHeight(44)
        self.btn_metadata.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #6366F1, stop:1 #4F46E5);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #818CF8, stop:1 #6366F1);
            }
        """)
        metadata_layout.addWidget(self.btn_metadata)
        self.layout.addWidget(self.metadata_card)
        self.layout.addSpacing(16)
        
        # Office Conversion Section
        self.office_card = QFrame()
        self.office_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        office_layout = QVBoxLayout(self.office_card)
        
        office_title = QLabel("📄 Office Conversion")
        office_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        office_layout.addWidget(office_title)
        
        office_desc = QLabel("Convert between PDF and Word, Excel, PowerPoint")
        office_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        office_layout.addWidget(office_desc)
        
        # Grid of buttons
        grid_layout = QHBoxLayout() # Use HBox for columns or Grid
        # Let's use a Grid for 2 columns
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # Helper to create styled buttons for this grid
        def create_grid_btn(text, color):
            btn = QPushButton(text)
            btn.setFixedHeight(44)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 {color}, stop:1 #1F2937);
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    border: 1px solid {color};
                }}
                QPushButton:hover {{
                    background: {color};
                }}
            """)
            return btn
            
        self.btn_pdf_word = create_grid_btn("PDF → Word", "#3B82F6")
        self.btn_word_pdf = create_grid_btn("Word → PDF", "#3B82F6")
        
        self.btn_pdf_excel = create_grid_btn("PDF → Excel", "#10B981")
        self.btn_excel_pdf = create_grid_btn("Excel → PDF", "#10B981")
        
        self.btn_pdf_ppt = create_grid_btn("PDF → PPT", "#F59E0B")
        self.btn_ppt_pdf = create_grid_btn("PPT → PDF", "#F59E0B")
        
        grid.addWidget(self.btn_pdf_word, 0, 0)
        grid.addWidget(self.btn_word_pdf, 0, 1)
        grid.addWidget(self.btn_pdf_excel, 1, 0)
        grid.addWidget(self.btn_excel_pdf, 1, 1)
        grid.addWidget(self.btn_pdf_ppt, 2, 0)
        grid.addWidget(self.btn_ppt_pdf, 2, 1)
        
        office_layout.addLayout(grid)
        self.layout.addWidget(self.office_card)
        self.layout.addSpacing(16)
        
        # Page Organization Section
        self.rem_card = QFrame()
        self.rem_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        rem_layout = QVBoxLayout(self.rem_card)
        
        rem_title = QLabel("📑 Page Organization")
        rem_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        rem_layout.addWidget(rem_title)
        
        rem_desc = QLabel("Keep specific pages, remove others")
        rem_desc.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        rem_layout.addWidget(rem_desc)
        
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("Enter pages to keep (e.g., 1, 3-5, 7)")
        self.pages_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 6px;
                background-color: #27272A;
                color: white;
                border: 1px solid #3F3F46;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #F59E0B;
            }
        """)
        rem_layout.addWidget(self.pages_input)
        
        self.btn_remove = QPushButton("📑 Extract Pages")
        self.btn_remove.setFixedHeight(44)
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #F59E0B, stop:1 #D97706);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #FBBF24, stop:1 #F59E0B);
            }
        """)
        rem_layout.addWidget(self.btn_remove)
        self.layout.addWidget(self.rem_card)
        
        self.layout.addStretch()
        
        self.current_path = None
        self.btn_compress.clicked.connect(self.run_compression)
        self.btn_convert.clicked.connect(self.run_conversion)
        self.btn_remove.clicked.connect(self.run_remove_pages)
        
        # Conversion Connections
        self.btn_pdf_word.clicked.connect(self.run_pdf_to_word)
        self.btn_word_pdf.clicked.connect(self.run_word_to_pdf)
        self.btn_pdf_excel.clicked.connect(self.run_pdf_to_excel)
        self.btn_excel_pdf.clicked.connect(self.run_excel_to_pdf)
        self.btn_pdf_ppt.clicked.connect(self.run_pdf_to_ppt)
        self.btn_ppt_pdf.clicked.connect(self.run_ppt_to_pdf)
        
        # New Tool Connections
        self.btn_watermark.clicked.connect(self.run_watermark)
        self.btn_encrypt.clicked.connect(self.run_encrypt)
        self.btn_decrypt.clicked.connect(self.run_decrypt)
        self.btn_rotate.clicked.connect(self.run_rotation)
        self.btn_extract.clicked.connect(self.run_text_extraction)
        self.btn_metadata.clicked.connect(self.show_metadata)
    
    def create_tool_card(self, title, description, color, button_text):
        """Helper to create consistent tool cards."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1A1A1D, stop:1 #161618);
                border: 1px solid #2A2A2F;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-bottom: 12px;")
        layout.addWidget(desc_label)
        
        button = QPushButton(button_text)
        button.setFixedHeight(44)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 {color}, stop:1 {self.darken_color(color)});
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background: {color};
            }}
        """)
        layout.addWidget(button)
        
        return card
    
    def darken_color(self, color):
        """Simple color darkening for gradients."""
        colors = {
            "#3B82F6": "#2563EB",
            "#10B981": "#059669",
            "#F59E0B": "#D97706"
        }
        return colors.get(color, color)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        return path

    def run_compression(self):
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
            if out:
                PDFEngine.compress_pdf(path, out)
                original_size = os.path.getsize(path) / 1024 / 1024
                compressed_size = os.path.getsize(out) / 1024 / 1024
                reduction = ((original_size - compressed_size) / original_size) * 100
                QMessageBox.information(self, "✅ Success", 
                                      f"PDF compressed successfully!\n\n"
                                      f"Original: {original_size:.2f} MB\n"
                                      f"Compressed: {compressed_size:.2f} MB\n"
                                      f"Reduction: {reduction:.1f}%")

    def run_conversion(self):
        path = self.select_file()
        if path:
            out_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Images")
            if out_dir:
                page_count = PDFEngine.get_page_count(path)
                PDFEngine.pdf_to_images(path, out_dir)
                QMessageBox.information(self, "✅ Success", 
                                      f"PDF converted to images!\n\n"
                                      f"Created {page_count} image files in:\n{out_dir}")

    def run_remove_pages(self):
        path = self.select_file()
        if not path:
            return

        pages_str = self.pages_input.text().strip()
        if not pages_str:
            QMessageBox.warning(self, "⚠️ No Pages Specified", 
                              "Please enter the pages you want to keep.\n\n"
                              "Examples:\n"
                              "• 1, 3, 5 (specific pages)\n"
                              "• 1-5 (range)\n"
                              "• 1, 3-5, 7 (combination)")
            return

        try:
            pages_to_keep = set()
            parts = pages_str.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages_to_keep.update(range(start-1, end))
                else:
                    pages_to_keep.add(int(part) - 1)
            
            sorted_pages = sorted(list(pages_to_keep))
            
            out, _ = QFileDialog.getSaveFileName(self, "Save Extracted Pages", "", "PDF Files (*.pdf)")
            if out:
                PDFEngine.remove_pages(path, sorted_pages, out)
                QMessageBox.information(self, "✅ Success", 
                                      f"Successfully extracted {len(sorted_pages)} pages!\n\n"
                                      f"Saved to:\n{out}")

        except ValueError:
            QMessageBox.critical(self, "❌ Invalid Format", 
                               "Invalid page format!\n\n"
                               "Please use numbers and dashes.\n"
                               "Examples: 1, 3-5, 7")

    def show_progress(self, message):
        """Helper to show a simple progress dialog or blocking wait."""
        # For simplicity, we just change cursor, but a dialog is better.
        # Let's use QProgressDialog to show we are busy
        from PySide6.QtWidgets import QProgressDialog
        progress = QProgressDialog(message, None, 0, 0, self)
        progress.setWindowTitle("Processing")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()
        return progress

    def run_pdf_to_word(self):
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Word Document", "", "Word Documents (*.docx)")
            if out:
                if not out.endswith('.docx'): out += '.docx'
                progress = self.show_progress("Converting PDF to Word...")
                success = PDFEngine.pdf_to_word(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to Word:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed.")

    def run_word_to_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Word Document", "", "Word Documents (*.docx *.doc)")
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Converting Word to PDF...")
                success = PDFEngine.word_to_pdf(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to PDF:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed.")

    def run_pdf_to_excel(self):
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Excel Spreadsheet", "", "Excel Files (*.xlsx)")
            if out:
                if not out.endswith('.xlsx'): out += '.xlsx'
                progress = self.show_progress("Converting PDF to Excel...")
                success = PDFEngine.pdf_to_excel(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to Excel:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed. No tables found or error occurred.")

    def run_excel_to_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Converting Excel to PDF...")
                success = PDFEngine.excel_to_pdf(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to PDF:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed.")

    def run_pdf_to_ppt(self):
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save PowerPoint", "", "PowerPoint Files (*.pptx)")
            if out:
                if not out.endswith('.pptx'): out += '.pptx'
                progress = self.show_progress("Converting PDF to PowerPoint...")
                success = PDFEngine.pdf_to_powerpoint(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to PowerPoint:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed.")

    def run_ppt_to_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PowerPoint", "", "PowerPoint Files (*.pptx *.ppt)")
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Converting PowerPoint to PDF...")
                success = PDFEngine.powerpoint_to_pdf(path, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", f"Converted to PDF:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Conversion failed.")
    
    def run_watermark(self):
        """Add watermark to PDF."""
        watermark_text = self.watermark_input.text().strip()
        if not watermark_text:
            QMessageBox.warning(self, "⚠️ No Watermark Text", 
                              "Please enter watermark text before applying.")
            return
        
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Watermarked PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Adding watermark...")
                success = PDFEngine.add_watermark(path, watermark_text, out)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", 
                                          f"Watermark applied successfully!\n\nSaved to:\n{out}")
                else:
                    QMessageBox.critical(self, "❌ Error", "Failed to add watermark.")
    
    def run_encrypt(self):
        """Encrypt PDF with password."""
        password = self.encrypt_password.text().strip()
        if not password:
            QMessageBox.warning(self, "⚠️ No Password", 
                              "Please enter a password for encryption.")
            return
        
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Encrypted PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Encrypting PDF...")
                success = PDFEngine.encrypt_pdf(path, out, password)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", 
                                          f"PDF encrypted successfully!\n\n"
                                          f"Password: {password}\n"
                                          f"Saved to:\n{out}")
                    self.encrypt_password.clear()
                else:
                    QMessageBox.critical(self, "❌ Error", "Failed to encrypt PDF.")
    
    def run_decrypt(self):
        """Decrypt password-protected PDF."""
        password = self.decrypt_password.text().strip()
        if not password:
            QMessageBox.warning(self, "⚠️ No Password", 
                              "Please enter the password to unlock the PDF.")
            return
        
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Decrypted PDF", "", "PDF Files (*.pdf)")
            if out:
                if not out.endswith('.pdf'): out += '.pdf'
                progress = self.show_progress("Decrypting PDF...")
                success = PDFEngine.decrypt_pdf(path, out, password)
                progress.close()
                if success:
                    QMessageBox.information(self, "✅ Success", 
                                          f"PDF decrypted successfully!\n\nSaved to:\n{out}")
                    self.decrypt_password.clear()
                else:
                    QMessageBox.warning(self, "❌ Decryption Failed", 
                                      "Failed to decrypt PDF.\n\n"
                                      "Possible reasons:\n"
                                      "• Incorrect password\n"
                                      "• File is not encrypted\n"
                                      "• File is corrupted")
    
    def run_rotation(self):
        """Rotate pages in PDF."""
        path = self.select_file()
        if not path:
            return
        
        # Get rotation angle from combo box
        angle_text = self.rotation_angle.currentText()
        angle_map = {
            "90° Clockwise": 90,
            "180°": 180,
            "270° Clockwise": 270
        }
        rotation = angle_map.get(angle_text, 90)
        
        # Determine which pages to rotate
        pages = None  # None means all pages
        if not self.rotate_all_pages.isChecked():
            # Could add page selection input here, for now just rotate all
            pages = None
        
        out, _ = QFileDialog.getSaveFileName(self, "Save Rotated PDF", "", "PDF Files (*.pdf)")
        if out:
            if not out.endswith('.pdf'): out += '.pdf'
            progress = self.show_progress(f"Rotating pages by {rotation}°...")
            success = PDFEngine.rotate_pages(path, out, rotation, pages)
            progress.close()
            if success:
                page_count = PDFEngine.get_page_count(out)
                QMessageBox.information(self, "✅ Success", 
                                      f"Pages rotated successfully!\n\n"
                                      f"Rotation: {rotation}°\n"
                                      f"Pages affected: {page_count}\n"
                                      f"Saved to:\n{out}")
            else:
                QMessageBox.critical(self, "❌ Error", "Failed to rotate pages.")
    
    def run_text_extraction(self):
        """Extract text from PDF to TXT file."""
        path = self.select_file()
        if not path:
            return
        
        out, _ = QFileDialog.getSaveFileName(self, "Save Extracted Text", "", "Text Files (*.txt)")
        if out:
            if not out.endswith('.txt'): out += '.txt'
            progress = self.show_progress("Extracting text from PDF...")
            
            try:
                # Extract text from all pages
                text = PDFEngine.extract_text(path)
                
                # Write to file
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                progress.close()
                
                # Count words and characters
                word_count = len(text.split())
                char_count = len(text)
                
                QMessageBox.information(self, "✅ Success", 
                                      f"Text extracted successfully!\n\n"
                                      f"Characters: {char_count:,}\n"
                                      f"Words: {word_count:,}\n"
                                      f"Saved to:\n{out}")
            except Exception as e:
                progress.close()
                QMessageBox.critical(self, "❌ Error", 
                                   f"Failed to extract text.\n\nError: {str(e)}")
    
    def show_metadata(self):
        """Display PDF metadata in a dialog."""
        path = self.select_file()
        if not path:
            return
        
        try:
            pdf_info = PDFEngine.get_pdf_info(path)
            dialog = MetadataDialog(pdf_info, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", 
                               f"Failed to read PDF metadata.\n\nError: {str(e)}")

class PDFMasterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Master - Professional PDF Tools")
        
        # Enable window resizing and set minimum size
        self.setMinimumSize(900, 600)
        self.resize(1280, 820)
        self.setStyleSheet(STYLESHEET)
        
        # Track fullscreen state
        self.is_fullscreen = False
        
        # Recent files manager
        self.recent_files = RecentFilesManager()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Workspace (Stacked Widget)
        self.workspace = QStackedWidget()
        self.workspace.setObjectName("Workspace")
        main_layout.addWidget(self.workspace)
        
        # Views
        self.view_page = QWidget()
        self.pdf_viewer = PDFViewer()
        self.init_view_page()
        self.workspace.addWidget(self.view_page)
        
        self.merge_page = QWidget()
        self.init_merge_page()
        self.workspace.addWidget(self.merge_page)

        self.split_page = QWidget()
        self.init_split_page()
        self.workspace.addWidget(self.split_page)
        
        self.tools_page = ToolsWidget()
        self.workspace.addWidget(self.tools_page)
        
        # Connections
        self.sidebar.btn_view.clicked.connect(lambda: self.switch_page(0))
        self.sidebar.btn_merge.clicked.connect(lambda: self.switch_page(1))
        self.sidebar.btn_split.clicked.connect(lambda: self.switch_page(2))
        self.sidebar.btn_tools.clicked.connect(lambda: self.switch_page(3))
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Fade-in animation on startup
        self.fade_in()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for quick navigation."""
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.switch_page(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.switch_page(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.switch_page(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.switch_page(3))
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_pdf)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self, self.exit_fullscreen)

    def fade_in(self):
        """Smooth fade-in animation on startup."""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
            self.status_bar.showMessage("Exited fullscreen mode (F11 to toggle)")
        else:
            self.showFullScreen()
            self.is_fullscreen = True
            self.status_bar.showMessage("Fullscreen mode active (F11 or ESC to exit)")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode if active."""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
            self.status_bar.showMessage("Exited fullscreen mode")

    def init_view_page(self):
        layout = QVBoxLayout(self.view_page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Welcome placeholder
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        welcome_icon = QLabel("📄")
        welcome_icon.setStyleSheet("font-size: 72px;")
        welcome_icon.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_icon)
        
        placeholder = QLabel("Open a PDF to Start Viewing")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #9CA3AF; font-size: 18px; font-weight: bold; margin: 16px 0;")
        welcome_layout.addWidget(placeholder)
        
        subtitle = QLabel("Drag & drop a file or click the button below")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 24px;")
        welcome_layout.addWidget(subtitle)
        
        self.btn_open = QPushButton("📂 Open PDF File")
        self.btn_open.setFixedSize(180, 50)
        self.btn_open.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                padding: 14px 28px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #60A5FA, stop:1 #3B82F6);
            }
        """)
        self.btn_open.clicked.connect(self.open_pdf)
        welcome_layout.addWidget(self.btn_open, 0, Qt.AlignCenter)
        
        # Recent files section
        recent_files = self.recent_files.get_recent_files()
        if recent_files:
            welcome_layout.addSpacing(32)
            recent_label = QLabel("Recent Files")
            recent_label.setStyleSheet("color: #9CA3AF; font-size: 14px; font-weight: bold;")
            recent_label.setAlignment(Qt.AlignCenter)
            welcome_layout.addWidget(recent_label)
            
            self.recent_list = QListWidget()
            self.recent_list.setMaximumHeight(150)
            self.recent_list.setStyleSheet("""
                QListWidget {
                    background-color: transparent;
                    border: none;
                    color: #60A5FA;
                    font-size: 12px;
                }
                QListWidget::item {
                    padding: 6px;
                }
                QListWidget::item:hover {
                    background-color: #27272A;
                    border-radius: 4px;
                }
            """)
            for file in recent_files[:5]:
                self.recent_list.addItem(f"📄 {os.path.basename(file)}")
            self.recent_list.itemClicked.connect(self.open_recent_file)
            welcome_layout.addWidget(self.recent_list)
        
        layout.addWidget(self.welcome_widget)
        layout.addWidget(self.pdf_viewer)
        self.pdf_viewer.hide()

    def init_merge_page(self):
        layout = QVBoxLayout(self.merge_page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.merge_widget = MergeWidget()
        layout.addWidget(self.merge_widget)

    def init_split_page(self):
        layout = QVBoxLayout(self.split_page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.split_widget = SplitWidget()
        layout.addWidget(self.split_widget)

    def switch_page(self, index):
        """Switch workspace page with smooth transition."""
        # Update workspace
        old_index = self.workspace.currentIndex()
        self.workspace.setCurrentIndex(index)
        
        # Update sidebar buttons
        btns = [self.sidebar.btn_view, self.sidebar.btn_merge, 
                self.sidebar.btn_split, self.sidebar.btn_tools]
        for i, btn in enumerate(btns):
            btn.setChecked(i == index)
        
        # Update status bar
        status_messages = [
            "Document Viewer - View and annotate PDFs",
            "Merge PDFs - Combine multiple documents",
            "Split PDF - Extract individual pages",
            "PDF Tools - Optimize and convert"
        ]
        self.status_bar.showMessage(status_messages[index])

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.recent_files.add_file(file_path)
            self.welcome_widget.hide()
            self.pdf_viewer.show()
            self.pdf_viewer.load_pdf(file_path)
            self.status_bar.showMessage(f"Opened: {os.path.basename(file_path)}")
    
    def open_recent_file(self, item):
        """Open a file from recent files list."""
        recent_files = self.recent_files.get_recent_files()
        index = self.recent_list.row(item)
        if index < len(recent_files):
            file_path = recent_files[index]
            if os.path.exists(file_path):
                self.welcome_widget.hide()
                self.pdf_viewer.show()
                self.pdf_viewer.load_pdf(file_path)
                self.status_bar.showMessage(f"Opened: {os.path.basename(file_path)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PDFMasterApp()
    window.show()
    sys.exit(app.exec())
