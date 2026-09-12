import os
import re
import tomllib
import sys

toml_path = r"d:\LOGSHEILD\scratch\gitleaks.toml"

with open(toml_path, 'r', encoding='utf-8') as f:
    toml_content = f.read()


try:
    config = tomllib.loads(toml_content)
except Exception as e:
    print(f"Failed to parse TOML: {e}")
    sys.exit(1)

gitleaks_rules = config.get("rules", [])
print(f"Loaded {len(gitleaks_rules)} rules from Gitleaks.")

# Now parse our generated_specifics.py to extract the tuples
gen_path = r"d:\LOGSHEILD\sidecar\logmask\catalog\generated_specifics.py"
with open(gen_path, 'r', encoding='utf-8') as f:
    gen_content = f.read()

# Match each line in GENERATED_SPECIFIC_DETECTORS
# Format:     (re.compile(r"REGEX"), "Name", "Company", "Category", 0.8),
pattern = r'    \(re\.compile\(r"(.*?)"\), "(.*?)", "(.*?)", "(.*?)", (.*?)\),'
matches = re.findall(pattern, gen_content)
print(f"Found {len(matches)} generated specific detectors.")

# Helper to normalize names for matching
def normalize(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

mapped_count = 0
new_lines = []

for match in matches:
    current_regex, name, company, category, confidence = match
    norm_name = normalize(name)
    
    # Try to find a matching rule in Gitleaks
    found_rule = None
    for rule in gitleaks_rules:
        g_id = normalize(rule.get("id", ""))
        g_desc = normalize(rule.get("description", ""))
        # if the ID matches heavily or is fully contained
        if g_id in norm_name or norm_name in g_id:
            found_rule = rule
            break
            
    if found_rule:
        g_regex = found_rule.get("regex")
        if g_regex:
            # We found a true mathematical regex!
            # Format the line with the new regex. Use raw string safe format.
            # Replace inner quotes carefully or just use triple quotes if needed
            # But the original format uses r"..."
            g_regex_escaped = g_regex.replace('"', '\\"')
            new_line = f'    (re.compile(r"{g_regex_escaped}"), "{name}", "{company}", "{category}", {confidence}),'
            new_lines.append(new_line)
            mapped_count += 1
            continue
            
    # Fallback to the original line
    new_line = f'    (re.compile(r"{current_regex}"), "{name}", "{company}", "{category}", {confidence}),'
    new_lines.append(new_line)

print(f"Successfully mapped {mapped_count} detectors to exact open-source regexes!")

# Reconstruct the file
header = gen_content.split('GENERATED_SPECIFIC_DETECTORS = [')[0] + 'GENERATED_SPECIFIC_DETECTORS = [\n'
footer = '\n]\n'
final_content = header + "\n".join(new_lines) + footer

with open(gen_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"Updated {gen_path}")
