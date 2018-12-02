<!-- ====================================================================== -->

# Overview

This page documents the OpenBenchmark platform developed in the scope of the [SODA project](http://www.soda.ucg.ac.me/) in collaboration with [Inria-EVA](https://team.inria.fr/eva/).
OpenBenchmark automates the experimentation and network performance benchmarking on selected testbeds supporting Internet of Things devices compliant with IEEE 802.15.4 standard.
OpenBenchmark instruments the execution of an experiment in real time following the pre-defined test scenarios and collects the data to calculate the network Key Performance Indicators (KPIs) in a fully automated manner.
See [Scenarios](#test-scenarios) for the definition of test scenarios.
See [KPIs](#key-performance-indicators) for the list of Key Performance Indicators.

OpenBenchmark focuses on a wireless communication technology called 6TiSCH that enables wire-like reliability and up to a decade of device lifetime on a pair of AA batteries.
The 6TiSCH stack is defined in the [IETF 6TiSCH working group](https://datatracker.ietf.org/wg/6tisch/about/) and relies on IEEE 802.15.4 hardware.
By default, OpenBenchmark supports the [OpenWSN](https://openwsn.atlassian.net/) implementation of 6TiSCH.
See [Testbeds](#testbeds) for the list of testbeds where experimentation with OpenBenchmark is available.

<!-- ====================================================================== -->

# Terminology

- 6LoWPAN Border Router (6LBR): A router that interconnects the low-power constrained network with the rest of the Internet.
- Gateway: An entity executing application-level code that is typically co-located with the 6LBR of the network.
- System Under Test (SUT): Refers to the low-power constrained network under test as a whole, encompassing the network Gateway and low-power constrained devices.
- Implementation Under Test (IUT): Refers to the implementation of the 6TiSCH protocol stack under test.
IUT is executed on low-power devices within the testbed.

<!-- ====================================================================== -->

# Requirements

This section lists the implementation requirements that MUST be met to enable either a new

- System Under Test (SUT), or
- IEEE 802.15.4 testbed

to be used with the OpenBenchmark platform.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Implementation Under Test

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[Experiment Control Commands](#experiment-control-commands)                |        MUST
[Experiment Performance Events](#experiment-performance-events)            |        MUST

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Testbed

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[OpenTestbed Software](https://github.com/openwsn-berkeley/opentestbed)    |        MUST

<!-- ====================================================================== -->

# Test Scenarios

The goal of an OpenBenchmark *test scenario* is to capture real-life use cases of a technology in order to benchmark its performance in a setting that is relevant to the end users: companies adopting the technology for their products and their customers.
A test scenario also allows the experiment to be fully reproducible and the results easily and fairly comparable, desirable properties from the research point of view.

A test scenario is mapped to an executable logic implemented within the *Experiment Controller* component that runs on the OpenBenchmark platform concurrently with the experiment in the testbed.
Experiment Controller sends commands to the nodes in the testbed in real time to trigger a desired action: configure radio transmit power, trigger application traffic, generate interference, ...
This requires the SUT, through e.g. the network Gateway, to handle the commands originating from the Experiment Controller.
These commands can be communicated to the IUT over the serial port thanks to the OpenTestbed software components running on the testbed infrastructure but how this exactly happens is specific to the SUT.
The format of the commands from the Experiment Controller to the SUT is specified in [Experiment Control Commands](#experiment-control-commands).

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
A      |  AC         | Periodic, uniformly in [25, 35] seconds        | Yes | None
AC     |  ZC         | Periodic, uniformly in [120,140] milliseconds  | No  | None

The table below lists other relevant settings:

Setting                   | Value
------------------------- | ----------------
Coverage Requirement      |  4-6 hops
Application Payload Size  |  100 bytes

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
Bursty Sensor Payload Size  |   100 bytes
Packets per Burst           |   10

<!-- ====================================================================== -->

# Key Performance Indicators

This section lists the high-level Key Performance Indicators (KPIs) that are calculated by OpenBenchmark.
Each subsection gives a short description of the KPI and what information is needed to calculate it.

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

- the instant packet is generated at the sender, and 
- the instant the packet is received by the application layer of the destination.

To calculate latency per packet, the sender needs to add a timestamp into the packets it sends.
The receiver calculates the latency by subtracting the current time from the time indicated in the received packet.
6TiSCH networks use the Absolute Slot Number (ASN) as the timestamp.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Radio Duty Cycle

Radio Duty Cycle (RDC) refers to the ratio between 

- the time that the radio chip is powered, and 
- the duration of the measuring interval.

Each node in the network needs to log the RDC specific to it.
In 6TiSCH network, RDC can be calculated based on the number of assigned cells in the TSCH schedule and the activity within the corresponding slots.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Network Formation Time

Network Formation Time refers to the initial phase when the network is forming.
It is an important KPI from the installation point of view.
We consider 3 different phases described in the following sections.

Each node in the network needs to log the timestamp of the corresponding events.

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Synchronization Phase

Synchronization phase refers to the time interval between

- the instant when a device is booted, and
- the instant when a device gets synchronized with the network and starts duty cycling.

In 6TiSCH networks, device is synchronized upon reception of a first Enhanced Beacon (EB) frame.

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Secure Join Phase

Secure Join phase refers to the time interval between

- the instant when a device gets synchronized with the network, and
- the instant corresponding to the end of the authentication, key and parameter distribution protocol.

Once a device completes the secure join phase, it starts acting as a network node.
In 6TiSCH networks, a device completes the secure join phase upon reception and successful decryption of a Join Request message of the Constrained Join Protocol (CoJP).

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Parent Selection and Bandwidth Assignment

Parent selection and bandwidth assignment phase refers to the time interval between

- the instant corresponding to the end of the authentication, key and parameter distribution protocol, and
- the instant the node has been successfully assigned the minimum bandwidth needed for it to start sending application traffic.

For a node to complete this phase, it first needs to select a routing parent and then request bandwidth.
Once the bandwidth with the default (preferred) parent is assigned, the node can start sending application traffic.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Number of Hops Traversed per Packet

Number of hops traversed per packet refers to the number of nodes in the network that have forwarded a given packet before it reached its final destination.
Under the assumption that all nodes in the network use a common value to set the Hop Limit field in the IPv6 header when originating a packet, this metric can be calculated at the final destination node by subtracting this common value with the value of the Hop Limit field in the received packet.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Synchronization Precision

This metric refers to the average clock drift measured between a pair of nodes.
In 6TiSCH networks, nodes exchange clock drift within the MAC-layer acknowledgment frames.
Each node in the network needs to log the measured clock drift and the identifier of the peer.

<!-- ====================================================================== -->

# Experiment Control Commands

`API version: 0.0.1`

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
api_version  | Set to `0.0.1` string                         | string
token        | Random token used to match the response       | string
date         | UTC time when experiment is launched          | string
firmware     | Identifier of the IUT used                    | string
testbed      | Name of the testbed used                      | string
nodes        | List of EUI64 of nodes used in the experiment | array of strings
scenario     | Identifier of the scenario requested          | string

```
Example:
    {
        "api_version"  : "0.0.1",
        "token"        : "123",
        "date"         : "Sun Dec 2 14:41:13 UTC 2018",
        "firmware"     : "OpenWSN-42a4007db7",
        "testbed"      : "w-iLab.t"
        "nodes"        : [  "00-12-4b-00-14-b5-b6-44",
                            "00-12-4b-00-14-b5-b6-45",
                            "00-12-4b-00-14-b5-b6-46"
                         ]
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

Field name    | Description                                                                              | JSON Type
------------- | ---------------------------------------------------------------------------------------- | -------
token         | Random token used to match the response                                                  | string
source        | EUI-64 of the node that MUST send an application packet                                  | string
destination   | EUI-64 of the destination node                                                           | string
packetToken   | Array of 4 bytes that MUST be included in the payload of the packet sent                 | array
packetPayload | Variable length array that MUST be included in the packet payload after the packetToken  | array
confirmable   | Whether the packet should be acknowledged at the application layer                       | bool

```
Example:
    {
        "token"         : "123",
        "source"        : "00-12-4b-00-14-b5-b6-44",
        "destination"   : "00-12-4b-00-14-b5-b6-45",
        "packetToken"   : [124, 122, 34, 31],
        "packetPayload" : [],
        "confirmable"   : true
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

<!-- ====================================================================== -->

# Experiment Performance Events

`API version: 0.0.1`

Performance data needed to calculate the KPIs is calculated by OpenBenchmark based on the events generated by the SUT.
SUT implements a software component called Agent bridging the constrained network and the OpenBenchmark platform.
Typically, the Agent can be implemented as part of the network Gateway where hardware constraints are less pronounced compared to the rest of the low-power network such that it can subscribe to different topics, and translate events triggered by the IUT into the format expected by OpenBenchmark.

How the Agent communicates with the IUT is specific to the implementation.
For example, in the OpenWSN implementation, Gateway (i.e. OpenVisualizer component) communicates with the nodes in the network over the OpenTestbed-emulated serial port by using HDLC framing and custom commands.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event Types

This section lists the events that MUST be handled by the SUT during the execution of the experiment.
For each event, SUT MUST publish a message on an appropriate MQTT topic, enclosing the message payload specific to the event, as specified below.
Additionally, SUT MAY log the events locally by generating a log file as specified in [Log File Format](log-file-format).

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
        "event"        : "packetSent"
        "timestamp"    : 2131,
        "packetToken"   : [124, 122, 34, 31],
        "source"       : "bbbb::0012:4b00:14b5:b648",
        "destination"  : "bbbb::1",
        "hopLimit"     : 255,
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
        "source"        : "bbbb::0012:4b00:14b5:b648",
        "destination"   : "bbbb::1",
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
To ensure interoperability between the log files generated by the SUT and the Experiment Controller, that are used to calculate KPIs, this section defines the file format.

The log file format MUST follow the [JSON line](http://jsonlines.org) specification.
The first line in the file describes the experiment and is defined in [Header Format](#header-format).
All other lines are JSON strings corresponding to different events occurring in the network and adhering to the format specified above.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

### Header

First line of the log file MUST be a string representation of the JSON object with following fields, all fields being mandatory:

Field name   | Description                                                        | JSON Type
------------ | ------------------------------------------------------------------ | -------
date         | UTC time when experiment is launched                               | string
experimentId | Opaque identifier of the experiment                                | string
testbed      | Name of the testbed used                                           | string
firmware     | Identifier of the IUT used                                         | string
nodes        | List of EUI64 of nodes used in the experiment                      | array of strings
scenario     | Identifier of the scenario requested                               | string

The values of these fields are obtained from `startBenchmark` request and response messages, specified in [Start Benchmark](#start-benchmark).

<!-- ====================================================================== -->
