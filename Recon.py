import os
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
from tqdm import tqdm

# 🎨 CLI Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 📦 File extension mapping
extension_categories = {
    'js': ['.js'],
    'json': ['.json'],
    'php': ['.php'],
    'asp': ['.asp', '.aspx'],
    'jsp': ['.jsp'],
    'html': ['.html', '.htm'],
    'txt': ['.txt', '.log'],
    'xml': ['.xml'],
    'sql': ['.sql'],
    'config': ['.conf', '.config', '.ini', '.env'],
    'zip': ['.zip', '.tar', '.gz', '.rar', '.7z'],
    'bak': ['.bak', '.old', '.backup'],
    'css': ['.css'],
}

# 🎯 Banner
def banner():
    print(f"""{Colors.OKCYAN}
╔═══════════════════════════════════════════════╗
║         🛡️  PassiveReconPro v1.0 🕵️‍♂️          ║
║     Advanced URL Intelligence & Analyzer      ║
╚═══════════════════════════════════════════════╝
{Colors.ENDC}""")

# 🔍 Check if path is a file
def is_file_path(path):
    return '.' in path.split('/')[-1]

# 🧪 Categorize by extension
def categorize_file(path):
    for category, extensions in extension_categories.items():
        if any(path.lower().endswith(ext) for ext in extensions):
            return category
    return 'others'

# 🧠 Main logic
def extract_dirs_files_params(urls):
    directories = set()
    files = set()
    parameters = set()
    domains = set()
    categorized_files = defaultdict(set)
    cms_hits = set()

    for url in tqdm(urls, desc=f"{Colors.OKBLUE}Analyzing URLs{Colors.ENDC}"):
        parsed = urlparse(url.strip())
        path = parsed.path
        domains.add(parsed.netloc)

        if not path or path == "/":
            continue

        # 🎯 Extract directories
        parts = path.strip("/").split("/")
        for i in range(1, len(parts)):
            dir_path = "/" + "/".join(parts[:i]) + "/"
            directories.add(dir_path)

        # 📄 Extract files
        if is_file_path(path):
            files.add(path)
            category = categorize_file(path)
            categorized_files[category].add(path)
        else:
            directories.add(path if path.endswith("/") else path + "/")

        # 🔍 CMS detection
        if "wp-admin" in path or "wp-content" in path:
            cms_hits.add("WordPress")
        if "public/index.php" in path:
            cms_hits.add("Laravel")

        # 🧵 Extract GET parameters
        query = parsed.query
        if query:
            params = parse_qs(query)
            parameters.update(params.keys())

    return sorted(directories), sorted(files), sorted(parameters), sorted(domains), categorized_files, cms_hits

# 📁 Read old data
def read_existing_set(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
        return set(line.strip() for line in f if line.strip())

# 📝 Write updated list (no duplicates)
def write_updated_list(filepath, new_items):
    existing_items = read_existing_set(filepath)
    combined = sorted(existing_items.union(new_items))
    with open(filepath, "w") as f:
        f.write("\n".join(combined))

# 💾 Save by extension
def save_all_wordlists(categorized_files):
    for category, paths in categorized_files.items():
        filepath = f"output/{category}.txt"
        write_updated_list(filepath, paths)
        print(f"{Colors.OKGREEN}[+] Saved {len(paths)} {category.upper()} paths to {filepath}{Colors.ENDC}")

# 📊 Print Summary
def print_summary(domains, directories, files, parameters, categorized_files, cms_hits):
    print(f"\n{Colors.HEADER}{Colors.BOLD}📊 Summary Report:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}🌐 Domains found: {len(domains)}")
    for d in domains:
        print(f"   - {d}")

    print(f"{Colors.OKGREEN}📁 Total directories: {len(directories)}")
    print(f"{Colors.OKBLUE}📄 Total files: {len(files)}")

    print(f"{Colors.WARNING}🔍 Parameters Extracted: {len(parameters)}")
    for p in parameters:
        print(f"   - {p}")

    print(f"{Colors.FAIL}🧩 CMS Detection Hits: {', '.join(cms_hits) if cms_hits else 'None'}{Colors.ENDC}")

    print(f"{Colors.BOLD}\n📂 File Extensions Breakdown:{Colors.ENDC}")
    for cat, items in categorized_files.items():
        print(f" - {cat.upper()}: {len(items)}")

# 🚀 Main function
def run_passive_recon(input_path):
    banner()

    if not os.path.exists(input_path):
        print(f"{Colors.FAIL}❌ File not found: {input_path}{Colors.ENDC}")
        return

    with open(input_path, "r", encoding='utf-8', errors='ignore') as f:
        urls = [line.strip() for line in f if line.strip()]

    directories, files, parameters, domains, categorized_files, cms_hits = extract_dirs_files_params(urls)

    os.makedirs("output", exist_ok=True)
    write_updated_list("output/dirs.txt", directories)
    write_updated_list("output/files.txt", files)
    write_updated_list("output/params.txt", parameters)

    save_all_wordlists(categorized_files)
    print_summary(domains, directories, files, parameters, categorized_files, cms_hits)

    print(f"\n{Colors.OKGREEN}✅ All results saved in 'output/' folder. Happy hacking! 🚀{Colors.ENDC}")

# 🧪 Direct usage example
if __name__ == "__main__":
    # 📝 Replace with your file or uncomment below to ask:
    # input_path = input("📂 Enter URL list file: ").strip()
    input_path = "urls.txt"
    run_passive_recon(input_path)
