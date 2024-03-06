#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}"
source ${root_dir}/../lib/perf.sh
declare -a bench_name_arr=("main")
for bench_name in ${bench_name_arr[@]}
do
    log_dir=$root_dir/results/${bench_name}/
    echo ${log_dir}
    rm -rf $log_dir && mkdir -p $log_dir/
    cmd_line="${work_dir}/${bench_name}"
    cd $work_dir
    repeats=3
    perf_cmd2 ${repeats} ${log_dir} -1 ${cmd_line} 
done
python3 ${root_dir}/parse_perf_stat_westmere.py
