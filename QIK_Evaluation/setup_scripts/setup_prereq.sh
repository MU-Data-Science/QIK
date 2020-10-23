#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..
QIK_CORE_NAME=QIK
USER=${USER}

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
export HOSTNAME=$(hostname)
echo 'export HOSTNAME='$HOSTNAME >> /users/$USER/.profile
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