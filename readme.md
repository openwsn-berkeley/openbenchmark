<p align="center"><img src="https://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_244/soda_logo_transparent_small.png"></p>

## Prerequisites

1. [Vagrant](https://www.vagrantup.com/)
2. An [IoT-LAB](https://www.iot-lab.info/) account


## Getting started

1. Start up Vagrant VM:
```
vagrant up
```

2. SSH into the server and run bootstrap.sh script:
```
vagrant ssh
./openbenchmark/bootstrap.sh
```

3. Upon the completion of the process, you will be given a public SSH key which is to be copied and pasted in your IoT-LAB account configuration

4. Write your IoT-LAB username into the experiment config file (../iotlab-exp-auto/conf.txt)
```
[exp-config]
user = YOUR_USER_NAME
```

5. Open a web browser and go to 127.0.0.1:8081


## Development

1. Run continuous rsync process on the host machine:
```
vagrant rsync-auto
```

2. Run Laravel Mix on the guest machine:
```
vagrant ssh
cd openbenchmark
npm run watch
```


