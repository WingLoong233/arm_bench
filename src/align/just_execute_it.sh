#! /bin/bash
align_dir=`pwd`

# # 负载结果parse并移动到指定位置
# cd ${align_dir}/../testsuite/
# sh parse_testsuite_and_move.sh

# 基本块结果重新parse
# for dir in "test_load_store2" "test_icache_iTLB" "test_branch_miss" "test_cpi2"
# do
#     cd ${align_dir}/../${dir}
#     python3 ./parse_perf_stat_westmere.py
# done

python3 ${align_dir}/../set_config.py
cd ${align_dir}
export target=readrandom_32_65536  # 对齐负载的名称, 例如readrandom_1_65536,oltp_read_write.lua_threads64,normal_nq100000, oltp_delete.lua_threads128等
echo "\ntarget: $target"
python3 ${align_dir}/../lib/generate_set_env.py --target=${target} --directory=${align_dir}
source ${align_dir}/set_env.sh
python3 align.py
