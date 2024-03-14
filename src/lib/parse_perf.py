# encoding: utf-8

import re
import os
import json
import numpy as np
import pandas as pd
import time
import math

pd.set_option('display.float_format', lambda x: '%.3f' % x)

cur_dir = os.path.abspath(os.path.dirname(__file__))

def replace_event_code(perf_out_path):
    arm_event_code_path = os.path.join(cur_dir, "arm_event_code.json")
    # 加载事件键值对的映射关系
    with open(arm_event_code_path, "r") as file:
        event_code_data = json.load(file)

    # 读取perf.out文件内容
    with open(perf_out_path, "r") as file:
        perf_out_content = file.read()

    # 将events中的key修改为对应的value
    for key, value in event_code_data["events"].items():
        # 通过正则表达式找到匹配的key并替换为value
        perf_out_content = re.sub(r"\b%s\b" % re.escape(key), value, perf_out_content)

    # 将修改后的内容写回perf.out文件
    with open(perf_out_path, "w") as file:
        file.write(perf_out_content)

    # print(str(perf_out_path) + " 已成功修改")

def my_sub(perf_path,perf_path1,perf_path2):
    if not os.path.exists(perf_path1):
        raise FileNotFoundError("%s" % perf_path1)
    if not os.path.exists(perf_path2):
        raise FileNotFoundError("%s" % perf_path2)
    with open(perf_path1,"r") as f:
        lines1 = f.readlines()
    with open(perf_path2,"r") as f:
        lines2 = f.readlines()
    assert len(lines1) == len(lines2),"len(lines1) != len(lines2)"
    lines3 = []
    for i in range(len(lines1)):
        line1 = lines1[i]
        line2 = lines2[i]
        line1 = line1.strip().replace(',', '')
        line2 = line2.strip().replace(',', '')
        line3 = ""
        obj1 = re.search('^([\d.]+) seconds time elapsed', line1)
        obj2 = re.search('^([\d.]+) seconds time elapsed', line2)
        if obj1 is not None and obj2 is not None:
            line3 = '{} seconds time elapsed'.format(float(obj1.group(1))-float(obj2.group(1)))
            lines3.append(line3)
            continue
        obj1 = re.search('^(\d+)\s+(\S+)', line1)
        obj2 = re.search('^(\d+)\s+(\S+)', line2)
        if obj1 is not None and obj2 is not None:
            cnt = int(obj1.group(1)) - int(obj2.group(1))
            if cnt < 0:
                cnt = 0 
            assert obj1.group(2) == obj2.group(2),"obj1.group(2) != obj2.group(2)"
            event = obj1.group(2)
            line3 = "{:>20,}\t{}".format(cnt,event)
            lines3.append(line3)
            continue
        line3 = line1
        lines3.append(line3)
    with open(perf_path,"w") as f:
        for line3 in lines3:
            f.write(line3)
            f.write("\n")

def get_perf_stat_result(perf_path):
    if not os.path.exists(perf_path):
        raise FileNotFoundError("%s" % perf_path)
    #print("perf stat log: %s" % perf_path)
    stat = dict()
    fd = open(perf_path, "r")
    for line in fd.readlines():
        line = line.strip().replace(',', '')
        obj = re.search('^([\d.]+) seconds time elapsed', line)
        if obj:
            stat['elapsed_time'] = float(obj.group(1))
            continue
        obj = re.search('^(\d+)\s+(\S+)', line)
        if obj:
            cnt = int(obj.group(1))
            event = obj.group(2)
            stat[event] = cnt
            continue
    fd.close()
    return stat

