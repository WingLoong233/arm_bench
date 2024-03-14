#! /bin/bash
cur_dir=`pwd`

has_c_folder=false

for folder in ${cur_dir}/results/*/ ; do
    echo $folder
    if [[ -d "$folder" && "$folder" == *c* ]]; then
        has_c_folder=true
        break
    fi
done

if $has_c_folder; then
    echo 'rm c'
    rm -rf ${cur_dir}/results/*c/
    python3 ${cur_dir}/parse_perf_stat_westmere.py
else
    echo 'get_c'
    cp -r ${cur_dir}/results_5_c/* ${cur_dir}/results/
    python3 ${cur_dir}/parse_perf_stat_westmere.py
fi
