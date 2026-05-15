import logging
from pathlib import Path

from  s3pathlib import S3Path

logger = logging.getLogger(__name__)

def stage_content(source_path: Path, staging_path: Path):
    """
    Stub function to stage content from source_path to staging_path.

    :param source_path: Local path to the source file to be staged.
    :type source_path: Path
    :param staging_path: Local path where the staged file will be saved.
    :type staging_path: Path
    """
    logger.info(f"Staging content from {str(source_path)} to {str(staging_path)}.")
    
def create_metadata_file(content_path: Path, metadata_file_path: Path):
    """
    Create a metadata file based on the content at the given path.

    :param content_path: Path to the file whose metadata will be used to generate the metadata file.
    :type content_path: Path
    :param metadata_file_path: Path where the generated metadata file will be saved.
    :type metadata_file_path: Path
    """
    logger.info(f"Generating metadata from {str(content_path)} into {str(metadata_file_path)}.")
    

def send_to_s3(source_path: Path, destination_s3_path: S3Path):
    """
    Stub function to send a file from source_path to destination_s3_path (S3).

    :param source_path: Local path to the source file to be uploaded.
    :type source_path: Path
    :param destination_s3_path: S3Path object representing the destination path in S3.
    :type destination_s3_path: S3Path
    """
    logger.info(f"Sending {str(source_path)} to {str(destination_s3_path)} using s3pathlib.")


