#!/bin/bash

# Shutdown Tomcat.
bash $HOME/apache-tomcat/bin/shutdown.sh

# Build the Index Engine.
cd $QIK_HOME/IndexEngine && ant war

# Transfer the build to Tomcat.
cp build/war/IndexEngine.war $HOME/apache-tomcat/webapps/

# Start Tomcat.
cd $HOME/logs
bash $HOME/apache-tomcat/bin/startup.sh
