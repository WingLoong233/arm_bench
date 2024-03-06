cur_dir=`pwd`

for dir in "test_load_store2" "test_icache_iTLB" "test_branch_miss" "test_cpi2"
do
    cd ${cur_dir}/${dir}
    # sh run_perf_westmere.sh
    bash test_run_arm_and_perf.sh
done
