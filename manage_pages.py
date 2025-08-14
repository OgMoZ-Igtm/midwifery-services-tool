import os
import re
import argparse
from collections import defaultdict
from datetime import datetime

PAGES_DIR = "pages"
LOG_FILE = "page_conflicts.log"
title_map = defaultdict(list)
name_map = defaultdict(list)
rename_log = []


def extract_page_title(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(
            r"st\.set_page_config\s*\(.*?page_title\s*=\s*[\"'](.+?)[\"']", content
        )
        return match.group(1) if match else None


def rename_file(old_path, new_name, dry_run=False):
    new_path = os.path.join(PAGES_DIR, new_name)
    if dry_run:
        print(f"[DRY-RUN] 🔄 Would rename: {os.path.basename(old_path)} → {new_name}")
    else:
        os.rename(old_path, new_path)
        print(f"🔄 Renamed: {os.path.basename(old_path)} → {new_name}")
        rename_log.append(f"{os.path.basename(old_path)} → {new_name}")


def scan_pages():
    for filename in os.listdir(PAGES_DIR):
        if filename.endswith(".py"):
            path = os.path.join(PAGES_DIR, filename)
            title = extract_page_title(path)
            if title:
                title_map[title].append(filename)
            name_key = filename.split("_")[-1].replace(".py", "").lower()
            name_map[name_key].append(filename)


def report_conflicts():
    print("\n🔍 Checking for conflicts...\n")
    total_conflicts = 0

    for title, files in title_map.items():
        if len(files) > 1:
            total_conflicts += 1
            print(f"⚠️ Duplicate page_title '{title}' in: {', '.join(files)}")

    for name_key, files in name_map.items():
        if len(files) > 1:
            total_conflicts += 1
            print(f"⚠️ Conflicting filename suffix '{name_key}' in: {', '.join(files)}")

    return total_conflicts


def fix_conflicts(dry_run=False):
    renamed_count = 0

    for title, files in title_map.items():
        if len(files) > 1:
            for i, file in enumerate(files):
                if i == 0:
                    continue
                new_name = f"{file[:-3]}_dup{i}.py"
                rename_file(os.path.join(PAGES_DIR, file), new_name, dry_run)
                renamed_count += 1

    for name_key, files in name_map.items():
        if len(files) > 1:
            for i, file in enumerate(files):
                new_name = f"{file[:-3]}_conflict{i}.py"
                rename_file(os.path.join(PAGES_DIR, file), new_name, dry_run)
                renamed_count += 1

    return renamed_count


def write_log():
    if rename_log:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n🗓️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for line in rename_log:
                f.write(f"{line}\n")
        print(f"\n📝 Log saved to {LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="🧩 Manage Streamlit multipage conflicts"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Just show what would be changed"
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="Automatically rename conflicting files"
    )
    args = parser.parse_args()

    scan_pages()
    total_conflicts = report_conflicts()

    if args.auto_fix or args.dry_run:
        print("\n⚙️ Resolving conflicts...\n")
        renamed = fix_conflicts(dry_run=args.dry_run)
        if not args.dry_run:
            write_log()
    else:
        renamed = 0


if __name__ == "__main__":
    main()
