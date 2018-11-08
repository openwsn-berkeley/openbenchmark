#!/bin/sh

# Script designed to bootstrap a Vagrant machine
sudo apt-get -y update
sudo apt-get -y upgrade

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
sudo apt-get -y install php7.2-openssl
sudo apt-get -y install php7.2-pdo
sudo apt-get -y install php7.2-mbstring
sudo apt-get -y install php7.2-tokenizer
sudo apt-get -y install php7.2-xml
sudo apt-get -y install php7.2-ctype
sudo apt-get -y install php7.2-json
sudo apt -y install unzip
# Laravel
cd ~
composer global require "laravel/installer"
composer create-project --prefer-dist laravel/laravel temp "5.6.*"
cd temp
mv .env.example .env
php artisan key:generate

# OpenWSN
cd ~
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
sudo pip install -r docs/requirements.txt

# Node.js
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs

# Link docs directory to public/docs
cd ~/openbenchmark/public
ln -s /home/vagrant/openbenchmark/docs/build/html docs

#overwrite Laravel project with our code on startup
cp -r -n ~/temp/* ~/openbenchmark/
cp -r -n ~/temp/.[!.]* ~/openbenchmark/

# remove original Laravel base project
sudo rm -rf ~/temp

# install node_modules
sudo apt-get install npm
cd ~/openbenchmark
npm install
npm update
nodejs node_modules/node-sass/scripts/install.js
npm rebuild node-sass

#Configure Apache to use PHP7.2-FPM
sudo a2enmod actions fastcgi alias proxy_fcgi

# overwrite default Apache config file now and at every startup
sudo cp ~/openbenchmark/system-config/000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo dos2unix /etc/apache2/sites-enabled/000-default.conf 

sudo cp ~/openbenchmark/system-config/envvars /etc/apache2/envvars
sudo dos2unix /etc/apache2/envvars

sudo cp ~/openbenchmark/system-config/www.conf /etc/php/7.2/fpm/pool.d/www.conf
sudo dos2unix /etc/php/7.2/fpm/pool.d/www.conf

sudo chown -R vagrant:vagrant /var/lib/apache2/fastcgi

# Start node.js as a deamon
sudo cp ~/openbenchmark/system-config/index.service /lib/systemd/system/index.service
sudo systemctl daemon-reload
sudo systemctl restart index

sudo rm -f ~/openvisualizer/build/runui/networkEvent.log*
echo "sudo rm -f ~/openvisualizer/build/runui/networkEvent.log*" >> ~/.bashrc

sudo rm -f ~/openvisualizer/build/runui/*.log*
echo "sudo rm -f ~/openvisualizer/build/runui/*.log*" >> ~/.bashrc

# compile app.js and app.css for development
npm run dev

ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
echo "==================================="
echo "Please publish the following SSH key on any server where automated SSH is requested"
cat ~/.ssh/id_rsa.pub
echo "==================================="

# Restart Apache and PHP7.2-FPM
sudo a2enmod rewrite
sudo service apache2 restart
sudo service php7.2-fpm restart