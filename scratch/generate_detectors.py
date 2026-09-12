import os
import sys
import glob

sys.path.insert(0, r"d:\LOGSHEILD")
try:
    from sidecar.logmask.catalog import ALL_SPECIFIC_DETECTORS
    implemented_names = {d[1].lower() for d in ALL_SPECIFIC_DETECTORS}
except Exception as e:
    print(f"Error importing catalog: {e}")
    implemented_names = set()

html_dir = r"d:\LOGSHEILD\gitguardian_specific_detectors"
html_files = glob.glob(os.path.join(html_dir, "*.html"))

generated_code = [
    '"""',
    'Generated Specific Detectors',
    '==============================',
    'Auto-generated from 400+ specific detector profiles.',
    'Uses KV-bound regexes to prevent Pass 2 False Positives.',
    '"""',
    '',
    'import re',
    '',
    'GENERATED_SPECIFIC_DETECTORS = ['
]

varname_additions = set()

def determine_category(name_lower):
    if any(x in name_lower for x in ['aws', 'azure', 'gcp', 'google', 'cloud', 'ocean', 'alibaba', 'tencent', 'heroku', 'vercel', 'netlify']):
        return "cloud"
    if any(x in name_lower for x in ['ai', 'openai', 'anthropic', 'hugging', 'model', 'llm', 'api']):
        return "ai"
    if any(x in name_lower for x in ['git', 'npm', 'docker', 'kubernetes', 'vault', 'jira', 'confluence', 'ci', 'cd']):
        return "vcs_cicd"
    if any(x in name_lower for x in ['sql', 'mongo', 'redis', 'db', 'database', 'kafka', 'amqp']):
        return "database"
    if any(x in name_lower for x in ['slack', 'discord', 'telegram', 'twilio', 'mail', 'message', 'smtp', 'sendgrid']):
        return "messaging"
    if any(x in name_lower for x in ['stripe', 'pay', 'bank', 'card', 'checkout']):
        return "payment"
    if any(x in name_lower for x in ['rsa', 'pem', 'pgp', 'key', 'cert', 'ssh', 'secret']):
        return "private_keys"
    return "generic"

missing_count = 0

for file in html_files:
    basename = os.path.basename(file).replace(".html", "")
    name = basename.replace("_", " ").title()
    
    if name.lower() in implemented_names:
        continue
        
    missing_count += 1
    
    # Heuristic categorization
    cat = determine_category(name.lower())
    
    # Company extraction (first word usually)
    company = name.split(" ")[0]
    
    # The variable name heuristic
    var_prefix = basename.replace("_", ".*?")
    
    # KV-bound pattern: requires the variable name to be near the secret to trigger specific detector rules
    # This prevents a random 32-char string from flagging as 400 different specific detectors in Pass 2
    pattern = f'(?i)(?:{var_prefix})[\\s=:]+([a-zA-Z0-9_\\-]{{16,}})'
    
    # confidence 0.85 ensures it hits the FLAG threshold minimum in the override rule, but isn't blindly MASK without other factors
    line = f'    (re.compile(r"{pattern}"), "{name}", "{company}", "{cat}", 0.85),'
    generated_code.append(line)
    
    varname_additions.add(basename.upper())
    varname_additions.add(basename.replace("_", ""))

generated_code.append(']')
generated_code.append('')

out_path = r"d:\LOGSHEILD\sidecar\logmask\catalog\generated_specifics.py"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(generated_code))
    
print(f"Generated {missing_count} detectors to {out_path}")

# Print out some varname additions for the next step
print("VARNAME Additions (sample):")
print(list(varname_additions)[:20])
