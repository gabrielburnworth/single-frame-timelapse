# Single Frame Timelapse
Create a "timelapse photo" using OpenCV by condensing all frames into one

__Install OpenCV on Debian:__
```
sudo apt-get install python-opencv python-numpy
```

For youtube video input:
`pip install pytube`

__Run the script:__

Run the script: `python single-frame-timelapse.py`

__Alternatively, use a python command line:__


```python
from single-frame-timelapse import SFTL
help(SFTL)
SFTL(stills='frames')
SFTL(video='car.avi', slice=0.75, stretch=2)
```