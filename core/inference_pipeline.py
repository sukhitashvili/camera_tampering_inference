import json
import os
from glob import glob
from typing import List, Optional
import logging

import cv2
import requests
from omegaconf import DictConfig

from core.detect_tampering import TamperingDetector


class InferencePipeline:
    def __init__(self, config: DictConfig):
        global logging
        logging.basicConfig(filename=config['logger_path'], format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger('logger')
        self.request_url = config['request_link']
        self.folders_to_check = config['folders_to_watch']
        self.folders_with_valid_images = config['folder_with_valid_images']
        self.thresholds_per_camera = config['thresholds_per_camera']
        self.image_formats = config['image_formats']
        self.tamp_det = TamperingDetector(run_every_nth=1,
                                          key_frame_path=None,
                                          threshold=self.thresholds_per_camera['default'])

    def setup_model(self, folder_path: str):
        """
        Resets model's threshold and key frame values per input folder based on folder/camera name
        Args:
            folder_path: Relative or full path to the folder

        Returns: None
        """
        valid_folder_path = self.get_valid_folder_path(folder_path=folder_path)
        camera_name = os.path.basename(valid_folder_path)
        key_frame_path = self.get_image_path(folder_path=valid_folder_path)
        if camera_name in self.thresholds_per_camera:
            thresh_value = float(self.thresholds_per_camera[camera_name])
            self.tamp_det.threshold = thresh_value
        self.tamp_det.set_key_frame_embedding(key_frame_path=key_frame_path)

    def get_valid_folder_path(self, folder_path: str) -> str:
        input_camera_name = os.path.basename(folder_path)
        for valid_folder_path in self.folders_with_valid_images:
            camera_name = os.path.basename(valid_folder_path)
            if camera_name == input_camera_name:
                return valid_folder_path

        raise ValueError('Input folder name and valid folder name does not match')

    def get_files(self, folder_path: str) -> List[str]:
        files = []
        for img_format in self.image_formats:
            file_path = os.path.join(folder_path, '*' + img_format)
            files_path = glob(file_path)
            files += files_path
        files.sort(key=os.path.getctime)  # sort file by creation time
        return files

    def get_image_path(self, folder_path: str) -> Optional[str]:
        image_pathes = self.get_files(folder_path=folder_path)
        if len(image_pathes) == 0:
            self.logger.info(f'No images in folder: {folder_path}')
            return None
        image_path = image_pathes[-1]  # take the last file from sorted list by creation date
        return image_path

    def run(self):
        """
        Runs models per folders specified in config and does model prediction.
        If tampering detected, then POST request is sent to the link

        Returns: None
        """
        for folder_path in self.folders_to_check:
            self.logger.info(f'Checking folder: {folder_path}')
            image_path = self.get_image_path(folder_path=folder_path)
            if image_path is None:
                continue
            self.setup_model(folder_path=folder_path)
            image = cv2.imread(image_path)
            prediction = self.tamp_det.inference(frame=image)
            self.logger.info(f'{folder_path}   :::: result: {prediction}')
            if prediction:
                info = {'camera_id': folder_path, 'tampering': prediction}
                r = requests.post(self.request_url,
                                  data=json.dumps(info),
                                  headers={'Content-Type': 'application/json'})
                self.logger.info(f'{folder_path}   :::: result status_code: {r.status_code}')
                self.logger.info(f'{folder_path}   :::: result text: {r.text}')
            os.remove(image_path)