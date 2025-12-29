# PDF Master

A professional PDF management tool built with Python and PySide6, featuring a modern dark-themed UI with comprehensive PDF manipulation capabilities.

## Features

### 📖 Document Viewer
- View PDF files with smooth navigation
- Zoom controls (in, out, fit to window)
- Page navigation (previous/next)
- Annotation support - add text annotations directly to PDFs
- Drag and drop support for quick file loading

### 🔀 Merge PDFs
- Combine multiple PDF files into a single document
- Drag and drop interface for easy file management
- Reorder files before merging
- Recent files tracking

### ✂️ Split PDFs
- Split PDF documents into individual pages
- Extract specific page ranges
- Drag and drop support
- Batch processing capabilities

### 🛠️ PDF Tools & Utilities

#### 🗜️ Compression
- Reduce file size while maintaining quality
- Optimized compression algorithms

#### 🖼️ Format Conversion
- **PDF to Images**: Convert pages to high-quality JPG/PNG images
- **Office Conversion**: 
  - PDF ↔ Word (.docx)
  - PDF ↔ Excel (.xlsx)
  - PDF ↔ PowerPoint (.pptx)

#### 💧 Watermarking
- Add custom text watermarks to all pages
- Configurable watermark text
- Professional watermark placement

#### 🔒 Security & Encryption
- **Encrypt PDFs**: Password-protect your documents
- **Decrypt PDFs**: Unlock password-protected files
- Secure encryption standards

#### 🔄 Page Rotation
- Rotate pages by 90°, 180°, or 270°
- Rotate all pages or specific pages
- Preserve document structure

#### 📝 Text Extraction
- Extract all text content from PDFs
- Save extracted text to .txt files
- Maintain text formatting where possible

#### ℹ️ Metadata Viewer
- View comprehensive PDF properties
- Display document information:
  - Title, Author, Subject
  - Creator, Producer
  - Creation and modification dates
  - **Security**: Watermark, Encrypt, and Decrypt PDFs.

#### 📑 Page Organization
- Extract specific pages (e.g., 1, 3-5, 7)
- Remove unwanted pages
- Create custom page selections

## User Interface (UI)
- **Modern Dark Theme**: Sleek, professional dark-themed interface with gradient accents
- **Drag & Drop Support**: Easily add files by dragging them into the application
- **Responsive Design**: Scrollable interfaces for comfortable viewing
- **Visual Feedback**: Smooth animations and hover effects
- **Status Bar**: Real-time progress updates and notifications
- **Tooltips**: Helpful hints for all major features

## 📦 Building the Application

You can build the application for your operating system (Windows, macOS, Linux) using the included build script.

**Prerequisites:**
- Python 3.8+ installed
- Dependencies installed (`pip install -r requirements.txt`)
- PyInstaller installed (`pip install pyinstaller`)

**Build Command:**
Run the following command from the project root:

```bash
python scripts/build_executable.py
```

- **Windows**: Generates a `.exe` file in the `dist` folder.
- **macOS**: Generates a `.app` bundle or executable in `dist`.
- **Linux**: Generates a binary executable in `dist`.

## Keyboard Shortcuts

- **Ctrl+1**: Switch to Document Viewer
- **Ctrl+2**: Switch to Merge PDFs
- **Ctrl+3**: Switch to Split PDF
- **Ctrl+4**: Switch to PDF Tools
- **Ctrl+O**: Add files (in Merge view)
- **Ctrl+M**: Merge PDFs (in Merge view)

## Installation

### Prerequisites

- Python 3.8+
- System libraries for Qt (Linux): `libxcb-cursor0`

### Setup

1. **Clone the repository** (or download the source code).

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   *Note: If you encounter `externally-managed-environment` errors on Linux, ensure you are working within the virtual environment.*

## Usage

Run the application:
```bash
python main.py
```

## Structure

- `main.py`: Main entry point and UI implementation.
- `scripts/pdf_engine.py`: Backend logic for PDF manipulations.
