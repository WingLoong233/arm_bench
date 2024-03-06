#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
if [ ! -d "$work_dir" ]; then  
    mkdir -p "$work_dir"  
fi
source ${root_dir}/../lib/perf.sh

let "i=1"
while [ $i -le 512 ]
# while [ $i -le 2048 ]
do
    export bench_name=stride${i}c
    export bias_flag=False
    cd ${root_dir}
    rm -f generate/stride*.S
    python3 generate/generate.py
    make -C generate change
    log_dir=$root_dir/results/${bench_name}
    rm -rf $log_dir && mkdir -p $log_dir
    cmd_line="${work_dir}/${bench_name}"
    repeats=3
    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}

    let "i=i*2"
done

# let "i=1"
# while [ $i -le 200 ]
# let "i=100"
# while [ $i -le 200 ]
let "i=1"
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

    if [ $i -le 31 ]; then
        let "i=i+1"
    # elif [ $i -lt 128 ]; then
    #     let "i=i+16"
    else
        let "i=i*2"
    fi
    # let "i=i*2"
done

python3 ${root_dir}/parse_perf_stat_westmere.py