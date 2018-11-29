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
If you would like to enable OpenBenchmark to benchmark your 6TiSCH implementation, your implementation needs to log or publish in real-time the experiment data following the [Data Format](#data-format) specification.

See [Testbeds](#testbeds) for the list of testbeds where experimentation with OpenBenchmark is available.
To enable OpenBenchmark to run on your IEEE 802.15.4-compliant testbed, we require [OpenTestbed](https://github.com/openwsn-berkeley/opentestbed) software to be ported to your testbed infrastructure.

<!-- ====================================================================== -->

# Test Scenarios

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Smart Home

<!-- paper "Performance Comparison of the RPL and LOADng Routing Protocols in a Home Automation Scenario" -->

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Smart Factory

<!-- RFC5673 Section 3.1 -->

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Scenario C

<!-- ====================================================================== -->

# Key Performance Indicators

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Reliability

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Latency

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Radio Duty Cycle

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Network Formation Time

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Synchronization

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Secure Join

<!-- . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  -->

### Bandwidth Assignment

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Number of Hops Traversed per Packet

<!-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  -->

## Synchronization Precision

<!-- ====================================================================== -->

# Data Format

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

