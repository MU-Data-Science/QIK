#!/usr/bin/env bash

# Creating a seperate conda environment due to its dependency on python 2.7.
conda create --name deepvision python=2.7
conda activate deepvision

# Cloning Faster R-CNN python implementation by Ross Girshick.
git clone --recursive https://github.com/rbgirshick/py-faster-rcnn.git

# Setting project path.
export FRCN_ROOT=`pwd`/py-faster-rcnn

# Installing necessary libraries
pip install cython numpy opencv-python scikit-learn easydict flask scikit-image

# Build the Cython modules.
cd $FRCN_ROOT/lib
make

# Caffe Installation.
sudo apt-get install -y libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
sudo apt-get install -y --no-install-recommends libboost-all-dev
sudo apt-get install -y libatlas-base-dev
for req in $(cat caffe-fast-rcnn/python/requirements.txt); do pip install $req; done
# Fixing common caffe installation issues. (Ref: https://github.com/BVLC/caffe/wiki/Commonly-encountered-build-issues)
sudo apt-get install -y libgflags-dev libgoogle-glog-dev liblmdb-dev 
sudo apt-get uninstall -y libatlas-base-dev

# Installing additional python libraries.
pip install protobuf pyyaml

#Build Caffe and pycaffe
cd $FRCN_ROOT/caffe-fast-rcnn
cp ../../Makefile.config .
make all
make -j8 && make pycaffe

# Adding to PYTHONPATH
export PYTHONPATH=`pwd`/python:$PYTHONPATH

# Download the Faster R-CNN Model
cd ../../data/models/ && bash fetch_models.sh
