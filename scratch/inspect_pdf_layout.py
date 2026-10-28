import sys
import io
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = fitz.open("LogShield_IEEE_Paper_Official.pdf")
print("=== PDF INSPECTION REPORT ===")
print(f"Total Pages: {len(doc)}")

for page_idx in range(len(doc)):
    page = doc[page_idx]
    rect = page.rect
    blocks = page.get_text("blocks")
    images = page.get_images()
    drawings = page.get_drawings()
    
    # Check text bounds
    min_x = min((b[0] for b in blocks), default=0)
    max_x = max((b[2] for b in blocks), default=0)
    min_y = min((b[1] for b in blocks), default=0)
    max_y = max((b[3] for b in blocks), default=0)
    
    print(f"\n--- Page {page_idx + 1} ({rect.width:.1f} x {rect.height:.1f} pt) ---")
    print(f"Text Blocks: {len(blocks)}, Images: {len(images)}, Drawings: {len(drawings)}")
    print(f"Text Bounding Box: X=[{min_x:.1f}, {max_x:.1f}], Y=[{min_y:.1f}, {max_y:.1f}]")
    
    # Check for text clipping past margins
    # Standard margins: Left 45 pt (0.625"), Right 612-45 = 567 pt
    left_margin_violations = [b for b in blocks if b[0] < 40]
    right_margin_violations = [b for b in blocks if b[2] > 572]
    top_margin_violations = [b for b in blocks if b[1] < 45]
    bottom_margin_violations = [b for b in blocks if b[3] > 740]
    
    if left_margin_violations:
        print(f"  [WARN] Left margin violation: {len(left_margin_violations)} blocks")
    if right_margin_violations:
        print(f"  [WARN] Right margin violation: {len(right_margin_violations)} blocks")
    if bottom_margin_violations:
        print(f"  [WARN] Bottom margin violation: {len(bottom_margin_violations)} blocks")
        
    # Sample first and last text block
    if blocks:
        first_text = blocks[0][4].strip().replace('\n', ' ')[:70]
        last_text = blocks[-1][4].strip().replace('\n', ' ')[:70]
        print(f"  Top content: {first_text}...")
        print(f"  Bottom content: {last_text}...")
        
    for img_idx, img in enumerate(images):
        xref = img[0]
        print(f"  Embedded Image {img_idx + 1}: xref={xref}, w={img[2]}, h={img[3]}")
doc.close()
