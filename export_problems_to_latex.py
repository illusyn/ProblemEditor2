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

# --- Load the centralized LaTeX template ---
template_path = os.path.join(os.path.dirname(__file__), "resources", "default_template.tex")
with open(template_path, "r", encoding="utf-8") as f:
    latex_template = f.read()

def main():
    os.makedirs("temp_images", exist_ok=True)
    print("Created temp_images directory (or it already existed).")
    parser = argparse.ArgumentParser(description="Export math problems to LaTeX.")
    parser.add_argument('--category', type=str, help='Export only problems in this category')
    parser.add_argument('--output', type=str, default='exports/problems_export.tex', help='Output LaTeX file')
    args = parser.parse_args()

    db = MathProblemDB()
    md_parser = MarkdownParser()

    # Get all problems (optionally filter by category)
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

    # For each problem, export all associated images from the DB
    for prob in problems:
        problem_id = prob['problem_id']
        db.cur.execute("""
            SELECT image_name FROM problem_images WHERE problem_id = ?
        """, (problem_id,))
        image_rows = db.cur.fetchall()
        for (image_name,) in image_rows:
            print(f"Attempting to export image: {image_name} for problem {problem_id}")
            success, msg = db.export_image(image_name=image_name)
            if success:
                print(f"Successfully exported {image_name}")
            else:
                print(f"Failed to export {image_name}: {msg}")

    # Ensure all images are copied to an 'images' folder next to the .tex file
    output_dir = os.path.dirname(args.output)
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    for prob in problems:
        problem_id = prob['problem_id']
        db.cur.execute("""
            SELECT image_name FROM problem_images WHERE problem_id = ?
        """, (problem_id,))
        image_rows = db.cur.fetchall()
        for (image_name,) in image_rows:
            found = False
            for src_dir in ["exports/images", "temp_images"]:
                src_path = os.path.join(src_dir, image_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, images_dir)
                    found = True
                    break
            if not found:
                print(f"Warning: Could not find image {image_name} to copy to images folder.")

    # --- Build all problems as a single LaTeX string ---
    all_problems_latex = ""
    for idx, prob in enumerate(problems):
        content = prob['content']
        problem_number = prob['problem_id']
        # Replace the first #problem with #problem{number:problem_number}
        content, n_subs = re.subn(r'(#problem)(\s*\n)', fr'\1{{number:{problem_number}}}\2', content, count=1)
        latex = md_parser.parse(content, context='export')
        # Replace all figure environments to use [H] placement
        latex = latex.replace(r"\begin{figure}[htbp]", r"\begin{figure}[H]")
        # Wrap each problem in a samepage environment
        all_problems_latex += "\\begin{samepage}\n" + latex + "\n\\end{samepage}\n"
        # Add extra vertical space between problems on the same page
        if not ((idx + 1) % 2 == 0 and (idx + 1) != len(problems)):
            all_problems_latex += "\\vspace{1cm}\n"
        # Insert a page break after every two problems, except after the last one
        if (idx + 1) % 2 == 0 and (idx + 1) != len(problems):
            all_problems_latex += "\\clearpage\n"

    # --- Fill the template ---
    full_latex = latex_template.replace("#CONTENT#", all_problems_latex)

    # Write to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_latex)

    print(f"Exported {len(problems)} problems to {args.output}")

if __name__ == "__main__":
    main()