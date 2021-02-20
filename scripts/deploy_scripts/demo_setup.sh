#!/usr/bin/env bash

# Constants.
HOME=${HOME}
QIK_HOME=${PWD}/../..
SYSTEM="15k"
SYSTEM_1="120k"
SYSTEM_2="15k"
SYSTEM_3="unsplash"

# Usage.
usage()
{
    echo "usage: demo_setup.sh [--home Home] [--qik QIK_Home] [--system ${SYSTEM_1} | ${SYSTEM_2} | ${SYSTEM_3}] [-h | --help]"
}

# Read input parameters.
while [ "$1" != "" ]; do
    case $1 in
        --home)
        	shift
        	HOME=$1
        	;;
        --qik)
        	shift
        	QIK_HOME=$1
        	;;
        --system)
        	shift
        	SYSTEM=$1
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

if [ ${SYSTEM} = ${SYSTEM_1} ]; then
  echo "Setting up the system for the 120k dataset"

  # Downloading the pre-constructed index
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/Eev0bVE2WzBMor4-n-xs3lwBHciqDcaDpyQ6LLzeyzhy5Q?download=1 -O $QIK_HOME/BaseX/data/Index.tar

  # Extracting the pre-constructed index
  cd $QIK_HOME/BaseX/data && tar -xvf Index.tar

  # Downloading the 120k Image dataset.
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EU96plY_Dj1Kkvg8fZ_0COAB5Vo-CckqAC0OjUdyBIghuw?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.parta
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EZHW5AObwsRNpPKIMHnOOagBcH7tcFv0rW4R70F3I2Drdw?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partb
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EaM7NGGzTDNIv8qOULk30fQBrYnhz-QFDlxDkm48Mxselg?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partc
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EaPg4AqwJKBPmtmKpXniR5kBiKbysRKRO4VxdIJ1_2G_9g?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partd

  # Extracting the 120k images dataset.
  cd $HOME/apache-tomcat/webapps && rm -rvf Images.tar
  cat Images.tar.parta >> Images.tar
  cat Images.tar.partb >> Images.tar
  cat Images.tar.partc >> Images.tar
  cat Images.tar.partd >> Images.tar
  tar -xvf Images.tar

  # Changing the old IP address.
  echo 'TOMCAT_OLD_IP_ADDR = "http://128.110.154.115:8080"' >> ${QIK_HOME}/QIK_Web/util/constants.py

elif [ ${SYSTEM} = ${SYSTEM_2} ]; then
  echo "Setting up the system for the 15k dataset"

  # Downloading the pre-constructed index
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EZedBIRgYntGpc9h_hsFezcBups95AkJgeR2TwyoFxW8tA?download=1 -O $QIK_HOME/BaseX/data/Index.tar

  # Extracting the pre-constructed index
  cd $QIK_HOME/BaseX/data && tar -xvf Index.tar

  # Downloading the 15k Image dataset
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/ESYcm3NFPoBHr0b4owabdikB6dBcWx7zMsJD_G2oww725Q?download=1 -O $HOME/apache-tomcat/webapps/Images.tar

  # Extracting the 15k images dataset.
  cd $HOME/apache-tomcat/webapps && tar -xvf Images.tar

  # Changing the old IP address.
  echo 'TOMCAT_OLD_IP_ADDR = "http://128.105.144.88:8080"' >> ${QIK_HOME}/QIK_Web/util/constants.py

elif [ ${SYSTEM} = ${SYSTEM_3} ]; then
  echo "Setting up Unsplash dataset"

  # Downloading the pre-constructed index
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EZmt3WOyro5OngC6gUxpJGYBUzK49phYlQ2dmzmruhQ1Ow?download=1 -O $QIK_HOME/BaseX/data/Index.tar

  # Extracting the pre-constructed index
  cd $QIK_HOME/BaseX/data && tar -xvf Index.tar

  # Downloading the Unsplash Image dataset.
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EXG2o1hFb4BNvvGRDhjqLNsB2f0J-cO4Sxnyi_qFeSZoIw?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.parta
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EVSzJllUe0NFookI3VpYQSwBuIjjd3xDYhP5Dp2qRprHvw?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partb
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EY1gDNw6r7VCtZj9uNw13rAB_1koBl47MMQB5Pye56LJeA?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partc
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EfSJEHFp9bJJjujcC4dRetgBTeFjtMejY_FCyRvXm1x2dg?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partd
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/Eby42ZJA96VGnxyASD-hwDYBCEVqWXFW3KF13eIBqtyscg?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.parte
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EZRJJYC5iHlFqDA7lERIW5sBCh7yaF3c_I-9f9Mwhq9ZPg?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partf
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/EWYyZ4PGiwBNrN0NfsU-RKoBbpHuYiY4kkSwrqK4xygkCw?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.partg
  wget https://mailmissouri-my.sharepoint.com/:u:/g/personal/az2z7_umsystem_edu/ESjYJIR907xLrbLM6u2hkC8Bsy1xCgxiuey1ebgD8-b9HA?download=1 -O $HOME/apache-tomcat/webapps/Images.tar.parth

  # Extracting the Unsplash Image dataset.
  cd $HOME/apache-tomcat/webapps && rm -rvf Images.tar
  cat Images.tar.parta >> Images.tar
  cat Images.tar.partb >> Images.tar
  cat Images.tar.partc >> Images.tar
  cat Images.tar.partd >> Images.tar
  cat Images.tar.parte >> Images.tar
  cat Images.tar.partf >> Images.tar
  cat Images.tar.partg >> Images.tar
  cat Images.tar.parth >> Images.tar
  tar -xvf Images.tar

  # Changing the old IP address.
  echo 'TOMCAT_OLD_IP_ADDR = "http://128.110.154.165:8080"' >> ${QIK_HOME}/QIK_Web/util/constants.py

else
  usage
fi