#!/bin/bash
# usage: init.sh  [--home Home] [--qik QIK_Home] [-h | --help]

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..
USER=${USER}

# Usage.
usage()
{
    echo "usage: init.sh [--user User] [--home Home] [--qik QIK_Home] [-h | --help]"
}

# Read input parameters.
while [ "$1" != "" ]; do
    case $1 in
    	--user)
        	shift
        	USER=$1
        	;;
        --home)
        	shift
        	HOME=$1
        	;;
        --qik)
        	shift
        	QIK_HOME=$1
        	;;
        -h | --help )           
        	usage
        	exit
        	;;
        * )                     
        	usage
            exit
    esac
    shift
done

# Installing Conda.
cd $HOME && wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
bash Anaconda3-2019.03-Linux-x86_64.sh -b -p $HOME/anaconda3
export PATH=$HOME/anaconda3/bin:$PATH
. /users/$USER/.bashrc
echo 'export PATH='$HOME'/anaconda3/bin:$PATH' >> /users/$USER/.profile
conda init
conda create -y --name qik_env python=3.6
conda activate qik_env
echo 'export PATH='$HOME'/anaconda3/envs/qik_env/bin::$PATH' >> /users/$USER/.profile

# Exports
export HOME=$HOME
echo 'export HOME='$HOME >> /users/$USER/.profile
export QIK_HOME=$QIK_HOME
echo 'export QIK_HOME='$QIK_HOME >> /users/$USER/.profile
IP=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep -v '10.10.1.*'`
export IP=$IP
echo 'export IP='$IP >> /users/$USER/.profile
export DB_ROOT=''
echo 'export DB_ROOT=""' >> /users/$USER/.profile
. /users/$USER/.profile

# Installing Java.
sudo apt-get -y update
cd $HOME && wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz
tar -xvf jdk-8u131-linux-x64.tar.gz
export JAVA_HOME="$HOME/jdk1.8.0_131"
echo 'export JAVA_HOME='$HOME'/jdk1.8.0_131' >> /users/$USER/.profile
export PATH="$PATH:$JAVA_HOME/bin"
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /users/$USER/.profile
. /users/$USER/.profile

# Installing Ant.
sudo apt-get -y install ant

# Setting up Tomcat.
cd $HOME && wget https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.20/bin/apache-tomcat-9.0.20.zip
unzip apache-tomcat-9.0.20.zip
mv apache-tomcat-9.0.20 apache-tomcat
chmod 777 apache-tomcat/bin/*
bash apache-tomcat/bin/startup.sh

# Installing Bazel.
sudo apt-get -y install pkg-config zip g++ zlib1g-dev unzip python
cd $HOME && wget https://github.com/bazelbuild/bazel/releases/download/0.25.3/bazel-0.25.3-installer-linux-x86_64.sh
chmod +x bazel-0.25.3-installer-linux-x86_64.sh
./bazel-0.25.3-installer-linux-x86_64.sh --user
export PATH="$PATH:$HOME/bin"
echo 'export PATH=$PATH:'$HOME'/bin' >> /users/$USER/.profile
. /users/$USER/.profile

# Downloading Large Files.
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EQ8OVRhr8kdAoL-n52IX-sEBEsUhOrK5Q_C_SkqTUAthUQ?download=1 -O $QIK_HOME/ML_Models/ShowAndTell/checkpoints/model.ckpt-5000000.data-00000-of-00001
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EVA9jI60C4xAoaxgmnt4s2EB4evfyx4PFs6X6Z4lzkii2Q?download=1 -O $QIK_HOME/IndexEngine/lib/stanford-corenlp-3.9.2-models.jar
wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/ERWi9gvm7epHpogQIhr8d8EB0-krRTswMoo6LjKpgPuDQg?download=1 -O $QIK_HOME/IndexEngine/lib/stanford-parser-3.9.2-models.jar

# Changing the IP address from localhost.
bash $QIK_HOME/scripts/deploy_scripts/change_ip.sh

# Setting up BaseX
cd $QIK_HOME && wget http://files.basex.org/releases/9.2/BaseX92.zip && unzip BaseX92.zip && mv basex BaseX
bash $QIK_HOME/BaseX/bin/basexserver -S
bash $QIK_HOME/BaseX/bin/basex -c "create db QIK"

# Installing APTED
cd $QIK_HOME && git clone https://github.com/JoaoFelipe/apted.git APTED

# Building and deploying the indexing engine.
bash $QIK_HOME/scripts/deploy_scripts/deploy_index_engine.sh

# Directory to save the query video.
mkdir $HOME/apache-tomcat/webapps/QIK_Video_Data

# Directory to save the query scenes.
mkdir $HOME/apache-tomcat/webapps/QIK_Scene_Data

# Setting Stanford Parser Classpath
export CLASSPATH=$QIK_HOME/IndexEngine/lib
echo 'export CLASSPATH=$QIK_HOME/IndexEngine/lib' >> /users/$USER/.profile

# Installing Python dependencies.
pip install -r $QIK_HOME/scripts/deploy_scripts/requirements.txt

# Starting up the Embedding web application.
cd $QIK_HOME/Embeddings
python app.py &>> Embeddings.log &

# Installing xvfb and emulating a vitural display.
sudo apt-get -y install xvfb
Xvfb :99 &
export DISPLAY=:99
echo 'export DISPLAY=:99' >> /users/$USER/.profile

# Installing pdfcrop
sudo apt-get -y install texlive-extra-utils

# Seting up Clip captioning model
pip install transformers==4.15.0
cd $QIK_HOME && pip install git+https://github.com/openai/CLIP.git
pip install scikit-image==0.17.2
pip install gdown==4.2.0
mkdir $QIK_HOME/QIK_Web/pretrained_models && wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EWBfqexNmcdPiG1wUdGm1vUBCf13bR8r_ECU0DFDX14t4A?download=1 -O $QIK_HOME/QIK_Web/pretrained_models/model_wieghts.pt

# mlpy installation for computing the LCS
sudo apt install -y g++ g++-5 libgsl-dev
cd $HOME && wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EYcYzEHSzqpLokHCLvTpN74B2NO0vsqmidhk2NQQTRlXNw?download=1 -O $HOME/mlpy-3.5.0.tar.gz
cd $HOME && tar -zxvf mlpy-3.5.0.tar.gz
cd $HOME/mlpy-3.5.0 && export CC=gcc-5 CXX=g++-5 && python setup.py build && python setup.py install

# Clean up unwanted files.
rm -rvf $HOME/bazel-0.25.3-installer-linux-x86_64.sh
rm -rvf $HOME/jdk-8u131-linux-x64.tar.gz
rm -rvf $HOME/apache-tomcat-9.0.20.zip
rm -rvf $HOME/solr-8.0.0.tgz
rm -rvf $QIK_HOME/BaseX92.zip

# Executing profile.
echo '. '$HOME'/.bashrc' >> /users/$USER/.profile
