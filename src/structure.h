#ifndef __SPACE_H__
#define __SPACE_H__
#include <vector>
#include <string>
#include <utility>

struct Param{
  std::string name;
  std::string type;
  std::vector<std::string> options;
  float min;
  float max;
  std::string defVal;
  Param(){}
  Param(std::string name,std::string type, std::string defVal){
    this->name = name;
    this->type = type;
    this->defVal = defVal;
    this->min = 0;
    this->max = 0;
  }
};

struct Space{
  int id;
  std::vector<Param*> params;
  Space(){}
  Space(std::vector<Param*> params,int id) {
    this->params = params;
    this->id = id;
  }
};

struct Task{
  Space* subspace;
  int step;
  Task(){subspace = NULL;step = 0;}
  Task(Space* subspace, int step) {
    this->subspace = subspace;
    this->step = step; 
  }
};

struct Result{
  std::vector<std::pair<std::string,std::string> > name2choice;
  float score;
  int id;
};



#endif