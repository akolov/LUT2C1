import os
import uuid
import xml.etree.ElementTree as ET
import subprocess
import sys

def generate_icc_and_costyle(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    source_dir = os.path.dirname(file_path)
    icc_file = os.path.join(source_dir, f"{base_name}.costyle.{base_name}.icc")
    costyle_file = os.path.join(source_dir, f"{base_name}.costyle")

    try:
        subprocess.run(
            ["ociobakelut", "--lut", file_path, "--format", "icc", "--description", base_name, icc_file],
            check=True
        )
        print(f"Generated ICC profile: {icc_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate ICC profile for {file_path}: {e}")
        return

    generated_uuid = str(uuid.uuid4())

    root = ET.Element("SL", Engine="1300")
    ET.SubElement(root, "E", K="FilmCurve", V="FujiGFX100-Film Standard.fcrv")
    ET.SubElement(root, "E", K="ICCProfile", V=f"{base_name}.icc")
    ET.SubElement(root, "E", K="Name", V=base_name)
    ET.SubElement(root, "E", K="StyleSource", V="Styles")
    ET.SubElement(root, "E", K="UUID", V=generated_uuid)

    # Write XML to file
    tree = ET.ElementTree(root)
    tree.write(costyle_file, encoding="utf-8", xml_declaration=True)
    print(f"Generated Capture One style file: {costyle_file}")

def process_files(input_path):
    if os.path.isfile(input_path) and (input_path.lower().endswith(".3dl") or input_path.lower().endswith(".cube")):
        generate_icc_and_costyle(input_path)
    elif os.path.isdir(input_path):
        for file_name in os.listdir(input_path):
            if file_name.endswith(".cube"):
                file_path = os.path.join(input_path, file_name)
                generate_icc_and_costyle(file_path)
    else:
        print("Invalid input. Please provide a *.3dl or *.cube file or a folder containing *.3dl and/or *.cube files.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lut2c1.py <file_or_dir>")
        sys.exit(1)

    input_path = sys.argv[1]
    process_files(input_path)
