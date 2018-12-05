#!/bin/bash

# Exit on error
set -e

OPENBENCHMARK_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
LARAVEL_ROOT="$OPENBENCHMARK_DIR/web/public"
GROUP="$( id -gn )"
INDEX_JS_PATH="$OPENBENCHMARK_DIR/experiment-control/nodejs_websocket/index.js"

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y software-properties-common

# Install Apache and Apache dependencies
sudo apt-get -y install apache2
cd /tmp && wget http://mirrors.kernel.org/ubuntu/pool/multiverse/liba/libapache-mod-fastcgi/libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb
sudo dpkg -i libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb; sudo apt install -f

# Install PHP 7.2 and Composer
sudo apt-get -y install python-software-properties
sudo add-apt-repository ppa:ondrej/php -y
sudo apt-get -y update
sudo apt-get -y install php7.2 php7.2-fpm php7.2-common
sudo apt-get -y install composer

# PHP extensions
sudo apt-get -y install php7.2-zip
sudo apt-get -y install php7.2-pdo
sudo apt-get -y install php7.2-mbstring
sudo apt-get -y install php7.2-tokenizer
sudo apt-get -y install php7.2-xml
sudo apt-get -y install php7.2-ctype
sudo apt-get -y install php7.2-json
sudo apt -y install unzip

# Laravel
cd $OPENBENCHMARK_DIR
composer global require "laravel/installer"
composer create-project --prefer-dist laravel/laravel temp "5.6.*"
cd temp
mv .env.example .env
php artisan key:generate

# OpenWSN
cd $OPENBENCHMARK_DIR
git clone https://github.com/openwsn-berkeley/coap.git

# FIXME private branch, change to the official repo once code is merged
git clone -b ov-dynamic-topic --single-branch https://github.com/bozidars27/openvisualizer.git

# Python-dev
sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo apt-get -y install gcc
sudo apt-get -y install scons

sudo pip install -U pyopenssl

# OpenVisualizer needs to be launched with sudo because of the TUN interface
sudo pip install -r $OPENBENCHMARK_DIR/openvisualizer/requirements.txt --ignore-installed
# OpenBenchmark scripts do not run with sudo
pip install -r $OPENBENCHMARK_DIR/requirements.txt --user

# Node.js and NPM
curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
sudo apt-get install -fy nodejs

# Link docs directory to public/docs
cd $OPENBENCHMARK_DIR/web/public
ln -s $OPENBENCHMARK_DIR/docs/build/html ./docs

#overwrite Laravel project with our code on startup
cd $OPENBENCHMARK_DIR
cp -r -n $OPENBENCHMARK_DIR/temp/* $OPENBENCHMARK_DIR/web/
cp -r -n $OPENBENCHMARK_DIR/temp/.[!.]* $OPENBENCHMARK_DIR/web/

# remove original Laravel base project
rm -rf $OPENBENCHMARK_DIR/temp

# configure node_modules
cd $OPENBENCHMARK_DIR/web
npm install
npm update

#Configure Apache to use PHP7.2-FPM
sudo a2enmod actions fastcgi alias proxy_fcgi

# overwrite default Apache config files
sudo cp $OPENBENCHMARK_DIR/system-config/000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo dos2unix /etc/apache2/sites-enabled/000-default.conf
sudo sed -i "s#@LARAVEL_ROOT@#$LARAVEL_ROOT#" /etc/apache2/sites-enabled/000-default.conf

sudo cp $OPENBENCHMARK_DIR/system-config/envvars /etc/apache2/envvars
sudo dos2unix /etc/apache2/envvars
sudo sed -i "s#@USER@#$USER#" /etc/apache2/envvars
sudo sed -i "s#@GROUP@#$GROUP#" /etc/apache2/envvars

sudo cp $OPENBENCHMARK_DIR/system-config/www.conf /etc/php/7.2/fpm/pool.d/www.conf
sudo dos2unix /etc/php/7.2/fpm/pool.d/www.conf
sudo sed -i "s#@USER@#$USER#" /etc/php/7.2/fpm/pool.d/www.conf
sudo sed -i "s#@GROUP@#$GROUP#" /etc/php/7.2/fpm/pool.d/www.conf

sudo chown -R $USER:$USER /var/lib/apache2/fastcgi

# Start node.js as a deamon
sudo cp $OPENBENCHMARK_DIR/system-config/index.service /lib/systemd/system/index.service
sudo sed -i "s#@USER@#$USER#" /lib/systemd/system/index.service
sudo sed -i "s#@INDEX_JS_PATH@#$INDEX_JS_PATH#" /lib/systemd/system/index.service
sudo systemctl daemon-reload
sudo systemctl restart index

sudo rm -f $OPENBENCHMARK_DIR/openvisualizer/build/runui/networkEvent.log*
echo "sudo rm -f $OPENBENCHMARK_DIR/openvisualizer/build/runui/networkEvent.log*" >> ~/.bashrc

sudo rm -f $OPENBENCHMARK_DIR/openvisualizer/build/runui/*.log*
echo "sudo rm -f $OPENBENCHMARK_DIR/openvisualizer/build/runui/*.log*" >> ~/.bashrc

# compile app.js and app.css for development
npm run dev

# generate the docs
cd $OPENBENCHMARK_DIR/docs
make html

ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
echo "==================================="
echo "Please publish the following SSH key on any server where automated SSH is requested"
cat ~/.ssh/id_rsa.pub
echo "==================================="

# Restart Apache and PHP7.2-FPM
sudo a2enmod rewrite
sudo service apache2 restart
sudo service php7.2-fpm restart
