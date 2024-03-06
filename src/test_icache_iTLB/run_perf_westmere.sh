#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
source ${root_dir}/../lib/perf.sh

let "i=128"
while [ $i -le 2048 ]
do
    export bench_name=stride${i}
    export bias_flag=False
    cd ${root_dir}
    rm -f generate/stride*.S
    python3 generate/generate.py
    make -C generate
    log_dir=$root_dir/results/${bench_name}
    rm -rf $log_dir && mkdir -p $log_dir
    cmd_line="${work_dir}/${bench_name}"
    repeats=3

    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}

    let "i=i*2"
done

let "i=0"
while [ $i -le 2000 ]
do
    export bench_name=stride${i}
    export bias_flag=False
    cd ${root_dir}
    rm -f generate/stride*.S
    python3 generate/generate.py
    make -C generate
    log_dir=$root_dir/results/${bench_name}
    rm -rf $log_dir && mkdir -p $log_dir
    cmd_line="${work_dir}/${bench_name}"
    repeats=3

    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}

    if [ $i -le 99 ]; then
        let "i=i+1"
    else
        let "i=i+50"
    fi
done

python3 ${root_dir}/parse_perf_stat_westmere.py
