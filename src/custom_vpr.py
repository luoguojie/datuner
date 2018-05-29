space = [
    ['EnumParameter', 'connection_driven_clustering', ['on', 'off']],
    ['EnumParameter', 'allow_unrelated_clustering', ['on', 'off']],
    ['EnumParameter', 'alpha_clustering', [0.1, 0.25, 0.5 , 0.75, 0.9]],
    ['EnumParameter', 'beta_clustering', [0.1, 0.25, 0.5 , 0.75, 0.9]],
    ['EnumParameter', 'cluster_seed_type', ['blend', 'timing', 'max_inputs']],

    ['EnumParameter', 'inner_num', [0.8, 1.0, 1.2, 10]],
    ['EnumParameter', 'init_t', [50.0, 100.0, 150.0]],
    ['EnumParameter', 'exit_t', [0.01, 0.02, 0.05]],
    ['EnumParameter', 'alpha_t', [0.01, 0.02, 0.05]],
    ['EnumParameter', 'place_chan_width', [80, 100, 120]],

    ['EnumParameter', 'first_iter_pres_fac', [0.0, 0.25, 0.5, 0.75]],
    ['EnumParameter', 'initial_pres_fac', [0.3, 0.5, 1.0, 5.0]],
    ['EnumParameter', 'pres_fac_mult', [1.0, 1.3, 1.5]],
    ['EnumParameter', 'acc_fac', [1.0, 1.25, 1.5]],
    ['EnumParameter', 'bb_factor', [2, 3, 4, 5]],
    ['EnumParameter', 'base_cost_type', ['demand_only', 'delay_normalized']],
    ['EnumParameter', 'bend_cost', [0.0, 0.25, 0.5, 0.75]],
    ['EnumParameter', 'min_incremental_reroute_fanout', [56, 64, 72]],
]

space_dep = [
    ['connection_driven_clustering', 'allow_unrelated_clustering', 'alpha_clustering',
        'beta_clustering', 'cluster_seed_type'],
    ['inner_num', 'init_t', 'exit_t', 'alpha_t', 'place_chan_width', ],
    ['first_iter_pres_fac', 'initial_pres_fac', 'pres_fac_mult', 'acc_fac', 'bb_factor', 
        'base_cost_type', 'bend_cost', 'min_incremental_reroute_fanout', ]
]

dependency = [
    [1, 0],
    [2, 1],
]

space_dep = []
dependency = []

budget = 24

runs_per_epoch = 6

workspace = 'work/datuner/vpr'

machines = [
    'ec2-18-207-195-25.compute-1.amazonaws.com',
    'ec2-52-87-150-239.compute-1.amazonaws.com',
    'ec2-34-201-46-137.compute-1.amazonaws.com',
    'ec2-54-165-46-215.compute-1.amazonaws.com',
]

remote_user = 'ubuntu'

flow = 'custom'
