#encoding: utf-8

import gen_tool


class BlockGenerator():
    def __init__(self, name, feature_dic=dict()):
        self.name = name
        self.feature_dic = feature_dic

    def declare_str(self, string, label):
        return gen_tool.declare_str(string, label)

    def func_begin(self, name, index):
        return gen_tool.func_begin(name, index)

    def func_end(self, name, index):
        return gen_tool.func_end(name, index)

    def file_begin(self, name="main.c"):
        return gen_tool.file_begin(name)

    def file_end(self):
        return gen_tool.file_end()

class Cache(BlockGenerator):
    def __init__(self, name, cache_size, cache_sets, cache_ways, array_name, array_size, inner_number, outer_number,
            stride, feature_dic=dict(), is_load=True, access_number_per_inner=1, traversal=False, change_flag=False):
        super(Cache,self).__init__(name,feature_dic)
        self.stride = stride
        self.cache_size = cache_size
        self.cache_sets = cache_sets
        self.cache_ways = cache_ways
        self.array_name = array_name
        self.array_size = array_size
        self.outer_number = outer_number
        self.inner_number = inner_number
        self.change_flag = change_flag
        self.access_number_per_inner = access_number_per_inner
        self.inner_num_ins = 3 + access_number_per_inner
        self.is_load = is_load
        self.traversal = traversal

    def set_change_flag(self, new_flag):
        self.change_flag = new_flag

    def get_change_flag(self):
        return self.change_flag

    def declare_var(self, index):
        return gen_tool.declare_var(self.array_name, self.array_size, index)

    def memset_block(self):
        return gen_tool.memset_block(self.array_name, self.array_size)

    def get_one_block(self, index, outer_number):
        return gen_tool.access_block2(self.array_name, self.array_size, index, 
                self.inner_number, outer_number, self.stride, 
                self.change_flag, self.is_load, self.access_number_per_inner, self.traversal)

class Cache2(BlockGenerator):
    def __init__(self, name, cache_size, cache_sets, cache_ways, array_size, inner_number, outer_number,
            stride, feature_dic=dict(), change_flag=False):
        super(Cache2,self).__init__(name, feature_dic)
        self.stride = stride
        self.cache_size = cache_size
        self.cache_sets = cache_sets
        self.cache_ways = cache_ways
        self.array_size = array_size
        self.inner_number = inner_number
        self.outer_number = outer_number
        self.change_flag = change_flag
        self.inner_num_ins = 5
        # print(f"Init a generator4.Cache2(icache_iTLB)\tname = {self.name}\tchange_flag = {change_flag}")

    def set_change_flag(self, new_flag):
        self.change_flag = new_flag
    
    def get_change_flag(self):
        # print(f"generator4.get_change_flag: {self.change_flag}")
        return self.change_flag

    def generate_icache_funcs(self, index):
        return gen_tool.generate_icache_funcs(index, self.inner_number, self.stride, self.change_flag)

    def get_one_block(self, index, outer_number):
        return gen_tool.access_func2(index, self.inner_number, outer_number, self.stride, self.change_flag)

class Branch(BlockGenerator):
    def __init__(self,name, inner_number, outer_number, threshold, max_value, feature_dic=dict()):
        super(Branch,self).__init__(name, feature_dic) 
        self.inner_number = inner_number
        self.outer_number = outer_number
        self.threshold = threshold
        self.max_value = max_value
        self.func_index = "1"
        self.func_name = "func" + self.func_index
        self.inner_num_ins = 9

    def generate_jmp_func(self, return_reg="r14"):
        return gen_tool.generate_jmp_func(self.func_index,return_reg)

    def get_one_block(self, index, outer_number):
        return gen_tool.generate_jmp_block(index, self.threshold,
                self.max_value, outer_number, func_name=self.func_name, return_reg="r14")

class Arithm(BlockGenerator):
    def __init__(self, name, inner_number, outer_number, head, instruction, feature_dic=dict(),
            inner_num_ins=20):
        super(Arithm, self).__init__(name, feature_dic)
        self.inner_number = inner_number
        self.outer_number = outer_number
        self.head = head
        self.instruction = instruction
        self.inner_num_ins = inner_num_ins

    def get_one_block(self, index, outer_number):
        # print("genarate cpi2-arithm_block2:")
        # print("instruction:\n", self.instruction)
        # print("index:\t", index, "\nouter_number:\t", outer_number, "\ninner_num_ins:\t", self.inner_num_ins)
        return gen_tool.arithm_block2(index, outer_number, self.inner_number,
                self.instruction, self.head,self.inner_num_ins)

