#!/usr/bin/python
#===================================================
# run DATuner
#===================================================
# @author : Chang Xu
# @date   : 4/20/2017
# @brief  : A python script to run DATuner
#
import re
import os
import sys
import optparse
import argparse

#-------------------------------------------------
# parse parameters and read information from py
#-------------------------------------------------
parser = argparse.ArgumentParser(description='command interface')
parser.add_argument('-f','--flow',type=str,dest='tool',choices=['vtr','vivado','quartus','custom'])
parser.add_argument('-b','--budget',type=int,default=1,dest='limit')
parser.add_argument('-t','--timeout',type=float,default=[7200.0,0.0,0.0,0.0],dest='stop',nargs=4,help='format: sec min hour day')
parser.add_argument('-p','--parallel',type=int,dest='para')
args = parser.parse_args()


if len(sys.argv) < 2:
  print "Please input parameter command line "
  parser.print_help()
  sys.exit(1)
  
pwd = os.getcwd()                                           # will return the path where the program is being called
if os.path.exists(pwd+'/vtr.py') and args.tool == 'vtr':
  sys.path.append(pwd)
  import vtr
  tool_path = eval(args.tool+'.tool_path')
elif os.path.exists(pwd+'/vivado.py') and args.tool == 'vivado':
  sys.path.append(pwd)
  import vivado
elif os.path.exists(pwd+'/quartus.py') and args.tool == 'quartus':
  sys.path.append(pwd)
  import quartus
else:
  print "nothing found under current folder"

# set up the workspace path
if eval(args.tool+'.work_space') == '':
  work_space = pwd + '/project'
  print 'work_space:'+work_space
else:
  if not os.path.exists(eval(args.tool+'.work_space')):
    work_space = eval(args.tool+'.work_space')
    print 'work_space:'+work_space
    os.makedirs(work_space)
  else:
    work_space = eval(args.tool+'.work_space')



design_path = eval(args.tool+'.design_path')
top_module = eval(args.tool+'.top_module')
proc_num = args.para
space_def = 'SPACE_DEF_HOLD'
py_code = 'PYTHON_CODE_HOLD'
datuner_path = '/home/sx233/datuner/releases/Linux_x86_64/scripts'
objective = 'OBJECTIVE_HOLD'
cst_value = 'CST_VALUE_HOLD'


# extract design name from design path
if eval(args.tool+'.design_path')[-1] == '/' :
  design_name = eval(args.tool+'.design_path').split('/')[-2]
else:
  design_name = eval(args.tool+'.design_path').split('/')[-1]

#-------parameters check------
if args.tool== '':
  print "please specify the tool name."
  sys.exit(1)

if design_name == '':
  print "please specify the design name."
  sys.exit(1)

if work_space == '':
  print "please specify the directory to save intermediate data."
  sys.exit(1)

if os.path.exists(datuner_path+"/../bin") == False:
  print datuner_path
  print "Please call DATuner under $HOME/releases/Linux_x86_64/scripts/"
  sys.exit(1)

if args.tool == "vtr":
  if os.path.exists(tool_path+"/scripts") == False:
    print "vtr path is not correct. Please check. The path should to point to .../vtr/vtr_release/vtr_flow"
    sys.exit(1)
elif args.tool == 'vivado':
  if top_module == '':
    print "vivado is used. Please specify the top module."
    sys.exit(1)
elif args.tool == 'quartus':
  if top_module == '':
    print "quartus is used. Please specify the top module."
    sys.exit(1)
else:
  if py_code== '':
    print "please specify the python code to excute OpenTuner."
    sys.exit(1)
  if space_def == '':
    print "please specify the space definition file."
    sys.exit(1)

tune_cst = 0
if args.tool == 'vivado':
  if eval(args.tool+'.modify_cst') == 'y' or eval(args.tool+'.modify_cst') == 'yes':
    tune_cst = 1
    if eval(args.tool+'.cst_value') == '':
      print "please support the default timing constraint."
      sys.exit(1)
    
if len(args.stop) < 4:
  print "please use the format: sec min hour day"
  sys.exit(1)
else:
  stoptime = float(args.stop[0])+float(args.stop[1])*60.0+float(args.stop[2])*3600.0+float(args.stop[3])*86400.0

#--------------------------
# Preparation & Check
#--------------------------

vtr_flags = [
    'resyn','resyn2','resyn3',
    'alpha_clustering','beta_clustering',
    'allow_unrelated_clustering','connection_driven_clustering',
    'alpha_t','seed','inner_num','timing_tradeoff',
    'inner_loop_recompute_divider','td_place_exp_first','td_place_exp_last',
    'max_router_iterations','initial_pres_fac','pres_fac_mult','acc_fac',
    'bb_factor','base_cost_type','astar_fac','max_criticality',
    'criticality_exp'
    ]

