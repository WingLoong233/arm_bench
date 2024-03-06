#encoding: utf-8

import os,sys
import json

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
sys.path.append(cur_dir+"/../../lib")

import gen_tool

if __name__ == "__main__":
    s = ''
    s += gen_tool.generate_icache_func11(6000000)
    # s += gen_tool.generate_icache_func(8000000)
    with open(f'{cur_dir}/func11.S', 'w', encoding='utf-8') as f:
        f.write(s)