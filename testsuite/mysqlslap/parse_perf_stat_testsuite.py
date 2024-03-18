# encoding: utf-8
import os,sys

cur_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cur_dir+"/../../src/lib")

from parse_perf import parse_perf_stat

if __name__ == "__main__":
    parse_perf_stat(cur_dir)

