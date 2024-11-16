import argparse
import os
import subprocess
import uuid
import xml.etree.ElementTree as ET
from typing import List

SUPPORTED_EXTENSIONS: List[str] = [".3dl", ".cube"]

def update_film_curve(costyle_file: str, fcrv_value: str) -> None:
    """
    Update the FilmCurve value in a Capture One style (.costyle) file.

    Args:
        costyle_file (str): Path to the .costyle file.
        fcrv_value (str): New FilmCurve value to update.
    """
    try:
        tree = ET.parse(costyle_file)
        root = tree.getroot()

        updated = False
        for elem in root.findall("E"):
            if elem.get("K") == "FilmCurve":
                elem.set("V", f"{fcrv_value}.fcrv")
                updated = True

        if updated:
            tree.write(costyle_file, encoding="utf-8", xml_declaration=True)
            print(f"Updated FilmCurve in: {costyle_file}")
        else:
            print(f"No FilmCurve element found in: {costyle_file}")
    except ET.ParseError as e:
        print(f"Failed to parse XML in {costyle_file}: {e}")

def generate_icc_and_costyle(file_path: str, fcrv_value: str) -> None:
    """
    Generate an ICC profile and a Capture One style file from a given LUT file.

    Args:
        file_path (str): Path to the LUT file.
        fcrv_value (str): FilmCurve value to be used in the style file.
    """
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
    ET.SubElement(root, "E", K="FilmCurve", V=f"{fcrv_value}.fcrv")
    ET.SubElement(root, "E", K="ICCProfile", V=f"{base_name}.icc")
    ET.SubElement(root, "E", K="Name", V=base_name)
    ET.SubElement(root, "E", K="StyleSource", V="Styles")
    ET.SubElement(root, "E", K="UUID", V=generated_uuid)

    # Write XML to file
    tree = ET.ElementTree(root)
    tree.write(costyle_file, encoding="utf-8", xml_declaration=True)
    print(f"Generated Capture One style file: {costyle_file}")

def is_supported_lut(input_path: str) -> bool:
    """
    Check if the input file is a supported LUT format.

    Args:
        input_path (str): Path to the file.

    Returns:
        bool: True if the file is supported, False otherwise.
    """
    return any(input_path.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)

def process_files(input_path: str, fcrv_value: str) -> None:
    """
    Process a given file or directory to generate ICC profiles and style files.

    Args:
        input_path (str): Path to a file or directory.
        fcrv_value (str): FilmCurve value to be used.
    """
    if os.path.isfile(input_path) and is_supported_lut(input_path):
        generate_icc_and_costyle(input_path, fcrv_value)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file_name in files:
                if is_supported_lut(file_name):
                    file_path = os.path.join(root, file_name)
                    generate_icc_and_costyle(file_path, fcrv_value)
    else:
        print("Invalid input. Please provide a *.3dl or *.cube file or a folder containing *.3dl and/or *.cube files.")

def update_costyle_files(input_path: str, fcrv_value: str) -> None:
    """
    Update .costyle files with the new FilmCurve value.

    Args:
        input_path (str): Path to a .costyle file or a directory containing .costyle files.
        fcrv_value (str): New FilmCurve value to update.
    """
    if os.path.isfile(input_path) and input_path.lower().endswith(".costyle"):
        update_film_curve(input_path, fcrv_value)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file_name in files:
                if file_name.lower().endswith(".costyle"):
                    costyle_file = os.path.join(root, file_name)
                    update_film_curve(costyle_file, fcrv_value)
    else:
        print("Invalid input. Please provide a .costyle file or a folder containing .costyle files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process LUT files or update FilmCurve in .costyle files.")
    parser.add_argument("input_path", type=str, help="Path to a LUT file, .costyle file, or directory.")
    parser.add_argument("--fcrv", type=str, required=True, help="Camera Film Curve.")
    parser.add_argument("--update", action="store_true", help="Update FilmCurve in existing .costyle files.")

    args = parser.parse_args()

    if args.update:
        update_costyle_files(args.input_path, args.fcrv)
    else:
        process_files(args.input_path, args.fcrv)
