# encoding: utf-8

import pandas as pd
import os,sys
import json
import numpy as np
import random
from scipy.optimize import minimize
import math
from scipy.optimize import nnls
from scipy.optimize import least_squares
import pickle
import datetime

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
sys.path.append(cur_dir+"/../lib")

with open(cur_dir+"/config.json", "r") as f:
    path_dic = json.load(f)["path"]


import generator4

feature_names = ["instructions","cpi","l1d_cache_misses","l1d_cache","l1d_cache_miss",
            "l1i_cache_load_misses","l1i_cache_loads","l1i_cache_load_miss","dtlb_misses",
            "dtlb","dtlb_miss","itlb_misses","itlb","itlb_miss","l2_cache_misses","l2_cache",
            "l2_cache_miss","l3_cache_misses","l3_cache","l3_cache_miss","stlb_misses","stlb","stlb_miss",
            "branch_misses","branch_instructions","branch_miss","load","store","br","fp","int","vector", "other","cpi",
            "loads","stores","fps","ints","others","cycles","total_uops","vector_uops"]

def get_gen_list(csv_path, type_name):
    gen_inf = pd.read_csv(csv_path, index_col=0)
    # 调试用
    # print("align.py, line34, gen_inf:\n", gen_inf)
    # log_path = os.path.join(cur_dir, 'gen_inf.log')
    # gen_inf.to_csv(log_path)

    if type_name == "access_memory":
        name1 = "dcache_dTLB"
    elif type_name == "access_function":
        name1 = "icache_iTLB"
    elif type_name == "branch_prediction":
        name1 = "branch_miss"
    elif type_name == "arithm":
        name1 = "instruction"
    else:
        name1 = "cpi2"
    with open(path_dic["profile"],'r',encoding='utf-8') as f:
        # gen_list1就是profile.json里面的值
        gen_list1 = json.load(f)[name1]
    if type_name == "access_memory":
        cache_size = gen_list1["cache_size"]
        cache_sets = gen_list1["cache_sets"]
        cache_ways = gen_list1["cache_ways"]
        array_name = gen_list1["array_name"]
        array_size = gen_list1["array_size"]
        inner_number = gen_list1["inner_number"]
        outer_number = gen_list1["outer_number"]
    elif type_name == "access_function":
        cache_size = gen_list1["cache_size"]
        cache_sets = gen_list1["cache_sets"]
        cache_ways = gen_list1["cache_ways"]
        array_size = gen_list1["array_size"]
        inner_number = gen_list1["inner_number"]
        outer_number = gen_list1["outer_number"]
    elif type_name == "branch_prediction":
        max_value = gen_list1["max_value"]
        inner_number = 16
        outer_number = gen_list1["outer_number"]
    elif type_name == "arithm":
        inner_number = gen_list1["inner_number"]
        outer_number = gen_list1["outer_number"]
        inner_num_ins = gen_list1["inner_num_ins"]
    else:
        inner_number = gen_list1["inner_number"]
        outer_number = gen_list1["outer_number"]
        inner_num_ins = gen_list1["inner_num_ins"]

    # 原代码有问题
    # 获得对应路径的perf-post.csv的表头，如：
    #  ['stride512c', 'stride256c', 'stride128c', 'stride2048c', 'stride1024c', 'stride4096c']
    # gen_names = gen_inf.columns.values.tolist()[1:]
    gen_names = gen_inf.columns.values.tolist()[:]
    # # # 调试
    # print("gen_names:\n", gen_names)
    # sys.exit()

    gen_list = []
    for name in gen_names:
        feature_dic = dict()
        for feature_name in feature_names:
            feature_dic[feature_name] = gen_inf.loc[feature_name,name]
        if type_name == "access_memory":
            li = name.split("_")
            access_number_per_inner = int(li[2])
            if li[0] == "load":
                is_load = True
            else:
                is_load = False
            if li[1][-1] == 'c':
                change_flag = True
                traversal = True
                stride = int(li[1][0:-1])
            else:
                change_flag = False
                traversal = False
                stride = int(li[1])
            # inner_number = gen_list1["inner_number"] // access_number_per_inner

            inner_number = gen_list1["inner_number"]
            outer_number = gen_list1["outer_number"]
            gen = generator4.Cache(name, cache_size, cache_sets, cache_ways, array_name, array_size,
                    inner_number, outer_number, stride, feature_dic, is_load, access_number_per_inner, traversal, change_flag)
            gen.set_change_flag(change_flag)
        elif type_name == "access_function":
            if name[-1] == "c":
                change_flag = True
                stride = int(name[6:-1])
            else:
                change_flag = False
                stride = int(name[6:])
            # k = gen_list1["inner_number"] * gen_list1["outer_number"]
            # if change_flag:
            #     inner_number = int(array_size / 3 / stride)
            #     outer_number = int(k * stride * 3 / array_size)
            # else:
            #     inner_number = gen_list1["inner_number"]
            #     outer_number = gen_list1["outer_number"]
            inner_number = gen_list1["inner_number"]
            outer_number = gen_list1["outer_number"]
            gen = generator4.Cache2(name, cache_size, cache_sets, cache_ways, array_size,
                    inner_number, outer_number, stride, feature_dic, change_flag)
            gen.set_change_flag(change_flag)
        elif type_name == "branch_prediction":
            threshold = int(name[9:])
            gen = generator4.Branch(name, inner_number, outer_number, threshold, max_value, feature_dic)
        elif type_name == "arithm":
            try:
                head = gen_list1[name]["head"]
            except:
                head = None
            instruction = gen_list1[name]["instruction"]
            gen = generator4.Arithm(name, inner_number, outer_number, head, instruction, feature_dic,20)
        else:
            try:
                head = gen_list1[name]["head"]
            except:
                head = None
            try:
                outer_number = gen_list1[name]["outer_number"]
            except:
                pass
            try:
                inner_number = gen_list1[name]["inner_number"]
            except:
                pass
            try:
                inner_num_ins = gen_list1[name]["inner_num_ins"]
            except:
                pass
            instruction = gen_list1[name]["instruction"]
            # gen = generator4.Arithm("cpi2-"+name, inner_number, outer_number, head, instruction, feature_dic,200)
            gen = generator4.Arithm(name, inner_number, outer_number, head, instruction, feature_dic,inner_num_ins)
        gen_list.append(gen)
    return gen_list

