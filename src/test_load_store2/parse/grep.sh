#!/bin/bash

file_name=$1  # 获取第一个命令行参数作为文件名
echo ''
for i in {0..16}
do
    echo "load_${i}_"
    grep "^load_${i}_" "$file_name"
    echo " "
    echo "store_${i}_"
    grep "^store_${i}_" "$file_name"
    echo " "
done

