# encoding: utf-8
import json
import os,sys

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
sys.path.append(cur_dir+"/../../lib")

import gen_tool

if __name__ == '__main__':
    bench_name = os.getenv('bench_name')
    bias_flag=os.getenv("bias_flag")
    with open(cur_dir+'/../../profile.json','r',encoding='utf-8') as f:
        data = json.load(f)['cpi2']
    outer_number = data["outer_number"]
    inner_number = data["inner_number"]
    instruction = data[bench_name]["instruction"]
    inner_num_ins = data["inner_num_ins"]
    try:
        head = data[bench_name]["head"]
    except:
        head = None
    try:
        outer_number = data[bench_name]["outer_number"]
    except:
        pass
    try:
        inner_number = data[bench_name]["inner_number"]
    except:
        pass
    try:
        inner_num_ins = data[bench_name]["inner_num_ins"]
    except:
        pass
    if bias_flag == "True":
        outer_number = 1

    print("inner_number:\t", inner_number)
    print("outer_number:\t", outer_number)
    s = gen_tool.file_begin('main.c')
    s += '\t.text\n'
    s += gen_tool.func_begin('main', 0)
    s += gen_tool.arithm_block2(0, outer_number, inner_number, instruction, head, inner_num_ins)
    s += gen_tool.func_end('main', 0)
    s += gen_tool.file_end()
    with open(cur_dir + '/' + bench_name + '.S', 'w', encoding='utf-8') as f:
        f.write(s)
