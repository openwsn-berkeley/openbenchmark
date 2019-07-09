| Branch         | Build Status  |
| -------------- | -------------:|
| master         | [![Build Status](https://travis-ci.com/openwsn-berkeley/openbenchmark.svg?branch=master)](https://travis-ci.com/openwsn-berkeley/openbenchmark)   |
| develop        | [![Build Status](https://travis-ci.com/openwsn-berkeley/openbenchmark.svg?branch=develop)](https://travis-ci.com/openwsn-berkeley/openbenchmark)  |

[<p align="center"><img src="https://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_244/soda_logo_transparent_small.png"></p>](https://www.soda.ucg.ac.me)

## About
This repository contains the code of the 6TiSCH benchmarking platform that automates the experimentation on different testbeds. 

#### Supported testbeds:
IoTLAB - Saclay
#### Supported 6TiSCH firmware:
OpenWSN

## Architecture
<p align="center"><img src="http://benchmark.6tis.ch/openbenchmark_architecture.png"></p>

## Prerequisites

1. [Vagrant](https://www.vagrantup.com/)
2. An [IoT-LAB](https://www.iot-lab.info/) account


## Getting started

1. Start up Vagrant VM:
```
vagrant up
```

2. SSH into the server and run `bootstrap.sh` script:
```
vagrant ssh
./openbenchmark/bootstrap.sh
```

3. Upon the completion of the process, you will be given a public SSH key which is to be copied and pasted into your IoT-LAB account configuration

4. Run `bootstrap_webdev.sh` script:
```
./openbenchmark/bootstrap_webdev.sh -mysql
```

5. Write your IoT-LAB username into the experiment configuration file: `~/openbenchmark/experiment_provisioner/conf.txt`
```
[iotlab-config]
user = YOUR_USER_NAME
broker = broker.mqttdashboard.com
```

6. To start the GUI, open a web browser and go to `127.0.0.1:8081`. Alternatively, you can start an experiment from the console.


## Starting an experiment via console

Workflow:

1. Resource provisioning:
```
python openbenchmark.py --action=reserve --scenario=YOUR_SCENARIO --testbed=YOUR_TESTBED
```

2. Firmware flashing:
```
python openbenchmark.py --action=flash --firmware=YOUR_FIRMWARE/REPO_URL --testbed=YOUR_TESTBED [--branch=REPO_BRANCH]
```
If `--firmware` is not specified, Provisioner will assume the default OpenWSN firmware
If parameter `--branch` is specified along with `--firmware`, Provisioner will treat the value of `--firmware` parameter as a URL of a Git repository, clone the repository, compile the source code and flash that firmware onto the nodes of the selected testbed
 
3. SUT start:
```
python openbenchmark.py --action=sut-start --scenario=YOUR_SCENARIO --testbed=YOUR_TESTBED
```

Additional actions:

- Independent Orchestrator startup:
```
python openbenchmark.py --action=orchestrator
```

- Independent OpenVisualizer startup:
```
python openbenchmark.py --action=ov --scenario=YOUR_SCENARIO --testbed=YOUR_TESTBED
```

If `--scenario` and `--testbed` parameters are not provided they will assume the default value of `demo-scenario` and `iotlab`, respectively


## Development

1. Run continuous rsync process on the host machine:
```
vagrant rsync-auto
```

2. Run Laravel Mix on the guest machine:
```
vagrant ssh
cd ~/openbenchmark/web
npm run watch
```