class Test_Result():
    def __init__(self, outer_number_li, feature_dic):
        self.outer_number_li = outer_number_li
        self.feature_dic = feature_dic

def align(target_miss_rate_dic, gen_list, epochs, num_ins):
    log = ""
    print_log = ""
    # 输出目标负载参数
    for k in target_miss_rate_dic.keys():
        v = target_miss_rate_dic[k]
        log += "target {}: {}\n".format(k, v)
        print_log += "target {}: {}\n".format(k, v)
        print("target {}:{}".format(k,v))
    # num_ins = 500000000
    # num_ins = 5000000000

    def align_by_test_result_li(test_result_li, target_miss_rate_dic, num_ins,
            last_test_result=None,last_error_li=None,epoch=1):
        # dcache misses per instruction
        DMPI_li = []
        for i in range(len(test_result_li)):
            DMPI_li.append(test_result_li[i].feature_dic["l1d_cache_misses"] /
                    test_result_li[i].feature_dic["instructions"]) 
        # dcache access per instruction
        DAPI_li = []
        for i in range(len(test_result_li)):
            DAPI_li.append(test_result_li[i].feature_dic["l1d_cache"] / test_result_li[i].feature_dic["instructions"])
        # icahce misses per instruction
        IMPI_li = []
        for i in range(len(test_result_li)):
            IMPI_li.append(test_result_li[i].feature_dic["l1i_cache_load_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # icache access per instruction
        IAPI_li = []
        for i in range(len(test_result_li)):
            IAPI_li.append(test_result_li[i].feature_dic["l1i_cache_loads"] /
                    test_result_li[i].feature_dic["instructions"])
        # l2(second) misses per instruction
        SMPI_li = []
        for i in range(len(test_result_li)):
            SMPI_li.append(test_result_li[i].feature_dic["l2_cache_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # l2(second) access per instruction
        SAPI_li = []
        for i in range(len(test_result_li)):
            SAPI_li.append(test_result_li[i].feature_dic["l2_cache"] /
                    test_result_li[i].feature_dic["instructions"])
        # l3(third) misses per instruction
        TMPI_li = []
        for i in range(len(test_result_li)):
            TMPI_li.append(test_result_li[i].feature_dic["l3_cache_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # l3(third) access per instruction
        TAPI_li = []
        for i in range(len(test_result_li)):
            TAPI_li.append(test_result_li[i].feature_dic["l3_cache"] /
                    test_result_li[i].feature_dic["instructions"])
        # dTLB misses per instruction
        DTMPI_li = []
        for i in range(len(test_result_li)):
            DTMPI_li.append(test_result_li[i].feature_dic["dtlb_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # dTLB access per instruction
        DTAPI_li = []
        for i in range(len(test_result_li)):
            DTAPI_li.append(test_result_li[i].feature_dic["dtlb"] /
                    test_result_li[i].feature_dic["instructions"])
        # iTLB misses per instruction
        ITMPI_li = []
        for i in range(len(test_result_li)):
            ITMPI_li.append(test_result_li[i].feature_dic["itlb_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # iTLB access per instruction
        ITAPI_li = []
        for i in range(len(test_result_li)):
            ITAPI_li.append(test_result_li[i].feature_dic["itlb"] /
                    test_result_li[i].feature_dic["instructions"])
        # sTLB misses per instruction
        STMPI_li = []
        for i in range(len(test_result_li)):
            STMPI_li.append(test_result_li[i].feature_dic["stlb_misses"] /
                test_result_li[i].feature_dic["instructions"])
        # sTLB access per instruction
        STAPI_li = []
        for i in range(len(test_result_li)):
            STAPI_li.append(test_result_li[i].feature_dic["stlb"] /
                test_result_li[i].feature_dic["instructions"])
        # branch misses per instruction
        BMPI_li = []
        for i in range(len(test_result_li)):
            BMPI_li.append(test_result_li[i].feature_dic["branch_misses"] /
                    test_result_li[i].feature_dic["instructions"])
        # branch access(instruction's number) per instruction
        BAPI_li = []
        for i in range(len(test_result_li)):
            BAPI_li.append(test_result_li[i].feature_dic["branch_instructions"] /
                    test_result_li[i].feature_dic["instructions"])
        # vector uops per instruction
        VUPI_li = []
        for i in range(len(test_result_li)):
            VUPI_li.append(test_result_li[i].feature_dic["vector_uops"] /
                    test_result_li[i].feature_dic["instructions"])
        # uops per instruction
        UPI_li = []
        for i in range(len(test_result_li)):
            UPI_li.append(test_result_li[i].feature_dic["total_uops"] /
                    test_result_li[i].feature_dic["instructions"])

        A = []
        b = []
        cnt1 = -1
        cnt2 = -1
        if "l1d_cache_miss" in target_miss_rate_dic.keys():
            cnt1 += 1
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(DMPI_li[i]-DAPI_li[i]*target_miss_rate_dic["l1d_cache_miss"])
                # print(f"dcache misses per instruction[{i}]:\t{DMPI_li[i]}")
                # print(f"dcache per instruction[{i}]:\t\t{DAPI_li[i]}")
                # print(f'target_miss_rate_dic["l1d_cache_miss"]:\t{target_miss_rate_dic["l1d_cache_miss"]}')
                # print(f'{DAPI_li[i]*target_miss_rate_dic["l1d_cache_miss"]}\n')
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["l1d_cache"] * target_miss_rate_dic["l1d_cache_miss"]
                        - last_test_result.feature_dic["l1d_cache_misses"])
            else:
                b.append(0)
        if "l1i_cache_load_miss" in target_miss_rate_dic.keys():
            cnt1 += 1
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(IMPI_li[i]-IAPI_li[i]*target_miss_rate_dic["l1i_cache_load_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["l1i_cache_loads"]*target_miss_rate_dic["l1i_cache_load_miss"]
                        - last_test_result.feature_dic["l1i_cache_load_misses"])
            else:
                b.append(0)
        if "l2_cache_miss" in target_miss_rate_dic.keys():
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(SMPI_li[i]-SAPI_li[i]*target_miss_rate_dic["l2_cache_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["l2_cache"]*target_miss_rate_dic["l2_cache_miss"]
                        - last_test_result.feature_dic["l2_cache_misses"])
            else:
                b.append(0)
        if "l3_cache_miss" in target_miss_rate_dic.keys():
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(TMPI_li[i]-TAPI_li[i]*target_miss_rate_dic["l3_cache_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["l3_cache"]*target_miss_rate_dic["l3_cache_miss"]
                        - last_test_result.feature_dic["l3_cache_misses"])
            else:
                b.append(0)
        if "dtlb_miss" in target_miss_rate_dic.keys():
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(DTMPI_li[i]-DTAPI_li[i]*target_miss_rate_dic["dtlb_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["dtlb"]*target_miss_rate_dic["dtlb_miss"]
                        - last_test_result.feature_dic["dtlb_misses"])
            else:
                b.append(0)
        if "itlb_miss" in target_miss_rate_dic.keys():
            cnt2 += 1
            li = []
            for i in range(len(test_result_li)):
                li.append(ITMPI_li[i]-ITAPI_li[i]*target_miss_rate_dic["itlb_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["itlb"]*target_miss_rate_dic["itlb_miss"]
                        - last_test_result.feature_dic["itlb_misses"])
            else:
                b.append(0)
        if "stlb_miss" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(STMPI_li[i]-STAPI_li[i]*target_miss_rate_dic["stlb_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["stlb"]*target_miss_rate_dic["stlb_miss"]
                        - last_test_result.feature_dic["stlb_misses"])
            else:
                b.append(0)
        if "branch_miss" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(BMPI_li[i]-BAPI_li[i]*target_miss_rate_dic["branch_miss"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["branch_instructions"]*target_miss_rate_dic["branch_miss"]
                        - last_test_result.feature_dic["branch_misses"])
            else:
                b.append(0)
        if "load" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["load"]-target_miss_rate_dic["load"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["load"]
                        - last_test_result.feature_dic["loads"])
            else:
                b.append(0)
        if "store" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["store"]-target_miss_rate_dic["store"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["store"]
                        - last_test_result.feature_dic["stores"])
            else:
                b.append(0)
        if "br" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["br"]-target_miss_rate_dic["br"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["br"]
                        - last_test_result.feature_dic["branch_instructions"])
            else:
                b.append(0)
        if "other" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["other"]-target_miss_rate_dic["other"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["other"]
                        - last_test_result.feature_dic["others"])
            else:
                b.append(0)
        if "fp" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["fp"]-target_miss_rate_dic["fp"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["fp"]
                        - last_test_result.feature_dic["fps"])
            else:
                b.append(0)
        if "int" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["int"]-target_miss_rate_dic["int"])
                # print(f'int{i}: {test_result_li[i].feature_dic["int"]}\n')
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["int"]
                        - last_test_result.feature_dic["ints"])
            else:
                b.append(0)
        if "vector" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                # li.append(VUPI_li[i]-UPI_li[i]*target_miss_rate_dic["vector"])
                li.append(test_result_li[i].feature_dic["vector"]-target_miss_rate_dic["vector"])
            A.append(li)
            if last_test_result is not None:
                # b.append(last_test_result.feature_dic["total_uops"]*target_miss_rate_dic["vector"]
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["vector"]
                        - last_test_result.feature_dic["vector_uops"])
            else:
                b.append(0)
        if "cpi" in target_miss_rate_dic.keys():
            li = []
            for i in range(len(test_result_li)):
                li.append(test_result_li[i].feature_dic["cpi"]-target_miss_rate_dic["cpi"])
            A.append(li)
            if last_test_result is not None:
                b.append(last_test_result.feature_dic["instructions"]*target_miss_rate_dic["cpi"]
                        - last_test_result.feature_dic["cycles"])
            else:
                b.append(0)
        li = []
        print("total chosen count: ", len(test_result_li))
        for i in range(len(test_result_li)):
            li.append(1)
        A.append(li)
        if last_test_result is not None:
            if epoch == 1:
                num_ins0 = num_ins
            else:
                num_ins0 = 0.2 * last_test_result.feature_dic["instructions"]
            b.append(num_ins0)
            for i in range(len(A)-1):
                for j in range(len(A[i])):
                    A[i][j] /= b[i]
                    if error_li is not None:
                        A[i][j] *= abs(error_li[i]) * 100
                b[i] = 1
                if error_li is not None:
                    b[i] *= abs(error_li[i]) * 100
        else:
            b.append(num_ins)
            for i in range(len(A)-1):
                total = sum(A[i])
                # total = math.sqrt(sum(x ** 2 for x in A[i]))
                # print("total", total)
                count = 0
                for j in range(len(A[i])):
                    A[i][j] = A[i][j]  / abs(total)
                    # if abs(A[i][j]) < 1e-5:
                    #     A[i][j] = 0.0
                #     if abs(A[i][j]) < 1e-4:
                #         count = 2
                #     if abs(A[i][j]) < 1e-5:
                #         count = 3
                # for j in range(len(A[i])):
                #     A[i][j] *= 10 ** count
                # here
        # print(A)
        # print(b)
        res0 = nnls(A,b)
        x0 = res0[0]
        return x0

    def cal_outer_number_array(xi, test_result_li, gen_li):
        instructions_array = np.array([x.feature_dic["instructions"] for x in gen_li], dtype=np.float64)
        outer_number_array0 = np.array([x.outer_number for x in gen_li], dtype=np.float64)
        outer_number_array = xi / instructions_array * outer_number_array0
        for i in range(len(outer_number_array)):
            if outer_number_array[i] < 0:
                outer_number_array[i] = 0
            outer_number_array[i] = round(outer_number_array[i])
        return outer_number_array

    def predict(outer_number_array,gen_li,print_flag=True,last_test_result=None):
        my_transform = {
                "l1d_cache_miss": ("l1d_cache_misses", "l1d_cache"),
                "l1i_cache_load_miss": ("l1i_cache_load_misses", "l1i_cache_loads"),
                "l2_cache_miss": ("l2_cache_misses", "l2_cache"),
                "branch_miss": ("branch_misses", "branch_instructions"),
                "load": ("loads", "instructions"),
                "store": ("stores", "instructions"),
                "br": ("branch_instructions", "instructions"),
                "fp": ("fps", "instructions"),
                "int": ("ints", "instructions"),
                "vector": ("vector_uops", "instructions"),
                "cpi": ("cycles", "instructions"),
        }
        ans_li =[]
        for k in target_miss_rate_dic.keys():
            ans1 = 0
            ans2 = 0
            feature1 = my_transform[k][0]
            feature2 = my_transform[k][1]
            for i in range(size):
                ans1 += gen_li[i].feature_dic[feature1] * outer_number_array[i] / gen_li[i].outer_number
                ans2 += gen_li[i].feature_dic[feature2] * outer_number_array[i] / gen_li[i].outer_number
            if last_test_result is not None:
                ans1 += last_test_result.feature_dic[feature1]
                ans2 += last_test_result.feature_dic[feature2]
            ans3 = ans1 / ans2 if ans2 != 0 else 0
            #if feature1 == "branch_misses":
            #    for i in range(size):
            #        ttt = gen_li[i].feature_dic[feature1] * outer_number_array[i] / gen_li[i].outer_number
            #        ttt2 = gen_li[i].feature_dic[feature2] * outer_number_array[i] / gen_li[i].outer_number
            #        print(gen_li[i].name)
            #        print(gen_li[i].is_syscall)
            #        print(ttt)
            #        print(ttt2)
            #    print(ans1)
            #    print(ans2)
            if print_flag:
                print("predict_{}: {}".format(k, ans3))
            ans_li.append(ans3)
            # # 调试
            # # print("feature1,feature2,ans1,ans2")
            # print(feature1)
            # print(feature2)
            # print(ans1)
            # print(ans2)
        ans = 0
        for i in range(size):
            ans += outer_number_array[i] * gen_li[i].feature_dic["instructions"] / gen_li[i].outer_number
        if print_flag:
            print("predict_{}: {}".format("num_ins", ans))
        predict_error_li = []
        count = 0
        for k in target_miss_rate_dic.keys():
            predict_error_li.append((ans_li[count] - target_miss_rate_dic[k])/target_miss_rate_dic[k])
            if print_flag:
                print("predict_{}_error: {}".format(k, predict_error_li[-1]))
            count += 1
        return predict_error_li

    # generate code
    def write_file(gen_li):
        s = ""
        s += gen_li[0].file_begin('main.c')
        s += '\t.text\n'  
        # for i in range(size):
        #     if isinstance(gen_li[i],generator4.Cache):
        #         # s += "\t.data\n"
        #         s += gen_li[i].declare_var(0)
        #         break
        count = 0
        for i in range(size):
            if outer_number_array[i] > 0:
                if isinstance(gen_li[i],generator4.Cache):
                    s += gen_li[i].declare_var(count)
                count += 1
        s += '\t.text\n'
        s += gen_li[0].func_begin('main', 0)
        count = 0
        s1 = ""
        s2 = ""
        s3 = ""
        s4 = ""
        for i in range(size):
            if outer_number_array[i] > 0:
                if isinstance(gen_li[i],generator4.Cache):
                    s1 += gen_li[i].get_one_block(count, int(outer_number_array[i]))
                elif isinstance(gen_li[i],generator4.Cache2):
                    s2 += gen_li[i].get_one_block(count, int(outer_number_array[i]))
                elif isinstance(gen_li[i],generator4.Branch):
                    s3 += gen_li[i].get_one_block(count, int(outer_number_array[i]))
                else:
                    s4 += gen_li[i].get_one_block(count, int(outer_number_array[i]))
                count += 1
        s += s1
        s += s2
        s += s3
        s += s4
        # s += "\tmovl\t$0, %eax\n"
        s += gen_li[0].func_end('main', 0)
        # 尝试将icachefunc放到main函数后
        count = 0
        for i in range(size):
            if outer_number_array[i] > 0:
                if isinstance(gen_li[i],generator4.Cache2):
                    s += gen_li[i].generate_icache_funcs(count)
                count += 1
        s += gen_li[0].file_end()
        print(">>> write_file END<<<")
        with open(cur_dir + '/main.S', 'w', encoding='utf-8') as f:
            f.write(s)
        # sys.exit()

    # make & run_perf
    def test(epoch):
        # print(">>> def test begin <<<")
        os.system("make")
        os.system("./run_perf_westmere.sh")
        # 调试
        # sys.exit()

        target = os.getenv("target")
        p = cur_dir+"/align_results_logs"
        if not os.path.exists(p):
            os.mkdir(p)
        p += f"/{target}"
        if not os.path.exists(p):
            os.mkdir(p)
        p += f"/{epoch}"
        if not os.path.exists(p):
            os.mkdir(p)
        # print("636 line, p:", p)
        os.system("cp " + cur_dir + "/results/main/* " + p)
        os.system("cp " + cur_dir + "/parse/perf-post.csv " + p)
        os.system("cp " + cur_dir + "/main.S " + p)
        os.system("cp " + cur_dir + "/set_env.sh " + p )
        df = pd.read_csv("parse/perf-post.csv",index_col=0)
        feature_dic = dict()
        for feature_name in feature_names:
            feature_dic[feature_name] = df.loc[feature_name,"main"]
        outer_number_li = list(outer_number_array)
        test_result = Test_Result(outer_number_li, feature_dic)
        # print(">>> def test END <<<")
        return test_result


    test_result_li = []
    size = len(gen_list)
    for i in range(size):
        li = [0 for i in range(size)]
        li[i] = gen_list[i].outer_number
        test_result_li.append(Test_Result(li,gen_list[i].feature_dic))

    x = align_by_test_result_li(test_result_li, target_miss_rate_dic, num_ins,None,None,1)
    outer_number_array = cal_outer_number_array(x, test_result_li, gen_list)
    gen_li = []
    for i in range(len(outer_number_array)):
        # print("name:", gen_list[i].name)
        if outer_number_array[i] > 0:
            gen_li.append(gen_list[i])
            # # 调试 
            # print("outer_number:", gen_list[i].outer_number)
            # print("feature_dic:", gen_list[i].feature_dic)
            # print(f"outer_number_array[{i}]:", outer_number_array[i], "\n")
            # # 调试END

    # gen_li = gen_list
    
    # there

    test_result_li = []
    size = len(gen_li)
    # 添加一些log，没啥用
    for i in range(len(gen_li)):
        if isinstance(gen_li[i],generator4.Cache):
            log += "Cache: {}\n".format(gen_li[i].name)
        elif isinstance(gen_li[i],generator4.Cache2):
            log += "Cache2: {}\n".format(gen_li[i].name)
        elif isinstance(gen_li[i],generator4.Branch):
            log += "Branch: {}\n".format(gen_li[i].name)
        else:
            log += "Arithm: {}\n".format(gen_li[i].name)
    for i in range(size):
        li = [0 for i in range(size)]
        li[i] = gen_li[i].outer_number
        test_result_li.append(Test_Result(li, gen_li[i].feature_dic))

    outer_number_array = np.array([1 for i in range(size)])


    epoch = 0
    error_li = []
    for k in target_miss_rate_dic.keys():
        error_li.append(abs(-100 - target_miss_rate_dic[k])/target_miss_rate_dic[k])
    error = max(error_li)
    best_error = 100
    best_epoch = -1

    last_test_result = None
    last_error_li = None

    while (error > 0.01 and epoch < epochs):
        epoch += 1
        x = align_by_test_result_li(test_result_li, target_miss_rate_dic, num_ins,last_test_result, last_error_li,epoch)
        outer_number_array = cal_outer_number_array(x, test_result_li, gen_li) 
        predict_error_li = predict(outer_number_array,gen_li,False,last_test_result)
        if last_test_result is not None:
            for i in range(len(outer_number_array)):
                outer_number_array[i] += last_test_result.outer_number_li[i]
        # sys.exit()
        print_log += "====================\n"
        print_log += f"{epoch}/{epochs}:\n"
        print("====================")
        print(f"{epoch}/{epochs}:")
        for i in range(size):
            if (outer_number_array[i] > 1e-10):
                if isinstance(gen_li[i],generator4.Cache):
                    print("access_block.{}: {}".format(gen_li[i].name, outer_number_array[i]))
                elif isinstance(gen_li[i],generator4.Cache2):
                    print("access_function.{}: {}".format(gen_li[i].name, outer_number_array[i]))
                elif isinstance(gen_li[i],generator4.Branch):
                    print("Branch.{}: {}".format(gen_li[i].name,outer_number_array[i]))
                else:
                    print("Arithm.{}: {}".format(gen_li[i].name,outer_number_array[i]))
                print_log += f".{gen_li[i].name}: {outer_number_array[i]}\n"

        write_file(gen_li) 
        test_result = test(epoch)
        last_test_result = test_result


        # this need more thoughts about how to add test_result ????
        miss_rate_li = []
        error_li = []
        for k in target_miss_rate_dic.keys():
            v1 = test_result.feature_dic[k]
            miss_rate_li.append(v1)
            v2 = target_miss_rate_dic[k]
            # if (k == "fp"):
            #     print("691 line, fp:\ntest_result:", v1, "target_miss_rate:", v2)
            error_li.append((v1-v2)/v2)
        last_error_li = error_li




        s = "{}/{}: ".format(epoch,epochs)
        for i in range(len(miss_rate_li)):
            s += str(miss_rate_li[i])
            if i != len(miss_rate_li) - 1:
                s += ", "
            else:
                s += "\n"
        for i in range(len(outer_number_array)):
            s += "{}".format(outer_number_array[i])
            if i != len(outer_number_array) - 1:
                s += ", "
            else:
                s += "\n"
        #print(s) 

        log += s
        log += "predict_error=("
        for i in range(len(predict_error_li)):
            log += "{}".format(predict_error_li[i])
            if i != len(predict_error_li) - 1:
                log += ", "
            else:
                log += ")\n"
        log += "error=("

        # metric_list ：target_miss_rate_dic，用来输出
        metric_list = list(target_miss_rate_dic.keys())
        print_log += "----predict_error----\n"
        print("----predict_error----")
        for i in range(len(predict_error_li)):
            print_log += f"predict error {metric_list[i]}={predict_error_li[i]}\n"
            print(f"predict error {metric_list[i]}={predict_error_li[i]}")
        print_log += "----real_error----\n"
        print("----real_error----")
        for i in range(len(error_li)):
            print_log += f"error {metric_list[i]}={error_li[i]}\n"
            print(f"error {metric_list[i]}={error_li[i]}")
            log += "{}".format(error_li[i])
            if i != len(error_li) - 1:
                log += ", "
            else:
                log += ")\n"

        error = max(map(lambda x: abs(x),error_li))
        print_log += f"error={error}\n"
        print(f"error={error}")
        if error < best_error:
            best_error = error
            best_epoch = epoch
        target = os.getenv("target")
        p = cur_dir + "/align_test_result_logs"
        if not os.path.exists(p):
            os.mkdir(p)
        if not os.path.exists(p + "/" + target):
            os.mkdir(p+ "/" + target)
        with open(p + "/" + target + "/test_result{}".format(epoch),"wb") as f:
            pickle.dump(test_result, f)

    log += "best epoch: {}\n".format(best_epoch)
    log += "best error: {}\n".format(best_error)
    if not os.path.exists("align_logs"):
        os.mkdir("align_logs")
    if not os.path.exists("align_logs/error0.01"):
        os.mkdir("align_logs/error0.01")
    if not os.path.exists("align_logs/error0.02"):
        os.mkdir("align_logs/error0.02")
    if not os.path.exists("align_logs/error0.05"):
        os.mkdir("align_logs/error0.05")
    if not os.path.exists("align_logs/error0.1"):
        os.mkdir("align_logs/error0.1")
    if not os.path.exists("align_logs/error0.15"):
        os.mkdir("align_logs/error0.15")
    if not os.path.exists("align_logs/other"):
        os.mkdir("align_logs/other")
    if best_error < 0.01:
        directory = "align_logs/error0.01"
    elif best_error < 0.02:
        directory = "align_logs/error0.02"
    elif best_error < 0.05:
        directory = "align_logs/error0.05"
    elif best_error < 0.1:
        directory = "align_logs/error0.1"
    elif best_error < 0.15:
        directory = "align_logs/error0.15"
    else:
        directory = "align_logs/other"
    target = os.getenv("target")
    with open(directory + "/{}.log".format(target), "w", encoding="utf-8") as f:
        f.write(log)

    print_log += f"best epoch: {best_epoch}\n"
    print_log += f"best error: {best_error}\n"
    print("best epoch: {}".format(best_epoch))
    print("best error: {}".format(best_error))

    # print_log输出
    if not os.path.exists("print_logs"):
        os.mkdir("print_logs")
    print_directory = "print_logs"
    target = os.getenv("target")
    # 获得当前时间
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime('%Y-%m-%d_%H-%M-%S')
    with open(print_directory + f"/{current_time_str}_{target}.log", "w", encoding="utf-8") as f:
        f.write(print_log)  

if __name__ == "__main__":
    target_l1d_cache_miss = float(os.getenv("target_l1d_cache_miss"))
    target_l1i_cache_load_miss = float(os.getenv("target_l1i_cache_load_miss"))
    target_l2_cache_miss = float(os.getenv("target_l2_cache_miss"))
    target_l3_cache_miss = float(os.getenv("target_l3_cache_miss"))
    target_dtlb_miss = float(os.getenv("target_dtlb_miss"))
    target_itlb_miss = float(os.getenv("target_itlb_miss"))
    target_stlb_miss = float(os.getenv("target_stlb_miss"))
    target_branch_miss = float(os.getenv("target_branch_miss"))
    target_load = float(os.getenv("target_load"))
    target_store = float(os.getenv("target_store"))
    target_br = float(os.getenv("target_br"))
    target_fp = float(os.getenv("target_fp"))
    target_int = float(os.getenv("target_int"))
    target_vector = float(os.getenv("target_vector"))
    target_other = float(os.getenv("target_other"))
    target_cpi = float(os.getenv("target_cpi"))

    type_names = ["access_function", "access_memory", "branch_prediction", "arithm2"]
    gen_list = []
    for type_name in type_names:
        gen_list += get_gen_list(path_dic[type_name], type_name)

    target_miss_rate_dic = {
        "l1d_cache_miss": target_l1d_cache_miss if target_l1d_cache_miss >= 1e-4 else None,
        "l1i_cache_load_miss": target_l1i_cache_load_miss if target_l1i_cache_load_miss >= 1e-4 else None,
        # "l2_cache_miss": target_l2_cache_miss if target_l2_cache_miss >= 1e-4 else None,
        "branch_miss": target_branch_miss if target_branch_miss >= 1e-4 else None,
        "load": target_load if target_load >= 1e-4 else None,
        "store": target_store if target_store >= 1e-4 else None,
        "br": target_br if target_br >= 1e-4 else None,
        "cpi": target_cpi if target_cpi >= 1e-4 else None,
        "int": target_int if target_int >= 1e-4 else None,
        "fp": target_fp if target_fp >= 1e-4 else None,
        "vector": target_vector if target_vector >= 1e-4 else None,
    }

    target_miss_rate_dic = {k: v for k, v in target_miss_rate_dic.items() if v is not None}


    # df = pd.DataFrame.from_dict(target_miss_rate_dic, orient='index')
    # print(df)
    # epochs = 10
    epochs = 5
    # num_ins = 500000000
    num_ins = 1000000000
    align(target_miss_rate_dic, gen_list, epochs, num_ins)

