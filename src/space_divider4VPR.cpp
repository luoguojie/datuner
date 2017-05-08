#include <iostream>
#include <vector>
#include <cassert>
#include "space_divider4VPR.h"
#include "structure.h"
#include <cstdio>
#include <cstdlib>

using namespace std;

void genOrgSpace4VPR(Space*& orgSpace) {
  vector<Param*> params; 
  Param* tmp = new Param("resyn","EnumParameter","off");
  tmp->options.push_back("on");
  tmp->options.push_back("off");
  params.push_back(tmp);

  tmp = new Param("resyn2","EnumParameter","off");
  tmp->options.push_back("on");
  tmp->options.push_back("off");
  params.push_back(tmp);

  tmp = new Param("resyn3","EnumParameter","off");
  tmp->options.push_back("on");
  tmp->options.push_back("off");
  params.push_back(tmp);

  tmp = new Param("alpha_clustering","FloatParameter","0.75");
  tmp->min = 0;
  tmp->max = 1;
  params.push_back(tmp);
  
  tmp = new Param("beta_clustering","FloatParameter","0.9");
  tmp->min = 0;
  tmp->max = 1;
  params.push_back(tmp);
  
  tmp = new Param("allow_unrelated_clustering","EnumParameter","on");
  tmp->options.push_back("on");
  tmp->options.push_back("off");
  params.push_back(tmp);
  
  tmp = new Param("connection_driven_clustering","EnumParameter","on");
  tmp->options.push_back("on");                       
  tmp->options.push_back("off");                      
  params.push_back(tmp);
  
  tmp = new Param("alpha_t","FloatParameter","0.8");
  tmp->min = 0.5;
  tmp->max = 0.9;
  params.push_back(tmp);
  
  tmp = new Param("seed","EnumParameter","1");
  tmp->options.push_back("1"); tmp->options.push_back("2"); tmp->options.push_back("3");
  tmp->options.push_back("4"); tmp->options.push_back("5");
  params.push_back(tmp);
  
  tmp = new Param("inner_num","EnumParameter","10");
  tmp->options.push_back("1"); tmp->options.push_back("10"); tmp->options.push_back("100");
  params.push_back(tmp);
  
  tmp = new Param("timing_tradeoff","FloatParameter","0.5");
  tmp->min = 0.3; 
  tmp->max = 0.7;
  params.push_back(tmp);

  tmp = new Param("inner_loop_recompute_divider","EnumParameter","0");
  tmp->options.push_back("1"); tmp->options.push_back("0"); tmp->options.push_back("5");
  params.push_back(tmp);
  
  tmp = new Param("td_place_exp_first","EnumParameter","1");
  tmp->options.push_back("1"); tmp->options.push_back("0"); tmp->options.push_back("3");
  params.push_back(tmp);
  
  tmp = new Param("td_place_exp_last","EnumParameter","8");
  tmp->options.push_back("5"); tmp->options.push_back("8"); tmp->options.push_back("10");
  params.push_back(tmp);
  
  tmp = new Param("max_router_iterations","EnumParameter","50");
  tmp->options.push_back("20"); tmp->options.push_back("50"); tmp->options.push_back("80");
  params.push_back(tmp);
  
  tmp = new Param("initial_pres_fac","FloatParameter","0.5");
  tmp->min = 0.3; 
  tmp->max = 100;
  params.push_back(tmp);
  
  tmp = new Param("pres_fac_mult","FloatParameter","1.3");
  tmp->min = 1.2; 
  tmp->max = 2;
  params.push_back(tmp);
  
  tmp = new Param("acc_fac","FloatParameter","1");
  tmp->min = 1; 
  tmp->max = 2;
  params.push_back(tmp);
  
  tmp = new Param("bb_factor","EnumParameter","3");
  tmp->options.push_back("1"); tmp->options.push_back("3"); tmp->options.push_back("5");
  params.push_back(tmp);
  
  tmp = new Param("base_cost_type","EnumParameter","delay_normalized");
  tmp->options.push_back("demand_only"); tmp->options.push_back("delay_normalized"); 
  params.push_back(tmp);
  
  tmp = new Param("astar_fac","FloatParameter","1.2");
  tmp->min = 1; 
  tmp->max = 2;
  params.push_back(tmp);
  
  tmp = new Param("max_criticality","FloatParameter","0.99");
  tmp->min = 0.8; 
  tmp->max = 1;
  params.push_back(tmp);
  
  tmp = new Param("criticality_exp","FloatParameter","1");
  tmp->min = 0.8; 
  tmp->max = 1;
  params.push_back(tmp);
  orgSpace = new Space(params,0);
  assert(orgSpace != NULL);
  /*
  for(int i = 0; i < orgSpace->params.size(); i++) {
    //cout<<orgSpace->params[i]->name<<endl;
    printf("%s,%s\n",orgSpace->params[i]->name, orgSpace->params[i]->type);
  }*/
}

void initDivision_VPR(Space* orgSpace, map<int,Space*>& spaceBuf) {
  Space* subspace = new Space(orgSpace->params,1);
  assert(subspace != NULL);
  spaceBuf.insert(pair<int,Space*>(1,subspace));
}

