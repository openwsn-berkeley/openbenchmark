#!/bin/bash

# Exit on error
set -e

# Print each command before executing it
set -o xtrace

OPENBENCHMARK_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
JFED_DIR=$OPENBENCHMARK_DIR/experiment-control/helpers/wilab/jfed_cli

# jFED installation
sudo apt-key adv --keyserver hkp://pool.sks-keyservers.net --recv-keys E7F4995E
echo "deb http://jfed.ilabt.imec.be/deb-repo stable main" | sudo tee /etc/apt/sources.list.d/jfed.list
sudo apt-get update
sudo apt-get -y install jfed 

# jFED CLI tools download
cd $JFED_DIR
wget https://jfed.ilabt.imec.be/releases/develop/190206-192/jar/jfed_cli.tar.gz
tar xfz jfed_cli.tar.gz
cp -a jfed_cli/. .
rm jfed_cli.tar.gz
rm -rf jfed_cli

# Opentestbed ESPEC clone
git clone -b espec --single-branch https://github.com/twalcari/opentestbed.git

# Java 11 and JavaFX 11 download
cd $JFED_DIR
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
wget -O openjfx-11.0.2_linux-x64_bin-sdk.zip http://gluonhq.com/download/javafx-11-0-2-sdk-linux/
sudo tar xfz openjdk-11.0.2_linux-x64_bin.tar.gz --directory /usr/lib/jvm
sudo unzip openjfx-11.0.2_linux-x64_bin-sdk.zip -d /usr/lib/jvm 

# Install xvfb
sudo apt-get install x11-xserver-utils -y

# jFed proxy configuration
mkdir ~/.jFed
cp $OPENBENCHMARK_DIR/system-config/experimenter-ssh.properties ~/.jFed