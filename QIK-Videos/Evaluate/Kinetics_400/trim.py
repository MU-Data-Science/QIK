# Imports
import os
import shutil
import subprocess
import shlex

# Constants
ANN_FILE = "/mydata/test.csv"
IN_VIDEO_DIR = "/mydata/Kinetics_Subset"
OUT_VIDEO_DIR = "/mydata/Kinetics_Subset_Trimmed"

if __name__ == "__main__":
    # Cleaning up the directory
    shutil.rmtree(OUT_VIDEO_DIR, ignore_errors=True)
    os.makedirs(OUT_VIDEO_DIR)

    # Reading the annotaions file
    with open(ANN_FILE) as f:
        lines = f.readlines()[1:];
        for line in lines:
            splits = line.split(",")

            # Obtaining the video id, start time and end time
            video_id = splits[1]
            start_time = splits[2]
            time_duration = int(splits[3]) - int(start_time)

            # Check if the file exists
            if not os.path.isfile(IN_VIDEO_DIR + "/" + video_id + ".mp4"):
                print("trim.py :: video_id :: " + video_id + " :: not present")
                continue

            # Trimming the video.
            print("trim.py :: Trimming video_id :: " + video_id + " :: start_time :: " + start_time + " :: time_duration :: " + str(time_duration))
            subprocess.Popen(shlex.split("ffmpeg -ss " + start_time + " -i " + IN_VIDEO_DIR + "/" + video_id + ".mp4" + " -t " + str(time_duration) + " -c copy " + OUT_VIDEO_DIR + "/" + video_id + ".mp4")) # To install ffmpeg: sudo apt-get update && sudo apt-get install -y ffmpeg

    print("trim.py :: Completed Trimming the video")


