#!/usr/bin/env python
"""
Export all math problems from the database to a LaTeX file.

Usage:
    python export_problems_to_latex.py [--category CATEGORY] [--output FILE]

Options:
    --category CATEGORY   Only export problems in this category
    --output FILE         Output LaTeX file (default: problems_export.tex)
    --all                 Include answer, earmark, and problem types after each problem
"""

import argparse
from db.math_db import MathProblemDB
from markdown_parser import MarkdownParser
import re
import os
import shutil
from db.math_image_db import MathImageDB
from config_loader import ConfigLoader
import sqlite3
import io

# Try to import PIL, but don't fail if it's not available
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def latex_escape(text):
    return text.replace('_', r'\_')

def export_images_from_content(problem_id, content, images_dir):
    """
    Export images that are referenced in the problem content.
    This handles cases where images are used in content but not in problem_images or problem_image_map.
    """
    exported_count = 0
    
    # Extract image references from content
    image_refs = re.findall(r'\\includegraphics.*?\{(.*?)\}', content)
    
    if not image_refs:
        return exported_count
    
    print(f"  Found {len(image_refs)} image references in content for problem {problem_id}")
    
    for image_name in image_refs:
        output_path = os.path.join(images_dir, image_name)
        
        # Skip if already exported
        if os.path.exists(output_path):
            continue
            
        # Try to get from math_images.db
        try:
            images_conn = sqlite3.connect("db/math_images.db")
            images_cursor = images_conn.cursor()
            
            images_cursor.execute("SELECT data FROM images WHERE name = ?", (image_name,))
            result = images_cursor.fetchone()
            
            if result:
                image_data = result[0]
                
                # Check if we need to convert DIB to PNG
                if HAS_PIL:
                    try:
                        # Try to open the image data
                        img = Image.open(io.BytesIO(image_data))
                        
                        # If it's DIB/BMP format and has .png extension, convert it
                        if img.format in ['DIB', 'BMP'] and image_name.endswith('.png'):
                            # Convert to PNG
                            png_buffer = io.BytesIO()
                            img.save(png_buffer, format='PNG')
                            image_data = png_buffer.getvalue()
                            print(f"    Converted {image_name} from DIB to PNG format")
                    except:
                        # If PIL fails, just use the raw data
                        pass
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                exported_count += 1
                print(f"    Exported {image_name} from math_images.db (via content scan)")
            else:
                print(f"    WARNING: {image_name} referenced in content but not found in math_images.db!")
            
            images_conn.close()
        except Exception as e:
            print(f"    ERROR exporting {image_name}: {e}")
    
    return exported_count

def export_missing_images_from_map(problem_id, images_dir):
    """
    Export images that are in problem_image_map but not in problem_images table.
    This handles cases where images are referenced but not properly stored in problem_images.
    """
    exported_count = 0
    
    # Connect to databases
    problems_conn = sqlite3.connect("db/math_problems.db")
    problems_cursor = problems_conn.cursor()
    
    # Get all image mappings for this problem
    problems_cursor.execute("""
        SELECT DISTINCT pim.image_name 
        FROM problem_image_map pim
        LEFT JOIN problem_images pi ON pim.image_name = pi.image_name AND pi.problem_id = ?
        WHERE pim.problem_id = ? AND pi.image_id IS NULL
    """, (problem_id, problem_id))
    
    missing_images = [row[0] for row in problems_cursor.fetchall()]
    problems_conn.close()
    
    if missing_images:
        print(f"  Found {len(missing_images)} images in problem_image_map but not in problem_images for problem {problem_id}")
    
    for image_name in missing_images:
        output_path = os.path.join(images_dir, image_name)
        
        # Skip if already exported
        if os.path.exists(output_path):
            continue
            
        # Try to get from math_images.db
        try:
            images_conn = sqlite3.connect("db/math_images.db")
            images_cursor = images_conn.cursor()
            
            images_cursor.execute("SELECT data FROM images WHERE name = ?", (image_name,))
            result = images_cursor.fetchone()
            
            if result:
                image_data = result[0]
                
                # Check if we need to convert DIB to PNG
                if HAS_PIL:
                    try:
                        # Try to open the image data
                        img = Image.open(io.BytesIO(image_data))
                        
                        # If it's DIB/BMP format and has .png extension, convert it
                        if img.format in ['DIB', 'BMP'] and image_name.endswith('.png'):
                            # Convert to PNG
                            png_buffer = io.BytesIO()
                            img.save(png_buffer, format='PNG')
                            image_data = png_buffer.getvalue()
                            print(f"    Converted {image_name} from DIB to PNG format")
                    except Exception as e:
                        print(f"    Warning: Could not process image format for {image_name}: {e}")
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                exported_count += 1
                print(f"    Exported {image_name} from math_images.db")
            else:
                # Try temp/images as last resort
                temp_path = f"temp/images/{image_name}"
                if os.path.exists(temp_path):
                    shutil.copy2(temp_path, output_path)
                    exported_count += 1
                    print(f"    Exported {image_name} from temp/images/")
                else:
                    print(f"    WARNING: Could not find {image_name} anywhere!")
            
            images_conn.close()
        except Exception as e:
            print(f"    ERROR exporting {image_name}: {e}")
    
    return exported_count

