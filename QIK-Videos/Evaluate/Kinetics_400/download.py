# Imports
import subprocess
import os
import time

# Constants
DATA_FILE = "/mydata/Kinetics/Kinetics400_Splits/Kinetics_Train_Subset.csv"
TEMP_VIDEO_DIR = "/mydata/Kinetics_Video_Data"
DOWNLOAD_DIR = "/mydata/Kinetics_Video_Data_Trimmed"
MAX_P_COUNT = 120


def get_process_count():
    output = subprocess.check_output('ps -xww | grep "/bin/sh -c youtube-dl" | wc -l', shell=True)
    return int(output) - 2


def download_data(file_name, download_url, start_time, end_time):
    # Obtaining the time duration
    time_duration = float(end_time) - float(start_time)

    # Forming the download command string
    download_cmd = "youtube-dl -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best\" -o " + TEMP_VIDEO_DIR + "/video_" + file_name + ".mp4 " + str(
        download_url) + " && ffmpeg -ss " + str(
        start_time) + " -i " + TEMP_VIDEO_DIR + "/video_" + file_name + ".mp4" + " -t " + str(
        time_duration) + " -c copy " + DOWNLOAD_DIR + "/" + file_name + ".mp4 && rm -rvf " + TEMP_VIDEO_DIR + "/video_" + file_name + ".mp4"

    # Starting the download as a background process
    subprocess.Popen(download_cmd, shell=True)


if __name__ == "__main__":
    # Creating directories if they do not exist
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Reading the data from the input
    with open(DATA_FILE) as data:
        lines = data.readlines()

        # Iterating over the download URLs
        for line in lines:
            # Splitting the line contents
            line_splits = line.rstrip().split(",")

            # Download the file
            download_data(line_splits[0], line_splits[1], line_splits[2], line_splits[3])

            # Wait before downloading (To prevent filling up space)
            if get_process_count() >= MAX_P_COUNT:
                while True:
                    time.sleep(5)
                    if get_process_count() <= MAX_P_COUNT:
                        break
