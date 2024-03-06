#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
source ${root_dir}/../lib/perf.sh


for access_number_per_inner in "1" "2" "4" "128"
do
    for cate in "load" "store"
    do

        let "i=0"
        # while [ $i -lt 10001 ]
        while [ $i -eq 0 ]
        do
            export bench_name=${cate}_${i}_${access_number_per_inner}
            export bias_flag=False
            cd ${root_dir}
            python3 generate/generate.py
            # make -C generate
            log_dir=$root_dir/results/${bench_name}
            rm -rf $log_dir && mkdir -p $log_dir
            cmd_line="${work_dir}/${bench_name}"
            repeats=3
            # perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
            # rm -f ${root_dir}/generate/${bench_name}.S
            if [ $i -lt 100 ];then
                let "i=i+1"
            else
                let "i=i+100"
            fi
        done

        # let "i=128"
        # while [ $i -lt 2049 ]
        # do
        #     export bench_name=${cate}_${i}_${access_number_per_inner}
        #     export bias_flag=False
        #     cd ${root_dir}
        #     python3 generate/generate.py
        #     make -C generate
        #     log_dir=$root_dir/results/${bench_name}
        #     rm -rf $log_dir && mkdir -p $log_dir
        #     cmd_line="${work_dir}/${bench_name}"
        #     repeats=3
        #     # perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
        #     # rm -f ${root_dir}/generate/${bench_name}.S
        #     let "i=i*2"
        # done

        # let "i=1"
        # while [ $i -lt 2049 ]
        # do
        #     export bench_name=${cate}_${i}c_${access_number_per_inner}
        #     export bias_flag=False
        #     cd ${root_dir}
        #     python3 generate/generate.py
        #     make -C generate
        #     log_dir=$root_dir/results/${bench_name}
        #     rm -rf $log_dir && mkdir -p $log_dir
        #     cmd_line="${work_dir}/${bench_name}"
        #     repeats=3
        #     # perf_cmd ${repeats} ${log_dir} -1 ${cmd_line}
        #     # rm -f ${root_dir}/generate/${bench_name}.S
        #     let "i=i*2"
        # done
    done
done

# python3 ${root_dir}/parse_perf_stat_westmere.py
