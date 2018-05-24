space_dep = []
space = []
task0 = []
Oparam = []
file = open('mpiccparams')
content = file.readlines()
for line in content:
    params = line.strip('\n').strip(' ').split(' ')
    for param in params:
        if not param.startswith('-'):
            continue
        param = param.replace('-', '_')[1:]
        if param.endswith('[=n]'):
            param = param.rstrip('[=n]')
            dimension = ['EnumParameter', param, range(10)]
        elif param.endswith('=n'):
            param = param.rstrip('=n')
            dimension = ['EnumParameter', param, range(10)]
        elif param.startswith('O'):
            Oparam.append(param.lstrip('O'))
            continue
        else:
            dimension = ['EnumParameter', param, ['on', 'off']]
        task0.append(dimension[1])
        space.append(dimension)
#space = []
task0.append('O')
space.append(['EnumParameter', 'O', Oparam])
space_dep.append(task0)
space_dep.append([ 'np'])
space.append(['EnumParameter', 'np', [1, 2, 4, 5, 10]])

dependency = [
    [1, 0]
]

#print space
#print space_dep

budget = 16

workspace = 'work/datuner/mm'

machines = [
    'ec2-35-171-20-217.compute-1.amazonaws.com',
    'ec2-174-129-60-254.compute-1.amazonaws.com',
]

flow = 'custom'

server_address = ('127.0.0.1', 10026)
