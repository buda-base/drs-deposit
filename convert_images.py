import os
import shutil
from PIL import Image
from tqdm import tqdm
from pathlib import Path

def process_directory(root_dir: Path):
    """
    Traverse the root directory to find 'images' directories and process them.
    """
    targets = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'images' in dirnames:
            targets.append(dirpath)

    if not targets:
        print(f"No 'images' directories found in {root_dir}")
        return

    for target in targets:
        print(f"\nProcessing top-level directory: {target}")
        images_dir = os.path.join(target, 'images')
        drs_dir = os.path.join(target, 'drs')
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
            print("  No files found to process.")
            continue

        # Iterate with tqdm progress bar
        for volume, fname, fpath in tqdm(all_files, desc="Converting", unit="img"):
            drs_vol_path = os.path.join(drs_dir, volume)
            os.makedirs(drs_vol_path, exist_ok=True)
            
            try:
                with Image.open(fpath) as img:
                    if img.format in ("TIFF", "TIF"):
                        shutil.copy2(fpath, drs_vol_path)
                    else:
                        base, _ = os.path.splitext(fname)
                        jp2_path = os.path.join(drs_vol_path, base + ".jp2")
                        converted_img = img.convert("RGB")
                        converted_img.save(jp2_path, format="JPEG2000", quality_mode="rates", quality_layers=[20])
                        converted_img.save(jp2_path, format="JPEG2000", quality_mode="dB", quality_layers=[41])
            except Exception as e:
                # Use tqdm.write to avoid breaking the progress bar display
                tqdm.write(f"Skipping {fpath}: Could not process image. Error: {e}")

if __name__ == "__main__":
    process_directory(Path("~/tmp/DRS3/sources").expanduser())