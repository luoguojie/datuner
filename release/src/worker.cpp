#include <cfloat>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
#include <utility>
#include "mpi.h"
#include "structure.h"
#include "msg_passing.h"
#include "autoTuner.h"
#include "space_partition.h"
#include <unistd.h>
#include <iostream>
#include <cassert>
#include <unistd.h>
#include <Python.h>

using namespace std;

int main(int argc, char** argv) {
  if(argc < 5) {
    printf("./worker -design <design name> -path <path2workspace> -pycode <pythoncode>\n");
    return 0;
  }
  int myrank;
  int pnum;
  int len;
  char hostname[MPI_MAX_PROCESSOR_NAME];
  MPI_Status status;
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD,&myrank);
  MPI_Comm_size(MPI_COMM_WORLD,&pnum);
  MPI_Get_processor_name(hostname,&len);
  printf("Worker = %d, My rank = %d, runing on %s\n",pnum,myrank,hostname);

  int tune_type = 0; //1: VPR 2: Vivado 3: ISE
  MPI_Recv(&tune_type,1,MPI_INT,0,0,MPI_COMM_WORLD,&status);
  
  //int exp_type = 0; //1: my 2: whole 3: restart 4: fix 5: fix-mab
  //MPI_Recv(&exp_type,1,MPI_INT,0,0,MPI_COMM_WORLD,&status);

  int share_best = 1; //0:false 1:true
  //MPI_Recv(&share_best,1,MPI_INT,0,0,MPI_COMM_WORLD,&status);
  
  string spacepath;
  bool diffdb = false;
  string design;
  int fake_argc = 0;
  char** fake_argv = NULL;
  vector<string> tmp_fake_argv;
  string pycode="";
  {
     int jump = 0;
     bool flag = false;
     string tmp = "-design";
     string tmp1 = "-diffdb";
     for(int i = 0; i < argc; i++) {
      if(strcmp(argv[i],"-path") == 0) {
        assert(i < argc-1);
        spacepath = string(argv[i+1]);
        jump = i+1;
        flag = true;
        continue;
      }
      if(strcmp(argv[i],tmp.c_str()) == 0) {
        assert(i < argc-1);
        design = string(argv[i+1]);
        jump = i+1;
        flag = true;
        continue;
      }
      if(strcmp(argv[i],"-pycode") == 0) {
        assert(i < argc-1);
        pycode=string(argv[i+1]);
        jump = i+1;
        flag = true;
        continue;
      }
      if(flag && i == jump) continue;
      if(strcmp(argv[i],tmp1.c_str()) == 0) {
        diffdb = true;
        continue;
      }

      tmp_fake_argv.push_back(string(argv[i]));
     }
     
     char rankname[50];
     sprintf(rankname,"--rank=%d",myrank);
     tmp_fake_argv.push_back(string(rankname));
     if(diffdb) {
      tmp_fake_argv.push_back("--database");
      string dbdir="/home/xuchang/nas/project/daTuner/experiment/vivado/"+design+"/";
      char dbtmp[20];
      sprintf(dbtmp,"rank%d",myrank);
      dbdir += string(dbtmp);
      dbdir += "/opentuner.db";
      tmp_fake_argv.push_back(dbdir);
     }


    if(share_best) {
      tmp_fake_argv.push_back("--seed-configuration");
      char name[500];
      sprintf(name,"StartPointSpace%d.json",myrank);
      //sprintf(name,"/proj/xsjhdstaff3/changx/project/parTuner/experiment/vpr/vtr_release/vtr_flow/tasks/openTunerTiming/experiment/my/ch_intrinsics/StartPointSpace%d.json",myrank);
      tmp_fake_argv.push_back(string(name));

    }

    /*
     fake_argc = tmp_fake_argv.size();
     fake_argv = new char*[fake_argc];
     for(int i = 0; i < fake_argc; i++) {
        fake_argv[i] = new char[100];
        strcpy(fake_argv[i],tmp_fake_argv[i].c_str());
     }*/
   
  }




  

  printf("worker start tuning\n");
 

  Py_Initialize();
  if(!Py_IsInitialized()) return -1;
  //PySys_SetArgv(fake_argc,fake_argv);
  //printf("Pass Initialization\n");

  int cond = 0;//0:stop, 1:autotuning
  while(1) {
    MPI_Recv(&cond,1,MPI_INT,0,0,MPI_COMM_WORLD,&status);
    if(cond == 0) break;
    
    int limit;
    MPI_Recv(&limit,1,MPI_INT,0,0,MPI_COMM_WORLD,&status);
    char str_limit[10];
    sprintf(str_limit,"%d",limit);
    bool flag_limit = false;
    for(int i = 0; i < tmp_fake_argv.size(); i++) {
      if(tmp_fake_argv[i].find("test-limit") != string::npos) {
        assert(i < tmp_fake_argv.size()-1);
        tmp_fake_argv[i+1] = string(str_limit);
        flag_limit = true;
        break;
      }
    }
    if(!flag_limit) {
      tmp_fake_argv.push_back("--test-limit");
      tmp_fake_argv.push_back(string(str_limit));
    }
    fake_argc = tmp_fake_argv.size();
    assert(!fake_argv);
    fake_argv = new char*[fake_argc];
    for(int i = 0; i < fake_argc; i++) {
      fake_argv[i] = new char[100];
      strcpy(fake_argv[i],tmp_fake_argv[i].c_str());
    }

 
  if(myrank == 1) {
    cout<<"debug argv "<<endl;
    for(int i = 0; i < fake_argc; i++) {
      cout<<fake_argv[i]<<endl;
    }
  }

    PySys_SetArgv(fake_argc,fake_argv);



    Task* task = NULL;
    Recv_Task(task, 0);
    assert(task != NULL);
    //printf("debug recved task %d,%d,%d,%d\n",myrank,task->step,task->subspace->id,task->subspace->params.size());
      
    vector<Result*> results;
    AutoTuner* tuner = new AutoTuner(task->subspace->id, design, tune_type); //start from 1
    assert(tuner != NULL);
    //usleep(1000000*myrank);
    //if(myrank == 1) 
    tuner->callOpenTuner(task,results,myrank,spacepath,pycode);

    /*
    Result* best_result = NULL;
    float score = +DBL_MAX;
    for(int i = 0; i < results.size(); i++) {
      if(score > results[i]->score) {
        score = results[i]->score;
        best_result = results[i];
        printf("My rank %d, result %f\n",myrank,score);
      }
    }
    if(best_result != NULL) Send_Result(best_result,0);
    //if(false){
    //}*/

    printf("rank %d sending results, result size %d\n",myrank, results.size());
    if(results.size() != 0) {
      Send_MultiResult(results,0);
    }
    else{ 
      Result* best_result = new Result();
      vector<pair<string,string> >name2choice;
      best_result->score = 10000;
      best_result->id = task->subspace->id;
      best_result->name2choice = name2choice;
      Send_Result(best_result,0);
    }
    if(fake_argv) {
      for(int i = 0; i < fake_argc; i++) {delete []fake_argv[i]; fake_argv[i] = NULL;}
      delete []fake_argv; fake_argv=NULL;
    }
  }

  Py_Finalize();
  MPI_Finalize();
  return 0;
}