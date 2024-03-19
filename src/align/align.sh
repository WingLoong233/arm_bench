#! /bin/bash

cur_dir=`pwd`
li1=("fillrandom_1_65536" "readrandom_1_65536" "readrandom_32_8192" "readrandom_16_65536" "readrandom_16_8192" \
    "readrandom_1_8192" "readrandom_32_65536" "compact_1_65536")
li2=("oltp_write_only.lua_threads128" "oltp_read_only.lua_threads64" "oltp_insert.lua_threads64" \
    "oltp_update_non_index.lua_threads64" \
    "oltp_delete.lua_threads128" "select_random_ranges.lua_threads64" \
    "oltp_read_only.lua_threads128" "oltp_read_write.lua_threads64" "oltp_delete.lua_threads64" \
    "select_random_ranges.lua_threads128" "select_random_points.lua_threads128" "oltp_update_non_index.lua_threads128" \
    "oltp_point_select.lua_threads128" "select_random_points.lua_threads64" "oltp_write_only.lua_threads64" \
    "oltp_insert.lua_threads128" "oltp_point_select.lua_threads64" "oltp_update_index.lua_threads128" \
    "oltp_update_index.lua_threads64" "oltp_read_write.lua_threads128")
li3=("partition_nq300000" "normal_nq300000" "normal_nq200000" "normal_nq100000" "partition_nq200000" "partition_nq100000")

# for target in ${li1[*]}
# do
#     echo "target: ${target}"
#     python3 ${cur_dir}/../lib/generate_set_env.py --target=${target} --directory=${cur_dir}
#     export target
#     source ${cur_dir}/set_env.sh
#     python3 align.py
# done

for target in ${li2[*]}
do
    echo "target: ${target}"
    python3 ${cur_dir}/../lib/generate_set_env.py --target=${target} --directory=${cur_dir}
    export target
    source ${cur_dir}/set_env.sh
    python3 align.py
done

# for target in ${li3[*]}
# do
#     echo "target: ${target}"
#     python3 ${cur_dir}/../lib/generate_set_env.py --target=${target} --directory=${cur_dir}
#     export target
#     source ${cur_dir}/set_env.sh
#     python3 align.py
# done

