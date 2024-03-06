import argparse
import os
import pandas as pd

cur_dir=os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target",type=str,default="")
    parser.add_argument("--directory",type=str,default=cur_dir)
    args = parser.parse_args()
    target = args.target
    directory = args.directory

    # df_list = [pd.read_csv(cur_dir+"/test_cases/sysbench.csv", index_col=0),
    #         # pd.read_csv(cur_dir+"/test_cases/rocksdb.csv", index_col=0),
    #         pd.read_csv(cur_dir+"/test_cases/mysqlslap.csv", index_col=0)]

    df_list = [pd.read_csv(cur_dir+"/test_cases/rocksdb.csv", index_col=0)]

    df = None
    for df1 in df_list:
        if target in df1.index:
            df = df1
            break
    # print(f"==>df:\n{df}")
    para_list = ["l1d_cache_miss","l1i_cache_load_miss","l2_cache_miss","l3_cache_miss",
            "dtlb_miss","itlb_miss","stlb_miss", 
            "branch_miss", "load", "store", "br", "fp","int","vector",
            "other","cpi","ipc", "syscall_rate"]
    s = "#! /bin/bash\n"
    for para in para_list:
        if para == "other":
            para_value = 1 - df.loc[target,"load"] - df.loc[target,"store"] - df.loc[target,"br"]
        else:
            para_value = df.loc[target,para]
        s += "export target_{}={}\n".format(para,para_value)
        # s += f"export target_{para}={para_value}\n"

    with open(directory+"/set_env.sh","w",encoding="utf-8") as f:
        f.write(s)

if __name__ == "__main__":
    main()
