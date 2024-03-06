#encoding: utf-8

import os,sys
import json

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
sys.path.append(cur_dir+"/../../lib/")

import gen_tool

if __name__ == "__main__":
    bench_name = os.getenv('bench_name')
    bias_flag = os.getenv("bias_flag")

    with open(cur_dir + '/../../profile.json', 'r' ,encoding='utf-8') as f:
        data = json.load(f)['branch_miss']
    threshold = int(bench_name[9:])
    # outer_number = 30000000
    # try:
    #     threshold = data[bench_name]['threshold']
    # except:
    #     threshold = int(bench_name[9:])
    print("threshold:\t" + str(threshold))

    max_value = data['max_value']
    outer_number = data['outer_number']
    # try:
    #     max_value = data[bench_name]['max_value']
    # except:
    #     max_value = data['max_value']
    # try:
    #     outer_number = data[bench_name]['outer_number']
    # except:
    #     outer_number = data['outer_number']
    # if bias_flag == "True":
    #     outer_number = 1

    s = gen_tool.file_begin('main.c')
    s += "\t.text\n"
    s += gen_tool.func_begin('main', 0)
    # s += gen_tool.generate_jmp_block(threshold, outer_number)
    s += gen_tool.generate_jmp_block(0, threshold, max_value, outer_number)
    s += gen_tool.func_end('main', 0)
    # s += gen_tool.generate_jmp_func(1, return_reg="x30")
    s += gen_tool.file_end()
    with open(cur_dir + '/' + bench_name + '.S', 'w', encoding='utf-8') as f:
        f.write(s)


