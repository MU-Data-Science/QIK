#!/bin/bash

# 1) Captions JSON.
cd $QIK_HOME/QIK_Evaluation && make && cd data
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EVlUkGbY6MdLhqNL32eir6IBop1_mDvhp8ZyATgjRLLhGw?download=1 -O captions_2017.json

# 2) Instances JSON.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EcWfuWe3ighBp7X7vEP7XjAB7iU2FX5vpHWULr_HHJTXgA?download=1 -O instances_2017.json

# 3) DIR Setup.
cd $QIK_HOME/ML_Models/DeepImageRetrieval && mkdir QIK_Data && cd QIK_Data

# Downloading the DIR Model
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/EU5h_fnPLJhBvevls58-EjgBkOvbZYG19DwKlXmfH1eDHg?download=1 -O Resnet-101-AP-GeM.pt

# Copying DIR Image List
cp $QIK_HOME/QIK_Evaluation/data/MSCOCO_Subset_2/MSCOCO_Subset_2.txt DIR_Candidates.txt

# Extracting DIR Features.
cd ../ && python -m dirtorch.extract_features --dataset 'ImageList("QIK_Data/DIR_Candidates.txt")' --checkpoint QIK_Data/Resnet-101-AP-GeM.pt --output QIK_Data/QIK_DIR_Features  --gpu 1

# 6) Downloading the 15k image subset.
cd $HOME/apache-tomcat/webapps/
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_mail_umkc_edu/ESYcm3NFPoBHr0b4owabdikB6dBcWx7zMsJD_G2oww725Q?download=1 -O QIK_MSCOCO.tar
tar -xvf QIK_MSCOCO.tar