#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
if [ ! -d "$work_dir" ]; then  
    mkdir -p "$work_dir"  
fi
source ${root_dir}/../lib/perf.sh

# 新版change
# let "i=1"
# # let "i=32"
# # while [ $i -le 32 ]
# while [ $i -le 2048 ]
# do
#     export bench_name=stride${i}c
#     export bias_flag=False
#     cd ${root_dir}
#     rm -f generate/stride*.S
#     python3 generate/generate.py
#     make -C generate change
#     log_dir=$root_dir/results/${bench_name}
#     rm -rf $log_dir && mkdir -p $log_dir
#     cmd_line="${work_dir}/${bench_name}"
#     repeats=3
#     start_time=$(date +%s)
#     perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
#     end_time=$(date +%s)
#     execution_time=$((end_time - start_time))
#     echo "execution time : $execution_time s"

#     # let "i=i*2"
#     if [ $i -le 31 ]; then
#         let "i=i+1"
#     # elif [ $i -lt 128 ]; then
#     #     let "i=i+16"
#     else
#         let "i=i*2"
#     fi
# done


# # 老版change
# let "i=1"
# while [ $i -le 32 ]
# # while [ $i -le 64 ]
# # while [ $i -le 2048 ]
# do
#     export bench_name=stride${i}c
#     export bias_flag=False
#     cd ${root_dir}
#     rm -f generate/stride*.S
#     python3 generate/generate.py
#     make -C generate change
#     log_dir=$root_dir/results/${bench_name}
#     rm -rf $log_dir && mkdir -p $log_dir
#     cmd_line="${work_dir}/${bench_name}"
#     repeats=3
#     start_time=$(date +%s)
#     perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
#     end_time=$(date +%s)
#     execution_time=$((end_time - start_time))
#     echo "execution time : $execution_time s"

#     if [ $i -le 1 ]; then
#         let "i=i+1"
#     else
#         let "i=i*2"
#     fi
# done


# 新新版change
let "i=1"
# let "i=32"
# while [ $i -le 32 ]
# while [ $i -le 64 ]
while [ $i -le 512 ]
do
    export bench_name=stride${i}c
    export bias_flag=False
    cd ${root_dir}
    rm -f generate/stride*c.S
    python3 generate/generate.py
    make -C generate change
    log_dir=$root_dir/results/${bench_name}
    rm -rf $log_dir && mkdir -p $log_dir
    cmd_line="${work_dir}/${bench_name}"
    repeats=3
    start_time=$(date +%s)
    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
    end_time=$(date +%s)
    execution_time=$((end_time - start_time))
    echo "execution time : $execution_time s"


    if [ $i -lt 16 ]; then
        let "i=i+1"
    elif [ $i -lt 64 ]; then
        let "i=i+1"
    # elif [ $i -lt 128 ]; then
    #     let "i=i+16"
    else
        let "i=i*2"
    fi
done


let "i=1"
# let "i=2048"
# while [ $i -le 2048 ]
while [ $i -le 4096 ]
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

    start_time=$(date +%s)
    perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
    end_time=$(date +%s)
    execution_time=$((end_time - start_time))
    echo "execution time : $execution_time s"


    if [ $i -lt 16 ]; then
        let "i=i+1"
    elif [ $i -lt 64 ]; then
        let "i=i+1"
    # elif [ $i -lt 128 ]; then
    #     let "i=i+16"
    else
        let "i=i*2"
    fi
    # let "i=i*2"
done


# let "i=50"
# while [ $i -le 2000 ]
# do
#     export bench_name=stride${i}
#     export bias_flag=False
#     cd ${root_dir}
#     rm -f generate/stride*.S
#     python3 generate/generate.py
#     make -C generate
#     log_dir=$root_dir/results/${bench_name}
#     rm -rf $log_dir && mkdir -p $log_dir
#     cmd_line="${work_dir}/${bench_name}"
#     repeats=3
#     start_time=$(date +%s)
#     perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
#     end_time=$(date +%s)
#     execution_time=$((end_time - start_time))
#     echo "execution time : $execution_time s"

#     let "i=i+50"
# done

python3 ${root_dir}/parse_perf_stat_westmere.py
