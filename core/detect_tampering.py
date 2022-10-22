from typing import Union

import cv2
import numpy as np
import torch
from PIL import Image

from utils.model_utils import resnet18_model_creator, resnet_transform


class TamperingDetector:
    def __init__(self,
                 run_every_nth: int = 1,
                 key_frame_path: Union[str] = None,
                 threshold: float = 0.4):
        """
        Args:
            run_every_nth: Variable to control at which N-th frame to run deep model.
                           If  run_every_nth=1 means model will be used per each input image.
                           run_every_nth>1 means algorithm will wait N-th frame and return previous prediction
                           until new frame is passed in.
            key_frame_path: Key frame path which will be used for comparison internally.
            threshold: Threshold value
        """
        # self.device = 'cpu'
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = resnet18_model_creator().to(self.device)
        self.transform = resnet_transform()
        self.cos_sim = torch.nn.CosineSimilarity(dim=1, eps=1e-08)
        self.threshold = threshold  # tampering is positive label (should be one)
        self.run_every_nth = int(run_every_nth)
        self.prev_prediction = False  # no tampering was happened before model predicts it
        self.frame_counter = 0
        self.key_frame_embedding = None
        if key_frame_path:
            self.key_frame_embedding = self.get_embedding(cv2.imread(key_frame_path))

    def get_embedding(self, frame: np.ndarray) -> torch.Tensor:
        """
        Args:
            frame (np.ndarray): (BGR) 3D image array read by opencv

        Returns: torch.Tensor
        """
        frame = frame[..., ::-1]  # to RGB from BGR
        pil_frame = Image.fromarray(frame)
        tran_frame = self.transform(pil_frame).to(self.device)
        embedding = self.predict_embedding(tran_frame)
        return embedding

    @torch.no_grad()
    def inference_(self, frame: np.ndarray) -> bool:
        """
        Args:
            frame (np.ndarray): (BGR) 3D image array read by opencv

        Returns:
            (bool | torch.Tensor): False if not enough frames are stored to pass through model, otherwise torch tensor
        """
        if not ((self.frame_counter % self.run_every_nth) == 0):  # if time margin have passed
            self.frame_counter += 1
            if self.prev_prediction:
                return True  # keep positive label until new prediction will be made
            else:
                return False  # no tampering could happen at this moment in time

        self.frame_counter += 1  # increase counter in any case, if "frame_time_margin" time passed or not
        new_embedding = self.get_embedding(frame=frame)
        prediction = self.predict_(new_embedding=new_embedding)
        return prediction

    @torch.no_grad()
    def inference(self, frame: np.ndarray) -> bool:
        """
        Predicts if a frame from a video is tampered.

        Args:
            frame (np.ndarray): (BGR) 3D image array read by opencv

        Returns:
            (bool): True if tampered, otherwise False
        """

        prediction = self.inference_(frame=frame)
        self.prev_prediction = prediction
        return prediction

    @torch.no_grad()
    def cosine_distance(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """
        Calculates cosine distance between vectors

        Args:
            x1 (torch.Tensor):  Image embedding vector
            x2 (torch.Tensor):  Image embedding vector

        Returns:
            (torch.Tensor): Distance scalar of type tensor from the range [0, 2]
        """
        return 1 - self.cos_sim(x1, x2)

    @torch.no_grad()
    def predict_embedding(self, tensor_image: torch.Tensor) -> torch.Tensor:
        """
        Passes 3D tensor image through model

        Args:
            tensor_image (torch.Tensor): 3D  image [C, H, W]
        Returns:
            (torch.Tensor): Embedding vector
        """
        embedding = self.model(tensor_image.unsqueeze(0))
        return embedding

    @torch.no_grad()
    def predict_(self, new_embedding: torch.Tensor) -> bool:
        """
        Passes input tensor through model and makes predictions

        Returns:
            (bool): True if tampering was detected by model, otherwise False
        """
        cos_dist = self.cosine_distance(self.key_frame_embedding,
                                        new_embedding).cpu().item()
        print('cos_dist:', cos_dist, '  <>   ', 'self.threshold:', self.threshold)
        prediction = cos_dist >= self.threshold  # tampering is positive label (should be one)
        return prediction

    @torch.no_grad()
    def set_key_frame_embedding(self, key_frame_path: str):
        """
        Sets key frame embedding.

        Args:
            key_frame_path: Key frame path which will be used for comparison internally.

        Returns:
            None
        """
        self.key_frame_embedding = self.get_embedding(cv2.imread(key_frame_path))
