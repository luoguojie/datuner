import sys
sys.path.append("SCRIPTPATH_HOLDER")
import logging
import re
import time
import os
import os.path
import argparse
import thread
import adddeps
import opentuner
import subprocess
from opentuner import ConfigurationManipulator
from opentuner import EnumParameter
from opentuner import FloatParameter
from opentuner import MeasurementInterface
from opentuner import Result

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('--myrank',type=int, default=0,
    help='the rank of process')
#argparser.add_argument('--tunecst',type=int,
#    help='specify whether to tune default cst or not')
#argparser.add_argument('--defaultcst',type=float,
#    help='specify the default cst')


#----------------------------------------
# Vivado parameter space
#----------------------------------------
Physoptdesign_flags = [
  'fanout_opt',
  'placement_opt',
  'critical_cell_opt',
  'retime',
  'rewire',
  'critical_pin_opt'
  ]



class VIVADOFlagsTuner(MeasurementInterface):
  design='BENCH_HOLDER'
  topmodule='TOPMODULE_HOLDER'
  workspace='WORKSPACE_HOLDER'
  designpath='DESIGNPATH_HOLDER'

  def __init__(self, *pargs, **kwargs):
    super(VIVADOFlagsTuner, self).__init__(program_name="hello", *pargs, **kwargs)

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """
    manipulator = ConfigurationManipulator()
    filename=self.workspace+"/space"+str(self.args.myrank)+".txt"
    if os.path.isfile(filename):
      f = open(filename,'r')
      while(1):
        line = f.readline()
        if not line: break
        buf = []
        buf = line.split()
        name = buf[0]
        paramType = buf[1]
        minval = buf[2]
        maxval = buf[3]
        optnum = buf[4]
        if paramType == "EnumParameter":
          opt = []
          for it in range(int(optnum)):
            opt.append(buf[5+it])
          manipulator.add_parameter(EnumParameter(name,opt))
        if paramType == "FloatParameter":
          manipulator.add_parameter(FloatParameter(name,float(minval),float(maxval)))
    return manipulator


  def run(self, desired_result, input, limit):
    """
    Compile and run a given configuration then
    return performance
    """
    start = time.time()
    cfg = desired_result.configuration.data
    result_id = desired_result.id

    cmd='mkdir -p '+self.workspace+'/'+str(self.args.myrank)+'/'
    subprocess.Popen(cmd,shell=True).wait()
    cmd='mkdir -p '+self.workspace+'/'+str(self.args.myrank)+'/'+str(result_id)+'/'
    subprocess.Popen(cmd,shell=True).wait()

    workdir = self.workspace+'/'+str(self.args.myrank)+'/'+str(result_id)+'/'
    srcdir = self.designpath+'/'+self.design+'/'

    cfg = desired_result.configuration.data

    fname = workdir+"/options.tcl"
    f = open(workdir+'/options.tcl','w')

    #for tcl
    optstr = 'opt_design -directive'
    placestr = 'place_design -directive'
    physoptstr = 'phys_opt_design'
    routestr = 'route_design -directive'

    #for result analysis
    optres = 'opt_design directive '
    placeres = 'place_design directive '
    physoptres = 'phys_opt_design '
    routeres = 'route_design directive '

    optres += ' '+cfg["Optdirective"]+' '
    optstr += ' '+cfg["Optdirective"]
    placeres += ' '+cfg['Placedirective']+' '
    placestr += ' '+cfg['Placedirective']
    for flag in Physoptdesign_flags:
      if cfg[flag] == 'on':
        physoptres += ' '+flag+'  on  '
      else:
        physoptres += ' '+flag+'  off  '

      if cfg[flag] == 'off':
        continue
      physoptstr += ' -'+flag

    routeres += ' '+cfg['Routedirective']+' '
    routestr += ' '+cfg['Routedirective']

    f.write(optstr+'\n')
    f.write(placestr+'\n')
    f.write(physoptstr+'\n')
    f.write(routestr+'\n')
    f.close()

    #tunetiming = args.tunecst
    #print "debug tunecst: "+str(tunetiming)
    #cstset = args.defaultcst
    #if tunetiming == 1:
    #  cstset = cfg['Timingcst']


    wns = 0.0
    SLUT=str(0)
    SReg=str(0)
    BRam=str(0)
    DSP=str(0)

    cmd = 'sed -e \'s:BENCH:'+self.design+':g\' -e \'s:TOPMODULE:'+self.topmodule+':g\' -e \'s:DESIGN_PATH:'+self.designpath+':g\' -e \'s:WORKDIR_HOLDER:'+workdir+':g\' '+self.designpath+'/../run_vivado.tcl > '+workdir+'run_vivado.tcl'
    subprocess.Popen(cmd,shell=True).wait()
    os.chdir(workdir)

    run_cmd = 'vivado -mode batch -source '+workdir+'/run_vivado.tcl'
    subprocess.call(run_cmd,shell=True)

    timingFile=workdir + '/output/post_route_timing.rpt'
    if os.path.isfile(timingFile):
      f = open(timingFile)
      while 1:
        line = f.readline()
        if line.find('Startpoint') != -1:
          f.readline()
          singleLine = f.readline()
          bufs = singleLine.split()
          i = len(bufs)
          if i >= 3:
            wns = float(bufs[2])
          else:
            while 1:
              singleLine = f.readline()
              bufs = singleLine.split()
              if len(bufs)+i >= 3:
                wns = float(bufs[2-i])
                break
              i = i+len(bufs)
          break
      f.close()
    else:
      wns=-10000


    ResourceFile = workdir+'/output/post_route_util.rpt'
    if os.path.isfile(ResourceFile):
      blockFlag = False
      f = open(ResourceFile)
      while 1:
        line = f.readline()
        if not line: break
        if line.find('Slice LUTs')!=-1:
          bufs = line.split("| ")
          SLUT = bufs[2]
        if line.find('Slice Registers')!=-1:
          bufs = line.split("| ")
          SReg = bufs[2]
        if line.find('Block RAM Tile') != -1 and blockFlag != True:
          bufs = line.split("| ")
          BRam = bufs[2]
          blockFlag = True
        if line.find('DSPs')!=-1:
          bufs = line.split("| ")
          DSP = bufs[2]
      f.close()

    end = time.time()

    myscore = wns
    #if tunetiming == 1:
    #  if wns != -10000:
    #    myscore = -(cstset-wns)

    writename='./result'+str(self.args.myrank)+'.txt'
    f = open(writename,'a')
    f.write('Configuration: '+optres+' '+placeres+' '+physoptres+' '+routeres)
#+' '+'Timingcst '+str(cstset))
    f.write(" WNS:  ")
    f.write(str(myscore))
    rt = str(end - start)
    f.write(" RT: "+rt)
    f.write(" SLUT: "+SLUT+"  SReg: "+SReg+"  BRam: "+BRam+"  DSP:  "+DSP)
    f.write(" \n")
    f.close()


    writename='./localresult'+str(self.args.myrank)+'.txt'
    f = open(writename,'a')
    f.write('Configuration: '+optres+' '+placeres+' '+physoptres+' '+routeres)
#+' '+'Timingcst '+str(cstset))
    f.write(' WNS '+str(myscore))
    f.write("\n")
    f.close()

    return Result(time=-myscore)


  #def save_final_config(self, configuration):
  #  """called at the end of tuning"""
  #  print "Optimal b01 options written to bench_config.json:", configuration.data
  #  self.manipulator().save_to_file(configuration.data,
  #                                  'inline_config.json')

if __name__ == '__main__':
  argparsers = opentuner.argparsers()
  argparsers.append(argparser)
  totalparser = argparse.ArgumentParser(parents=argparsers)
  args = totalparser.parse_args()

  mycmd='rm -f ./localresult'+str(args.myrank)+'.txt'
  subprocess.call(mycmd,shell=True)

  VIVADOFlagsTuner.main(args)