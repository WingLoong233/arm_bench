.PHONY:all

all: $(OBJS)
	@gcc -o main.o -c main.S
	@gcc -o main main.o ../test_icache_iTLB/generate/func11.o  ../test_branch_miss/generate/func1.o
	@chmod +x main
	@cp main ../build
