.PHONY: change

default:
	gcc -o ${bench_name}.o -c ${bench_name}.S
	gcc -o ${bench_name} ${bench_name}.o func11.o
	chmod +x ${bench_name}
	mv ${bench_name} ../build/${bench_name}
	rm -f ${bench_name}.o

change:
	gcc -o ${bench_name} ${bench_name}.S
	chmod +x ${bench_name}
	mv ${bench_name} ../build/${bench_name}
	rm -f ${bench_name}.o
