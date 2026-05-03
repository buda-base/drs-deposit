import os
import shutil
import logging
from PIL import Image
from tqdm import tqdm
from pathlib import Path

def process_directory(root_dir: Path, drs_name: str, use_tqdm: bool = False):
    """
    Traverse the root directory to find 'images' directories and process them.
    """
    def progress_iter(iterable, **kwargs):
        if use_tqdm:
            return tqdm(iterable, **kwargs)
        else:
            return iterable

    targets = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'images' in dirnames:
            targets.append(dirpath)

    if not targets:
        logging.warning(f"No 'images' directories found in {root_dir}")
        return

    for target in targets:
        logging.info(f"\nProcessing top-level directory: {target}")
        images_dir = os.path.join(target, 'images')
        drs_dir = os.path.join(target, drs_name)
        os.makedirs(drs_dir, exist_ok=True)

        # Gather all files from all volumes first to track total progress
        all_files = []
        for volume in os.listdir(images_dir):
            vol_path = os.path.join(images_dir, volume)
            if os.path.isdir(vol_path):
                for fname in os.listdir(vol_path):
                    fpath = os.path.join(vol_path, fname)
                    if os.path.isfile(fpath):
                        all_files.append((volume, fname, fpath))

        if not all_files:
            logging.info("  No files found to process.")
            continue

        for volume, fname, fpath in progress_iter(all_files, desc="Converting", unit="img"):
            drs_vol_path = os.path.join(drs_dir, volume)
            os.makedirs(drs_vol_path, exist_ok=True)
            # Skip files that end in json
            if fname.lower().endswith('.json'):
                continue
            try:
                with Image.open(fpath) as img:
                    if img.format in ("TIFF", "TIF"):
                        shutil.copy2(fpath, drs_vol_path)
                    else:
                        base, _ = os.path.splitext(fname)
                        jp2_path = os.path.join(drs_vol_path, base + ".jp2")
                        converted_img = img.convert("RGB")
                        
                        # Calculate the compression rate to match the original file size
                        orig_size_bytes = os.path.getsize(fpath)
                        uncompressed_size_bytes = converted_img.width * converted_img.height * 3
                        target_rate = max(1.0, uncompressed_size_bytes / orig_size_bytes)
                        
                        converted_img.save(jp2_path, format="JPEG2000", quality_mode="rates", quality_layers=[target_rate])
            except Exception as e:
                # Use tqdm.write to avoid breaking the progress bar display
                msg = f"Skipping {fpath}: Could not process image. Error: {e}"
                if use_tqdm:
                    tqdm.write(msg)
                logging.error(msg)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert images in 'images' directories to JPEG2000 and copy TIFFs, placing results in a drs* output directory.")
    parser.add_argument(
        '-s', '--src_dir',
        required=True,
        help="Source root directory to search for 'images' folders."
    )
    parser.add_argument(
        '-o', '--output_dir_name',
        required=True,
        help="Name to append to 'drs-' to form the output directory name (e.g., '3' makes 'drs3')."
    )
    parser.add_argument(
        '--tqdm',
        action='store_true',
        help="Show tqdm progress bar (for local testing; disable for Docker or non-interactive runs)."
    )
    args = parser.parse_args()


    import sys
    import re
    src_path = Path(args.src_dir).expanduser()

    # Set up standard terminal logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # Check if src_dir exists
    if not src_path.exists() or not src_path.is_dir():
        logging.error(f"Error: Source directory '{src_path}' does not exist or is not a directory.")
        sys.exit(1)

    # Validate output_dir_name for illegal characters (cross-platform safe)
    # Disallow /, \\, :, *, ?, ", <, >, | and empty string
    illegal_pattern = r'[\\/:*?"<>|]'
    if not args.output_dir_name or re.search(illegal_pattern, args.output_dir_name):
        logging.error("Error: --output_dir_name contains illegal characters or is empty. "
                      "Avoid /, \\, :, *, ?, \", <, >, | and use a non-empty name.")
        sys.exit(1)

    drs_name = f"drs-{args.output_dir_name}"
    process_directory(src_path, drs_name, use_tqdm=args.tqdm)
