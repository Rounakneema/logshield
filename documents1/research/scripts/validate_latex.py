import re
import sys

def validate_latex(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    errors = []
    in_verbatim = False
    in_equation = False
    
    for idx, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        
        # Track lstlisting or verbatim
        if r'\begin{lstlisting}' in line or r'\begin{verbatim}' in line:
            in_verbatim = True
            continue
        if r'\end{lstlisting}' in line or r'\end{verbatim}' in line:
            in_verbatim = False
            continue
        if in_verbatim:
            continue

        # Strip comments
        # Avoid \% being counted as comment
        no_comment = ""
        escaped = False
        for c in line:
            if c == '\\':
                escaped = not escaped
                no_comment += c
            elif c == '%' and not escaped:
                break
            else:
                escaped = False
                no_comment += c
        
        # Check equation environments
        if any(env in no_comment for env in [r'\begin{equation}', r'\begin{align}', r'\begin{gather}']):
            in_equation = True
        if any(env in no_comment for env in [r'\end{equation}', r'\end{align}', r'\end{gather}']):
            in_equation = False

        # If outside display equation, check inline math
        # Look for unescaped underscores outside $...$ and outside \url{} and \href{}
        # Replace \url{...} with placeholder
        cleaned = re.sub(r'\\url\{[^}]*\}', '', no_comment)
        cleaned = re.sub(r'\\texttt\{[^}]*\}', '', cleaned)
        cleaned = re.sub(r'\\ref\{[^}]*\}', '', cleaned)
        cleaned = re.sub(r'\\label\{[^}]*\}', '', cleaned)
        cleaned = re.sub(r'\\cite\{[^}]*\}', '', cleaned)
        cleaned = re.sub(r'\\bibitem\{[^}]*\}', '', cleaned)
        cleaned = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', '', cleaned)

        # Check for unescaped _ outside $
        if not in_equation:
            parts = cleaned.split('$')
            for p_idx, part in enumerate(parts):
                if p_idx % 2 == 0:  # Outside math
                    # Look for unescaped _
                    matches = re.finditer(r'(?<!\\)_', part)
                    for m in matches:
                        errors.append((idx, f"Unescaped underscore: ...{part[max(0, m.start()-15):min(len(part), m.end()+15)]}..."))

        # Check for unclosed $
        parts = cleaned.split('$')
        if len(parts) % 2 == 0 and not in_equation:
            errors.append((idx, f"Mismatched inline $ in line: {line}"))

    print(f"Validation finished. Total potential issues: {len(errors)}")
    for line_num, err in errors:
        print(f"Line {line_num}: {err}")
    return len(errors)

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'paper/logshield_ieee_paper.tex'
    sys.exit(validate_latex(path))
