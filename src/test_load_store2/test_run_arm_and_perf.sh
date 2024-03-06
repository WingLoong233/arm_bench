#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
if [ ! -d "$work_dir" ]; then  
    mkdir -p "$work_dir"  
fi
source ${root_dir}/../lib/perf.sh

for cate in "load" "store"
do
    for access_number_per_inner in "1" "2" "4" "8" "16" "32" "64" "128"
    # for access_number_per_inner in "1" "2" "4" "16" "64"
    do
        let "i=0"
        # while [ $i -le 4096 ]
        while [ $i -le 2048 ]
        do
            # i*access_number_per_inner小于等于256 或 (i 是 8 的整数倍 且 i*access_number_per_inner <32760)
            if [[ $(( i*access_number_per_inner*4 )) -le 256 ]] || [[ $(( i % 2 )) -eq 0 && $(( i*access_number_per_inner*4 )) -lt 32760 ]]; then
            # if [[ $(( i*access_number_per_inner )) -le 256 ]] || [[ $(( i % 8 )) -eq 0 && $(( i*access_number_per_inner )) -lt 32760 ]]; then
                export bench_name=${cate}_${i}_${access_number_per_inner}
                export bias_flag=False
                cd ${root_dir}
                rm -f generate/${cate}*.S
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
                # rm -f ${root_dir}/generate/${bench_name}.S
            fi

            # 比较好
            if [ $i -lt 128 ];then
                let "i=i+1"
            elif [ $i -lt 1024 ];then
                let "i=i+128"
            else
                let "i=i*2"
            fi

            # if [ $i -lt 8 ];then
            #     let "i=i+1"
            # elif [ $i -lt 128 ]; then
            #     # let "i=i+8"
            #     let "i=i*2"
            # else
            #     # let "i=i+128"
            #     let "i=i*2"
            # fi
        done
    done
    
    for access_number_per_inner in "256" "512" "1024"
    do
        let "i=0"
        while [ $i -le 0 ]
        do
            if [[ $(( i*access_number_per_inner*4 )) -le 256 ]] || [[ $(( i % 2 )) -eq 0 && $(( i*access_number_per_inner*4 )) -lt 32760 ]]; then
                export bench_name=${cate}_${i}_${access_number_per_inner}
                export bias_flag=False
                cd ${root_dir}
                rm -f generate/${cate}*.S
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
            fi
            let "i=i+10"
        done
    done

    # change模式误差太大，放弃
    # for access_number_per_inner in "4" "16"
    # for access_number_per_inner in "4"
    # do
    #     let "i=64"
    #     while [ $i -le 512 ]
    #     # let "i=1"
    #     # while [ $i -le 128 ]
    #     do
    #         if [[ $(( i*access_number_per_inner*4 )) -le 256 ]] || [[ $(( i % 2 )) -eq 0 && $(( i*access_number_per_inner*4 )) -lt 32760 ]]; then
    #             export bench_name=${cate}_${i}c_${access_number_per_inner}
    #             export bias_flag=False
    #             cd ${root_dir}
    #             rm -f generate/${cate}*.S
    #             python3 generate/generate.py
    #             make -C generate
    #             log_dir=$root_dir/results/${bench_name}
    #             rm -rf $log_dir && mkdir -p $log_dir
    #             cmd_line="${work_dir}/${bench_name}"
    #             repeats=3
    #             start_time=$(date +%s)
    #             perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
    #             end_time=$(date +%s)
    #             execution_time=$((end_time - start_time))
    #             echo "execution time : $execution_time s"
    #         fi
    #         let "i=i*2"
    #     done
    # done
done

python3 ${root_dir}/parse_perf_stat_westmere.py