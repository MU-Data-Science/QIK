from sys import path
path.append("util/")

import math
import numpy as np
import cv2
import clip_caption_generator
import constants

from string import Template
from PIL import Image
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.platform import get_aspect_ratio
from scenedetect.platform import get_and_create_path
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

def get_image_arr(scene_list, video_manager, num_images=3, frame_margin=1,
                image_extension='jpg', encoder_param=95,
                image_name_template='$VIDEO_NAME-Scene-$SCENE_NUMBER-$IMAGE_NUMBER',
                output_dir=constants.QIK_SCENES_PATH, downscale_factor=1, show_progress=False,
                scale=None, height=None, width=None):
    """
    Obtained from: https://github.com/Breakthrough/PySceneDetect/blob/master/scenedetect/scene_manager.py
    """

    ret_lst = []

    if not scene_list:
        return {}
    if num_images <= 0 or frame_margin < 0:
        raise ValueError()

    video_name = video_manager.get_video_name()

    # Reset video manager and downscale factor.
    video_manager.release()
    video_manager.reset()
    video_manager.set_downscale_factor(downscale_factor)
    video_manager.start()

    # Setup flags and init progress bar if available.
    completed = True
    progress_bar = None
    if show_progress and tqdm:
        progress_bar = tqdm(
            total=len(scene_list) * num_images,
            unit='images',
            dynamic_ncols=True)

    filename_template = Template(image_name_template)

    scene_num_format = '%0'
    scene_num_format += str(max(3, math.floor(math.log(len(scene_list), 10)) + 1)) + 'd'
    image_num_format = '%0'
    image_num_format += str(math.floor(math.log(num_images, 10)) + 2) + 'd'

    framerate = scene_list[0][0].framerate

    timecode_list = [
        [
            FrameTimecode(int(f), fps=framerate) for f in [
                # middle frames
                a[len(a)//2] if (0 < j < num_images-1) or num_images == 1

                # first frame
                else min(a[0] + frame_margin, a[-1]) if j == 0

                # last frame
                else max(a[-1] - frame_margin, a[0])

                # for each evenly-split array of frames in the scene list
                for j, a in enumerate(np.array_split(r, num_images))
            ]
        ]
        for i, r in enumerate([
            # pad ranges to number of images
            r
            if 1+r[-1]-r[0] >= num_images
            else list(r) + [r[-1]] * (num_images - len(r))
            # create range of frames in scene
            for r in (
                range(start.get_frames(), end.get_frames())
                # for each scene in scene list
                for start, end in scene_list
                )
        ])
    ]

    image_filenames = {i: [] for i in range(len(timecode_list))}
    aspect_ratio = get_aspect_ratio(video_manager)
    if abs(aspect_ratio - 1.0) < 0.01:
        aspect_ratio = None

    for i, scene_timecodes in enumerate(timecode_list):
        for j, image_timecode in enumerate(scene_timecodes):
            video_manager.seek(image_timecode)
            ret_val, frame_im = video_manager.read()
            if ret_val:
                file_path = '%s.%s' % (
                    filename_template.safe_substitute(
                        VIDEO_NAME=video_name,
                        SCENE_NUMBER=scene_num_format % (i + 1),
                        IMAGE_NUMBER=image_num_format % (j + 1),
                        FRAME_NUMBER=image_timecode.get_frames()),
                    image_extension)
                image_filenames[i].append(file_path)
                if aspect_ratio is not None:
                    frame_im = cv2.resize(
                        frame_im, (0, 0), fx=aspect_ratio, fy=1.0,
                        interpolation=cv2.INTER_CUBIC)

                # Get frame dimensions prior to resizing or scaling
                frame_height = frame_im.shape[0]
                frame_width = frame_im.shape[1]

                # Figure out what kind of resizing needs to be done
                if height and width:
                    frame_im = cv2.resize(
                        frame_im, (width, height), interpolation=cv2.INTER_CUBIC)
                elif height and not width:
                    factor = height / float(frame_height)
                    width = int(factor * frame_width)
                    frame_im = cv2.resize(
                        frame_im, (width, height), interpolation=cv2.INTER_CUBIC)
                elif width and not height:
                    factor = width / float(frame_width)
                    height = int(factor * frame_height)
                    frame_im = cv2.resize(
                        frame_im, (width, height), interpolation=cv2.INTER_CUBIC)
                elif scale:
                    frame_im = cv2.resize(
                        frame_im, (0, 0), fx=scale, fy=scale,
                        interpolation=cv2.INTER_CUBIC)

                ret_lst.append(frame_im)
                cv2.imwrite(
                    get_and_create_path(file_path, output_dir),
                    frame_im)
            else:
                completed = False
                break
            if progress_bar:
                progress_bar.update(1)

    if not completed:
        print('Could not generate all output images.')

    return ret_lst


def obtain_scenes(video_path):
    # Create our video & scene managers, then add the detector.
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())

    try:

        # Improve processing speed by downscaling before processing.
        video_manager.set_downscale_factor()

        # Start the video manager and perform the scene detection.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list()

        # Obtain the images
        return get_image_arr(scene_list, video_manager)

    finally:
         video_manager.release()

