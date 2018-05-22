import os
from opentuner import MeasurementInterface
from opentuner import Result

class ProgramTunerWrapper(MeasurementInterface):
    def cfg_to_flags(cfg):
        ccflags = []
        runflags = []
        for name, value in cfg.items():
            if name == 'O':
                ccflags.append('-O' + value)
            elif name == 'np':
                runflags.append('-np' + value)
            elif value == 'on':
                ccflags.append('-' + name)
            else:
                ccflags.append('-' + name + '=' + str(value))
        return ccflags, runflags

    def compile_mpicc(flags, result_id):
        tmp_dir = './tmp/%d' % result_id
        try:
            os.stat(tmp_dir)
        except OSError:
            os.mkdir(tmp_dir)
        output_dir = tmp_dir + '/mm_bin'
        cmd = 'mpicc -o '+ outpu_dir + ' '.join(flags) + 'mpi.c'
        compile_result = self.call_program(cmd)
        if compile_result['returncode'] != 0:
            log.warning('gcc error ' + compile_result['stderr'])
            return False
        return True

    def run_mpirun(flags, result_id):
        bin_dir = './tmp/%d/%s' % result_id, mm_bin
        cmd = 'mpirun ' + ' '.join(flags) + bin_dir

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        result_id = desired_result.id
        ccflags, runflags = self.cfg_to_flags(cfg)
        if self.compile_mpicc(flags, result_id):
            result = run_mpirun(runflags, result_id)
        return Result(time = result)
        
