import os
import sys

def render_pdf_to_images(pdf_path, output_dir, dpi=150):
    import fitz  # PyMuPDF
    
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    print(f"Total pages in {pdf_path}: {len(doc)}")
    
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    
    image_paths = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = os.path.join(output_dir, f"page_{page_num + 1:02d}.png")
        pix.save(out_path)
        image_paths.append(out_path)
        print(f"Rendered Page {page_num + 1}/{len(doc)} -> {out_path} ({pix.width}x{pix.height})")
        
    doc.close()
    return image_paths

if __name__ == "__main__":
    pdf_path = os.path.abspath("LogShield_IEEE_Paper_Official.pdf")
    output_dir = os.path.abspath("scratch/paper_page_previews")
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
        
    render_pdf_to_images(pdf_path, output_dir)
