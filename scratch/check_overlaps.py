import sys
import io
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = fitz.open("LogShield_IEEE_Paper_Official.pdf")

print("=== CHECKING FOR OVERLAPPING TEXT RECTANGLES ===")
total_overlaps = 0
for pno in range(len(doc)):
    page = doc[pno]
    blocks = page.get_text("blocks")
    # b: (x0, y0, x1, y1, text, block_no, block_type)
    # block_type 0 is text
    text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]
    
    overlaps_on_page = 0
    for i in range(len(text_blocks)):
        r1 = fitz.Rect(text_blocks[i][:4])
        for j in range(i + 1, len(text_blocks)):
            r2 = fitz.Rect(text_blocks[j][:4])
            # Intersection rect
            inter = r1 & r2
            # Allow tiny rounding overlap (< 1 pt)
            if inter.is_valid and inter.width > 2 and inter.height > 2:
                # Check if they really collide
                t1 = text_blocks[i][4].strip().replace('\n', ' ')[:40]
                t2 = text_blocks[j][4].strip().replace('\n', ' ')[:40]
                print(f"Page {pno + 1} Overlap ({inter.width:.1f}x{inter.height:.1f} pt):")
                print(f"   Block A: '{t1}'")
                print(f"   Block B: '{t2}'")
                overlaps_on_page += 1
                total_overlaps += 1
    if overlaps_on_page == 0:
        print(f"Page {pno + 1}: Clean (0 overlaps)")

print(f"\nTotal Text Overlaps across entire paper: {total_overlaps}")
doc.close()
