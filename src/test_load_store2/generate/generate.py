#encoding: utf-8

import os,sys
import json

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
sys.path.append(cur_dir+"/../../lib")

import gen_tool

if __name__ == "__main__":
    bench_name = os.getenv('bench_name')
    bias_flag = os.getenv("bias_flag")

    with open(cur_dir + '/../../profile.json', 'r' ,encoding='utf-8') as f:
        data = json.load(f)['dcache_dTLB']
        
    # k = data["inner_number"] * data["outer_number"]

    li = bench_name.split("_")
    print("store/load:\t\t\t\t" + li[0])
    print("两次访问之间的间距 stride:\t\t" + li[1])
    print("连续访问次数access_number_per_inner:\t" + li[2])

    array_name = data['array_name']
    array_size = data['array_size']
    inner_number = data["inner_number"]
    outer_number = data["outer_number"]
    is_load = True if li[0] == "load" else False
    access_number_per_inner = int(li[2])
    change_flag = True if li[1][-1] == 'c' else False
    stride = int(li[1][0:-1]) if change_flag else int(li[1])

    # if li[1][-1] == 'c':
    #     traversal = True
    #     stride = int(li[1][0:-1])
    # else:
    #     traversal = False
    #     stride = int(li[1]) 

    # if bias_flag == "True":
    #     if li[1][-1] == 'c':
    #         outer_number = array_size // (data["inner_number"] * stride)
    #     else:
    #         outer_number = 1


    s = gen_tool.file_begin('main.c')
    # s += "\t.text\n"
    s += gen_tool.declare_var(array_name, array_size, 0)
    s += '\t.text\n'
    s += gen_tool.func_begin('main', 0)
    s += gen_tool.access_block2(array_name, array_size, 0, inner_number, outer_number, stride, change_flag, is_load,
            access_number_per_inner)
    s += gen_tool.func_end('main', 0)
    s += gen_tool.file_end()
    
    with open(cur_dir + '/' + bench_name + '.S', 'w', encoding='utf-8') as f:
        f.write(s)


