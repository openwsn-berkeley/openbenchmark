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

# Requirements

This section lists the implementation requirements that MUST be met to enable either a new

- Implementation Under Test (IUT), or
- IEEE 802.15.4 testbed

to be used with the OpenBenchmark infrastructure.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Implementation Under Test

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[Experiment Control Commands](#experiment-control-commands)                |        MUST
[Experiment Performance Data Format](#experiment-performance-data-format)  |        MUST

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Testbed

Specification                                                              | Requirement Level
-------------------------------------------------------------------------- | -----------------
[OpenTestbed Software](https://github.com/openwsn-berkeley/opentestbed)    |        MUST

<!-- ====================================================================== -->

# Test Scenarios

The goal of an OpenBenchmark *test scenario* is to capture real-life use cases of a technology in order to benchmark its performance in a setting that is relevant to the end users: companies adopting the technology for their products and their customers.
A test scenario also allows the experiment to be fully reproducible and the results easily and fairly comparable, desirable properties from the research point of view.

A test scenario is mapped to an executable logic implemented within the *Experiment Controller* component that runs on OpenBenchmark infrastructure concurrently with the experiment in the testbed.
Experiment Controller sends commands to the nodes in the testbed in real time to trigger a desired action: configure radio transmit power, trigger application traffic, generate interference, ...
This requires the IUT to handle the commands originating from the Experiment Controller.
These commands can be communicated to the IUT over the serial port thanks to the OpenTestbed software components running on the testbed infrastructure.
The format of the commands is specified in [Experiment Control Commands](#experiment-control-commands).

Each scenario describes the application traffic pattern and load and the desirable coverage requirements in the number of hops in the network.
The description of a scenario is generic, with testbed-specific mappings.

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Building Automation

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
In 6TiSCH networks, a device completes the secure join phase upon reception and successful decryption of a Join Response message.

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

<!-- ====================================================================== -->

# Experiment Performance Data Format

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## File Format

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Header

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event Types

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Event Definitions

<!-- ====================================================================== -->

# Testbeds

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## w-iLab.t

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## IoT-lab Saclay

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## OpenTestbed

