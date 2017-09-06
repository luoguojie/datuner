import os
import sys

def dataset(x,datatype):
  '''
  the datatype determine the surface of the search space  
  '''
  y = [ ]
  if datatype == "linear":
    for i in range(1000):
      y.append(1000-i)  
  else:
    y.append(random.uniform(1, 1000))
  return y[x]

def dump_result(rank,qor):
  filename = 'qor'+str(rank)+'.txt'
  f = open(filename,'w')
  f.write(str(qor))
  f.close()

if __name__ == '__main__':
  rank = sys.argv[1]
  index = sys.argv[2]
  datatype = "linear"
  qor = dataset(int(index), datatype)
  dump_result(rank,qor)