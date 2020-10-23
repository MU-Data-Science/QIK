#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..

# Creating data directories.
cd $QIK_HOME/ML_Models/DeepImageRetrieval && mkdir QIK_Data && cd QIK_Data

# Installing
conda install -y numpy matplotlib tqdm scikit-learn pytorch torchvision cudatoolkit=10.0 -c pytorch

# Downloading the DIR Model.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EU5h_fnPLJhBvevls58-EjgBkOvbZYG19DwKlXmfH1eDHg?download=1 -O Resnet-101-AP-GeM.pt

# Creating DIR Image List.
image_lst=$(cat $QIK_HOME/Reproduce_Results/data/15K_Dataset.txt)
for image in $image_lst; do
  echo "$HOME/apache-tomcat/webapps/QIK_Image_Data/$image" >> DIR_Candidates.txt
done

# Extracting DIR Features.
cd ../ && python -m dirtorch.extract_features --dataset 'ImageList("QIK_Data/DIR_Candidates.txt")' --checkpoint QIK_Data/Resnet-101-AP-GeM.pt --output QIK_Data/QIK_DIR_Features --gpu 0
