#!/usr/bin/env bash

# Installation Commands (If not already installed)
# sudo apt-get install ffmpeg && pip install scenedetect[opencv-headless]

if [[ $# -ne 1 ]]; then
	echo "usage: detect_scenes.sh <VIDEO_PATH>"
    exit
fi

scenedetect -i ${1} detect-content list-scenes -n save-images
