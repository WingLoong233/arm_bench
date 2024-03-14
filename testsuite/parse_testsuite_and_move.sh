testsuite_dir=`pwd`

# for dir in "mysqlslap" "sysbench" "rocksdb"
for dir in "rocksdb"
do
    cd ${testsuite_dir}/${dir}
    python3 parse_perf_stat_testsuite.py
    cp -r ${testsuite_dir}/${dir}/parse/T.csv ${testsuite_dir}/../src/lib/test_cases/${dir}.csv
done
