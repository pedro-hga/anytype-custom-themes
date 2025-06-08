import os
import shutil
import zipfile
import cairosvg

def generate_assets():
    INPUT_FILE = "colors.txt"

    SIZES = [128, 144, 192]
    SHAPES = ["circle", "square", "hexagon", "diamond"]
    FILLS = ["filled", "outline"]

    print(f"Starting asset generation for theme from '{INPUT_FILE}'...")

    try:
        with open(INPUT_FILE, 'r') as f:
            lines = [line.strip().rstrip(';') for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: '{INPUT_FILE}' not found. Please create this file in the same directory.")
        return

    if not lines:
        print(f"Error: '{INPUT_FILE}' is empty or improperly formatted.")
        return

    theme = lines[0]
    colors = {}

    for line in lines[1:]:
        if line.startswith("--") and ":" in line:
            name, hex_code = line.split(":", 1)
            color_name = name.strip().lstrip("--")
            hex_value = hex_code.strip()
            colors[color_name] = hex_value

    if not colors:
        print(f"Warning: No colors found in '{INPUT_FILE}'. Please check its format.")
        return

    OUTPUT_DIR = theme
    ZIP_PATH = f"{theme}.zip"

    if os.path.exists(OUTPUT_DIR):
        print(f"Removing existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created main output directory: {OUTPUT_DIR}")

    generated_files = []

    print("\nGenerating SVG and PNG assets...")
    CANVAS_SIZE = 192

    for size in SIZES:
        size_output_dir = os.path.join(OUTPUT_DIR, str(size))
        os.makedirs(size_output_dir, exist_ok=True)
        print(f"  Created subdirectory: {size_output_dir}")

        for shape in SHAPES:
            for filltype in FILLS:
                for color_name, hex_code in colors.items():
                    base_name = f"{theme}-{size}-{shape}-{filltype}-{color_name}"
                    svg_filename = f"{base_name}.svg"
                    png_filename = f"{base_name}.png"
                    
                    svg_path = os.path.join(size_output_dir, svg_filename)
                    png_path = os.path.join(size_output_dir, png_filename)

                    svg_open = f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_SIZE}" height="{CANVAS_SIZE}">'

                    if shape == "circle":
                        cx = cy = CANVAS_SIZE // 2
                        stroke_width = 12
                        if size == 192:
                            r = CANVAS_SIZE // 2 - (stroke_width // 2 if filltype == "outline" else 0)
                        else:
                            r = size // 3
                        if filltype == "filled":
                            element = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{hex_code}"/>'
                        else:
                            element = f'<circle cx="{cx}" cy="{cy}" r="{r - stroke_width // 2}" fill="none" stroke="{hex_code}" stroke-width="{stroke_width}"/>'
                    
                    elif shape == "hexagon":
                        cx = cy = CANVAS_SIZE // 2
                        stroke_width = 12
                        if size == 192:
                            radius = CANVAS_SIZE // 2 - (stroke_width if filltype == "outline" else 0)
                        else:
                            radius = size // 3
                        
                        # Calculate hexagon points
                        import math
                        points = []
                        for i in range(6):
                            angle = i * math.pi / 3
                            x = cx + radius * math.cos(angle)
                            y = cy + radius * math.sin(angle)
                            points.append(f"{x:.1f},{y:.1f}")
                        points_str = " ".join(points)
                        
                        corner_radius = radius * 0.1
                        if filltype == "filled":
                            element = f'<polygon points="{points_str}" fill="{hex_code}" rx="{corner_radius}" ry="{corner_radius}"/>'
                        else:
                            inner_radius = radius - stroke_width // 2
                            inner_points = []
                            for i in range(6):
                                angle = i * math.pi / 3
                                x = cx + inner_radius * math.cos(angle)
                                y = cy + inner_radius * math.sin(angle)
                                inner_points.append(f"{x:.1f},{y:.1f}")
                            inner_points_str = " ".join(inner_points)
                            inner_corner_radius = inner_radius * 0.1
                            element = f'<polygon points="{inner_points_str}" fill="none" stroke="{hex_code}" stroke-width="{stroke_width}" rx="{inner_corner_radius}" ry="{inner_corner_radius}"/>'
                    
                    elif shape == "diamond":
                        cx = cy = CANVAS_SIZE // 2
                        stroke_width = 12
                        if size == 192:
                            radius = CANVAS_SIZE // 2 - (stroke_width if filltype == "outline" else 0)
                        else:
                            radius = size // 3
                        
                        points = [
                            f"{cx},{cy - radius}",  # top
                            f"{cx + radius},{cy}",  # right
                            f"{cx},{cy + radius}",  # bottom
                            f"{cx - radius},{cy}"   # left
                        ]
                        points_str = " ".join(points)
                        
                        corner_radius = radius * 0.15
                        if filltype == "filled":
                            element = f'<polygon points="{points_str}" fill="{hex_code}" rx="{corner_radius}" ry="{corner_radius}"/>'
                        else:
                            inner_radius = radius - stroke_width // 2
                            inner_points = [
                                f"{cx},{cy - inner_radius}",
                                f"{cx + inner_radius},{cy}",
                                f"{cx},{cy + inner_radius}",
                                f"{cx - inner_radius},{cy}"
                            ]
                            inner_points_str = " ".join(inner_points)
                            inner_corner_radius = inner_radius * 0.15
                            element = f'<polygon points="{inner_points_str}" fill="none" stroke="{hex_code}" stroke-width="{stroke_width}" rx="{inner_corner_radius}" ry="{inner_corner_radius}"/>'
                    else:
                        stroke_width = 12
                        if size == 192:
                            side = CANVAS_SIZE - stroke_width  # Inset by stroke width
                            offset_x = offset_y = stroke_width // 2
                            rx = ry = side * 0.05
                        else:
                            side = int(size / 1.5)
                            offset_x = (CANVAS_SIZE - side) / 2
                            offset_y = (CANVAS_SIZE - side) / 2
                            rx = ry = side * 0.2
                        
                        if filltype == "filled":
                            element = (
                                f'<rect x="{offset_x}" y="{offset_y}" width="{side}" height="{side}" '
                                f'rx="{rx}" ry="{ry}" fill="{hex_code}"/>'
                            )
                        else:
                            element = (
                                f'<rect x="{offset_x + stroke_width // 2}" y="{offset_y + stroke_width // 2}" width="{side - stroke_width}" height="{side - stroke_width}" '
                                f'rx="{rx}" ry="{ry}" fill="none" stroke="{hex_code}" stroke-width="{stroke_width}"/>'
                            )

                    svg_code = f"""{svg_open}
  {element}
</svg>"""

                    with open(svg_path, "w") as svg_file:
                        svg_file.write(svg_code)

                    try:
                        cairosvg.svg2png(bytestring=svg_code.encode("utf-8"), write_to=png_path)
                    except Exception as e:
                        print(f"Error converting {svg_filename} to PNG: {e}")
                        print("Please ensure CairoSVG is correctly installed and its system dependencies are met.")
                        print("On Debian/Ubuntu, you might need: 'sudo apt-get install libcairo2 libgdk-pixbuf2.0-0 libpangocairo-1.0-0'")
                        return

                    generated_files.extend([svg_path, png_path])

    print(f"\nCreating ZIP file: {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, "w") as zipf:
        for file_path in generated_files:
            arcname = os.path.relpath(file_path, OUTPUT_DIR)
            zipf.write(file_path, arcname)

    print(f"\n✅ Done! {len(generated_files)} files created in '{OUTPUT_DIR}'.")
    print(f"📦 Zipped output: '{os.path.join(os.getcwd(), ZIP_PATH)}'")

if __name__ == "__main__":
    generate_assets()
