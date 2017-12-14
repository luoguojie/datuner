import sys
import argparse
import opentuner
from opentuner import ConfigurationManipulator
from opentuner import EnumParameter
from opentuner import FloatParameter
from opentuner import MeasurementInterface
from opentuner import Result
import socket
import pickle
import os
from setup import *

if os.path.exists(os.getcwd() + '/vtr.py'):
  import vtr
  tool_path = eval(flow + '.tool_path')
elif os.path.exists(os.getcwd() + '/vivado.py'):
  import vivado
  top_module = eval(flow + '.top_module')
elif os.path.exists(os.getcwd() + '/quartus.py'):
  from quartus import server_address as server_address
  from quartus import space as space
  from quartus import designdir as designdir
  from quartus import top_module as top_module
elif os.path.exists(os.getcwd() + '/custom.py'):
  from custom import server_address as server_address
  from custom import space as space
else:
  print "missing [tool_name].py under current folder"
  sys.exit(1)

class ProgramTuner(ProgramTunerWrapper):
  # Create a TCP/IP socket
  conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Connect the socket to the port where the server is listening
  print (server_address)
  conn.connect(server_address)
  conn.send(pickle.dumps(['init']))

  param = []
  try:
    # param is a list that specifies the search space
    param = pickle.loads(conn.recv(8096))
  finally:
    conn.close()

  def manipulator(self):
    manipulator = ConfigurationManipulator()
    for item in self.param:
      param_type, param_name, param_range = item
      if param_type == 'EnumParameter':
        manipulator.add_parameter(EnumParameter(param_name, param_range))
    return manipulator

  def save_final_config(self, configuration):
    """called at the end of tuning"""
    print "Optimal options written to bench_config.json:", configuration.data
    self.manipulator().save_to_file(configuration.data, 'inline_config.json')

  def dumpresult(self, cfg, res, metadata = []):
    """
    Compile and run a given configuration then
    return performance
    """
    f = open('./localresult.txt', 'a')
    for key in cfg:
      f.write(str(key) + "," + str(cfg[key]) + ",")
    f.write(str(res))
    f.write('\n')
    f.close()
    try:
      conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      conn.connect(server_address)
      msg = []
      for key in cfg:
        msg.append([key, cfg[key]])
      conn.send(pickle.dumps(['respond', msg, metadata, res]))
      conn.close() 
    except:
      print "connection error!\n"

if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  ProgramTuner.main(argparser.parse_args())
