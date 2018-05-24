import math
import copy

def check_design_point_in_space(design_point, target_space):
# return true if 'design_point' lies within 'target_space'
  for i in design_point[0]:
    for j in target_space:
      if i[0] == j[1]:
        if j[0] == 'EnumParameter':
          if (not i[1] in j[2]):
            return False
          else:
            break
  return True


def calculate_conditional_entropy(target_space, dimension, average_qor, \
                                      global_result):
# calculate the conditional entropy assuming partitioning along 'dimension' 
  conditional_entropy = 0
  # values store all possible values for the parameter in 'dimension'
  values = dimension[2]

  for value in values:
    # for each value of dimension, formulate a subspace with the specific 
    # value, used to check whether a design point lies in the proposed subspace
    target_subspace = copy.deepcopy(target_space)
    for i in target_subspace:
      if i[1] == dimension[1]:
        i[2] = [value]
        break

    # evaluate design points in target_subspace
    num_pts, num_good_pts, num_bad_pts = 0, 0, 0
    for design_point in global_result:
      if check_design_point_in_space(design_point, target_subspace):
        num_pts += 1
        if design_point[-1] <= average_qor: 
          num_good_pts += 1
        else: 
          num_bad_pts += 1
    
    # an empty set of points does not contribute to entropy
    if num_pts == 0:
      continue
    num_pts, num_good_pts, num_bad_pts =  \
      map(float, [num_pts, num_good_pts, num_bad_pts])
    # calculate the entropy of target_subspace
    entropy_good_pts, entropy_bad_pts = 0, 0
    if num_good_pts > 0:
      entropy_good_pts = -(num_good_pts/num_pts*math.log(num_good_pts/num_pts))
    if num_bad_pts > 0:
      entropy_bad_pts = -(num_bad_pts/num_pts*math.log(num_bad_pts/num_pts))
    target_subspace_entropy = entropy_good_pts + entropy_bad_pts
    # accumulate to the overall coonditional_entropy, omitting normalization
    # since |D_i| is the same for all partitions
    conditional_entropy += num_pts * target_subspace_entropy

  return conditional_entropy    

def topo_sort(space_dep, dependency):
# run a topo sort on dependency and return the sorted list
  n = len(space_dep)
  degree = [0 for i in range(n)]
  for dep in dependency:
    degree[dep[0]] += 1
  queue = []
  tlist = []
  for i in range(n):
    if degree[i] == 0:
      queue.append(i)
  while len(queue):
    t = queue.pop(0)
    children = []
    for dep in dependency:
      if dep[1] == t:
        children.append(dep[0])
        degree[dep[0]] -= 1
        if degree[dep[0]] == 0:
          queue.append(dep[0])
    task = {}
    task['num'] = t
    task['list'] = space_dep[t]
    task['sum'] = 0
    task['min_entropy'] = 1e9
    task['min_dimension'] = ''
    task['children'] = children
    tlist.append(task)
  return tlist

def find_task(dimension, tlist):
  for task in tlist:
    for dim in task['list']:
      if dimension == dim:
        return task

def select_dimension(target_space, global_result, space_dep, dependency):
# return the dimension with the largest information gain
  sum_qor = 0
  for i in global_result:
    sum_qor += i[-1]
  average_qor = float(sum_qor) / len(global_result)

  if not len(space_dep):
  # space without dependency
    best_conditional_entropy = 1e9
    for dimension in target_space:
      if len(dimension[2]) == 1:
        continue
      conditional_entropy = \
          calculate_conditional_entropy(target_space, dimension, average_qor, \
                                        global_result)
      if conditional_entropy < best_conditional_entropy:
        best_conditional_entropy = conditional_entropy
        target_dimension = dimension[1]
    return target_dimension
  else:
  # space with dependency
    tlist = topo_sort(space_dep, dependency)
    for dimension in target_space:
      if len(dimension[2]) == 1:
        continue
      conditional_entropy = calculate_conditional_entropy(target_space, dimension, \
                                                          average_qor, global_result)
      task = find_task(dimension[1], tlist)
      task['sum'] += conditional_entropy
      if conditional_entropy < task['min_entropy']:
        task['min_entropy'] = conditional_entropy
        task['min_dimension'] = dimension[1]

    for task in tlist:
      task['avg'] = task['sum'] / len(task['list'])
      print '[Task] #', task['num'], 'avg entropy:', task['avg'], 'min entropy:', task['min_entropy'],\
            'min dimension:', task['min_dimension'], 'children:', task['children']
    
    for task in tlist:
      flag = False
      for child in task['children']:
        for tsk in tlist:
          if tsk['num'] == child:
            child_tsk = tsk
            break
        if task['min_entropy'] < child_tsk['min_entropy'] or task['avg'] < child_tsk['avg']:
          flag = True
          break
      if not len(task['children']) or flag:
        return task['min_dimension']

def partition_space(subspaces, global_result, space_dep, dependency):
  # select the subspace with the highest score to partition
  best_score = -1e9
  for space_tuple in subspaces:
    if space_tuple[1] > best_score:
      target_space, best_score, target_freq = space_tuple
      target_space_tuple = space_tuple

  dimension_to_partition = select_dimension(target_space, global_result, space_dep, dependency)

  print 'space partition on dimension: ' + dimension_to_partition
  for dimension in target_space:
    if dimension[1] == dimension_to_partition:
      values = dimension[2]
      break

  # for each value of 'dimension', create a subspace and add to subspaces
  for value in values:
    target_space_copy = copy.deepcopy(target_space)
    for dimension in target_space_copy:
      if dimension[1] == dimension_to_partition:
        dimension[2] = [value]
        break
    subspaces.append([target_space_copy, 0, target_freq])

  # remove the original target_space
  subspaces.remove(target_space_tuple)


def update_score(t, subspaces, global_result):
  for space_tuple in subspaces:
    num_points, total_qor = 0, 0
    for design_point in global_result:
      if check_design_point_in_space(design_point, space_tuple[0]):
        num_points += 1
        total_qor += -design_point[1]
    if num_points == 0:
      space_tuple[1] = math.sqrt(2*math.log(t)/space_tuple[2])
    else:
      space_tuple[1] = total_qor / num_points \
                        + math.sqrt(2*math.log(t)/space_tuple[2])


def select_space(t, subspaces, global_result):
  update_score(t, subspaces, global_result)
  best_score = -1e9
  for space_tuple in subspaces:
    if space_tuple[1] > best_score:
      best_space, best_score = space_tuple[0], space_tuple[1]
      best_space_tuple = space_tuple
  best_space_tuple[2] += 1
  return best_space
