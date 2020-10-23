#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..

# Installing FR-CNN.
cd $QIK_HOME/ML_Models/DeepVision && bash setup.sh

# Activating the conda environment.
source activate deepvision

# Setting python path after installation.
export PYTHONPATH=$QIK_HOME/ML_Models/DeepVision/py-faster-rcnn/caffe-fast-rcnn/python:$PYTHONPATH

# Extracting features.
python read_data.py && python features.py

# Starting the FR-CNN web app.
python qik_search.py &>> /dev/null &