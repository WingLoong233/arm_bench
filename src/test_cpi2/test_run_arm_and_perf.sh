#!/bin/bash
root_dir=`pwd`
work_dir="${root_dir}/build"
if [ ! -d "$work_dir" ]; then  
    mkdir -p "$work_dir"  
fi
source ${root_dir}/../lib/perf.sh

# declare -a bench_name_arr=("vector_add" "x87_add" \
# "ILP4_add_0_r32" \
# "add_r32_r32" "subl_r32_r32" \
# "mul_r8" "imul_r8" "mul_r16" "imul_r16" "mul_r32" "imul_r32")

# declare -a bench_name_arr=( \
# "add_r32_r32" "ILP4_add_0_r32" "sub_r32_r32" \
# "mul_r32" "smull_r32" "mul_r64" "smulh_r64" \
# "float_add" "vector_add" "div_r64" "syscall" "nop" "mov"\
# )

declare -a bench_name_arr=( \
"add_r32_r32" "float_add" "float_add_1" "float_add_2" \
"vector_add" "syscall" "nop" "mov" \
)

# declare -a bench_name_arr=("float_add")

for bench_name in ${bench_name_arr[@]}
do
    export bench_name
    export bias_flag=False
    cd ${root_dir}
    # rm -f generate/*.S
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
done
python3 ${root_dir}/parse_perf_stat_westmere.py
