import os
import shutil
from datetime import datetime
from glob import glob
from typing import Optional


def process_images(file_path: str, folder_name_to_keep_tampered_imgs: Optional[str], keeping_time_in_seconds: int = 30):
    folder = '/'.join(file_path.split('/')[:-1])
    image_name = os.path.basename(file_path)
    dest_folder = os.path.join(folder, folder_name_to_keep_tampered_imgs)
    os.makedirs(dest_folder, exist_ok=True)
    image_name = image_name.split('.')[0] + '_' + str(datetime.now()) + '.' + image_name.split('.')[1]
    dest_path = os.path.join(dest_folder, image_name)
    shutil.copy(file_path, dest_path)

    # delete old images in folder_name_to_keep_tampered_imgs folder
    files_folder = os.path.join(dest_folder, '*')
    files = glob(files_folder)
    files.sort(key=os.path.getctime)
    current_time = datetime.now()
    for file in files:
        file_date = datetime.fromtimestamp(os.path.getmtime(file))
        diff = (current_time - file_date).total_seconds()
        if diff > keeping_time_in_seconds:
            os.remove(file)
