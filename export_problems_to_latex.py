#!/usr/bin/env python
"""
Export all math problems from the database to a LaTeX file.

Usage:
    python export_problems_to_latex.py [--category CATEGORY] [--output FILE]

Options:
    --category CATEGORY   Only export problems in this category
    --output FILE         Output LaTeX file (default: problems_export.tex)
"""

import argparse
from db.math_db import MathProblemDB
from markdown_parser import MarkdownParser
import re
import os
import shutil
from db.math_image_db import MathImageDB

def main():

    parser = argparse.ArgumentParser(description="Export math problems to LaTeX.")
    parser.add_argument('--category', type=str, help='Export only problems in this category')
    parser.add_argument('--output', type=str, default='exports/problems_export.tex', help='Output LaTeX file')
    args = parser.parse_args()

    db = MathProblemDB()
    md_parser = MarkdownParser()
    image_db = MathImageDB()

    # Export all problems (optionally filter by category)
    if args.category:
        success, categories = db.get_categories()
        if not success:
            print("Failed to get categories.")
            return
        cat_id = next((c['category_id'] for c in categories if c['name'] == args.category), None)
        if cat_id is None:
            print(f"Category '{args.category}' not found.")
            return
        success, problems = db.get_problems_list(category_id=cat_id, limit=10000)
    else:
        success, problems = db.get_problems_list(limit=10000)
    if not success:
        print("Failed to get problems:", problems)
        return

    # Ensure all images are exported from the DB to the export images directory
    output_dir = os.path.dirname(args.output)
    print(f"=====================output_dir: {output_dir}")
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    for prob in problems:
        content = prob['content']
        # Find all image names in the LaTeX content
        image_names = re.findall(r'\\includegraphics(?:\[.*?\])?\{([^\}]+)\}', content)
        print(f"Image names found in content: {image_names}")
        for image_name in image_names:
            output_path = os.path.join(images_dir, image_name)
            print(f"[SCRIPT DEBUG] About to export image: {image_name} to {output_path}")
            success, msg = image_db.export_to_file(image_name, output_path)
            if not success:
                print(f"Warning: Could not export image {image_name} to {images_dir}: {msg}")

    # --- Build all problems as a single LaTeX string ---
    all_problems_latex = ""
    for idx, prob in enumerate(problems):
        content = prob['content']
        problem_number = prob['problem_id']
        content, n_subs = re.subn(r'(#problem)(\s*\n)', fr'\1{{number:{problem_number}}}\2', content, count=1)
        latex = md_parser.parse(content, context='export')
        latex = latex.replace(r"\\begin{figure}[htbp]", r"\\begin{figure}[H]")
        all_problems_latex += "\\begin{samepage}\n" + latex + "\n\\end{samepage}\n"
        if not ((idx + 1) % 2 == 0 and (idx + 1) != len(problems)):
            all_problems_latex += "\\vspace{1cm}\n"
        if (idx + 1) % 2 == 0 and (idx + 1) != len(problems):
            all_problems_latex += "\\clearpage\n"
    # --- Use create_latex_document to assemble the full document ---
    full_latex = md_parser.create_latex_document(all_problems_latex)
    # Write to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_latex)

    print(f"Exported {len(problems)} problems to {args.output}")

if __name__ == "__main__":
    main()