def parse_perf_stat(WORKSPACE_DIR):
    #cur_dir = os.path.abspath(os.path.dirname(__file__))
    #WORKSPACE_DIR=os.path.abspath(cur_dir)
    parse_path = os.path.join(WORKSPACE_DIR, "parse")
    if not os.path.exists(parse_path):
        os.makedirs(parse_path)

    bench_list = os.listdir(WORKSPACE_DIR + "/results")
    stat_list = []
    # 将每个基本块的perf.out修改后将其合并到stat_list
    for bench_name in bench_list:
        perf_path = os.path.join(WORKSPACE_DIR, "results/" + bench_name + "/perf.out")
        replace_event_code(perf_path)
        stat = get_perf_stat_result(perf_path)
        stat_list.append(stat)

    # 使用 bench_list 作为行索引
    df = pd.DataFrame(stat_list, index=bench_list)
    raw_path = os.path.join(parse_path,'raw.csv')
    df.to_csv(raw_path)
    df = df[sorted(df.columns)]
    #print(">>>> all results <<<< \n %s" % df.T)
    # df.T.to_csv("./parse/perf.csv")

    # print(df)
    # >>>>> post pocessing <<<<<
    # total_uops = df["UOPS_ISSUED.ANY"]
    total_uops = 0
    total_ins = df["INST_RETIRED"]
    cycles = df["CPU_CYCLES"]
    cycles_k = 0

    ipc = total_ins / cycles
    cpi = cycles / total_ins

    branch_misses  = df["BR_MIS_PRED_RETIRED"]
    branch_instructions = df["BR_RETIRED"]
    branch_miss = branch_misses.div(branch_instructions, fill_value=0)  

    #llc_cache_mpki = 1000. * df["LLC-loads"] / total_ins
    l1i_cache_mpki = 1000. * df["L1I_CACHE_REFILL"] / total_ins
    l1d_cache_mpki = 1000. * df["L1I_CACHE"] / total_ins

    # metric of L1-dcache
    l1d_cache_misses = df["L1D_CACHE_REFILL"]
    l1d_cache = df["L1D_CACHE"]
    l1d_cache_miss = l1d_cache_misses.div(l1d_cache, fill_value=0)  

    # metric of L1-icache
    l1i_cache_load_misses = df["L1I_CACHE_REFILL"]
    l1i_cache_loads = df["L1I_CACHE"]
    l1i_cache_load_miss = l1i_cache_load_misses.div(l1i_cache_loads, fill_value=0)  


    # l2_cache_mpki  = 1000. * df["L2_RQSTS.MISS"] / total_ins
    # l3_cache_mpki  = 1000. * df["MEM_LOAD_RETIRED.L3_MISS"] / total_uops

    # metric of L2-cache
    l2_cache_misses = df['L2D_CACHE_REFILL']
    l2_cache = df['L2D_CACHE']
    l2_cache_miss = l2_cache_misses.div(l2_cache, fill_value=0)  

    # metirc of L3-cache
    l3_cache_misses = df['LL_CACHE_MISS_RD']
    l3_cache = df['LL_CACHE_RD']
    l3_cache_miss = l3_cache_misses.div(l3_cache, fill_value=0)  

    # metric of dTLB and iTLB
    # itlb_miss      = df["iTLB-load-misses"] / df["iTLB-loads"]
    # dtlb_miss      = df["dTLB-load-misses"] / df["dTLB-loads"]
    itlb_misses = df["L1I_TLB_REFILL"]
    itlb = df["L1I_TLB"]
    itlb_miss = itlb_misses.div(itlb, fill_value=0)  

    dtlb_misses = df["L1D_TLB_REFILL"]
    dtlb = df["L1D_TLB"]
    dtlb_miss = dtlb_misses.div(dtlb, fill_value=0)  

    # invalid
    # metirc of sTLB(l2-tlb)
    stlb_hits = 0
    stlb_misses = 0
    stlb = 0
    stlb_miss = 0

    ## insmix
    loads = df["LD_SPEC"]
    stores = df["ST_SPEC"]
    fps = df["VFP_SPEC"]
    vector_uops = df["ASE_SPEC"]
    ints = df["DP_SPEC"]

    load  = df["LD_SPEC"] / total_ins
    store = df["ST_SPEC"] / total_ins
    br    = df["BR_RETIRED"] / total_ins
    fp    = df["VFP_SPEC"] / total_ins
    vector = df["ASE_SPEC"] / total_ins
    int = df["DP_SPEC"] / total_ins

    # others = np.maximum(total_ins - loads - stores - branch_instructions, 0)
    others = 0
    other = 0
    # system call rate
    syscall_rate = 0


    post_df = pd.DataFrame({
        "total_ins": total_ins,
        "total_uops": total_uops,
        "cycles": cycles,
        "cycles:k": cycles_k,
        "ipc": ipc,
        "cpi": cpi,
        "instructions": total_ins,

        "branch_miss": branch_miss,
        "branch_misses": branch_misses,
        "branch_instructions": branch_instructions,

        #"llc_cache_mpki": llc_cache_mpki,
        "l1i_cache_mpki": l1i_cache_mpki,
        "l1d_cache_mpki": l1d_cache_mpki,
        # "l2_cache_mpki": l2_cache_mpki,
        # "l3_cache_mpki": l3_cache_mpki,

        "l1d_cache_misses":  l1d_cache_misses,
        "l1d_cache": l1d_cache,
        "l1i_cache_load_misses": l1i_cache_load_misses,
        "l1d_cache_miss": l1d_cache_miss,
        "l1i_cache_loads": l1i_cache_loads,
        "l1i_cache_load_miss": l1i_cache_load_miss,

        "l2_cache_misses":  l2_cache_misses,
        "l2_cache": l2_cache,
        "l2_cache_miss": l2_cache_miss,

        "l3_cache_misses": l3_cache_misses,
        "l3_cache": l3_cache,
        "l3_cache_miss": l3_cache_miss,

        "dtlb_misses": dtlb_misses,
        "dtlb": dtlb,
        "dtlb_miss": dtlb_miss,
        "itlb_misses": itlb_misses,
        "itlb": itlb,
        "itlb_miss": itlb_miss,

        "stlb":  stlb,
        "stlb_misses": stlb_misses,
        "stlb_miss": stlb_miss,

        "load": load,
        "store": store,
        "br": br,
        "fp": fp,
        "int": int,
        "vector": vector,
        "other": other,
        "syscall_rate": syscall_rate,
        "loads": loads,
        "stores": stores,
        "fps": fps,
        "ints": ints,
        "vector_uops": vector_uops, 
        "others": others,
    })
    # }, dtype=float)
    post_df = post_df.astype('float64')


    # print(post_df)

    # # 输出syscall_rate数据
    # print("syscall_rate:\n", syscall_rate)
    # txt_path = os.path.join(parse_path, "syscall_rate.txt")
    # syscall_rate.T.to_csv(txt_path)

    # # 输出l1i_cache_load_miss
    # print("l1i_cache_load_miss:\n", l1i_cache_load_miss)
    txt_path = os.path.join(parse_path, "l1i_cache_load_miss.txt")
    l1i_cache_load_miss.T.to_csv(txt_path)

    # 输出branch_miss数据
    # print("branch_miss:\n", branch_miss)
    txt_path = os.path.join(parse_path, "branch_miss.txt")
    branch_miss.T.to_csv(txt_path)

    # # 输出l1d_cache_miss数据
    # print("l1d_cache_miss:\n", l1d_cache_miss)
    txt_path = os.path.join(parse_path, "l1d_cache_miss.txt")
    l1d_cache_miss.T.to_csv(txt_path)

    # # 输出itlb_miss数据
    # print("iTLB Rate:\n", itlb_miss)
    # txt_path = os.path.join(parse_path, "itlb_miss.txt")
    # itlb_miss.T.to_csv(txt_path)
   
    # print("l3_cache_miss:\n", l3_cache_miss)
    # txt_path = os.path.join(parse_path, "l3_cache_miss.txt")
    # l3_cache_miss.T.to_csv(txt_path)

    # print("br:\n", br)
    txt_path = os.path.join(parse_path, "br.txt")
    br.T.to_csv(txt_path)

    # print("load:\n", load)
    txt_path = os.path.join(parse_path, "load.txt")
    load.T.to_csv(txt_path)

    # print("store:\n", store)
    txt_path = os.path.join(parse_path, "store.txt")
    store.T.to_csv(txt_path)

    # print("vector:\n", vector)
    txt_path = os.path.join(parse_path, "vector.txt")
    vector.T.to_csv(txt_path)

    # print("fp:\n", fp)
    txt_path = os.path.join(parse_path, "fp.txt")
    fp.T.to_csv(txt_path)

    # print("int:\n", int)
    txt_path = os.path.join(parse_path, "int.txt")
    int.T.to_csv(txt_path)

    # print("cpi:\n", cpi)
    txt_path = os.path.join(parse_path, "cpi.txt")
    cpi.T.to_csv(txt_path)

    csv_path = os.path.join(parse_path, "perf-post.csv")
    csv_path2 = os.path.join(parse_path,"T.csv")
    post_df.T.to_csv(csv_path)
    post_df.to_csv(csv_path2)

