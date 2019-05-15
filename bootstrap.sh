#!/bin/bash

# Exit on error
set -e

# Print each command before executing it
set -o xtrace

export LC_ALL=en_US.UTF-8

OPENBENCHMARK_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
OPENWSN_DIR=$OPENBENCHMARK_DIR/../openwsn

# FIXME private branch, change to the official repo once code is merged
TAG_COAP=develop_COAP-44
TAG_OV=OV-7
REPO_COAP=https://github.com/malishav/coap.git
REPO_OV=https://github.com/malishav/openvisualizer.git

sudo apt-get update
sudo apt -y install build-essential
sudo apt -y install git

### Below is a verbatim copy of the OpenWSN install.sh script
# until a typo in openvisualizer installation gets fixed
mkdir $OPENWSN_DIR
sudo apt-get install -y git
cd $OPENWSN_DIR
git clone https://github.com/openwsn-berkeley/openwsn-fw.git
git clone https://github.com/openwsn-berkeley/openvisualizer.git
git clone https://github.com/openwsn-berkeley/coap.git
cd $OPENWSN_DIR/openwsn-fw/
sudo apt-get install -y python-dev
sudo apt-get install -y scons
sudo apt-get install -y python-pip
cd $OPENWSN_DIR/openvisualizer/
sudo apt-get install -y python-tk
sudo pip install -r requirements.txt --ignore-installed
cd $OPENWSN_DIR/coap/
sudo pip install -r requirements.txt
sudo apt-get install -y gcc-arm-none-eabi
sudo apt-get install -y gcc-msp430

cd $OPENBENCHMARK_DIR
### End of OpenWSN install.sh script copy

wget https://openwsn.atlassian.net/wiki/download/attachments/29196302/install.sh 
#bash install.sh
rm install.sh

# Update OpenWSN-CoAP with the correct commit name
cd $OPENWSN_DIR/coap
git remote add -t $TAG_COAP -f repository $REPO_COAP
git checkout $TAG_COAP

# Update OpenVisualizer with the correct commit name
cd $OPENWSN_DIR/openvisualizer
git remote add -t $TAG_OV -f repository $REPO_OV
git checkout $TAG_OV

# Install OpenBenchmark requirements; OpenBenchmark scripts do not run with sudo
pip install --upgrade pip
pip install -r $OPENBENCHMARK_DIR/requirements.txt --user

ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
echo "==================================="
echo "Please publish the following SSH key on any server where automated SSH is requested"
cat ~/.ssh/id_rsa.pub
echo "==================================="

