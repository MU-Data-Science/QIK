#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..
QIK_CORE_NAME=QIK
USER=${USER}
QIK_INDEX_URL="https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EZedBIRgYntGpc9h_hsFezcBups95AkJgeR2TwyoFxW8tA?download=1"

# Directory to save the query image.
mkdir $HOME/apache-tomcat/webapps/QIK

# Downloading Large Files.
# 1) Show and tell model.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EQ8OVRhr8kdAoL-n52IX-sEBEsUhOrK5Q_C_SkqTUAthUQ?download=1 -O $QIK_HOME/ML_Models/ShowAndTell/checkpoints/model.ckpt-5000000.data-00000-of-00001
# 2) Stanford NLP jar.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EVA9jI60C4xAoaxgmnt4s2EB4evfyx4PFs6X6Z4lzkii2Q?download=1 -O $QIK_HOME/IndexEngine/lib/stanford-corenlp-3.9.2-models.jar
# 3) Stanford Parser Jar.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/ERWi9gvm7epHpogQIhr8d8EB0-krRTswMoo6LjKpgPuDQg?download=1 -O $QIK_HOME/IndexEngine/lib/stanford-parser-3.9.2-models.jar
# 4) MSCOCO 15K Image dataset.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/ESYcm3NFPoBHr0b4owabdikB6dBcWx7zMsJD_G2oww725Q?download=1 -O $HOME/apache-tomcat/webapps/QIK_MSCOCO.tar
# 5) MSCOCO Instances JSON.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EcWfuWe3ighBp7X7vEP7XjAB7iU2FX5vpHWULr_HHJTXgA?download=1 -O $QIK_HOME/Reproduce_Results/data/instances_2017.json
# 6) MSCOCO Captions JSON.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EVlUkGbY6MdLhqNL32eir6IBop1_mDvhp8ZyATgjRLLhGw?download=1 -O $QIK_HOME/Reproduce_Results/data/captions_2017.json

# Changing the IP address from localhost.
bash $QIK_HOME/scripts/deploy_scripts/change_ip.sh

# Setting up BaseX
cd $QIK_HOME && wget http://files.basex.org/releases/9.2/BaseX92.zip && unzip BaseX92.zip && mv basex BaseX
bash $QIK_HOME/BaseX/bin/basexserver -S
bash $QIK_HOME/BaseX/bin/basex -c "create db QIK"

# Setting up Solr.
cd $HOME && wget https://archive.apache.org/dist/lucene/solr/8.0.0/solr-8.0.0.tgz
tar -xvf solr-8.0.0.tgz
chmod +x solr-8.0.0/bin/*
export SOLR_ULIMIT_CHECKS=false
echo 'export SOLR_ULIMIT_CHECKS=false' >> /users/$USER/.profile
. /users/$USER/.profile

# Setting Stanford Parser Classpath
export CLASSPATH=$QIK_HOME/IndexEngine/lib
echo 'export CLASSPATH=$QIK_HOME/IndexEngine/lib' >> /users/$USER/.profile

# Starting Solr.
./solr-8.0.0/bin/solr start

# Creating QIK core.
./solr-8.0.0/bin/solr create -c $QIK_CORE_NAME

# Installing APTED
cd $QIK_HOME && git clone https://github.com/JoaoFelipe/apted.git APTED

# Building and deploying the indexing engine.
bash $QIK_HOME/scripts/deploy_scripts/deploy_index_engine.sh

# Installing Python dependencies.
pip install -r $QIK_HOME/scripts/deploy_scripts/requirements.txt

# Intalling pycoco
cd $QIK_HOME/Reproduce_Results/pycocotools && make all && make install

# Extracting the image dataset downloaded.
cd $HOME/apache-tomcat/webapps/ && tar -xvf QIK_MSCOCO.tar

# Clean up unwanted files.
rm -rvf $HOME/bazel-0.25.3-installer-linux-x86_64.sh
rm -rvf $HOME/jdk-8u131-linux-x64.tar.gz
rm -rvf $HOME/apache-tomcat-9.0.20.zip
rm -rvf $HOME/solr-8.0.0.tgz
rm -rvf $QIK_HOME/BaseX92.zip

# Downloading index files.
wget $QIK_INDEX_URL -O ${QIK_HOME}/BaseX/data/QIK.tar
cd ${QIK_HOME}/BaseX/data && tar -xvf QIK.tar