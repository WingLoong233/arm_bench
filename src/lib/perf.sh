#!/bin/bash

function perf_cmd(){
    repeats=$1
    log_dir=$2
    process_id=$3
    cmd_line=${*:4}
    if [ ! -d ${log_dir} ]; then
        mkdir -p ${log_dir}
    fi
    echo "~~~~~~"
    echo ${process_id}
    if [ ${process_id} -eq -1 ];then
        set -x
        (time perf stat -r ${repeats} \
            -e 'r8,r11,r10,r12' \
            -e 'r3,r4,r1,r14' \
            -e 'r17,r16,r37,r36' \
            -e 'r5,r25,r2,r26,r2D,r2F' \
            -e 'r70,r71,r73,r75,r74' \
            -o ${log_dir}/perf.out \
            ${cmd_line}) \
        > /dev/null 2> $log_dir/run.perf.err
        #> $log_dir/run.perf.log 2> $log_dir/run.perf.err
        # 删除了r2A,r2B（L3D_CACHE_REFILL,L3D_CACHE）没用
        set +x
    else
        set -x
		# -e 'instructions,cycles,cycles:u,cycles:k' \
		# -e 'branch-load-misses,branch-loads' \
		# -e 'L1-dcache-load-misses,L1-dcache-loads' \
		# -e 'L1-icache-load-misses,L1-icache-loads' \
		# -e 'r17,r16,r37,r36' \
		# -e 'dTLB-load-misses,dTLB-loads' \
		# -e 'iTLB-load-misses,iTLB-loads' \
		# -e 'r2D,r2F' \
		# -e 'r70,r71,r73,r75,r74' \
        (time perf stat -r ${repeats} \
            -e 'r8,r11,r10,r12' \
            -e 'r3,r4,r1,r14' \
            -e 'r17,r16,r37,r36' \
            -e 'r5,r25,r2,r26,r2D,r2F' \
            -e 'r70,r71,r73,r75,r74' \
            -o ${log_dir}/perf.out \
            -p ${process_id} \
            ${cmd_line}) \
        > /dev/null 2> $log_dir/run.perf.err
        set +x
    fi
}



#  , , , 
#  , ,l2dcachem,l2dcaches
# l3dcachem,l3dcaches, , 
#  , , , 
#  , ,l2TLB_m,l2TLB,vector
# ld,st,int,fp

function perf_cmd2(){
    repeats=$1
    log_dir=$2
    process_id=$3
    cmd_line=$4

    declare -a events=( \
        "r8,r11,r10,r12" \
        "r3,r4,r1,r14" \
        "r17,r16,r37,r36,r2F" \
        "r5,r25,r2,r26,r2D" \
        "r70,r71,r73,r75,r74" \
    )

    for ((i=0;i<${#events[@]};i++)); do
        sub_perf_cmd "$repeats" "$log_dir" "$process_id" "$cmd_line" "$i" "${events[$i]}"
    done

    # 指定要处理的文件名规则，如sub_perf1.out、sub_perf2.out等
    pattern="sub_perf*.out"

    # 删除前五行和最后一行，并将结果输出到新文件中
    for file in ${log_dir}/${pattern}; do
        tail -n +6 "${file}" | head -n -2 > "${file}.tmp"
    done

    # 将所有临时文件合并为一个文件 perf.out
    cat ${log_dir}/${pattern}.tmp > ${log_dir}/perf.out


    # 删除所有临时文件
    rm ${log_dir}/${pattern}
    rm ${log_dir}/${pattern}.tmp
}


function sub_perf_cmd(){
    repeats=$1
    log_dir=$2
    process_id=$3
    cmd_line=$4
    i=$5
    event=$6
    # echo $i
    # echo $event
    if [ ! -d ${log_dir} ]; then
        mkdir -p ${log_dir}
    fi
    if [ ${process_id} -eq -1 ];then
        set -x
        (time perf stat -r ${repeats} \
            -e "${event}" \
            -o ${log_dir}/sub_perf${i}.out \
            ${cmd_line}) \
        > /dev/null 2> $log_dir/run.perf.err
        #> $log_dir/run.perf.log 2> $log_dir/run.perf.err
        set +x
    else
        set -x
        (time perf stat -r ${repeats} \
            ${event} \
            -o ${log_dir}/sub_perf${i}.out \
            -p ${process_id} \
            ${cmd_line}) \
        > /dev/null 2> $log_dir/run.perf.err
        set +x
    fi
}



