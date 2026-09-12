import os
import re
import json
import yaml
import sys

truffle_path = r"d:\LOGSHEILD\scratch\trufflehog.json"
secrets_path = r"d:\LOGSHEILD\scratch\secrets_db.yml"
gen_path = r"d:\LOGSHEILD\sidecar\logmask\catalog\generated_specifics.py"

# Load TruffleHog rules
with open(truffle_path, 'r', encoding='utf-8') as f:
    truffle_rules = json.load(f)

# Load Secrets Patterns DB rules
with open(secrets_path, 'r', encoding='utf-8') as f:
    secrets_db = yaml.safe_load(f)
    secrets_rules = secrets_db.get("patterns", [])

# Load existing generated detectors
with open(gen_path, 'r', encoding='utf-8') as f:
    gen_content = f.read()

pattern = r'    \(re\.compile\(r"(.*?)"\), "(.*?)", "(.*?)", "(.*?)", (.*?)\),'
matches = re.findall(pattern, gen_content)

def normalize(name):
    return re.sub(r'[^a-z0-9]', '', str(name).lower())

mapped_count = 0
new_lines = []

for match in matches:
    current_regex, name, company, category, confidence = match
    norm_name = normalize(name)
    
    # We only want to map ones that are STILL using our KV-bound format
    if "(?i)(?:" not in current_regex:
        # It's already an exact regex (e.g. from Gitleaks)! Leave it alone.
        new_line = f'    (re.compile(r"{current_regex}"), "{name}", "{company}", "{category}", {confidence}),'
        new_lines.append(new_line)
        continue
        
    found_regex = None
    
    # Check TruffleHog
    for rule_name, rule_regex in truffle_rules.items():
        if normalize(rule_name) in norm_name or norm_name in normalize(rule_name):
            found_regex = rule_regex
            break
            
    # Check Secrets Patterns DB if not found
    if not found_regex:
        for rule_wrapper in secrets_rules:
            rule = rule_wrapper.get("pattern", {})
            r_name = rule.get("name", "")
            r_regex = rule.get("regex", "")
            if normalize(r_name) in norm_name or norm_name in normalize(r_name):
                found_regex = r_regex
                break
                
    if found_regex:
        g_regex_escaped = found_regex.replace('"', '\\"').replace('\n', '')
        new_line = f'    (re.compile(r"{g_regex_escaped}"), "{name}", "{company}", "{category}", {confidence}),'
        new_lines.append(new_line)
        mapped_count += 1
    else:
        new_line = f'    (re.compile(r"{current_regex}"), "{name}", "{company}", "{category}", {confidence}),'
        new_lines.append(new_line)

print(f"Successfully mapped {mapped_count} ADDITIONAL detectors to exact open-source regexes!")

header = gen_content.split('GENERATED_SPECIFIC_DETECTORS = [')[0] + 'GENERATED_SPECIFIC_DETECTORS = [\n'
footer = '\n]\n'
final_content = header + "\n".join(new_lines) + footer

with open(gen_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"Updated {gen_path}")
