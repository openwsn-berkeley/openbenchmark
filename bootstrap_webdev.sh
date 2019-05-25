#!/bin/bash

# Exit on error
set -e

# Print each command before executing it
set -o xtrace

OPENBENCHMARK_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
LARAVEL_ROOT="$OPENBENCHMARK_DIR/web/public"
GROUP="$( id -gn )"

# Create system swap as PHP installation may fail without it
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y software-properties-common

# Install Apache and Apache dependencies
sudo apt-get -y install apache2
cd /tmp && wget http://mirrors.kernel.org/ubuntu/pool/multiverse/liba/libapache-mod-fastcgi/libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb
sudo dpkg -i libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb; sudo apt install -f

# Install PHP 7.2 and Composer
sudo apt-get -y install python-software-properties
LC_ALL=C.UTF-8 sudo add-apt-repository ppa:ondrej/php -y
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
sudo apt-get -y install php7.2-mysql
sudo apt -y install unzip

# Laravel
cd $OPENBENCHMARK_DIR
composer global require "laravel/installer"
composer create-project --prefer-dist laravel/laravel temp "5.6.*"
cd temp
mv .env.example .env
php artisan key:generate

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

sudo cp $OPENBENCHMARK_DIR/system-config/.env $OPENBENCHMARK_DIR/web/.env
sudo dos2unix $OPENBENCHMARK_DIR/web/.env

sudo chown -R $USER:$USER /var/lib/apache2/fastcgi

# compile app.js and app.css for development
npm run dev

# generate the docs
cd $OPENBENCHMARK_DIR/docs
make html

# install MySQL
if [ ! -z "$1" ] && [ "$1" = "-mysql" ]
then
    sudo apt-get install -y mysql-server
    sudo mysql -u root -p -e 'CREATE USER "openbenchmark"@"localhost" IDENTIFIED BY "openbenchmark";'
    sudo mysqladmin -u root -p create openbenchmark
    sudo mysql -u root -p -e 'GRANT ALL PRIVILEGES ON openbenchmark.* TO "openbenchmark"@"localhost";'
    cd $OPENBENCHMARK_DIR/web
    php artisan migrate
fi

# Restart Apache and PHP7.2-FPM
sudo a2enmod rewrite
sudo service apache2 restart
sudo service php7.2-fpm restart
