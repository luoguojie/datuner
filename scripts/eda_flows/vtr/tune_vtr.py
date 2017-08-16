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

#--------------------------------------------
# VTR parameter space
#--------------------------------------------

abc_flags = [
    'resyn','resyn2','resyn3'
    ]
vtr_pack_flags = [
    'alpha_clustering','beta_clustering',
    'allow_unrelated_clustering','connection_driven_clustering'
    ]
vtr_place_flags = [
    'alpha_t','seed','inner_num','timing_tradeoff',
    'inner_loop_recompute_divider','td_place_exp_first','td_place_exp_last'
    ]
vtr_route_flags = [
    'max_router_iterations','initial_pres_fac','pres_fac_mult','acc_fac',
    'bb_factor','base_cost_type','astar_fac','max_criticality',
    'criticality_exp'
    ]


class VTRTuner(MeasurementInterface):
  design='BENCH_HOLDER'
  workspace='WORKSPACE_HOLDER'
  vtrpath='VTRFLOWPATH_HOLDER'
  scriptpath='SCRIPTPATH_HOLDER'

  def __init__(self, *pargs, **kwargs):
    super(VTRTuner, self).__init__(program_name="hello", *pargs, **kwargs)

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

    #generate configuration
    abc_config = " "
    run_abc_cmd = " "
    for flag in abc_flags:
      abc_config += flag + ' '+str(cfg[flag])+' '
      if cfg[flag] == 'on':
        run_abc_cmd += '{0}; '.format(flag)
    run_abc_cmd += ' '+run_abc_cmd

    vtr_config = " "
    run_vtr_cmd = " "
    for flag in vtr_pack_flags:
      run_vtr_cmd += '    \"--'+flag+'\",       \"{0}\",'.format(cfg[flag])
      vtr_config += flag +' '+str(cfg[flag])+' '
    for flag in vtr_place_flags:
      run_vtr_cmd += '    \"--'+flag+'\",       \"{0}\",'.format(cfg[flag])
      vtr_config += flag +' '+str(cfg[flag])+' '
    for flag in vtr_route_flags:
      run_vtr_cmd += '    \"--'+flag+'\",       \"{0}\",'.format(cfg[flag])
      vtr_config += flag +' '+str(cfg[flag])+' '

    #runvtr
    res = []
    requestor = desired_result.requestor
    self.runvtr(run_abc_cmd,run_vtr_cmd, abc_config, vtr_config, result_id, res, requestor)
    end = time.time()
    return Result(time=-float(res[0]))

  def runvtr(self,run_abc_cmd, run_vtr_cmd, abc_config, vtr_config, reqid, res, requestor):
    start = time.time()
    #path to vtr scripts
    basedir=self.vtrpath
    sdir = basedir+'/scripts/'
    workdir = self.workspace+'/'

    #run_abc_cmd = ""
    cmd = 'sed -e \'s:ABC_OTHER_OPTIONS:'+run_abc_cmd+':g\' -e \'s:VPR_OTHER_OPTIONS:'+run_vtr_cmd+':g\' -e \'s:VTRFlowPath_Holder:'+self.vtrpath+':g\' '+self.scriptpath+'/eda_flows/vtr/run_vtr_flow.pl > '+workdir+'run_vtr_flow_'+str(self.args.myrank)+'.pl'
    subprocess.Popen(cmd,shell=True).wait()
    cmd = 'chmod u+x '+workdir+'run_vtr_flow_'+str(self.args.myrank)+'.pl'
    subprocess.Popen(cmd,shell=True).wait()
    cmd = 'mkdir -p '+workdir+str(self.args.myrank)
    subprocess.Popen(cmd,shell=True).wait()
    cmd = 'mkdir -p '+workdir+str(self.args.myrank)+'/'+str(reqid)+'/'
    subprocess.Popen(cmd,shell=True).wait()

    arch = basedir+'/arch/timing/k6_frac_N10_mem32K_40nm.xml'
    bench = basedir+'/benchmarks/verilog/'+self.design+'.v'
    cmd = workdir+'run_vtr_flow_'+str(self.args.myrank)+'.pl '+bench+' '+arch+' -temp_dir '+workdir+str(self.args.myrank)+'/'+str(reqid)
    subprocess.Popen(cmd,shell=True).wait()
    cmd = sdir+'parse_vtr_flow.pl '+workdir+str(self.args.myrank)+'/'+str(reqid)+' '+self.scriptpath+'/eda_flows/vtr/vtr_parse_result.txt > '+workdir+str(self.args.myrank)+'/'+str(reqid)+'/parseResult.txt'
    subprocess.Popen(cmd,shell=True).wait()


    min_chan_width = 0
    chipSize = 0
    logicarea = 0
    routearea = 0
    fmax = -10000
    rt = 0
    placementwl = 0
    nets = 0
    blocks = 0
    clb = 0
    io = 0
    bram = 0
    mult = 0
    file=workdir+str(self.args.myrank)+'/'+str(reqid)+'/parseResult.txt'
    if os.path.isfile(file):
      f= open(file)
      while 1:
        line = f.readline()
        if not line: break
        if line.find("vpr_status") == -1:
          bufs = line.split()
          min_chan_width = bufs[1]
          chipSize = bufs[2]
          logicarea = bufs[3]
          routearea = bufs[4]
          fmax = -float(bufs[6])
          rt = float(bufs[7])+float(bufs[8])+float(bufs[9])
          nets = bufs[10]
          blocks = bufs[11]
          clb = bufs[12]
          io = float(bufs[13])+float(bufs[14])
          bram = float(bufs[15])
          mult = float(bufs[16])
      f.close()
    res.append(fmax)
    res.append(rt)
    res.append(blocks)

    cmd = 'rm -r '+workdir+str(self.args.myrank)+'/'+str(reqid)
    subprocess.Popen(cmd,shell=True).wait()
    cmd = 'rm '+workdir+'run_vtr_flow_'+str(self.args.myrank)+'.pl'
    subprocess.Popen(cmd,shell=True).wait()

    end = time.time()
    f = open('./result_'+str(self.args.myrank)+'.txt','a')
    f.write('abcConfig: '+run_abc_cmd+' ')
    f.write('vtrConfig: '+run_vtr_cmd+' ')
    f.write(str(min_chan_width)+' '+str(chipSize)+' '+str(logicarea)+' '+str(routearea)+' '
      +str(rt)+' '+str(nets)+' '
      +str(blocks)+' '+str(clb)+' '+str(io)+' '+str(bram)+' '+str(mult)+' '
      +str(end-start)+' '+str(requestor)+' '+str(float(fmax))+'\n')
    f.close()

    f = open('./localresult'+str(self.args.myrank)+'.txt','a')
    f.write(abc_config+' ')
    f.write(vtr_config+' ')
    f.write(str(float(fmax))+'\n')
    f.close()


if __name__ == '__main__':
  argparsers = opentuner.argparsers()
  argparsers.append(argparser)
  totalparser = argparse.ArgumentParser(parents=argparsers)
  args = totalparser.parse_args()

  mycmd='rm -f ./localresult'+str(args.myrank)+'.txt'
  subprocess.call(mycmd,shell=True)

  VTRTuner.main(args)



