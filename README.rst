Latency Monitor plugin
======================
Simple `Server Density`_ agent v2 plugin for monitoring network latency and packet loss, inspired by SmokePing_.

Installing
==================
if no custom plugins installed:
- create /etc/sd-agent/checks.d
- change owner for /etc/sd-agent/checks.d to sd-agent:sd-agent

always:
- copy file latency_monitor.py to /etc/sd-agent/checks.d/
- create config latency_monitor.yaml at /etc/sd-agent/conf.d/

Config options
==============
**name** - destination name
**ip** - destination ip
**is_adaptive** - adaptive option for ping command (faster ping if enabled, default - false)
**packets_qty** - packets quantity to send

Metrics
=============
latency_monitor.trans_packet
latency_monitor.recv_packets
latency_monitor.packet_loss
latency_monitor.response_min
latency_monitor.response_avg
latency_monitor.response_max


Additional Information
======================
How long it takes for the plugin to complete depends on the packet_count variable and the number of hosts you monitor.

*Note: Plugin should work on both Linux and FreeBSD although, FreeBSD is currently not officially supported by Server Density.*

.. _Server Density: http://www.serverdensity.com/
.. _SmokePing: http://oss.oetiker.ch/smokeping/