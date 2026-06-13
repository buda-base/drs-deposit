import logging
import os
import shutil
from pathlib import Path

from PIL import Image
from tqdm.asyncio import tqdm

# Context configures, we access
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transcode_work(root_dir: Path, work_name: str, use_tqdm: bool = False):
    """
    Traverse the root directory to find 'images' directories and process them.

    :param root_dir: Root directory to search for 'images' directories.
    :type root_dir: Path
    :param work_name: Name of the work directory to create/process.
    :type work_name: str
    :param use_tqdm: Whether to use tqdm for progress display.
    :type use_tqdm: bool
    """
    
    def progress_iter(iterable, **kwargs):
        if use_tqdm:
            return tqdm(iterable, **kwargs)
        else:
            return iterable


    targets = []
    for dirpath, dirnames, filenames in os.walk(root_dir):  # noqa: B007
        if 'images' in dirnames:
            targets.append(dirpath)

    if not targets:
        logging.warning(f"No 'images' directories found in {root_dir}")
        return

    for target in targets:
        logging.info(f"Processing top-level directory: {target}")
        # stubelicious
        continue
        images_dir = os.path.join(target, 'images')
        drs_dir = os.path.join(target, work_name)
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
                convert_one(fpath, drs_vol_path, fname)
            except Exception as e:
                # Use tqdm.write to avoid breaking the progress bar display
                msg = f"Skipping {fpath}: Could not process image. Error: {e}"
                if use_tqdm:
                    tqdm.write(msg)
                logging.error(msg)

def convert_one(fpath, drs_vol_path, fname, quality_mode, quality_layers) -> None:
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
    return target_rate


def transcode_volume(volume_path: Path, drs_vol_path: Path):
    """
    Transcode all images in a volume directory.

    :param volume_path: Path to the volume directory containing images.
    :type volume_path: Path
    :param drs_vol_path: Path to the output directory where transcoded images will be saved.
    :type drs_vol_path: Path
    """

    for fname in os.listdir(volume_path):
        if fname.lower().endswith('.json'):
                continue
        fpath = Path(volume_path, fname)
        try:
            convert_one(fpath, drs_vol_path, fname)
        except Exception as e:
            raise RuntimeError(f"Skipping {fpath}: Could not process image. Error: {e}") from e