def main():

    parser = argparse.ArgumentParser(description="Export math problems to LaTeX.")
    parser.add_argument('-c', '--category', type=str, help='Export only problems in this category')
    parser.add_argument('-o', '--output', type=str, default='exports/problems_export.tex', help='Output LaTeX file')
    parser.add_argument('-a', '--all', action='store_true', help='Include answer, earmark, and problem types after each problem')
    args = parser.parse_args()

    db = MathProblemDB()
    config_manager = ConfigLoader('default_config.json')
    md_parser = MarkdownParser(config_manager=config_manager)
    image_db = MathImageDB()

    # Force preview-style LaTeX preamble for export
    config_manager.config['preview'] = {
        'font_family': 'Calibri',
        'font_size': 14,
        'math_font_family': 'Cambria Math',
        'math_font_size': 14
    }

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

    # Sort problems by problem_id ascending
    problems = sorted(problems, key=lambda p: p['problem_id'])

    # Ensure all images are exported from the DB to the export images directory
    output_dir = os.path.dirname(args.output)
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    for prob in problems:
        problem_id = prob['problem_id']
        # Get all images for this problem from the DB
        success, prob_data = db.get_problem(problem_id, with_images=True, with_categories=False)
        if not success:
            print(f"Warning: Could not get images for problem {problem_id}: {prob_data}")
            continue
        images = prob_data.get('images', [])
        for img in images:
            image_id = img['image_id']
            image_name = img['image_name']
            output_path = os.path.join(images_dir, image_name)
            # Use MathProblemDB.export_image to export by image_id
            success, msg = db.export_image(image_id=image_id, output_path=output_path)
            if not success:
                print(f"Warning: Could not export image {image_name} (id={image_id}) to {images_dir}: {msg}")
        
        # Also check for images in problem_image_map that aren't in problem_images
        export_missing_images_from_map(problem_id, images_dir)
        
        # Also check for images referenced in content that aren't in either table
        export_images_from_content(problem_id, prob['content'], images_dir)

    # --- Build all problems as a single LaTeX string ---
    all_problems_latex = ""
    for idx, prob in enumerate(problems):
        content = prob['content']
        problem_number = prob['problem_id']
        latex = md_parser.parse(content, context='export')
        latex = latex.replace(r"\\begin{figure}[htbp]", r"\\begin{figure}[H]")
        all_problems_latex += "\\begin{samepage}\n" + latex + "\n"
        if args.all:
            answer = prob.get('answer', '').strip()
            answer_block = ''
            # Problem ID
            answer_block += r'\textbf{ID:} ' + str(problem_number) + r'\\' + '\n'
            if answer:
                answer_block += r'\textbf{Answer:} $' + latex_escape(answer) + r'$\\' + '\n'
            earmark = prob.get('earmark', None)
            if earmark not in [None, 0, '', False, '0', 'False']:
                answer_block += r'\textbf{Earmark:} Yes\\' + '\n'
            db_types = MathProblemDB()
            success, types = db_types.get_types_for_problem(problem_number)
            db_types.close()
            if success and types:
                type_names = ', '.join([latex_escape(t['name']) for t in types])
                answer_block += r'\textbf{Types:} ' + type_names + r'\\' + '\n'
            # Add categories
            categories = prob.get('categories', [])
            if categories:
                cat_names = ', '.join([latex_escape(cat['name']) for cat in categories])
                answer_block += r'\textbf{Categories:} ' + cat_names + r'\\' + '\n'
            if answer_block:
                all_problems_latex += f'''{{\color{{blue!70!black}}
{answer_block}}}
'''
        all_problems_latex += "\\end{samepage}\n"
        if not ((idx + 1) % 2 == 0 and (idx + 1) != len(problems)):
            all_problems_latex += "\\vspace{1cm}\n"
        if (idx + 1) % 2 == 0 and (idx + 1) != len(problems):
            all_problems_latex += "\\clearpage\n"
    # --- Use create_latex_document to assemble the full document ---
    full_latex = md_parser.create_latex_document(all_problems_latex)
    
    # Fix the graphicspath for export context - since the .tex file is in exports/,
    # it should look for images in ./images/ not ./exports/images/
    full_latex = full_latex.replace(
        r'\graphicspath{{./}{./images/}{./exports/images/}} ',
        r'\graphicspath{{./}{./images/}}'
    ).replace(
        r'\graphicspath{{./}{./images/}{./exports/images/}}',
        r'\graphicspath{{./}{./images/}}'
    )
    
    # Write to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_latex)

    print(f"Exported {len(problems)} problems to {args.output}")

if __name__ == "__main__":
    main()