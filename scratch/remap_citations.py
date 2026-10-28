import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sort_references import old_to_new, sorted_refs

def remap_text_citations(text):
    """
    Carefully replaces bracketed citations [x] with their new index [y].
    Handles multiple citations in a single bracket e.g. [2, 3] or [12]-[14] or [2], [3].
    """
    # Replace [old_id] with a temporary token __CITE_ID__
    def replace_bracket(match):
        inner = match.group(1)
        # Check if inner is pure numbers/commas/spaces/hyphens
        parts = re.split(r'([,\s–\-]+)', inner)
        new_parts = []
        for p in parts:
            if p.isdigit():
                old_val = int(p)
                if old_val in old_to_new:
                    new_val = old_to_new[old_val]
                    new_parts.append(str(new_val))
                else:
                    new_parts.append(p)
            else:
                new_parts.append(p)
        return "[" + "".join(new_parts) + "]"

    # Pattern matches [1] or [1, 2] or [1], [2]
    # We do a two-pass replacement to avoid cascading replacements (e.g. 1 -> 6, then 6 -> 3)
    def tag_bracket(match):
        inner = match.group(1)
        parts = re.split(r'([,\s–\-]+)', inner)
        new_parts = []
        for p in parts:
            if p.isdigit():
                old_val = int(p)
                if old_val in old_to_new:
                    new_parts.append(f"__CITE_{old_to_new[old_val]}__")
                else:
                    new_parts.append(p)
            else:
                new_parts.append(p)
        return "[" + "".join(new_parts) + "]"

    # Tag all
    tagged = re.sub(r'\[(\d+(?:[,\s–\-]+\d+)*)\]', tag_bracket, text)
    
    # Untag
    untagged = re.sub(r'__CITE_(\d+)__', r'\1', tagged)
    return untagged

if __name__ == "__main__":
    sample = "systems [1]; observability [2], [3]. Output [4]. Study [5], [6]. Tooling [12]-[14]."
    remapped = remap_text_citations(sample)
    print("Original:", sample)
    print("Remapped:", remapped)
