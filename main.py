import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QLabel, QFrame, QSplitter, QScrollArea, QLineEdit
)
from PySide6.QtCore import Qt, QSize, QBuffer, QIODevice
from PySide6.QtGui import QIcon, QAction, QPixmap, QImage
from scripts.pdf_engine import PDFEngine

# Mocking a simple theme based on design inspiration
STYLESHEET = """
QMainWindow {
    background-color: #0F0F10;
}
QFrame#Sidebar {
    background-color: #161618;
    border-right: 1px solid #27272A;
}
QPushButton#SidebarBtn {
    background-color: transparent;
    color: #A1A1AA;
    border: none;
    padding: 10px;
    text-align: left;
    font-size: 14px;
    border-radius: 6px;
}
QPushButton#SidebarBtn:hover {
    background-color: #27272A;
    color: #FFFFFF;
}
QPushButton#SidebarBtn:checked {
    background-color: #3F3F46;
    color: #FFFFFF;
}
QWidget#Workspace {
    background-color: #0F0F10;
}
QLabel#Title {
    color: #FAFAFA;
    font-size: 18px;
    font-weight: bold;
}
"""

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)
        
        self.title = QLabel("PDF Master")
        self.title.setObjectName("Title")
        layout.addWidget(self.title)
        layout.addSpacing(20)
        
        self.btn_view = QPushButton(" Document Viewer")
        self.btn_view.setCheckable(True)
        self.btn_view.setChecked(True)
        self.btn_view.setObjectName("SidebarBtn")
        layout.addWidget(self.btn_view)
        
        self.btn_merge = QPushButton(" Merge PDF")
        self.btn_merge.setCheckable(True)
        self.btn_merge.setObjectName("SidebarBtn")
        layout.addWidget(self.btn_merge)
        
        self.btn_split = QPushButton(" Split PDF")
        self.btn_split.setCheckable(True)
        self.btn_split.setObjectName("SidebarBtn")
        layout.addWidget(self.btn_split)
        
        self.btn_tools = QPushButton(" PDF Tools")
        self.btn_tools.setCheckable(True)
        self.btn_tools.setObjectName("SidebarBtn")
        layout.addWidget(self.btn_tools)
        
        layout.addStretch()
        
        self.btn_settings = QPushButton(" Settings")
        self.btn_settings.setObjectName("SidebarBtn")
        layout.addWidget(self.btn_settings)

class PDFViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(50)
        self.toolbar.setStyleSheet("background-color: #161618; border-bottom: 1px solid #27272A;")
        toolbar_layout = QHBoxLayout(self.toolbar)
        
        self.btn_prev = QPushButton("←")
        self.btn_next = QPushButton("→")
        self.page_label = QLabel("Page: 0 / 0")
        self.page_label.setStyleSheet("color: white; margin: 0 10px;")
        
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_out = QPushButton("-")
        
        for btn in [self.btn_prev, self.btn_next, self.btn_zoom_in, self.btn_zoom_out]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("background-color: #27272A; color: white; border-radius: 4px;")
        
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_zoom_out)
        toolbar_layout.addWidget(self.btn_zoom_in)
        
        self.layout.addWidget(self.toolbar)
        
        # Scroll Area for PDF
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: #0F0F10;")
        
        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignCenter)
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

class MergeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("Merge PDF Documents")
        self.title.setObjectName("Title")
        self.layout.addWidget(self.title)
        
        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QListWidget.InternalMove)
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #161618;
                border: 1px solid #27272A;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.file_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Files")
        self.btn_clear = QPushButton("Clear")
        self.btn_merge = QPushButton("Merge & Save")
        
        for btn in [self.btn_add, self.btn_clear, self.btn_merge]:
            btn.setStyleSheet("padding: 10px; border-radius: 6px; font-weight: bold;")
            
        self.btn_add.setStyleSheet(self.btn_add.styleSheet() + "background-color: #27272A; color: white;")
        self.btn_clear.setStyleSheet(self.btn_clear.styleSheet() + "background-color: #7F1D1D; color: white;")
        self.btn_merge.setStyleSheet(self.btn_merge.styleSheet() + "background-color: #3B82F6; color: white;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_merge)
        self.layout.addLayout(btn_layout)
        
        self.btn_add.clicked.connect(self.add_files)
        self.btn_clear.clicked.connect(self.file_list.clear)
        self.btn_merge.clicked.connect(self.merge_files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            self.file_list.addItems(files)

    def merge_files(self):
        if self.file_list.count() < 2:
            QMessageBox.warning(self, "Warning", "Please add at least 2 files to merge.")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if output_path:
            paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            if PDFEngine.merge_pdfs(paths, output_path):
                QMessageBox.information(self, "Success", f"PDFs merged successfully to {output_path}")

class SplitWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("Split PDF Document")
        self.title.setObjectName("Title")
        self.layout.addWidget(self.title)
        
        self.info_label = QLabel("Select a PDF to split into individual pages")
        self.info_label.setStyleSheet("color: #A1A1AA; margin-bottom: 10px;")
        self.layout.addWidget(self.info_label)
        
        self.btn_select = QPushButton("Select PDF")
        self.btn_select.setStyleSheet("background-color: #27272A; color: white; padding: 10px; border-radius: 6px;")
        self.layout.addWidget(self.btn_select)
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #71717A;")
        self.layout.addWidget(self.file_path_label)
        
        self.layout.addStretch()
        
        self.btn_split = QPushButton("Split Now")
        self.btn_split.setStyleSheet("background-color: #3B82F6; color: white; padding: 15px; border-radius: 6px; font-weight: bold;")
        self.layout.addWidget(self.btn_split)
        
        self.current_path = None
        self.btn_select.clicked.connect(self.select_file)
        self.btn_split.clicked.connect(self.split_file)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self.current_path = path
            self.file_path_label.setText(path)

    def split_file(self):
        if not self.current_path:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            if PDFEngine.split_pdf(self.current_path, output_dir):
                QMessageBox.information(self, "Success", f"PDF split into pages in: {output_dir}")

class ToolsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("Optimization & Conversion")
        self.title.setObjectName("Title")
        self.layout.addWidget(self.title)
        
        # Compression Section
        self.comp_card = QFrame()
        self.comp_card.setStyleSheet("background-color: #161618; border: 1px solid #27272A; border-radius: 8px; padding: 15px;")
        comp_layout = QVBoxLayout(self.comp_card)
        comp_layout.addWidget(QLabel("<b>Compress PDF</b><br><small>Reduce file size without losing quality.</small>"))
        self.btn_compress = QPushButton("Compress Selected File")
        self.btn_compress.setStyleSheet("background-color: #3B82F6; color: white; padding: 10px; border-radius: 4px;")
        comp_layout.addWidget(self.btn_compress)
        self.layout.addWidget(self.comp_card)
        
        self.layout.addSpacing(20)
        
        # Image Conversion Section
        self.img_card = QFrame()
        self.img_card.setStyleSheet("background-color: #161618; border: 1px solid #27272A; border-radius: 8px; padding: 15px;")
        img_layout = QVBoxLayout(self.img_card)
        img_layout.addWidget(QLabel("<b>PDF to Image</b><br><small>Convert pages into high-quality JPG/PNG.</small>"))
        self.btn_convert = QPushButton("Convert to Images")
        self.btn_convert.setStyleSheet("background-color: #10B981; color: white; padding: 10px; border-radius: 4px;")
        img_layout.addWidget(self.btn_convert)
        self.layout.addWidget(self.img_card)
        
        self.layout.addStretch()
        
        self.current_path = None
        self.btn_compress.clicked.connect(self.run_compression)
        self.btn_convert.clicked.connect(self.run_conversion)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        return path

    def run_compression(self):
        path = self.select_file()
        if path:
            out, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
            if out:
                PDFEngine.compress_pdf(path, out)
                QMessageBox.information(self, "Success", "PDF compressed successfully!")

    def run_conversion(self):
        path = self.select_file()
        if path:
            out_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Images")
            if out_dir:
                PDFEngine.pdf_to_images(path, out_dir)
                QMessageBox.information(self, "Success", "PDF converted to images!")

class PDFMasterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Master - Pro PDF Editing")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
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

    def init_view_page(self):
        layout = QVBoxLayout(self.view_page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Welcome placeholder (initially visible)
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        placeholder = QLabel("Open a PDF to start viewing")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #71717A; font-size: 16px;")
        welcome_layout.addWidget(placeholder)
        
        self.btn_open = QPushButton("Open PDF")
        self.btn_open.setFixedWidth(120)
        self.btn_open.setStyleSheet("background-color: #3B82F6; color: white; padding: 8px; border-radius: 4px;")
        self.btn_open.clicked.connect(self.open_pdf)
        welcome_layout.addWidget(self.btn_open, 0, Qt.AlignCenter)
        
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
        self.workspace.setCurrentIndex(index)
        btns = [self.sidebar.btn_view, self.sidebar.btn_merge, self.sidebar.btn_split, self.sidebar.btn_tools]
        for i, btn in enumerate(btns):
            btn.setChecked(i == index)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.welcome_widget.hide()
            self.pdf_viewer.show()
            self.pdf_viewer.load_pdf(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMasterApp()
    window.show()
    sys.exit(app.exec())
