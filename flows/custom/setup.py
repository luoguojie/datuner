import os
from custom import space_dep
from opentuner import MeasurementInterface
from opentuner import Result

class ProgramTunerWrapper(MeasurementInterface):
    def cfg_to_flags(self, cfg):
        packflags = []
        placeflags = []
        routeflags = []
        for name in space_dep[0]:
            for k, v in cfg.items():
                if k == name:
                    packflags.append('--' + name + ' ' + str(v))
                    break
        for name in space_dep[1]:
            for k, v in cfg.items():
                if k == name:
                    placeflags.append('--' + name + ' ' + str(v))
                    break
        for name in space_dep[2]:
            for k, v in cfg.items():
                if k == name:
                    routeflags.append('--' + name + ' ' + str(v))
                    break
        return packflags, placeflags, routeflags

    def runvpr(self, packflags, placeflags, routeflags):
        args = '--pack --place --route'
        args = args + ' ' + ' '.join(packflags)
        args = args + ' ' + ' '.join(placeflags)
        args = args + ' ' + ' '.join(routeflags)
        circuit = 'diffeq2'
        cmd = 'cd ~/tmp/input/' + circuit + '/; ~/tmp/vtr-verilog-to-routing/vpr/vpr ../k6_frac_N10_mem32K_40nm.xml diffeq2 ' + args
        #print cmd
        result = self.call_program(cmd)
        if result['returncode'] != 0:
            print cmd
            print 'Run vpr error:', result['stderr']
            return 1e9
        print 'Run time:', result['time']
        return result['time'] 

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        result_id = desired_result.id
        packflags, placeflags, routeflags = self.cfg_to_flags(cfg)
        result = self.runvpr(packflags, placeflags, routeflags)
        self.dumpresult(cfg, result)
        return Result(time = result)
        
