import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
import os

class PDFEngine:
    """Core engine for PDF manipulations using PyMuPDF and pypdf."""
    
    @staticmethod
    def merge_pdfs(paths, output_path):
        writer = PdfWriter()
        for path in paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        return True

    @staticmethod
    def get_page_count(path):
        doc = fitz.open(path)
        count = doc.page_count
        doc.close()
        return count

    @staticmethod
    def render_page(path, page_num, zoom=2.0):
        doc = fitz.open(path)
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to bytes for Qt
        img_data = pix.tobytes("ppm")
        doc.close()
        return img_data

    @staticmethod
    def split_pdf(path, output_dir):
        """Splits a PDF into individual pages."""
        reader = PdfReader(path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_name = os.path.splitext(os.path.basename(path))[0]
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
        return True

    @staticmethod
    def remove_pages(path, pages_to_keep, output_path):
        """Removes pages from a PDF by keeping only specified indices."""
        reader = PdfReader(path)
        writer = PdfWriter()
        for i in pages_to_keep:
            if i < len(reader.pages):
                writer.add_page(reader.pages[i])
        
        with open(output_path, "wb") as f:
            writer.write(f)
        return True

    @staticmethod
    def add_text_annotation(path, page_num, text, x, y, output_path):
        """Adds a text annotation to a specific page."""
        doc = fitz.open(path)
        page = doc.load_page(page_num)
        page.insert_text((x, y), text, color=(1, 0, 0)) # Red text
        doc.save(output_path)
        doc.close()
        return True

    @staticmethod
    def compress_pdf(path, output_path):
        """Simple compression by re-saving with optimization."""
        doc = fitz.open(path)
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return True

    @staticmethod
    def pdf_to_images(path, output_dir, fmt="png"):
        """Converts all PDF pages to image files."""
        doc = fitz.open(path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_name = os.path.splitext(os.path.basename(path))[0]
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            pix.save(os.path.join(output_dir, f"{base_name}_{i+1}.{fmt}"))
        doc.close()
        return True
