#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
if [ ! -d "$work_dir" ]; then  
    mkdir -p "$work_dir"  
fi
source ${root_dir}/../lib/perf.sh

let "i=0"
while [ $i -le 1023 ]
# let "i=0"
# while [ $i -lt 1 ]
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
    start_time=$(date +%s)
    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
    end_time=$(date +%s)
    execution_time=$((end_time - start_time))
    echo "execution time : $execution_time s"

    # if [ $i -lt 1 ];then
    #     let "i=i+1"
    # else
    #     let "i=i+1"
    # fi
    let "i=i+1"
    # let "i=i+10"
done
python3 ${root_dir}/parse_perf_stat_westmere.py

