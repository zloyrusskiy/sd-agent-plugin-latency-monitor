import os
import re
import sys
import subprocess
from checks import AgentCheck

class LatencyMonitor(AgentCheck):
  def __init__(self, name, init_config, agentConfig, instances=None):
    AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    # Compile frequently used regular expressions
    if sys.platform == 'linux2':
      self.packetStatsRe = re.compile(r'(\d+) packets transmitted, (\d+) received, (.*?)% packet loss, time (\d+)ms')
      self.responseStatsRe = re.compile(r'rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms')
        
    elif sys.platform.find('freebsd') != -1:
      self.packetStatsRe = re.compile(r'(\d+) packets transmitted, (\d+) packets received, (.*?)% packet loss')
      self.responseStatsRe = re.compile(r'round-trip min/avg/max/(stddev|std-dev) = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms')

    self.ipv4Re = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    self.ipv6Re = re.compile(r'^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$', re.IGNORECASE)

  def check(self, instance):
    tags = instance.get('tags', [])
    if tags is None:
      tags = []
    else:
      tags = list(set(tags))

    packets_qty = instance.get('packets_qty', 10)
    ip = instance.get('ip')
    name = instance.get('name', ip)
    is_adaptive = instance.get('is_adaptive', False)

    tags.append('name:{}'.format(name))

    try:
      if re.match(self.ipv4Re, ip) != None:
        command = 'ping'
      elif re.match(self.ipv6Re, ip) != None:
        command = 'ping6'
      else:
        raise Exception("{} is not ip address".format(ip))

      if bool(is_adaptive):
        ping_cmd = [command, '-A', '-c', str(packets_qty), ip]
      else:
        ping_cmd = [command, '-c', str(packets_qty), ip]


      response = subprocess.Popen(ping_cmd, stdout = subprocess.PIPE, close_fds = True).communicate()[0]
      latencyStatus = self.parseResponse(response, tags)
    except Exception as e:
      self.log.error("Failed to ping {0}."
                     "\nError {1}".format(name, e))

  def parseResponse(self, response, tags):
    packetStats = re.search(self.packetStatsRe, response)
    responseStats = re.search(self.responseStatsRe, response)

    if packetStats != None:
      self.gauge('latency_monitor.trans_packets', packetStats.group(1), tags=tags)
      self.gauge('latency_monitor.recv_packets', packetStats.group(2), tags=tags)
      self.gauge('latency_monitor.packet_loss', packetStats.group(3), tags=tags)

      if responseStats != None:
        self.gauge('latency_monitor.response_min', responseStats.group(1), tags=tags)
        self.gauge('latency_monitor.response_avg', responseStats.group(2), tags=tags)
        self.gauge('latency_monitor.response_max', responseStats.group(3), tags=tags)

  
if __name__ == '__main__':
  # Load the check and instance configurations
  check, instances = LatencyMonitor.from_yaml('/etc/sd-agent/conf.d/latency_monitor.yaml')
  for instance in instances:
    print "\nRunning the check against ip: {}".format(instance['ip'])
    check.check(instance)
    print 'Metrics: {}'.format(check.get_metrics())