def parse_bias_perf_stat(WORKSPACE_DIR):
    parse_path = os.path.join(WORKSPACE_DIR, "parse")
    if not os.path.exists(parse_path):
        os.makedirs(parse_path)

    bench_list = os.listdir(WORKSPACE_DIR + "/bias_results")
    stat_list = []
    for bench_name in bench_list:
        perf_path = os.path.join(WORKSPACE_DIR,
                             "bias_results/"+ bench_name + "/TMP.out")
        replace_event_code(perf_path)
        stat = get_perf_stat_result(perf_path)
        stat_list.append(stat)
    df = pd.DataFrame(stat_list, index=bench_list)
    raw_path = os.path.join(parse_path,'bias_raw.csv')
    df.to_csv(raw_path)
    df = df[sorted(df.columns)]

    # metric of L1-dcache
    l1d_cache_misses = df["L1-dcache-load-misses"]

    # metric of L1-icache
    l1i_cache_load_misses = df["L1-icache-load-misses"]

    # metric of L2-cache
    l2_cache_misses = df['L2_RQSTS.MISS']
    l2_cache = df['L2_RQSTS.REFERENCES']

    # metirc of L3-cache
    l3_cache_misses = df['LLC.Misses']
    l3_cache = df['LLC.Reference']

    itlb_misses = df["iTLB-load-misses"]
    dtlb_misses = df["dTLB-load-misses"]

    fps = df["INST_RETIRED.X87"]
    vector_uops = (df["SSEX_UOPS_RETIRED.PACKED_SINGLE"] + df["SSEX_UOPS_RETIRED.SCALAR_SINGLE"] +
            df["SSEX_UOPS_RETIRED.PACKED_DOUBLE"] + df["SSEX_UOPS_RETIRED.SCALAR_DOUBLE"] +
            df["SSEX_UOPS_RETIRED.VECTOR_INTEGER"])

    post_df = pd.DataFrame({
        "l1d_cache_misses":  l1d_cache_misses,
        "l1i_cache_load_misses": l1i_cache_load_misses,

        "l2_cache_misses":  l2_cache_misses,
        "l2_cache": l2_cache,

        "l3_cache_misses": l3_cache_misses,
        "l3_cache": l3_cache,

        "dtlb_misses": dtlb_misses,
        "itlb_misses": itlb_misses,

        "fps": fps,
        "vector_uops": vector_uops,
    }, dtype=np.float)

    csv_path = os.path.join(parse_path, "bias_perf-post.csv")
    csv_path2 = os.path.join(parse_path,"bias_T.csv")
    post_df.T.to_csv(csv_path)
    post_df.to_csv(csv_path2)



### x86 ###

def replace_event_code_x86(perf_path):
    arm_event_code_path = os.path.join(cur_dir, "arm_event_code.json")
    with open(perf_path, "r", encoding="utf-8") as f:
        s = f.read()
    with open(perf_path+".old", "w", encoding="utf-8") as f:
        f.write(s)
    with open(arm_event_code_path, "r" ,encoding="utf-8") as f:
        index2event = json.load(f)['events']
    li1 = []
    li2 = []
    for key in index2event.keys():
        li1.append(key)
        li2.append(index2event[key])
    for i in range(len(li1)):
        s = s.replace(li1[i], li2[i])
    with open(perf_path, "w", encoding="utf-8") as f:
        f.write(s)
