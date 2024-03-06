.PHONY:all
all:
	gcc -o ${bench_name} ${bench_name}.S
	chmod +x ${bench_name}
	mv ${bench_name} ../build/${bench_name}
.PHONY:clean
clean:
	rm ${bench_name}
	rm ${bench_name}.S
	rm ../build/${bench_name}