void spaceDivision4VPR(Space* orgSpace, vector<Space*>& spaceBuf, int snum){
  //static division
  //TODO: dynamic division
  //alpha_t 0.1
  //allow_unrelated_clustering on/off
  spaceBuf.resize(0);
  vector<vector<string> > tmp;
  tmp.resize(snum);
  for(int i = 0; i < snum; i++) {
    tmp[i].resize(2);
  }
  tmp[0][0]="0.6"; tmp[0][1] = "on";
  tmp[1][0]="0.6"; tmp[1][1] = "off";
  tmp[2][0]="0.7"; tmp[2][1] = "on";
  tmp[3][0]="0.7"; tmp[3][1] = "off";
  tmp[4][0]="0.8"; tmp[4][1] = "on";
  tmp[5][0]="0.8"; tmp[5][1] = "off";
  tmp[6][0]="0.9"; tmp[6][1] = "on";
  tmp[7][0]="0.9"; tmp[7][1] = "off";

  for(int i = 0; i < tmp.size(); i++) {
    vector<Param*> tmp_vector;
    for(int j = 0; j < orgSpace->params.size(); j++) {
      Param* tmp_param = new Param(orgSpace->params[j]->name, orgSpace->params[j]->type, orgSpace->params[j]->defVal);
      tmp_param->options = orgSpace->params[j]->options;
      tmp_param->min = orgSpace->params[j]->min;
      tmp_param->max = orgSpace->params[j]->max;
      tmp_vector.push_back(tmp_param);
    }
    
    for(int j = 0; j < tmp_vector.size(); j++) {
      if(tmp_vector[j]->name == "alpha_t") {
        tmp_vector[j]->min = atof(tmp[i][0].c_str())-0.1;
        tmp_vector[j]->max = atof(tmp[i][0].c_str());
      }
      if(tmp_vector[j]->name == "allow_unrelated_clustering") {
        tmp_vector[j]->options.clear();
        tmp_vector[j]->options.push_back(tmp[i][1]);
      }
    }
    
    Space* tmpspace = new Space(tmp_vector,i+1);
    assert(tmpspace != NULL);
    spaceBuf.push_back(tmpspace);
  }
 
  /*
  for(int i = 0; i < spaceBuf.size(); i++) {
    Space* tmpspace = spaceBuf[i];
    assert(tmpspace != NULL);
    cout<<"debug id "<<tmpspace->id<<endl;
    for(int j = 0; j < tmpspace->params.size(); j++) {
      Param* tmpparam = tmpspace->params[j];
      assert(tmpparam != NULL);
      if(tmpparam->name == "alpha_t") {
        cout<<"debug "<<i<<" "<<tmpparam->min<<" "<<tmpparam->max<<endl;
      }
    }
  }*/
}

void initDivision8_VPR(Space* orgSpace, std::map<int,Space*>& spaceBuf){
  int snum = 8;
  spaceBuf.clear();
  vector<vector<string> > tmp;
  tmp.resize(snum);
  tmp[0].push_back("on"); tmp[0].push_back("0.6"); tmp[0].push_back("demand_only");
  tmp[1].push_back("on"); tmp[1].push_back("0.6"); tmp[1].push_back("delay_normalized");
  tmp[2].push_back("on"); tmp[2].push_back("0.8"); tmp[2].push_back("demand_only");
  tmp[3].push_back("on"); tmp[3].push_back("0.8"); tmp[3].push_back("delay_normalized");
  tmp[4].push_back("off"); tmp[4].push_back("0.6"); tmp[4].push_back("demand_only");
  tmp[5].push_back("off"); tmp[5].push_back("0.6"); tmp[5].push_back("delay_normalized");
  tmp[6].push_back("off"); tmp[6].push_back("0.8"); tmp[6].push_back("demand_only");
  tmp[7].push_back("off"); tmp[7].push_back("0.8"); tmp[7].push_back("delay_normalized");


  for(int i = 0; i < tmp.size(); i++) {
    vector<Param*> tmp_vector;
    for(int j = 0; j < orgSpace->params.size(); j++) {
      Param* tmp_param = new Param(orgSpace->params[j]->name, orgSpace->params[j]->type, orgSpace->params[j]->defVal);
      tmp_param->options = orgSpace->params[j]->options;
      tmp_param->min = orgSpace->params[j]->min;
      tmp_param->max = orgSpace->params[j]->max;
      tmp_vector.push_back(tmp_param);
    }
    
    for(int j = 0; j < tmp_vector.size(); j++) {
      if(tmp_vector[j]->name == "allow_unrelated_clustering") {
        tmp_vector[j]->options.clear();
        tmp_vector[j]->options.push_back(tmp[i][0]);
        tmp_vector[j]->defVal = tmp[i][0];
      }
      if(tmp_vector[j]->name == "alpha_t") {
        tmp_vector[j]->options.clear();
        //tmp_vector[j]->options.push_back(tmp[i][1]);
        //tmp_vector[j]->defVal = tmp[i][1];
        tmp_vector[j]->min = atof(tmp[i][1].c_str())-0.1;
        tmp_vector[j]->max = atof(tmp[i][1].c_str())+0.1;
      }
      if(tmp_vector[j]->name == "base_cost_type") {
        tmp_vector[j]->options.clear();
        tmp_vector[j]->options.push_back(tmp[i][2]);
        tmp_vector[j]->defVal = tmp[i][2];
      }
    }
    
    Space* tmpspace = new Space(tmp_vector,i+1); //space start from 1
    assert(tmpspace != NULL);
    spaceBuf.insert(pair<int,Space*> (i+1,tmpspace));
  }
}