vivado_cst_flags = [
    'Optdirective','Placedirective','fanout_opt',
    'placement_opt','critical_cell_opt','critical_pin_opt',
    'retime','rewire','Routedirective',
    'tune_cst'
    ]
    
vivado_flags = vivado_cst_flags[0:-1]

quartus_flags = [
  'map_effort',  'map_optimize',  'fit_effort',
  'fit_optimize_io_register_for_timing',  'fit_pack_register', 'fit_tdc'
  ]
    
design = design_name
designdir = design_path
workspace = work_space+"/"+args.tool+"/"+design
try:
  os.makedirs(workspace)
except:
  pass

# set up the user defined search space  

if args.tool == 'vtr':
  f = open(workspace+'/vtr_space.txt','a')                       
  for flag in vtr_flags:
    if isinstance(eval(args.tool+'.'+flag), str) or isinstance(eval(args.tool+'.'+flag), float) or isinstance(eval(args.tool+'.'+flag), int):
      pass
    elif (len(eval(args.tool+'.'+flag)) > 2 or isinstance(eval(args.tool+'.'+flag)[0], str)):
      word = '{'
      length = len(eval(args.tool+'.'+flag))
      for index in range(length):
        word += str(eval(args.tool+'.'+flag)[index]) + ', '
      word = word[0:-2]
      word += '}'
      f = open(workspace+'/vtr_space.txt','a')
      f.write(flag+' EnumParameter '+word+'\n')
    else:
      f = open(workspace+'/vtr_space.txt','a')
      word = '[' + str(eval(args.tool+'.'+flag)[0]) + ' ,' + str(eval(args.tool+'.'+flag)[1]) + ']'
      f.write(flag+' FloatParameter '+word+'\n')
    f.close()

if args.tool == 'vivado':
  if tune_cst == 0:
    flags = vivado_flags
  else:
    flags = vivado_cst_flags
  f = open(workspace+'/vivado_space.txt','a')                       
  for flag in flags:
    if isinstance(eval(args.tool+'.'+flag), str) or isinstance(eval(args.tool+'.'+flag), float) or isinstance(eval(args.tool+'.'+flag), int):
      pass
    elif (len(eval(args.tool+'.'+flag)) > 2 or isinstance(eval(args.tool+'.'+flag)[0], str)):
      word = '{'
      length = len(eval(args.tool+'.'+flag))
      for index in range(length):
        word += str(eval(args.tool+'.'+flag)[index]) + ', '
      word = word[0:-2]
      word += '}'
      f = open(workspace+'/vivado_space.txt','a')
      f.write(flag+' EnumParameter '+word+'\n')
    else:
      f = open(workspace+'/vivado_space.txt','a')
      word = '[' + str(eval(args.tool+'.'+flag)[0]) + ' ,' + str(eval(args.tool+'.'+flag)[1]) + ']'
      f.write(flag+' FloatParameter '+word+'\n')
    f.close()

if args.tool == 'quartus':
  f = open(workspace+'/quartus_space.txt','a')                       
  for flag in quartus_flags:
    if isinstance(eval(args.tool+'.'+flag), str) or isinstance(eval(args.tool+'.'+flag), float) or isinstance(eval(args.tool+'.'+flag), int):
      pass
    elif (len(eval(args.tool+'.'+flag)) > 2 or isinstance(eval(args.tool+'.'+flag)[0], str)):
      word = '{'
      length = len(eval(args.tool+'.'+flag))
      for index in range(length):
        word += str(eval(args.tool+'.'+flag)[index]) + ', '
      word = word[0:-2]
      word += '}'
      f = open(workspace+'/quartus_space.txt','a')
      f.write(flag+' EnumParameter '+word+'\n')
    else:
      f = open(workspace+'/quartus_space.txt','a')
      word = '[' + str(eval(args.tool+'.'+flag)[0]) + ' ,' + str(eval(args.tool+'.'+flag)[1]) + ']'
      f.write(flag+' FloatParameter '+word+'\n')
    f.close()

# copy necessary file to workspace
binDir =  datuner_path+"/../bin"
cpcmd = "cp "+binDir+"/DATuner_master "+binDir+"/DATuner_worker "+workspace
os.system(cpcmd)

if args.tool == "vtr":
  srcFile = datuner_path+"/eda_flows/"+args.tool+"/tune"+args.tool+".py"
  sedcmd = "sed -e \"s:BENCH_HOLDER:"+design+":g\" -e \"s:WORKSPACE_HOLDER:"+workspace+":g\" -e \"s:VTRFLOWPATH_HOLDER:"+tool_path+":g\" -e \"s:SCRIPTPATH_HOLDER:"+datuner_path+":g\" "+srcFile+" > "+workspace+"/tune"+args.tool+".py"
  os.system(sedcmd)
