#!/bin/bash

# Exit on error
set -e

# Print each command before executing it
set -o xtrace

OPENBENCHMARK_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
JFED_DIR=$OPENBENCHMARK_DIR/experiment_provisioner/helpers/wilab/jfed_cli
JVM_DIR="/usr/lib/jvm"

if [ ! -d $JVM_DIR ]; then
	sudo mkdir $JVM_DIR
fi

sudo apt-get install unzip

# Java 11 and JavaFX 11 download
cd $JFED_DIR
if [ ! -f "$JVM_DIR/jdk-12.0.1" ]; then
	wget https://cdn.azul.com/zulu/bin/zulu12.2.3-ca-jdk12.0.1-linux_x64.tar.gz
	sudo tar xfz zulu12.2.3-ca-jdk12.0.1-linux_x64.tar.gz --directory $JVM_DIR
	rm zulu12.2.3-ca-jdk12.0.1-linux_x64.tar.gz
	sudo mv $JVM_DIR/zulu12.2.3-ca-jdk12.0.1-linux_x64 $JVM_DIR/jdk-12.0.1
fi
if [ ! -f "$JVM_DIR/javafx-sdk-12.0.1" ]; then
	wget -O openjfx-12.0.1_linux-x64_bin-sdk.zip http://gluonhq.com/download/javafx-12-0-1-sdk-linux/
	sudo unzip openjfx-12.0.1_linux-x64_bin-sdk.zip -d /usr/lib/jvm
	rm openjfx-12.0.1_linux-x64_bin-sdk.zip
fi

# Install xvfb and xrandr
sudo apt-get install xvfb -y
sudo apt-get install x11-xserver-utils -y

# Installation of the missing dependencies needed by jFed
sudo apt-get install -y -f libxrender1 libxtst6 libxi6 gtk2-engines libxtst6 libxxf86vm1 freeglut3 libxslt1.1 xbase-clients xterm

# jFED CLI tools download
cd $JFED_DIR
wget https://jfed.ilabt.imec.be/releases/develop/190206-192/jar/jfed_cli.tar.gz
tar xfz jfed_cli.tar.gz
cp -a jfed_cli/. .
rm jfed_cli.tar.gz
rm -rf jfed_cli

# Opentestbed ESPEC clone
if [ ! -d "opentestbed" ]; then
	git clone -b espec --single-branch https://github.com/malishav/opentestbed.git
fi

# jFed proxy configuration
mkdir -p ~/.jFed
cp $OPENBENCHMARK_DIR/system-config/experimenter-ssh.properties ~/.jFed

# dos2unix on sh files
dos2unix *.sh