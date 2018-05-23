import os
from opentuner import MeasurementInterface
from opentuner import Result

class ProgramTunerWrapper(MeasurementInterface):
    def cfg_to_flags(self, cfg):
        ccflags = []
        runflags = []
        for name, value in cfg.items():
            name = name.replace('_', '-')
            if name == 'O':
                ccflags.append('-O' + value)
            elif name == 'np':
                runflags.append('-np ' + str(value))
            elif value == 'on':
                ccflags.append('-' + name)
            elif value == 'off':
                continue
            else:
                ccflags.append('-' + name + '=' + str(value))
        return ccflags, runflags

    def compile_mpicc(self, flags, result_id):
        tmp_dir = './tmp'
        try:
            os.stat(tmp_dir)
        except OSError:
            os.mkdir(tmp_dir)
        tmp_dir = './tmp/%d' % result_id
        try:
            os.stat(tmp_dir)
        except OSError:
            os.mkdir(tmp_dir)
        output_dir = tmp_dir + '/mm_bin'
        cmd = 'mpicc -o '+ output_dir + ' ' + ' '.join(flags) + ' mpi.c'
        print 'compile: '+ cmd
        compile_result = self.call_program(cmd)
        if compile_result['returncode'] != 0:
            print 'mpicc error: ' + compile_result['stderr']
            return False
        return True

    def run_mpirun(self, flags, result_id):
        bin_dir = './tmp/%d/mm_bin' % result_id
        cmd = 'mpirun ' + ' '.join(flags) + ' '+ bin_dir + ' data/matrixa.txt data/matrixb.txt'
        print 'run: ' + cmd
        run_result = self.call_program(cmt)
        if run_result['returncode'] != 0:
            print 'mpirun error ' + run_result['stderr']
            result = 1e9
        else:
            result = run_result['time']
        return result

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        result_id = desired_result.id
        ccflags, runflags = self.cfg_to_flags(cfg)
        if self.compile_mpicc(ccflags, result_id):
            result = run_mpirun(runflags, result_id)
        else:
            result = 1e9
        self.dumpresult(cfg, result)
        return Result(time = result)
        
