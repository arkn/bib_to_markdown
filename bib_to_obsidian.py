#!/usr/bin/env python3
# Recommended to save this file as bib_to_obsidian.py

import bibtexparser
import bibtexparser.bibdatabase
import re
import os
import argparse
import sys

# (Helper functions are unchanged)
def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be used as a valid OS filename."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    return sanitized[:150].strip()

def clean_title(title: str) -> str:
    """Removes extra curly braces from a BibTeX title."""
    return re.sub(r'[{}]', '', title)

def format_tags(keywords_str: str) -> list[str]:
    """Converts keywords into Obsidian tag format."""
    if not keywords_str:
        return []
    tags = []
    kw_list = re.split(r'[;,]', keywords_str)
    for kw in kw_list:
        if not kw.strip(): continue
        tag = ''.join(kw.strip().title().split()).replace('-', '/')
        tags.append(tag)
    return tags

def parse_authors(authors_str: str) -> list[str]:
    """Parses the BibTeX author string into a list of names."""
    if not authors_str:
        return []
    cleaned_str = re.sub(r'\s*\n\s*', ' ', authors_str)
    return [author.strip() for author in cleaned_str.split(' and ')]

def create_literature_note_from_entry(entry: dict, output_dir: str):
    """Generates a Markdown file from a single BibTeX entry."""
    # --- Data Extraction ---
    bib_key = entry.get('ID', 'no_id')
    title = clean_title(entry.get('title', 'No Title'))
    journal = entry.get('journaltitle', '') or entry.get('journal', '')
    doi = entry.get('doi', '')
    url = entry.get('url', '')
    year = entry.get('year', '') or entry.get('date', 'n.d.').split('-')[0]
    tags = format_tags(entry.get('keywords', ''))
    
    # --- Author and Abstract Cleaning ---
    author_list = parse_authors(entry.get('author', ''))
    authors_body_formatted = ", ".join([f"[[{author}]]" for author in author_list])
    
    abstract = entry.get('abstract', '')
    # ★★★ FIX: Clean up newlines and extra whitespace in the abstract ★★★
    if abstract:
        abstract = re.sub(r'\s*\n\s*', ' ', abstract).strip()

    # --- Generate Markdown Content ---
    md_content = "---\n"
    md_content += f"title: \"{title}\"\n"
    if author_list:
        md_content += "author:\n"
        for author in author_list:
            md_content += f"  - {author}\n"
    if journal: md_content += f"journal: \"{journal}\"\n"
    if year and year != 'n.d.': md_content += f"year: {year}\n"
    if doi: md_content += f"doi: \"{doi}\"\n"
    if url: md_content += f"url: {url}\n"
    if tags:
        md_content += "tags:\n"
        for tag in tags:
            md_content += f"  - {tag}\n"
    md_content += "---\n\n"
    
    md_content += f"# {title}\n\n"
    if authors_body_formatted: md_content += f"- **Authors**: {authors_body_formatted}\n"
    if journal: md_content += f"- **Journal**: {journal}\n"
    if year and year != 'n.d.': md_content += f"- **Year**: {year}\n"
    
    md_content += "\n## TL;DR\n\n> Add a one-sentence summary here.\n\n"
    # Use the cleaned abstract
    md_content += f"## Abstract\n{abstract or 'No abstract available.'}\n\n"
    md_content += "## ✍️ My Notes\n\n> Add your personal notes and thoughts here.\n\n\n"
    md_content += "## 📚 BibTeX\n```bibtex\n"
    
    single_entry_db = bibtexparser.bibdatabase.BibDatabase()
    single_entry_db.entries = [entry]
    md_content += f"{bibtexparser.dumps(single_entry_db)}\n```\n"

    # --- Write to File ---
    sanitized_title = sanitize_filename(title)
    file_name = f"{sanitized_title} ({bib_key}).md"
    output_path = os.path.join(output_dir, file_name)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✅ Literature note '{output_path}' created successfully.")
    except IOError as e:
        print(f"❌ Error writing to file '{output_path}': {e}", file=sys.stderr)

# (Functions process_bib_file and main are unchanged)
def process_bib_file(file_path: str, output_dir: str):
    """Reads a .bib file and processes each entry."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        return
    print(f"\n--- 📖 Processing file: {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8') as bibfile:
            bib_database = bibtexparser.load(bibfile)
            if not bib_database.entries:
                print(f"ℹ️ No BibTeX entries found in '{file_path}'.")
                return
            for entry in bib_database.entries:
                create_literature_note_from_entry(entry, output_dir)
    except Exception as e:
        print(f"❌ An error occurred while processing '{file_path}': {e}", file=sys.stderr)

def main():
    """Main function to parse command-line arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Generates Obsidian literature notes (Markdown) from BibTeX files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "bibfiles", 
        metavar="FILE", 
        nargs='+', 
        help="Path to the source .bib file(s)."
    )
    parser.add_argument(
        "-o", "--output-dir", 
        default=".", 
        help="Output directory for the Markdown files.\n(Default: current directory)"
    )
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"--- 📂 Output directory created: {args.output_dir} ---")
    for bib_file_path in args.bibfiles:
        process_bib_file(bib_file_path, args.output_dir)
    print("\n--- ✨ Processing complete ---")

if __name__ == '__main__':
    main()
