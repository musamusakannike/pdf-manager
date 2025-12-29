# PDF Master

A professional PDF management tool built with Python and PySide6.

## Features

- **PDF Viewer**: View PDF files with zoom and navigation controls.
- **Merge PDFs**: Combine multiple PDF files into a single document.
- **Split PDFs**: Split a PDF document into individual pages.
- **Tools**: 
  - **Compress PDF**: Reduce file size without losing quality.
  - **PDF to Image**: Convert pages into high-quality images.

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
