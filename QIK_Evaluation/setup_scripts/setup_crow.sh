#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..

# Obtaining the model.
wget http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_16_layers.caffemodel -O $QIK_HOME/ML_Models/CroW/vgg/VGG_ILSVRC_16_layers.caffemodel

# Activating the conda environment.
source activate deepvision

# Setting python path after installation.
export PYTHONPATH=$QIK_HOME/ML_Models/DeepVision/py-faster-rcnn/caffe-fast-rcnn/python:$PYTHONPATH

# Extracting the features.
cd $QIK_HOME/ML_Models/CroW && python extract_features.py --images $HOME/apache-tomcat/webapps/QIK_Image_Data --out out