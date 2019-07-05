<!-- ====================================================================== -->

# Overview

This page documents the OpenBenchmark platform developed jointly by the [SODA team](http://www.soda.ucg.ac.me/) at the [University of Montenegro](https://www.ucg.ac.me) and [Inria-EVA](https://team.inria.fr/eva/).
OpenBenchmark automates the experimentation and network performance benchmarking on selected testbeds supporting Internet of Things devices compliant with IEEE 802.15.4 standard.
OpenBenchmark instruments the execution of an experiment in real time following the pre-defined test scenarios and collects the data to calculate the network Key Performance Indicators (KPIs) in a fully automated manner.


<figure>
  <p align="center"><img src="_static/overview.png">
  <figcaption>Fig. 1. Overview of OpenBenchmark functionality.</figcaption></p>
</figure>

See [Terminology](#terminology) for the definition of terms used in this documentation.
See [Scenarios](#test-scenarios) for the definition of test scenarios.
See [KPIs](#key-performance-indicators) for the list of Key Performance Indicators.
See [OpenBenchmark Architecture](#openbenchmark-architecture) for the description of the OpenBenchmark software architecture.
See [OpenBenchmark Compliance Requirements](#openbenchmark-compliance-requirements) for a summary of APIs, data formats and other relevant implementation choices.

OpenBenchmark focuses on a wireless communication technology called 6TiSCH that enables wire-like reliability and up to a decade of device lifetime on a pair of AA batteries.
The 6TiSCH stack is defined in the [IETF 6TiSCH working group](https://datatracker.ietf.org/wg/6tisch/about/) and relies on IEEE 802.15.4 hardware.
By default, OpenBenchmark supports the [OpenWSN](https://openwsn.atlassian.net/) implementation of 6TiSCH.

<!-- ====================================================================== -->

# Terminology

- 6LoWPAN Border Router (6LBR): A router that interconnects the low-power constrained network with the rest of the Internet.
- Network Gateway: An entity executing application-level code that is typically co-located with the 6LBR of the network.
- System Under Test (SUT): Refers to the low-power constrained network under test as a whole, encompassing the Network Gateway and low-power constrained devices.
- Implementation Under Test (IUT): Refers to the implementation of the 6TiSCH protocol stack under test.
IUT is executed on low-power devices within the testbed.

<!-- ====================================================================== -->

# Test Scenarios

The goal of an OpenBenchmark *test scenario* is to capture real-life use cases of a technology in order to benchmark its performance in a setting that is relevant to the end users: companies adopting the technology for their products and their customers.
A test scenario also allows the experiment to be fully reproducible and the results easily and fairly comparable, desirable properties from the research point of view.

Each scenario describes the application traffic pattern and load and the desirable coverage requirements in the number of hops in the network.
The description of a scenario is generic, with testbed-specific mappings.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Building Automation

```
Scenario Identifier: "building-automation"
```

Building automation systems typically consist of different areas and zones [RFC5867](https://datatracker.ietf.org/doc/rfc5867).
As per RFC5867, an area corresponds to a physical locale within a building, typically a room with different types of sensors to feed HVAC or lighting subsystems.
Each area has its own area controller.
Zone represents a logical partition of the system, consisted of multiple areas.
A zone has its zone controller, that is fed with data originating at the area controllers.

Within a building, there may be multiple zones depending on the specifics of the use case: multi tenants vs single tenant, separation by floors, etc.
In terms of the definition of this scenario, we consider a multi-area, single-zone building automation system.
Each area encompasses devices serving multiple subsystems like HVAC, lightning or fire detection.

The table below lists different logical roles a node in the network can have and their occurrence:

Logical role           | Occurrence       | Description
---------------------- | ---------------- | ---------------------------------------------------------------
Monitoring Sensor (MS) |  3 / area        | Sensor monitoring a physical value: temperature, flow, light
Event Sensor (ES)      |  4 / area        | Asynchronous event detection sensors: smoke, window/door reed switches
Actuator (A)           |  2 / area        | Node performing some physical action, e.g. light dimmer
Area Controller (AC)   |  1 / area        | Node controlling a given area, communicating with the zone controller.
Zone Controller (ZC)   |  1 / network     | Node controlling a given zone and potentially forwarding traffic outside the local network.


During the mapping of this scenario to a given testbed, the number of logical areas should be defined first.
Devices within a logical area should be place in close physical proximity of each other and the area controller.

Sender | Destination | Traffic pattern and load                       | Ack | Action
------ | ----------- | ---------------------------------------------- | --- | -------------
MS     |  AC         | Periodic, uniformly in [25, 35] seconds        | Yes | None
ES     |  AC         | Poisson, mean of 10 packets/hour               | Yes | Forward to ZC
AC     |  A          | Poisson, mean of 10 packets/hour               | Yes | None
A      |  AC         | Periodic, uniformly in [25, 35] seconds        | Yes | None
AC     |  ZC         | Periodic, uniformly in [120,140] milliseconds  | No  | None

The table below lists other relevant settings:

Setting                   | Value
------------------------- | ----------------
Coverage Requirement      |  4-6 hops
Application Payload Size  |  80 bytes

The coverage requirement is an approximation based on RFC5867 deployment requirements.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Home Automation

<!-- paper "Performance Comparison of the RPL and LOADng Routing Protocols in a Home Automation Scenario" -->

```
Scenario Identifier: "home-automation"
```

The scenario has been derived from the requirements discussed in [RFC5826](https://datatracker.ietf.org/doc/rfc5826/) and [WCNC13PERFORMANCE](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6554867).

The table below lists different logical roles a node in the network can have:

Logical role           | Occurrence       | Description
---------------------- | ---------------- | ---------------------------------------------------------------
Monitoring Sensor (MS) |  49%             | Sensor monitoring a physical value, e.g. temperature, humidity
Event Sensor (ES)      |  21%             | Asynchronous event detection sensors, e.g. human presence
Actuator (A)           |  30%             | Node performing some physical action, e.g. light dimmer, relay
Control Unit (CU)      |  1/network       | Central unit controlling the automation system

The traffic patterns for different logical roles are given in the table below:

Sender | Destination | Traffic pattern and load                 | Ack | Action
------ | ----------- | ---------------------------------------- | --- | -------------
MS     |  CU         | Periodic, uniformly in [3, 5] minutes    | No  | None
ES     |  CU         | Poisson, mean of 10 packets/hour         | Yes | Trigger burst
A      |  CU         | Periodic, uniformly in [3, 5] minutes    | Yes | None 
CU     |  multiple A | Poisson, mean of 10 5-packet bursts/hour | Yes | None

The table below lists other relevant settings:

Setting                   | Value
------------------------- | ----------------
Coverage Requirement      |   2-4 hops
Application Payload Size  |   10 bytes

The coverage requirement is based on the emulated topology of a smart house given in [WCNC13PERFORMANCE](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6554867).
Application payload size is based on the requirements provided in RFC5826.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Industrial Monitoring

<!-- RFC5673 Section 3.1 -->

```
Scenario Identifier: "industrial-monitoring"
```

The scenario has been derived from the requirements discussed in [RFC5673](https://datatracker.ietf.org/doc/rfc5673/).

The table below lists different logical roles a node in the network can have:

Logical role           | Occurrence       | Description
---------------------- | ---------------- | ---------------------------------------------------------------
Sensor (S)             |  90%             | Traditional monitoring sensor: temperature, pressure, fluid flow, ...
Bursty Sensor (BS)     |  10%             | Monitoring sensor transmitting large quantities of data: e.g. vibration monitor
Gateway (G)            |  1/network       | Application gateway

The traffic patterns for different logical roles are given in the table below:

Sender | Destination | Traffic pattern and load                 | Ack | Action
------ | ----------- | ---------------------------------------- | --- | -------------
S      |  G          | Periodic, uniformly in [1, 60] seconds   | No  | None
BS     |  G          | Periodic, uniformly in [1, 60] minutes   | No  | None

The table below lists other relevant settings:

Setting                     | Value
--------------------------- | ----------------
Coverage Requirement        |   5-10 hops
Sensor Payload Size         |   10 bytes
Bursty Sensor Payload Size  |   80 bytes
Packets per Burst           |   10

<!-- ====================================================================== -->

# Key Performance Indicators

This section lists the high-level Key Performance Indicators (KPIs).
Each subsection gives a short description of the KPI and what information is needed to calculate it.
The first four presented KPIs are relevant for the industry stakeholders, while the latter KPIs are also useful from the research point of view.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Reliability

Reliability refers to the ratio between packets received and packets sent by the application.
Therefore, this KPI refers to the end-to-end reliability.
A packet may fail a transmission on a given link and be later retransmitted.
However, failed packet transmission on a given link does not influence the end-to-end reliability if the packet eventually arrives at the destination.

To calculate end-to-end reliability, each sender node needs to log the destination and the number of application packets sent.
Each receiver node needs to log the number of application packets received and the sender.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Latency

Latency refers to the time interval between

- the instant packet is generated by the applicaton layer at the sender, and
- the instant the packet is received by the application layer of the destination.

To calculate latency per packet, the sender needs to add a timestamp into the packets it sends.
The receiver calculates the latency by subtracting the current time from the time indicated in the received packet.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Radio Duty Cycle

Radio Duty Cycle (RDC) refers to the ratio between 

- the time that the radio chip is powered, and 
- the duration of the measurement period.

Each node in the network needs to log the RDC specific to it.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Number of Hops Traversed per Packet

A research relevant KPI, number of hops traversed per packet refers to the number of nodes in the network that have forwarded a given packet before it reached its final destination.
Under the assumption that all nodes in the network use a common value to set the Hop Limit field in the IPv6 header when originating a packet, this metric can be calculated at the final destination node by subtracting this common value with the value of the Hop Limit field in the received packet.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Synchronization Precision

A research relevant KPI, synchronization precision refers to the average clock drift measured between a pair of nodes.
In 6TiSCH networks, nodes exchange clock drift within the MAC-layer acknowledgment frames.
Each node in the network needs to log the measured clock drift and the identifier of the peer.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Network Formation Time

Network Formation Time refers to the initial phase when the network is forming.
It is an important KPI from the installation point of view.
To aid during the research process, we consider 3 different subphases of the network formation time described in the following.

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Synchronization Phase Time

Synchronization phase time refers to the time interval between

- the instant when a device is booted, and
- the instant when a device gets synchronized with the network and starts duty cycling.

In 6TiSCH networks, device is synchronized upon reception of a first Enhanced Beacon (EB) frame.

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Secure Join Phase Time

Secure Join phase time refers to the time interval between

- the instant when a device gets synchronized with the network, and
- the instant corresponding to the end of the authentication, key and parameter distribution protocol.

Once a device completes the secure join phase, it starts acting as a network node.
In 6TiSCH networks, a device completes the secure join phase upon reception and successful decryption of a Join Request message of the Constrained Join Protocol (CoJP).

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Parent Selection and Bandwidth Assignment Phase Time

Parent selection and bandwidth assignment phase time refers to the time interval between

- the instant corresponding to the end of the authentication, key and parameter distribution protocol, and
- the instant the node has been successfully assigned the minimum bandwidth needed for it to start sending application traffic.

For a node to complete this phase, it first needs to select a routing parent and then request bandwidth.
Once the bandwidth with the default (preferred) parent is assigned, the node can start sending application traffic.

<!-- ====================================================================== -->

# OpenBenchmark Architecture

<figure>
  <p align="center"><img src="_static/architecture.png">
  <figcaption>Fig. 2. OpenBenchmark software architecture. SUT is composed of IUTs and the Network Gateway.</figcaption></p>
</figure>

The OpenBenchmark consists of following components:

- Agent: A component running at the Network Gateway side, translating OpenBenchmark commands to the format that the IUT implements, and also converting performance data from the IUT to the format expected by OpenBenchmark.
- Experiment Provisioner. A component in charge of testbed node reservation, firmware flashing, and launching the necessary software components that run at testbed infrastructure side. These include the Network Gateway, and the serial port emulation software (OpenTestbed) that make the testbed nodes appear to the Network Gateway as if they were physically connected.
- Experiment Orchestrator. A component in charge of orchestrating the SUT according to the selected test scenario.
The Experiment Orchestrator interprets the test scenario files and instruments the experiment based on the interpreted data.
- Performance Event Handler. A component in charge of handling performance data events coming from the SUT.
Based on these events, Performance Event Handler generates the experiment data sets and calculates the KPIs.
- Web server. A Laravel-based (PHP) backend and Vue.js-based frontend allowing the user to access the OpenBenchmark platform through a graphical interface.
The backend serves as a bridge between the frontend and the rest of the OpenBenchmark components that are implemented in Python.
The backend provides a RESTful API that enables the use of OpenBenchmark by 3$^{rd}$ party applications.

Apart from developing new software components that will fully automate the benchmarking process, OpenBenchmark leverages and complements the existing effort in the open-source community to enable benchmarking of the pilot implementation of 6TiSCH: the OpenWSN project.
These projects include:

- OpenTestbed project: An open-source solution running on the testbed infrastructure that allows the communication with the firmware implementation executing in the testbed to be accessed as if it were running locally on the user’s machine.
Essentially, OpenTestbed emulates the serial port connectivity over the MQTT protocol and allows the user to remotely flash the firmware on testbed devices.
As part of the SODA effort, we extended the support of OpenTestbed to IoT-lab Saclay site, and our partners from iMec extended its support for w.iLab.t testbed.
- OpenVisualizer project: An open-source implementation of a 6TiSCH gateway compatible with the OpenWSN firmware project.
As part of the SODA effort, together with our external partners from Inria, we extended the OpenVisualizer to support the local execution on user’s premises while the 6TiSCH nodes are in testbed, by using the OpenTestbed functionalities.

<!-- ====================================================================== -->

# OpenBenchmark Compliance Requirements

This section lists the implementation requirements that MUST be met to enable either a new

- System Under Test (SUT), or
- IEEE 802.15.4 testbed

to be used with the OpenBenchmark platform.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Implementation Under Test

Implementation Under Test (IUT) communicates with the OpenBenchmark platform through the Agent component whose implementation is specific to the IUT.

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[Experiment Control Commands API](#experiment-control-commands-api)        |        MUST
[Experiment Performance Events API](#experiment-performance-events-api)    |        MUST

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Testbed

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[OpenTestbed Software](https://github.com/openwsn-berkeley/opentestbed)    |        MUST

<!-- ====================================================================== -->

# Experiment Control Commands API

`API version: "0.0.1"`

This section lists the commands that MUST be handled by the SUT, as well as the behavior of the SUT when the Agent is first initialized.
Commands are carried over MQTT in a request-response fashion.
Each command is published on a separate topic, as specified below.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Start Benchmark

*Description:* This command is sent by the SUT to the Experiment Controller before an experiment is launched.
It allows the SUT to obtain an experiment identifier needed to publish the performance data.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Request

MQTT topic:

```
    openbenchmark/command/startBenchmark
```

Payload of the request MUST be a JSON object with following fields:

Field name   | Description                                   | JSON Type
------------ | --------------------------------------------- | -------
api_version  | Set to implemented API version                | string
token        | Random token used to match the response       | string
date         | RFC2822 time when experiment is launched      | string
firmware     | [IUT identifier](#supported-iuts), with a custom suffix | string
testbed      | [Testbed identifier](#supported-testbeds)     | string
nodes        | Map of testbed hosts and nodes' EUI64 address | object
scenario     | Identifier of the scenario requested          | string

```
Example:
    {
        "api_version"  : "0.0.1",
        "token"        : "123",
        "date"         : "Wed, 06 Feb 2019 17:46:55 +0100",
        "firmware"     : "OpenWSN-42a4007db7",
        "testbed"      : "wilab"
        "nodes"        : {
                            "nuc0-35": "00-12-4b-00-14-b5-b6-44",
                            "nuc0-36": "00-12-4b-00-14-b5-b6-45",
                            "nuc0-37": "00-12-4b-00-14-b5-b6-46"
                         }
        "scenario"     : "building-automation"
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Response

```
topic:
    openbenchmark/response/startBenchmark
```
Payload of the response MUST be a JSON object with following fields:

Field name   | Description                             | JSON Type | Presence Requirement
------------ | --------------------------------------- | --------- | ---------------------
token        | Token echoed from the request           | string    | MUST
success      | Indicator of success                    | bool      | MUST
experimentId | Opaque identifier of the experiment     | string    | MAY (if success)

```
Example:
    {
        "token"        : "123",
        "success"      : true,
        "experimentId" : "1880b5363d7"
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Echo

*Description:* This command can be sent by either party, the Experiment Controller or the SUT, to check the connectivity of the other party.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Request

MQTT topic:

```
    openbenchmark/experimentId/EXPERIMENTID/command/echo
```

EXPERIMENTID MUST be set to the value obtained from the `startBenchmark` response.

Payload of the request MUST be a JSON object with following fields:

Field name   | Description                                                        | JSON Type
------------ | ------------------------------------------------------------------ | -------
token        | Random token used to match the response                            | string

```
Example:
    {
        "token"        : "123",
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Response

```
topic:
    openbenchmark/experimentId/EXPERIMENTID/response/echo
```
Payload of the response MUST be a JSON object with following fields:

Field name   | Description                             | JSON Type | Presence Requirement
------------ | --------------------------------------- | --------- | ---------------------
token        | Token echoed from the request           | string    | MUST
success      | Indicator of success                    | bool      | MUST

```
Example:
    {
        "token"        : "123",
        "success"      : true,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Send Packet

*Description:* This command is sent by the Experiment Controller to the SUT to trigger the sending of an application packet.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Request

MQTT topic:

```
    openbenchmark/experimentId/EXPERIMENTID/command/sendPacket
```

EXPERIMENTID MUST be set to the value obtained from the `startBenchmark` response.

Payload of the request MUST be a JSON object with following fields:

Field name       | Description                                                                                                           | JSON Type
---------------- | --------------------------------------------------------------------------------------------------------------------- | -------
token            | Random token used to match the response                                                                               | string
source           | EUI-64 of the node that MUST send an application packet                                                               | string
destination      | EUI-64 of the destination node                                                                                        | string
packetsInBurst   | Number of packets in the burst that MUST be generated consequently by the node                                        | integer
packetToken      | Array of 5 bytes, MUST be included in the payload. First byte of the included token MUST correspond to packet index in the burst | array
packetPayloadLen | Length of the dummy payload that MUST be included in the packet                                                       | integer
confirmable      | Whether the packet should be acknowledged at the application layer                                                    | bool

```
Example:
    {
        "token"            : "123",
        "source"           : "00-12-4b-00-14-b5-b6-44",
        "destination"      : "00-12-4b-00-14-b5-b6-45",
        "packetsInBurst"   : 1
        "packetToken"      : [00, 124, 122, 34, 31],
        "packetPayloadLen" : 5,
        "confirmable"      : true
    }

```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Response

```
topic:
    openbenchmark/experimentId/EXPERIMENTID/response/sendPacket
```
Payload of the response MUST be a JSON object with following fields:

Field name   | Description                             | JSON Type | Presence Requirement
------------ | --------------------------------------- | --------- | ---------------------
token        | Token echoed from the request           | string    | MUST
success      | Indicator of success                    | bool      | MUST

```
Example:
    {
        "token"        : "123",
        "success"      : true,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Configure Transmit Power

*Description:* This command is sent by the Experiment Controller to the SUT to configure the transmit power at a given node in the testbed.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Request

MQTT topic:

```
    openbenchmark/experimentId/EXPERIMENTID/command/configureTransmitPower
```

EXPERIMENTID MUST be set to the value obtained from the `startBenchmark` response.

Payload of the request MUST be a JSON object with following fields:

Field name   | Description                                                        | JSON Type
------------ | ------------------------------------------------------------------ | -------
token        | Random token used to match the response                            | string
source       | EUI-64 of the node that MUST be configured                         | string
power        | Transmit power value in dBm                                        | integer

```
Example:
    {
        "token"        : "123",
        "source"       : "00-12-4b-00-14-b5-b6-44",
        "power"        : 0,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Response

```
topic:
    openbenchmark/experimentId/EXPERIMENTID/response/configureTransmitPower
```
Payload of the response MUST be a JSON object with following fields:

Field name   | Description                             | JSON Type | Presence Requirement
------------ | --------------------------------------- | --------- | ---------------------
token        | Token echoed from the request           | string    | MUST
success      | Indicator of success                    | bool      | MUST

```
Example:
    {
        "token"        : "123",
        "success"      : true,
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Trigger Network Formation

*Description:* This command is sent by the Experiment Controller to the SUT to trigger the formation of the network, and so the experiment.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Request

MQTT topic:

```
    openbenchmark/experimentId/EXPERIMENTID/command/triggerNetworkFormation
```

EXPERIMENTID MUST be set to the value obtained from the `startBenchmark` response.

Payload of the request MUST be a JSON object with following fields:

Field name   | Description                                                        | JSON Type
------------ | ------------------------------------------------------------------ | -------
token        | Random token used to match the response                            | string
source       | EUI-64 of the node that MUST act as the coordinator of the network | string

```
Example:
    {
        "token"        : "123",
        "source"       : "00-12-4b-00-14-b5-b6-44",
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Response

```
topic:
    openbenchmark/experimentId/EXPERIMENTID/response/triggerNetworkFormation
```
Payload of the response MUST be a JSON object with following fields:

Field name   | Description                             | JSON Type | Presence Requirement
------------ | --------------------------------------- | --------- | ---------------------
token        | Token echoed from the request           | string    | MUST
success      | Indicator of success                    | bool      | MUST

```
Example:
    {
        "token"        : "123",
        "success"      : true,
    }
```
<!-- ====================================================================== -->

# Experiment Performance Events API

`API version: 0.0.1`

Performance data needed to calculate the KPIs is calculated by OpenBenchmark based on the events generated by the SUT.
SUT implements a software component called Agent bridging the constrained network and the OpenBenchmark platform.
Typically, the Agent can be implemented as part of the Network Gateway where hardware constraints are less pronounced compared to the rest of the low-power network such that it can subscribe to different topics, and translate events triggered by the IUT into the format expected by OpenBenchmark.

How the Agent communicates with the IUT is specific to the implementation.
For example, in the OpenWSN implementation, Network Gateway (i.e. OpenVisualizer component) communicates with the nodes in the network over the OpenTestbed-emulated serial port by using HDLC framing and custom commands.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event Types

This section lists the events that MUST be handled by the SUT during the execution of the experiment.
For each event, SUT MUST publish a message on an appropriate MQTT topic, enclosing the message payload specific to the event, as specified below.
Additionally, SUT MAY log the events locally by generating a log file as specified in [Log File Format](#log-file-format).

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Topic

MQTT topic used for all events specified in this section MUST have the following format:

```
    openbenchmark/experimentId/EXPERIMENTID/nodeId/EUI64/performanceData
```

EXPERIMENTID MUST be set to a string, opaque to the SUT, that is returned by the Experiment Controller at the beginning of the experiment.
EUI64 MUST be set to the Extended Unique Identifier of the device originating the event.
Each byte of the EUI64 MUST be encoded as a hex integer and delimited with a '-' character.

Example of EUI64:
```
    00-12-4b-00-14-b5-b6-48
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Message Payload

Message payload MUST be encoded as a JSON object.

The table below summarizes different fields that may appear in the JSON object.
Normative requirements of each field are specific to the event and are given in the following sections.

Field name   | Description                                 | Value guidance                                   | JSON Type
------------ | ------------------------------------------- | ------------------------------------------------ | ---------
event        | Name of the event                           | See event definition sections                    | string
timestamp    | Timestamp when the event is triggered       | Current ASN in the network                       | integer
packetToken  | Unique token used to match packets          | Received from `sendPacket` command request       | array
source       | Source IPv6 address of the packet           | IPv6 address in RFC4291 format                   | string
destination  | Destination IPv6 address of the packet      | IPv6 address in RFC4291 format                   | string
hopLimit     | Used to calculate number of traversed hops  | Value of the Hop Limit field in the IPv6 header  | integer
dutyCycle    | Local measurement of radio duty cycle       | Percentage                                       | float
clockDrift   | Local measurement of clock drift            | Drift in microseconds                            | float

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Common Fields

Field name | Event | Presence Requirement
---------- | ----- | ---------------------
event      | all   | MUST
source     | all   | MUST
timestamp  | all   | MUST

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Event: Packet Sent

*Description:* This event corresponds to the sending of an application packet.
The values in the payload MUST correspond to the instant when the application code generated a packet.

Value of the event field MUST be set to:

```
    "packetSent"
```
The table below lists which fields need to be included in the message payload.

Field name  | Event        | Presence Requirement
----------- | ------------ | -----------
packetToken | packetSent   | MUST
source      | packetSent   | MUST
destination | packetSent   | MUST
hopLimit    | packetSent   | MUST


```
Example:
    {
        "event"            : "packetSent"
        "timestamp"        : 2131,
        "packetToken"      : [124, 122, 34, 31],
        "source"           : "00-12-4b-00-14-b5-b6-44",
        "destination"      : "00-12-4b-00-14-b5-b6-45",
        "hopLimit"         : 255,
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Packet Received

*Description:* This event corresponds to the reception of an application packet.
The values in the payload MUST correspond to the instant when the application code received a packet.

Value of the event field MUST be set to:

```
    "packetReceived"
```

The table below lists which fields need to be included in the message payload.

Field name  | Event             | Presence Requirement
----------- | ----------------- | -----------
packetToken | packetReceived    | MUST
source      | packetReceived    | MUST
destination | packetReceived    | MUST
hopLimit    | packetReceived    | MUST


```
Example:
    {
        "event"         : "packetReceived"
        "timestamp"     : 2151,
        "packetToken"   : [124, 122, 34, 31],
        "source"        : "00-12-4b-00-14-b5-b6-45",
        "destination"   : "00-12-4b-00-14-b5-b6-44",
        "hopLimit"      : 252,
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Network Formation Completed

*Description*: This event corresponds to the completion of the network formation phase.
The event MUST be generated by each node when it is ready to start sending application traffic.

Value of the event field MUST be set to:

```
    "networkFormationCompleted"
```

There are no additional fields other than those specified in [Common Fields](#common-fields).

```
Example:
    {
        "event"         : "networkFormationCompleted"
        "timestamp"     : 57,
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Synchronization Completed

*Description*: This event corresponds to the initial synchronization of the device with the network.
The event MUST be generated by each device once it is synchronized.

Value of the event field MUST be set to:

```
    "synchronizationCompleted"
```

There are no additional fields other than those specified in [Common Fields](#common-fields).

```
Example:
    {
        "event"         : "synchronizationCompleted"
        "timestamp"     : 15,
    }
```
<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Secure Join Completed

*Description*: This event corresponds to the completion of the secure join process.
The event MUST be generated by each device once it completes the Constrained Join Protocol (CoJP).

Value of the event field MUST be set to:

```
    "secureJoinCompleted"
```

There are no additional fields other than those specified in [Common Fields](#common-fields).

```
Example:
    {
        "event"         : "secureJoinCompleted"
        "timestamp"     : 30,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Bandwidth Assigned

*Description*: This event corresponds to the assignment of the minimal bandwidth required by a node to start sending application traffic.
The event MUST be generated by each node when it can start sending application traffic.

Value of the event field MUST be set to:

```
    "bandwidthAssigned"
```

There are no additional fields other than those specified in [Common Fields](#common-fields).

```
Example:
    {
        "event"         : "bandwidthAssigned"
        "timestamp"     : 45,
    }
```

In 6TiSCH networks, this event corresponds with the `networkFormationCompleted` event.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Radio Duty Cycle Measurement

*Description:* This event corresponds to a measurement of the radio duty cycle.
This event MUST be generated periodically by each node in the network with a period not exceeding 5 minutes.

Value of the event field MUST be set to:

```
    "radioDutyCycleMeasurement"
```

The table below lists which fields need to be included in the message payload.

Field name  | Event                       | Presence Requirement
----------- | --------------------------- | -----------
dutyCycle   | radioDutyCycleMeasurement   | MUST


```
Example:
    {
        "event"         : "radioDutyCycleMeasurement"
        "timestamp"     : 2151,
        "dutyCycle"     : 0.59,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event: Clock Drift Measurement

*Description:* This event corresponds to a measurement of a clock drift of a node with its routing parent.
This event MUST be generated periodically by each node in the network with a period not exceeding 5 minutes.

Value of the event field MUST be set to:

```
    clockDriftMeasurement
```

The table below lists which fields need to be included in the message payload.

Field name  | Event                   | Presence Requirement
----------- | ----------------------- | -----------
clockDrift  | clockDriftMeasurement   | MUST


```
Example:
    {
        "event"         : "clockDriftMeasurement"
        "timestamp"     : 2151,
        "clockDrift"    : 156.25,
    }
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Log File Format

Requirements specified in this section are OPTIONAL for implementation by the SUT.
Apart from publishing the data relevant to an event on MQTT, an SUT may also store it locally in a log file.
To ensure interoperability between the log files generated by the SUT and the Performance Event Handler, that are used to calculate KPIs, this section defines the file format.

The log file format MUST follow the [JSON line](http://jsonlines.org) specification.
The first line in the file describes the experiment and is defined in [Header Format](#header-format).
All other lines are JSON strings corresponding to different events occurring in the network and adhering to the format specified above.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Header

First line of the log file MUST be a string representation of the JSON object with following fields:

Field name   | Presence Requirement
------------ | ---------------------
date         | MUST
experimentId | MUST
testbed      | MUST
firmware     | MUST
nodes        | MUST
scenario     | MUST

The values of these fields follow the format specified in [Start Benchmark](#start-benchmark).

<!-- ====================================================================== -->

# RESTful API

`API version: "0.0.1"`

This section lists HTTP routes that can be used to trigger an experiment on OpenBenchmark platform without having to access the GUI. This method of access is particularly useful for machine users and CI systems. The actions which assume a longer process can be monitored in real-time via the following MQTT topics:

Data                | Topic                         | Description
------------------- | ------------------------------|------------------------------------------------------------- 
step-notifications  | openbenchmark/1/notifications | Notifications indicating a completed step/action                
debug-notifications | openbenchmark/1/debug         | Debugging data provided by the OpenBenchmark core                
kpi-data            | openbenchmark/1/kpi           | Calculated KPIs                                             
raw-data            | openbenchmark/1/raw           | Raw data acquired from the SUT used for calculating the KPIs


<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## General data retreival

*Description:* This route is used for fetching all the information about available scenarios and testbeds. Additionally, the route may be used to retrieve the information about the structure of a particular scenario

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

`GET`

```
    http://127.0.0.1/api/general/{param}/{scenario}/{testbed}
```

Field name   | Description                                                                       | Type                  | Values
------------ | ----------------------------------------------------------------------------------| ----------------------| --------------------------
param        | Indicates what type of information is going to be fetched                         | string                | scenarios, testbeds, nodes
scenario     | Used with `param=nodes` to indicate which scenario should the data be fetched for | string                |
testbed      | Used with `param=nodes` to indicate which testbed should the data be fetched for  | string                |

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Experiment startup

*Description:* This set of routes is used for completing every step of the experiment startup workflow. All of the routes share a similar response JSON:

```
Response:
{
    "http_code": 200,
    "message": {
        "action": "reserve",
        "broker": "broker.mqttdashboard.com",
        "monitoring-topics": {
            "step-notifications"  : "openbenchmark/1/notifications",
            "debug-notifications" : "openbenchmark/1/debug",
            "kpi-data"            : "openbenchmark/1/kpi",
            "raw-data"            : "openbenchmark/1/raw"
        }
    }
}

```  

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Node reservation

*Description:* This route is used to reserve the resources on a selected testbed for a selected scenario

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

`GET`

```
    http://127.0.0.1/api/reserve-nodes/{scenario}/{testbed}
```

Field name   | Description     | Type                  
------------ | ----------------| -------
scenario     | Chosen scenario | string                
testbed      | Chosen testbed  | string

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Starting SUT and Experiment Orchestrator

*Description:* This route is used for starting SUT and 

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

`GET`

```
    http://127.0.0.1/api/start-ov/{scenario}/{testbed}/{simulator}
```

Field name   | Description                             | Type                  
------------ | ----------------------------------------| -------
scenario     | Chosen scenario                         | string                
testbed      | Chosen testbed                          | string
simulator    | Start an experiment with SUT simulator  | string/optional

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Experiment termination

*Description:* This route is used for terminating an ongoing experiment

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

`GET`

```
    http://127.0.0.1/api/exp-terminate
```

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Experiment repeatability

*Description:* This set of routes is used for storing and retreiving the information about a previously executed experiment, in order to allow repeatability

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Fetch experiment configuration

`GET`

```
    http://127.0.0.1/api/experiment/{experiment_token}
```

Field name         | Description                     | Type   
------------------ | --------------------------------| -------
experiment_token   | A unique experiment identifier  | string               

```
Response:
{
    "http_code": 200,
    "message": {
        "experiment_token": "ab356ol4",
        "scenario": "demo-scenario",
        "testbed": "iotlab",
        "firmware": "default",
        "created_at": "2019-05-20 15:20:05",
        "updated_at": "2019-05-20 15:20:05"
    }
}

```   

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Store experiment configuration

`POST`

```
    http://127.0.0.1/api/store
```

Field name        | Description                     | Type   
----------------- | --------------------------------| -------
scenario          | Selected scenario               | string
testbed           | Selected testbed                | string   

```
Response:
{
    "http_code": 200,
    "message": {
        "experiment_token": "ab356ol4",
        "scenario": "demo-scenario",
        "testbed": "iotlab",
        "firmware": "default",
        "created_at": "2019-05-20 15:20:05",
        "updated_at": "2019-05-20 15:20:05"
    }
}

```         
<!-- ====================================================================== -->

# Experiment Provisioner

Experiment Provisioner is a part of the Python core which communicates with the testbed, provisions the resources, and triggers the Experiment Orchestrator and SUT. All the calls of the RESTful API (which are used by the GUI as well), infact, trigger one of the actions of the Experiment Provisioner. Experiment Provisioner may be started manually from the console, by invoking the entry point Python script in its directory (`python ~/openbenchmark/experiment_provisioner/main.py`) with the following parameters:

Parameter name    | Type    | Choices                                                                    | Required  | Default  
----------------- | --------| ---------------------------------------------------------------------------| ----------| --------
--action          | string  | check, reserve, terminate, flash, ov-start                           | true      | -
--scenario        | string  | demo-scenario, building-automation, home-automation, industrial-monitoring | false     | demo-scenario
--testbed         | string  | iotlab, wilab                                                              | false     | iotlab
--firmware        | string  | - 																		 | false     | 03oos_openwsn_prog
--user-id         | string  | -																			 | true      | -
--simulator       | boolean | -																			 | false     | false


Parameter name    | Description
----------------- | ----------------------------------------------------------------------------------------------------------------------
--action          | Type of action the provisioner needs to perform: experiment check, resource reservation, experiment termination, firmware flashing (via OTBox), SUT and Orchestrator startup
--scenario        | Selected scenario
--testbed         | Selected testbed
--firmware        | Selected firmware
--user-id         | OpenBenchmark user account ID (since the work on OpenBenchmark user management is still in progress, any generic ID may be used for now)
--simulator       | Indicates whether the provisioner should start the SUT or simulate its events

<!-- ====================================================================== -->

# Test Scenario Implementation

A test scenario is defined in a JSON config file.
The JSON file consists of a generic part describing the scenario "instance", and a testbed-specific part describing how the instance is mapped to a specific testbed through physical nodes to use and their transmission power.
Application traffic is encoded as an array of objects carrying the time instants relative to the beginning of the experiment when a node is instructed to send an application packet.
These time instants follow the distributions discussed in [Test Scenarios](#test-scenarios).
The following listing depicts a JSON snippet describing the generic building automation test scenario instance.

```

{
    "identifier": "building-automation",
    "duration_min": 180,
    "number_of_nodes": 40,
    "payload_size": 80,
    "nodes": {
        "openbenchmark00": {
            "role": "zone-controller",
            "area": 0,
            "traffic_sending_points": {}
        },
        "openbenchmark01": {
            "role": "monitoring-sensor",
            "area": 0,
            "traffic_sending_points": [
                {
                    "time_sec": 25.708,
                    "destination": "openbenchmark26",
                    "confirmable": true
                },
                {
                    "time_sec": 57.885,
                    "destination": "openbenchmark06",
                    "confirmable": true
                },
                {
                    "time_sec": 87.179,
                    "destination": "openbenchmark06",
                    "confirmable": true
                },
                ...
        },
        "openbenchmark04": {
            "role": "actuator",
            "area": 0,
            "traffic_sending_points": [
                {
                    "time_sec": 34.606,
                    "destination": "openbenchmark36",
                    "confirmable": true
                },
                {
                    "time_sec": 60.302,
                    "destination": "openbenchmark16",
                    "confirmable": true
                },
        },
        ...
    }
}
```

An example scenario mapping to the wilab.t testbed is presented below with node_id field denoting wilab.t-specific testbed host identifier.

```
{
    "openbenchmark00": {
        "node_id": "nuc10-41-0",
        "transmission_power_dbm": -5
    },
    "openbenchmark01": {
        "node_id": "nuc10-13-0",
        "transmission_power_dbm": -5
    },
    "openbenchmark02": {
        "node_id": "nuc10-13-1",
        "transmission_power_dbm": -5
    },
    "openbenchmark03": {
        "node_id": "nuc10-36-0",
        "transmission_power_dbm": -5
    },
    "openbenchmark04": {
        "node_id": "nuc10-36-1",
        "transmission_power_dbm": -5
    },
    "openbenchmark05": {
        "node_id": "nuc10-35-0",
        "transmission_power_dbm": -5
    },
    "openbenchmark06": {
        "node_id": "nuc10-35-1",
        "transmission_power_dbm": -5
    },
    "openbenchmark07": {
        "node_id": "nuc10-34-0",
        "transmission_power_dbm": -5
    },
    "openbenchmark08": {
        "node_id": "nuc10-34-1",
        "transmission_power_dbm": -5
    },
    ...
}
```

The following figure depicts the mapping of the building-automation scenario to wilab resources, and the separation of logical areas:

<figure>
  <p align="center"><img src="_static/scenario-building-wilabt.png">
  <figcaption>Fig. 3. Mapping of building-automation scenario to wilab testbed.</figcaption></p>
</figure>

The mapping of the same scenario to iotlab Saclay site is presented below:

<figure>
  <p align="center"><img src="_static/scenario-building-iotlab.png">
  <figcaption>Fig. 4. Mapping of building-automation scenario to iotlab testbed, Saclay site.</figcaption></p>
</figure>

The reader is referred to the [OpenBenchmark github repository](https://github.com/openwsn-berkeley/openbenchmark) for the complete specification of scenarios.

<!-- ====================================================================== -->

# Supported IUTs

Name                                                |  Identifier
--------------------------------------------------- | ------------
[OpenWSN](http://www.openwsn.org/)                  | "openwsn"

<!-- ====================================================================== -->

# Supported Testbeds

Name                                                |  Identifier
--------------------------------------------------- | ------------
[IoT-LAB](https://www.iot-lab.info/)                | "iotlab"
[w-iLab.t](https://doc.ilabt.imec.be/ilabt/wilab/)  | "wilab"

<!-- ====================================================================== -->

