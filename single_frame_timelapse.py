"""Single Frame TimeLapse.

Create a timelapse photo by taking a slice from each frame
and condensing it into a single image.
"""
import cv2
import numpy as np
import os, os.path
import sys

def SFTL(**kwargs):
    """Create a timelapse photo.

    Notes:
        If the slice width is calculated as less than zero,
            the a slice width of one will be used. This may
            result in a wide output image if the number of frames
            is large. A stretch value of less than one may
            not squish the output further for this reason.
            Additionally, pixels may be repeated in a video
            so that the entire video length is represented in the
            output image if the video length is long.
        The youtube option assumes an 720p mp4 is available to download.
        The stills option assumes each frame is named "frame_####.png",
            starting with "frame_0000.png".
    
    Arguments:
        Input (choose one of three):
            stills: name of directory of photos to combine
            video: name of video to process
            youtube: URL of video to process
        
        Processing Options:
            slice: Horizonal location (0 - 1) of the beginning of 
                   a slice to read of each frame.
                   This shows the change in a single vertial
                   strip over time.
            mirror: Run backward in time after end of time period.
                    'half' to reverse halway through,
                    'full' to reverse at end.
            stretch: Stretch the time period shown over a smaller
                     or larger width.
            fixedwidth: (Default = False) Use fixedwidth=True to attempt
                        to keep the aspect ratio of the original image.
                        Otherwise, a large number of input frames will
                        create a very wide image.

        debug: Output debug info.

    Examples:
        SFTL(stills='frames')
        SFTL(stills='frames', slice=0.5, mirror='half')
        SFTL(video='car.avi', slice=0.75, stretch=2)
        SFTL(youtube='https://youtu.be/DmYK479EpQc', slice=0.5)

    """

    stills = None
    video = None
    youtube = None
    slice = None
    mirror = None
    stretch = None
    fixedwidth = False
    debug = False
    for key in kwargs:
        if key == 'slice': slice = kwargs[key]
        if key == 'mirror': mirror = kwargs[key]
        if key == 'stills': stills = kwargs[key]
        if key == 'video': video = kwargs[key]
        if key == 'youtube': youtube = kwargs[key]
        if key == 'stretch': stretch = kwargs[key]
        if key == 'fixedwidth': fixedwidth = kwargs[key]
        if key == 'debug': debug = kwargs[key]

    def add(img1, img2):
        img = np.concatenate((img1, img2), axis=1)
        return img

    def add_slice(TLP, frame_count, i, frame):
        # Determine slice location and width
        y, x, o = frame.shape
        if slice is not None:
            left = int(slice * x)
        if mirror == 'half': x /= 2
        slice_width_float = x / frame_count
        slice_width = int(slice_width_float)
        if slice_width < 1: slice_width = 1
        if slice is None:
            left = slice_width * i
            if left > slice_width_float * i:
                left = int(slice_width_float * i)
        if stretch is not None and stretch < 1:
            slice_width = int(slice_width * stretch)
            if slice_width < 1: slice_width = 1
            right = left + slice_width
        elif stretch is not None:
            right = left + int(slice_width * stretch)
        else:
            right = left + slice_width

        if i == 0:
            TLP = frame[:, 0:0]

        # Fixed width option processing
        new_slice_width = right - left
        final_width = new_slice_width * frame_count
        if final_width > x and fixedwidth and new_slice_width == 1:
            k = int(frame_count / x)
            if i % k != 0:
                return TLP
        elif fixedwidth:
            add_stretch = x / (new_slice_width * frame_count)
            right = left + int(new_slice_width * add_stretch)

        TLP = add(TLP, frame[:, left:right])

        if debug:
            print '{}/{} s={},{},{} {}'.format(i, 
             frame_count, slice_width, left, right, TLP.shape)

        return TLP

    def save(TLP):
        if mirror is not None:
            TLP = add(TLP, cv2.flip(TLP, 1))

        filename = "SFTL"
        if stills is not None:
            filename += "_{}".format(stills)
        elif video is not None:
            filename += "_{}".format(video)
        if slice is not None:
            filename += "_slice={}".format(slice)
        if mirror is not None:
            filename += "_{}-mirror".format(mirror_method)
        if stretch is not None:
            filename += "_stretch={}".format(stretch)
        if fixedwidth:
            filename += "_fixedwidth"
        filename += ".png"
        cv2.imwrite(filename, TLP)

    def process_stills():
        TLP = None
        frame_count = len([name for name in os.listdir(stills)
               if os.path.isfile(os.path.join(stills, name))])
        print "{} still images to include from '{}'.".format(frame_count, stills)
        for i in range(0, frame_count):
            filename =  stills + "/frame_{:04d}.jpg".format(i)
            sys.stdout.write('\rProcessing file: {}'.format(filename))
            sys.stdout.flush()
            frame = cv2.imread(filename)
            TLP = add_slice(TLP, frame_count, i, frame)
        save(TLP)

    def process_video():
        TLP = None
        video_input = cv2.VideoCapture(video)
        frame_count = video_input.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        print "{} frames to include from '{}'.".format(frame_count, video)
        i = 0
        while video_input.isOpened():
            sys.stdout.write('\rProcessing frame: {}'.format(i))
            sys.stdout.flush()
            ret, frame = video_input.read()
            if not ret: break
            TLP = add_slice(TLP, frame_count, i, frame)
            i += 1
        video_input.release()
        save(TLP)

    print '-' * 30
    if any(option is not None for option in [slice, mirror, stretch]):
        print "Processing options:"
        if slice is not None: print "  Slice = {}".format(slice)
        if mirror is not None: print "  Mirror = {}".format(mirror)
        if stretch is not None: print "  Stretch = {}".format(stretch)
        if fixedwidth: print "  Fixed Width = True"

    if stills is not None:
        process_stills()
    elif video is not None:
        process_video()
    elif youtube is not None:
        from pytube import YouTube
        yt = YouTube(youtube)
        video = yt.filename + '.mp4'
        if debug: print yt.get_videos()
        video_to_dl = yt.get('mp4', '720p')
        try:
            open(video)
        except IOError:
            video_to_dl.download('.')
        process_video()
    else:
        print "Please input either stills='frames', " + \
              "video='name.avi', or youtube='<url>'.\n" + \
              "View help(SFTL) for more information."
    print '\n' + '-' * 30

if __name__ == "__main__":
    SFTL()

    # Tests
    if 0:
        slices = [None, 0.5] # beginning of slice horizontal location (percent)
        mirror_methods = [None, 'full', 'half']
        stretches = [None, 0.5, 2]

        for slice in slices:
            for mirror_method in mirror_methods:
                for stretch in stretches:
                    SFTL(stills='frames',
                         slice=slice, mirror=mirror_method, stretch=stretch)

                    SFTL(video='car.avi',
                         slice=slice, mirror=mirror_method, stretch=stretch)

                    SFTL(youtube='https://youtu.be/DmYK479EpQc',
                         slice=slice, mirror=mirror_method, stretch=stretch)
