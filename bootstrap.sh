#!/bin/sh

# Script designed to bootstrap a Vagrant machine

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install python-software-properties
sudo add-apt-repository ppa:ondrej/php
sudo apt-get -y update
sudo apt-get -y install php7.2
sudo apt-get -y install composer
# PHP extensions
sudo apt-get -y install php7.2-zip
sudo apt-get -y install php7.2-openssl
sudo apt-get -y install php7.2-pdo
sudo apt-get -y install php7.2-mbstring
sudo apt-get -y install php7.2-tokenizer
sudo apt-get -y install php7.2-xml
sudo apt-get -y install php7.2-ctype
sudo apt-get -y install php7.2-json
sudo apt -y install unzip
# Laravel
cd ..
composer global require "laravel/installer"
composer create-project --prefer-dist laravel/laravel benchmarking "5.6.*"
cd benchmarking
mv .env.example .env
php artisan key:generate
# OpenWSN
cd ..
git clone https://github.com/openwsn-berkeley/coap.git
git clone -b ov-iot-lab --single-branch https://github.com/bozidars27/openvisualizer.git
git clone https://github.com/bozidars27/iotlab-exp-auto.git
# Python-dev
sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo apt-get -y install gcc
sudo apt-get -y install scons
sudo pip install -r openvisualizer/requirements.txt
sudo pip install -r iotlab-exp-auto/requirements.txt
# Node.js
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs

# overwrite Laravel project with our code on startup
cp -r ~/soda-benchmarking/* ~/benchmarking/
echo "cp -r ~/soda-benchmarking/* ~/benchmarking/" >> ~/.bashrc

# overwrite default Apache config file now and at every startup
sudo cp ~/soda-benchmarking/apache-config/000-default.conf /etc/apache2/sites-enabled/000-default.conf
echo "sudo cp ~/soda-benchmarking/apache-config/000-default.conf /etc/apache2/sites-enabled/000-default.conf" >> ~/.bashrc
sudo cp ~/soda-benchmarking/apache-config/envvars /etc/apache2/envvars
echo "sudo cp ~/soda-benchmarking/apache-config/envvars /etc/apache2/envvars" >> ~/.bashrc
rm -f ~/openvisualizer/build/runui/networkEvent.log*
echo "rm -f ~/openvisualizer/build/runui/networkEvent.log*" >> ~/.bashrc

rm -f ~/openvisualizer/build/runui/*.log*
echo "rm -f ~/openvisualizer/build/runui/*.log*" >> ~/.bashrc

ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
echo "==================================="
echo "Please publish the following SSH key on any server where automated SSH is requested"
cat ~/.ssh/id_rsa.pub
echo "==================================="

sudo a2enmod rewrite
sudo service apache2 restart

