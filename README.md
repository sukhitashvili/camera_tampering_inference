# Camera Tampering Detection
Code for camera tampering detection with deep learning techniques.

### Installation

To install required libraries run this command (it installs Pytorch with GPU processing support): 
```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu116
```

### How to test?

For testing the algorithm on example videos you should use `test_tempering_det.py` file.

You can test the algorithm on video video provided in `./data` folder via this command:
```python
python test_tempering_det.py --video_path="./data/IDefocusing01.avi" --key_frame_path="./data/key_frame.jpg"
```

### How to use detection class itself?
In `test_tempering_det.py` on lines `#19` and `#28` you can find how the tampering detection
class is used. The algorithm class is located in `detect_tampering.py` file, and 
it requires the following arguments:
- `run_every_nth`: Variable to control at which N-th frame to run deep model.
                           If  `run_every_nth=1` means model will be used per each input image.
                           `run_every_nth`>1 means algorithm will wait N-th frame and return previous prediction
                           until new frame is passed in.
- `key_frame_path`: Key frame path which will be used for comparison internally.