#  cpcmd = "cp "+datuner_path+"/eda_flows/"+args.tool+"/"+args.tool+"_space.txt "+workspace
#  os.system(cpcmd)

elif args.tool == "vivado":
  srcFile = datuner_path+"/eda_flows/"+args.tool
  if tune_cst ==1:
    srcFile = srcFile + "/tunevivado_cst.py"
  else:
    srcFile = srcFile + "/tunevivado.py"
    
  print "debug use "+srcFile
  sedcmd = "sed -e \"s:BENCH_HOLDER:"+design+":g\" -e \"s:WORKSPACE_HOLDER:"+workspace+":g\" -e \"s:TOPMODULE_HOLDER:"+top_module+":g\" -e \"s:SCRIPTPATH_HOLDER:"+datuner_path+":g\" -e \"s:DESIGNPATH_HOLDER:"+designdir+":g\" "+srcFile+" > "+workspace+"/tune"+args.tool+".py"
  os.system(sedcmd)

#  space_file_cmd ="cp "+datuner_path+"/eda_flows/"+args.tool+"/"+args.tool+"_space.txt "+workspace
#  if tune_cst == 1:
#    print "debug tune cst"
#    lower_cst = float(cst_value) * 0.8
#    upper_cst = float(cst_value) * 1.5
#    space_file_cmd="sed -e \"s:LOWER_BOUND_HOLDER:"+str(lower_cst)+":g\" -e \"s:UPPER_BOUND_HOLDER:"+str(upper_cst)+":g\" "+datuner_path+"/eda_flows/"+args.tool+"/"+args.tool+"_space_cst.txt > "+workspace+"/"+args.tool+"_space.txt"
#  os.system(space_file_cmd)

elif args.tool == "quartus":
  srcFile = datuner_path+"/eda_flows/"+args.tool+"/tune"+args.tool+".py"
  sedcmd = "sed -e \"s:BENCH_HOLDER:"+design+\
           ":g\" -e \"s:WORKSPACE_HOLDER:"+workspace+\
           ":g\" -e \"s:TOPMODULE_HOLDER:"+top_module+\
           ":g\" -e \"s:SCRIPTPATH_HOLDER:"+datuner_path+\
           ":g\" -e \"s:DESIGNPATH_HOLDER:"+designdir+\
           ":g\" "+srcFile+" > "+workspace+"/tune"+args.tool+".py"
  os.system(sedcmd)
#  cpcmd = "cp "+datuner_path+"/eda_flows/"+args.tool+"/"+args.tool+"_space.txt "+workspace
#  os.system(cpcmd) 

else:
  srcFile = py_code
  sedcmd = "sed -e \"s:BENCH_HOLDER:"+design+":g\" -e \"s:WORKSPACE_HOLDER:"+workspace+":g\" -e \"s:SCRIPTPATH_HOLDER:"+datuner_path+":g\" "+srcFile+" > "+workspace+"/tuneProgram.py"
  os.system(sedcmd)
  cpcmd = "cp "+datuner_path+"/eda_flows/user_program_example/programWrapper.py "+workspace
  os.system(cpcmd)
  cpcmd = "cp "+datuner_path+"/adddeps.py "+workspace
  os.system(cpcmd)


#---------------------------
# Run DATuner
#---------------------------
os.chdir(workspace)
try:
  os.remove("log")
  shutil.rmtree("opentuner.db")
except:
  pass

mpi_path="mpirun"

if args.tool == "vtr" or args.tool == "vivado" or args.tool == "quartus":
  runcmd = mpi_path+" -np 1 "+\
    "./DATuner_master -"+args.tool+" --test-limit "+str(args.limit)+" --stop-after "+\
    str(stoptime)+" --path "+workspace+" : -np "+str(proc_num)+" --hostfile "+\
    datuner_path+"/my_hosts "+"./DATuner_worker -design "+design+" -path "+workspace+\
    " -tune_cst "+str(tune_cst)+" --parallelism=1 > log"
  os.system(runcmd)
else:
  runcmd = mpi_path+" -np 1 "+\
      "./DATuner_master --space "+space_def+" --path "+workspace+" --test-limit "+args.limit+\
      " --stop-after "+stoptime+" : -np "+proc_num+" --hostfile "+\
      datuner_path+"/my_hosts "+"./DATuner_worker -design "+design+" -path "+workspace+\
      " --parallelism=1 > log"
  os.system(runcmd)
