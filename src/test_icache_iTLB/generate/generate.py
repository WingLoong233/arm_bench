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
        data = json.load(f)['icache_iTLB']

    # if bench_name[-1] == 'c':
    #     change_flag = True
    #     stride = int(bench_name[6:-1])
    # else:
    #     change_flag = False
    #     stride = int(bench_name[6:])

    # if change_flag:
    #     inner_number = int(array_size / 3 / stride)
    #     outer_number = int(k * stride * 3 / array_size)
    # else:
    #     inner_number = data["inner_number"]
    #     outer_number = data["outer_number"]

    k = data["inner_number"] * data["outer_number"]
    array_size = data['array_size']

    change_flag = bench_name.endswith('c')
    stride = int(bench_name[6:-1]) if change_flag else int(bench_name[6:])
    inner_number = data["inner_number"]
    outer_number = data["outer_number"]

    print(f"stride:\t\t{stride}")
    print(f"change_flag:\t{change_flag}")
    # print("outer_number:\t", outer_number)

    # if bias_flag == "True":
    #     outer_number = 1

    # s = gen_tool.file_begin('main.c')
    # s += '\t.text\n'
    # s += gen_tool.generate_icache_func(stride, inner_number)
    # main_index = inner_number + 100
    # s += gen_tool.func_begin('main', main_index)
    # s += gen_tool.icache_block(main_index, outer_number)
    # s += gen_tool.func_end('main', main_index)

    s = ""
    s += gen_tool.file_begin('main.c')
    s += '\t.text\n'
    # 只有change_flag == True时才生成函数，否则返回""
    s += gen_tool.generate_icache_funcs(0, inner_number, stride, change_flag)
    s += gen_tool.func_begin('main', 0)
    s += gen_tool.access_func2(0, inner_number, outer_number, stride, change_flag)
    s += gen_tool.func_end('main', 0)
    s += gen_tool.file_end()

    with open(cur_dir + '/' + bench_name + '.S', 'w', encoding='utf-8') as f:
        f.write(s)

