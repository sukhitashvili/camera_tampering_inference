# Camera Tampering Detection
Code for camera tampering detection with deep learning techniques.

# Installation

### First install dependencies (if already installed skip this step)

To install required libraries run this command (it installs Pytorch with GPU processing support): 
```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu116
```

### Service installation

Before service installation you should configure `config.yaml` file.

Inside config file please provide following required information:

- `request_link` - Is link where post request will be sent if tampering detected;
- `logger_path` - Is logger file location used for testing/monitoring. Better if you create it at more accessible location;
- `folders_to_watch` - Contains listed full paths to folders which should be monitored. Folder name should be camera id. You can extract full path of a file or folder in
linux with `CRTL+c` and `CRTL+v` commands (like copy & pasting a file);
- `folder_with_valid_images` - Contains listed full paths to folders with valid images per camera. 
Camera folder name should match with camera id being monitored.
- `thresholds_per_camera` - Contains default value for threshold. To change threshold values per camera you should 
provide camera id name and needed threshold value.
- `image_formats` - There are image formats listed which are looked for by algorithm.

### Setup Cron jobs

Cron jobs are linux services that are running periodically.
So the tampering detection pipeline will be running by Cron job processes. 
Ubuntu has preinstalled Cron program but if you machines does not have you should install it, it's free.
To install cron jobs with predefinied processing time in minutes use `bash` script of the repo.

To install cron job run:
```bash
bash install.sh INTERVAL_IN_MINUTES
```

So for example, if you want to run algorithm every 30 minutes then run this command:
```bash
bash install.sh 30
```

To check if job was registered run this command (It should output cron job timing and command):
```bash
sudo crontab -l -u root
```

To stop running job use this command:
```bash
sudo service cron stop
```

To delete all jobs use this command:
```bash
sudo crontab -r -u root
```

# Notes

Algorithm **deletes** images in monitored folders after processing so pleas be aware of it.