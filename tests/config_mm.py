space = []
Oparam = []
file = open('mpiccparams')
content = file.readlines()
for line in content:
    params = line.strip('\n').strip(' ').split(' ')
    for param in params:
        if not param.startswith('-'):
            continue
        if param.endswith('[=n]'):
            param = param.rstrip('[=n]')
            dimension = ['EnumParameter', param[1:], range(10)]
        elif param.endswith('=n'):
            param = param.rstrip('=n')
            dimension = ['EnumParameter', param[1:], range(10)]
        elif param.startswith('-O'):
            Oparam.append(param.lstrip('-O'))
        else:
            dimension = ['EnumParameter', param[1:], ['on', 'off']]
        space.append(dimension)
space.append(['EnumParameter', 'O', Oparam])
space.append(['EnumParameter', 'np', [1, 2, 5, 10, 20, 50]])

#print space

budget = 8

workspace = '/work/datuenr/workspace'

machines = [

]

flow = 'matrix-multiply'

server_address = ('127.0.0.1', 10026)
