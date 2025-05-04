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

def main():
    os.makedirs("temp_images", exist_ok=True)
    print("Created temp_images directory (or it already existed).")
    parser = argparse.ArgumentParser(description="Export math problems to LaTeX.")
    parser.add_argument('--category', type=str, help='Export only problems in this category')
    parser.add_argument('--output', type=str, default='exports/problems_export.tex', help='Output LaTeX file')
    args = parser.parse_args()

    db = MathProblemDB()
    parser = MarkdownParser()

    # Get all problems (optionally filter by category)
    if args.category:
        # You may need to look up the category_id by name
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
        # Get all images for this problem
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

    # Start LaTeX document
    latex_lines = [
        r"\documentclass{exam}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{graphicx}",
        r"\usepackage{fontspec}",
        r"\usepackage{adjustbox}",
        r"\usepackage{float}",
        r"\graphicspath{{./images/}}",
        r"\setlength{\parindent}{0pt}",
        r"\raggedright",
        r"\begin{document}",
        r"\footnotesize",
        ""
    ]

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
            # Find the image in the database export location (should be in exports/images or similar)
            # Try to copy from exports/images or temp_images if it exists
            found = False
            for src_dir in ["exports/images", "temp_images"]:
                src_path = os.path.join(src_dir, image_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, images_dir)
                    found = True
                    break
            if not found:
                print(f"Warning: Could not find image {image_name} to copy to images folder.")

    for idx, prob in enumerate(problems):
        # Each problem's content is in markdown, so convert to LaTeX
        # Prepend problem number to the first #problem command in the content
        content = prob['content']
        problem_number = prob['problem_id']
        # Replace the first #problem with #problem{number:problem_number}
        content, n_subs = re.subn(r'(#problem)(\s*\n)', fr'\1{{number:{problem_number}}}\2', content, count=1)
        latex = parser.parse(content, context='export')
        # Replace all figure environments to use [H] placement
        latex = latex.replace(r"\begin{figure}[htbp]", r"\begin{figure}[H]")
        # Wrap each problem in a samepage environment to prevent page breaks within a problem
        latex_lines.append(r"\begin{samepage}")
        latex_lines.append(latex)
        latex_lines.append(r"\end{samepage}")
        # Add extra vertical space between problems on the same page
        if not ((idx + 1) % 2 == 0 and (idx + 1) != len(problems)):
            latex_lines.append(r"\vspace{1cm}")
        latex_lines.append("")
        # Insert a page break after every two problems, except after the last one
        if (idx + 1) % 2 == 0 and (idx + 1) != len(problems):
            latex_lines.append(r"\clearpage")

    latex_lines.append(r"\end{document}")

    # Write to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))

    print(f"Exported {len(problems)} problems to {args.output}")

    # Remove figure environment and centering from images in LaTeX output
    # Replace any \begin{figure}[H]...\end{figure} with just the inner \adjustbox line
    def extract_adjustbox(match):
        content = match.group(0)
        adjustbox_match = re.search(r'(\\adjustbox\{[^}]+\}\{\\includegraphics.*?\})', content, re.DOTALL)
        if adjustbox_match:
            return adjustbox_match.group(1)
        return content  # fallback: return original if not matched
    latex = re.sub(r'\\begin\{figure\}\[H\](.*?)\\end\{figure\}', extract_adjustbox, latex, flags=re.DOTALL)

if __name__ == "__main__":
    main()