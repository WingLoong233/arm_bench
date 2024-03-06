#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
source ${root_dir}/../lib/perf.sh

let "i=0"
while [ $i -le 1023 ]
do
    export bench_name=threshold${i}
    export bias_flag=False

    cd ${root_dir}
    rm -f generate/threshold*.S
    python3 generate/generate.py
    make -C generate
    log_dir=$root_dir/results/${bench_name}
    echo ${log_dir}

    rm -rf $log_dir && mkdir -p $log_dir
    cmd_line="${work_dir}/${bench_name}"
    cd $work_dir
    repeats=3

    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}

    let "i=i+1"
done
python3 ${root_dir}/parse_perf_stat_westmere.py
