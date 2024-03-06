## 1. 测量基本块的各项指标

```shell
sh run_basic_block.sh
# 4类基本块，对应目录分别为test_load_store2,test_icache_iTLB,test_branch_miss,test_cpi2
# 运行结果的perf原始数据保存在{}/restuls,处理过的版本保存在{}/parse/perf-post.csv
```

## 2. 使用基本块构造代理负载

```shell
python3 set_config.py
cd align
cur_dir=`pwd`
export target=normal_nq200000 # 对齐负载的名称, 例如readrandom_1_65536,oltp_read_write.lua_threads64,normal_nq100000等
python3 ${cur_dir}/../lib/generate_set_env.py --target=${target} --directory=${cur_dir}
source ${cur_dir}/set_env.sh
python3 align.py
# 运行结果保存在align_logs和align_results_logs中，前者保存各类基本块运行的次数和各项指标的误差，后者保存各项指标的测量结果以及代理负载的具体代码
```

