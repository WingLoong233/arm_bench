#encoding: utf-8

def load_number_to_reg(number, reg):
    hex_0_15 = hex((number >> 0) & 0xFFFF)[2:].zfill(4)
    hex_16_31 = hex((number >> 16) & 0xFFFF)[2:].zfill(4)
    hex_32_47 = hex((number >> 32) & 0xFFFF)[2:].zfill(4)
    hex_48_63 = hex((number >> 48) & 0xFFFF)[2:].zfill(4)
    s = f"\tmovz\t{reg}, #0x{hex_0_15}\n"
    s += f"\tmovk\t{reg}, #0x{hex_16_31}, lsl #16\n"
    s += f"\tmovk\t{reg}, #0x{hex_32_47}, lsl #32\n"
    s += f"\tmovk\t{reg}, #0x{hex_48_63}, lsl #48\n"
    return s

def arithm_block(index, iterators,num_per_iter,instruction,head=None):
    s = "\tmovl\t$" + str(iterators) + ", " + "%r13d\n"
    if head is not None:
        s += head
    s += ".L" + str(index) + "_B:\n"
    for i in range(num_per_iter):
        s += instruction
    s += "\tsubl\t$1, %r13d\n"
    s += "\tje .L" + str(index) + "_E\n"
    s += "\tjmp .L" + str(index) + "_B\n"
    s += ".L" + str(index) + "_E:\n"
    return s

def declare_data(index,number=0,number_type="int"):
    s = ""
    s += "data" + str(index) + ":\n"
    s += ".byte "
    for i in range(8):
        s += "0x00"
        if i != 7:
            s += ","
        else:
            s += "\n"
    return s

def arithm_block2(index, outer_number, inner_number,instruction,head,inner_num_ins=20):
    instructions = instruction.strip("\n").split("\n")
    formatted_instructions = []
    # instruction = instruction.strip("\n")
    # li = instruction.split("\n")
    s = ""
    if head is not None:
        s += head
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg(inner_number, "x12")
    s += "\tb .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    for i in range(inner_num_ins):
        formatted_instructions.append("\t" + instructions[i % len(instructions)])
    s += "\n".join(formatted_instructions)
    s += "\n"
    # j = 0
    # for i in range(inner_num_ins):
    #     s += "\t"+li[j] + "\n"
    #     j = (j+1)%len(li)
    s += "\tadd\tx11, x11, #1\n"
    s += "\tcmp\tx11, x12\n"
    s += "\tblt .L" + str(index) + "_IB\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += "\tbeq .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmov\tx11, 0\n"
    s += "\tb .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s


def declare_var(name='array', size=16777216, index=0, align=3):
    s = ""

    s += f"\t.text\n"
    s += f"\t.global\t{name}{index}\n"
    s += f"\t.bss\n"
    s += f"\t.align\t{align}\n"
    s += f"\t.type\t{name}{index}, %object\n"
    s += f"\t.size\t{name}{index}, {size}\n"
    s += f"{name}{index}:\n"
    s += f"\t.zero\t{size}\n"

    # for number in initial_list:
    #     s += "\t.long\t" + str(number) + "\n"
    # if size - 4 * len(initial_list) > 0:
    #     s += "\t.zero\t" + str(size - 4 * len(initial_list)) + "\n"

    # s += "\t.data\n"
    # s += "\t" + name + ": .space " + str(size) + "\n"
    return s

def declare_str(string, label):
    s = label + ":\n"
    s += "\t.string\t" + '"' + string + '"' + "\n"
    return s

def memset_block(array_name, array_size):
    # memset
    s = "\tmovq\t$" + str(array_size) + ", %rdx\n"
    s += "\tmovl\t$0, %esi\n"
    s += "\tmovl\t$" + array_name + ", %edi\n"
    s += "\tcall\tmemset\n"
    return s

def access_block(array_name, array_size, index, inner_number, outer_number, stride,
        is_memset=True,is_load=True,access_number_per_inner=1):
    s = ""
    if is_memset:
        # memset
        s += "\tmovq\t$" + str(array_size) + ", %rdx\n"
        s += "\tmovl\t$0, %esi\n"
        s += "\tmovl\t$" + array_name + ", %edi\n"
        s += "\tcall\tmemset\n"
    # access
    s += "\tmovl\t$" + str(outer_number) + ", " + "%r13d\n"
    if stride == 0:
        s += "\tmovq\t$" + str(array_name) + "+" + str(1 * inner_number * access_number_per_inner) + ", %r12\n"
    else:
        s += "\tmovq\t$" + str(array_name) + "+" + str(stride * inner_number * access_number_per_inner) + ", %r12\n"
    s += "\tjmp .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    for i in range(access_number_per_inner):
        count = int(i * stride)
        if stride == 0:
            if is_load:
                s += "\tmovl\t(%r12), %esi\n"
            else:
                s += "\tmovl\t%esi, (%r12)\n"
        else:
            if is_load:
                s += "\tmovl\t" + str(count) + "(%rbx), %esi\n"
            else:
                s += "\tmovl\t%esi, " + str(count) + "(%rbx)\n"
    if stride == 0:
        s += "\taddq\t$" + str(1 * access_number_per_inner) + ", %rbx\n"
    else:
        s += "\taddq\t$" + str(stride * access_number_per_inner) + ", %rbx\n"
    s += "\tcmpq\t" + "%rbx, %r12\n"
    s += "\tjne .L" + str(index) + "_IB\n"
    s += "\tsubl\t$1, %r13d\n"
    s += "\tje .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmovq\t$" + array_name + ", %rbx\n"
    s += "\tjmp .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s

def access_block2_old(array_name, array_size, index, inner_number, outer_number, stride,
        is_memset=True,is_load=True,access_number_per_inner=1,traversal=False):
    s = ""
    if is_memset:
        # memset
        s += "\tmovq\t$" + str(array_size) + ", %rdx\n"
        s += "\tmovl\t$0, %esi\n"
        s += "\tmovl\t$" + array_name + ", %edi\n"
        s += "\tcall\tmemset\n"
    # access
    s += "\tmovl\t$" + str(outer_number) + ", " + "%r13d\n"
    s += "\tmovq\t$0, %rbx\n"
    s += "\tmovq\t$x, %r11\n"
    s += "\tmovq\t$0, %r12\n"
    s += "\tjmp .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    for i in range(access_number_per_inner):
        count = int(i * stride)
        if stride == 0:
            if is_load:
                s += "\tmovl\t0(%r11), %esi\n"
            else:
                s += "\tmovl\t%esi, 0(%r11)\n"
        else:
            if is_load:
                s += "\tmovl\t" + str(count) + "(%r11, %rbx, 1), %esi\n"
            else:
                s += "\tmovl\t%esi, " + str(count) + "(%r11, %rbx, 1)\n"
    if stride == 0:
        s += "\taddq\t$" + str(1 * access_number_per_inner) + ", %rbx\n"
    else:
        s += "\taddq\t$" + str(stride * access_number_per_inner) + ", %rbx\n"
    s += "\tcmpq\t" + "%rbx, %r12\n"
    s += "\tjne .L" + str(index) + "_IB\n"
    s += "\tsubl\t$1, %r13d\n"
    s += "\tje .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    if traversal:
        s += "\tandq\t$" + str(array_size - 1) + ", %r12\n"
        if stride == 0:
            s += "\taddq\t$" + str(1 * inner_number * access_number_per_inner) + ", %r12\n"
        else:
            s += "\taddq\t$" + str(stride * inner_number * access_number_per_inner) + ", %r12\n"
        s += "\tandq\t$" + str(array_size - 1) + ", %rbx\n"
    else:
        s += "\tmovq\t$0, %rbx\n"
        if stride == 0:
            s += "\tmovq\t$" + str(1 * inner_number * access_number_per_inner) + ", %r12\n"
        else:
            s += "\tmovq\t$" + str(stride * inner_number * access_number_per_inner) + ", %r12\n"
        s += "\tnop\n"
    s += "\tjmp .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s

def access_block2_arm_old(array_name, array_size, index, inner_number, outer_number, stride,
        is_memset=True,is_load=True,access_number_per_inner=1,traversal=False):

    s = ""

    # outer_number填入x13
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg((1 if stride == 0 else stride) * inner_number, "x12")
    # s += "\tmov\tx12, #" + str((1 if stride == 0 else stride) * inner_number) + "\n"
    s += f"\tldr\tx11, ={array_name}\n"
    # s += f"\tmov\tx3, #{str(int(stride * access_number_per_inner)) if stride != 0 else '1'}\n"
    s += f"\tmov\tx3, #{(stride if stride != 0 else 1) * access_number_per_inner}\n"
    # s += f"\tmov\tx3, #{stride * access_number_per_inner}\n"
    s += f"\tb\t.L{index}_OB\n"


    s += f".L{index}_IB:\n"
    for i in range(access_number_per_inner):
        # offset = str(int(i * stride)) if stride != 0 else "1"
        offset = str(int(i * stride))
        load_or_store = "ldr" if is_load else "str"
        s += f"\t{load_or_store} x0, [x2, #{offset}]\n"
    # 若stride==0，x2不变
    if (stride != 0):
        s += f"\tadd\tx2, x2, x3\n"
    s += f"\tadd\tx1, x1, x3\n"
    s += "\tcmp\tx1, x12\n"
    s += f"\tbne\t.L{index}_IB\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += f"\tbeq\t.L{index}_OE\n"
    s += f".L{index}_OB:\n"
    s += "\tmov\tx0, #0\n"
    s += "\tmov\tx1, #0\n"
    s += "\tmov\tx2, x11\n"
    s += f"\tb\t.L{index}_IB\n"
    s += f".L{index}_OE:\n"
    return s

def access_block2(array_name, array_size, index, inner_number, outer_number, stride,
        change_flag=False, is_load=True, access_number_per_inner=1, traversal=False):

    s = ""
    # outer_number填入x13
    s += load_number_to_reg(outer_number, "x13")
    # change模式inner_number固定为32（其实多少都不影响，只要是access_number_per_inner的倍数就行）
    if (change_flag):
        s += load_number_to_reg(64, "x12")
    else:
        s += load_number_to_reg(inner_number, "x12")
    # s += f"\tldr\tx11, ={array_name}\n"
    # x11存储数组起始
    s += f"\tadrp x11, {array_name}{index}\n\tadd x11, x11, :lo12:{array_name}{index}\n"
    # x10存储数组上界(不是真的上界，而是再读取一轮会碰到上界)
    array_end = array_size - (stride if stride != 0 else 1) * 4 * inner_number - 100
    s += load_number_to_reg(array_end, "x10")
    s += f"\tadd x10, x10, x11\n"
    # x3存储一次内循环向前进多少个字节（stride*access_number_per_inner*字节大小）（.align3说明8字节边界 但int是32位，4字节）
    s += f"\tmov\tx3, #{(stride if stride != 0 else 1) * 4 * access_number_per_inner}\n"
    s += "\tmov\tx0, #0\n"
    s += "\tmov x2, x11\n"
    s += f"\tb\t.L{index}_OB\n"

    s += f".L{index}_IB:\n"
    for i in range(access_number_per_inner):
        # offset = str(int(i * stride)) if stride != 0 else "1"
        # 理论上应该 = i * stride * 4，但是之前用i * stride效果很好，不妨一试(不行，没用)
        offset = i * stride * 4
        # offset = i * stride
        load_or_store = "ldr" if is_load else "str"
        s += f"\t{load_or_store} x0, [x2, #{offset}]\n"
    # 若stride==0，x2不变
    if (stride != 0):
        s += f"\tadd x2, x2, x3\n"
    s += f"\tadd x1, x1, #{access_number_per_inner}\n"
    s += "\tcmp x1, x12\n"
    s += f"\tblt .L{index}_IB\n"
    s += "\tsub x13, x13, #1\n"
    s += "\tcmp x13, #0\n"
    s += f"\tbeq .L{index}_OE\n"
    s += f".L{index}_OB:\n"
    s += "\tmov x1, #0\n"
    if (change_flag):
        s += "\tcmp x2, x10\n"
        s += f"\tblt .L{index}_IB\n"
    s += f"\tmov x2, x11\n"
    s += f"\tb .L{index}_IB\n"
    s += f".L{index}_OE:\n"
    return s



# def load_block(array_name,array_size, index=0,inner_number,outer_number,stride,is_load=True,access_number_per_inner=1,traversal=False):
#     # 初始化寄存器：x13--数组的首地址存储到寄存器，x0--偏移量，x1--间距。
#     s = "\tldr x13, =" + array_name + "\n\tmov x0, #0\n\tmov x1, #" + str(stride) + "\n"
#     # 循环 loop
#     s += "loop:\n\tldr w2, [x13, x0]\n\tadd x0, x0, x1\n\t cmp x0, #" + array_size + "\n\tblt loop\n"

#     for i in range(access_number_per_inner):
#         s += "movl %esi, {}(%r11, %rbx, 1)\n".format(offset)
#         offset += interval

def access_func(first_func, access_length, index, inner_number, outer_number, stride, func_size=7):
    s = "\tmovq\t$" + str(outer_number) + ", " + "%r13\n"
    s += "\tmovq\t$" + str(first_func) + "+" + str(func_size * stride * inner_number) + ", %r12\n"
    s += "\tjmp .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    s += "\tcall\t*%rbx\n"
    s += "\taddq\t$" + str(func_size * stride) + ", %rbx\n"
    s += "\tcmpq\t" + "%rbx, %r12\n"
    s += "\tjne .L" + str(index) + "_IB\n"
    s += "\tsubq\t$1, %r13\n"
    s += "\tje .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmovq\t$" + first_func + ", %rbx\n"
    s += "\tjmp .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s

def access_func2_old(first_func, access_length, index, inner_number, outer_number, stride, func_size=3,return_reg='r14'):
    s = "\tmovq\t$" + str(outer_number) + ", " + "%r13\n"
    if stride == 0:
        s += "\tmovq\t$" + str(first_func) + "+" + str(func_size * 1 * inner_number) + ", %r12\n"
    else:
        s += "\tmovq\t$" + str(first_func) + "+" + str(func_size * stride * inner_number) + ", %r12\n"
    s += "\tmovq\t$.R"+str(index) + ", %" + return_reg + "\n"
    s += "\tjmp .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    if stride == 0:
        s += "\tjmp\t*%r12\n"
    else:
        s += "\tjmp\t*%rbx\n"
    s += ".R" + str(index) + ":"
    if stride == 0:
        s += "\taddq\t$" + str(func_size * 1) + ", %rbx\n"
    else:
        s += "\taddq\t$" + str(func_size * stride) + ", %rbx\n"
    s += "\tcmpq\t" + "%rbx, %r12\n"
    s += "\tjne .L" + str(index) + "_IB\n"
    s += "\tsubq\t$1, %r13\n"
    s += "\tje .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmovq\t$" + first_func + ", %rbx\n"
    s += "\tjmp .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s

def access_func2_arm_old(first_func, index, outer_number, stride): 
    s = ""
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg(stride*4*2, "x1")
    s += f".L{index}:\n"
    s += f"\tbl {first_func}\n"
    s += "\tnop\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += f"\tbgt .L{index}\n"
    return s

# 存储代码
def access_func2_buffer(index, inner_number, outer_number, stride, change_flag): 
    s = ""
    # 代码1
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg(stride*4*inner_number, "x12")
    s += load_number_to_reg(stride*4, "x3")
    s += f"\tadr x11, .L{index}_M\n"
    s += f".L{index}_STR:\n"
    s += f"\tb func11\n"
    s += f".L{index}_M:\n"
    s += f"\tadd x0, x0, x3\n"
    s += "\tcmp x0, x2\n"
    s += f"\tbgt .L{index}_C\n"
    s += "\tbr x0\n"
    s += f".L{index}_C:\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += f"\tbgt .L{index}_STR\n"
    # 代码2
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg(stride*4*2, "x1")
    s += f"\tadr x11, .L{index}_M\n"
    s += f".L{index}:\n"
    s += f"\tb func12\n"
    # s += "\tnop\n"
    s += f".L{index}_M:\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += f"\tbgt .L{index}\n"
    return s

def access_func2(index, inner_number, outer_number, stride, change_flag): 
    s = ""
    if (change_flag == False):
        # 正常模式
        s += load_number_to_reg(outer_number, "x13")
        s += load_number_to_reg(stride*4*inner_number, "x12")
        s += load_number_to_reg(stride*4, "x3")
        s += f"\tadr x11, .L{index}_M\n"
        s += f".L{index}_STR:\n"
        s += f"\tb func11\n"
        s += f".L{index}_M:\n"
        s += f"\tadd x0, x0, x3\n"
        s += "\tcmp x0, x2\n"
        s += f"\tbgt .L{index}_C\n"
        s += "\tbr x0\n"
        s += f".L{index}_C:\n"
        s += "\tsub\tx13, x13, #1\n"
        s += "\tcmp\tx13, #0\n"
        s += f"\tbgt .L{index}_STR\n"
    else:
        # 异态模式
        s += load_number_to_reg(outer_number, "x13")
        s += f"\tadr x11, .L{index}_M\n"
        s += f".L{index}:\n"
        s += f"\tb icachefunc{index}\n"
        s += f".L{index}_M:\n"
        s += "\tsub\tx13, x13, #1\n"
        s += "\tcmp\tx13, #0\n"
        s += f"\tbgt .L{index}\n"
    return s

def generate_icache_funcs(index, inner_number, stride, change_flag):
    s = ""
    if (change_flag):
        s += f"\t.align 2\n"
        s += f"\t.global icachefunc{index}\n"
        s += f"\t.type icachefunc{index}, %function\n"
        s += f"icachefunc{index}:\n"
        for i in range(stride*inner_number+1):
            s += f".ICACHE{index}_{i}:\n"
            if i > stride*(inner_number-1):
                s += f"\tbr x11\n"
            else:
                s += f"\tb .ICACHE{index}_{i+stride}\n"
        s += "\tret\n"
        s += f"\t.size icachefunc{index}, .-icachefunc{index}\n"
    return s


def generate_icache_func11(func_number):
    s = ""
    s += "\t.text\n"
    s += "\t.align\t2\n"
    s += "\t.global\tfunc11\n"
    s += "\t.type\tfunc11, %function\n"
    s += "func11:\n"
    s += f".LFB11:\n"
    s += f"\tadr x10, .Func11\n"
    s += f"\tadd x2, x12, x10\n"
    s += f"\tmov x0, x10\n"
    s += f".Func11:\n"
    for _ in range(func_number):
        s += "\tbr x11\n"
    s += f"ret\n"
    return s

def generate_icache_func_c(index, func_number):
    s = ""
    # s += file_begin('main.c')
    s += "\t.text\n"
    s += "\t.align\t2\n"
    s += f"\t.global\tfunc{index}\n"
    s += f"\t.type\tfunc{index}, %function\n"
    s += f"func{index}:\n"
    s += f"\tadr x0, .F12\n"
    s += f".F12:\n"
    for _ in range(func_number):
        # x0存储下一个地址，x1存储stride*4*2（每个指令4个字节，每个块2个指令），x2存储跳转次数上限（暂定1024-2048*stride*4*2）
        s += "\tadd x0, x0, x1\n"
        # s += "\tcmp x0, x2\n"
        # s += "\tbgt x3\n"
        s += "\tbr x0\n"
    for _ in range(8000):
        s += "\tbr x11\n"
    s += "\tret\n"
    s += f"\t.size\tfunc{index}, .-func{index}\n"
    s += file_end()
    return s

def generate_icache_func_old(stride, inner_number):
    s = ""
    for i in range(inner_number):
        s += f"\t.align 2\n"
        s += f"\t.global func{i}\n"
        s += f"\t.type func{i}, %function\n"
        s += f"func{i}:\n"
        s += f".LFB{i}:\n"

        if i + stride >= inner_number:
            s += f"\tret\n"
        else:
            s += f"\tb func{i + stride}\n"

        s += f".LFE{i}:\n"
        s += f"\t.size func{i}, .-func{i}\n"
    return s




def icache_block(index, outer_number):
    s = ""
    hex_0_15 = hex((outer_number >> 0) & 0xFFFF)[2:].zfill(4)
    hex_16_31 = hex((outer_number >> 16) & 0xFFFF)[2:].zfill(4)
    hex_32_47 = hex((outer_number >> 32) & 0xFFFF)[2:].zfill(4)
    hex_48_63 = hex((outer_number >> 48) & 0xFFFF)[2:].zfill(4)
    s += "\tmovz\tx13, #0x" + str(hex_0_15) + "\n"
    s += "\tmovk\tx13, #0x" + str(hex_16_31) + ", lsl #16\n"
    s += "\tmovk\tx13, #0x" + str(hex_32_47) + ", lsl #32\n"
    s += "\tmovk\tx13, #0x" + str(hex_48_63) + ", lsl #48\n"
    s += "\tb .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    s += "\tbl func0\n"
    s += "\tnop\n"
    # s += "\tadd\tw12, w12, #1\n"
    # s += "\tcmp\tw12, #" + str(inner_number)+ "\n"
    # s += "\tbne .L" + str(index) + "_IB\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += "\tbeq .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmov\tw12, 0\n"
    s += "\tb .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s


def generate_jmp_func_old(index,return_reg="r14"):
    s = "\t.globl	func"+str(index)+"\n"
    s += "\t.type\tfunc" + str(index) + ", @function\n"
    s += "func" + str(index) + ":\n"
    s += ".LFB" + str(index) + ":\n"
    s += "\t.cfi_startproc\n"
    s += "\tjmp *%"+str(return_reg) + "\n"
    s += "\t.cfi_endproc\n"
    s += ".LFE"+str(index)+":\n"
    s += "\t.size	func"+str(index)+", .-func"+str(index)+"\n"
    return s


def generate_jmp_func(index,return_reg="r14"):
    s = ""
    s += "\t.align\t2\n"
    s += f"\t.global\tfunc{index}\n"
    s += f"\t.type\tfunc{index}, %function\n"
    s += f"func{index}:\n"
    s += f".LFB{index}:\n"
    # s += "\tstp\tx29, x30, [sp, -16]!\n"
    s += "\tnop\n"
    # s += "\tldp\tx29, x30, [sp], 16\n"
    s += "\tret\n"
    s += f".LFE{index}:\n"
    s += f"\t.size\tfunc{index}, .-func{index}\n"
    return s

def generate_jmp_block_old(index, threshold, max_value, outer_number, func_name="func1",return_reg="r14"):
    s = "\tmovq\t$" + str(outer_number) + ", " + "%r13\n"
    s += "\tmovq\t$0, %r12\n"
    s += ".L" + str(index)+"_B:\n"
    for i in range(16):
        s += "\timulq\t$1103515245, %r12, %r12\n"
        s += "\taddq\t$12345, %r12\n"
        s += "\tandq\t$2147483647, %r12\n"
        s += "\tmovq\t%r12, %r15\n"
        s += "\tandq\t$"+ str(max_value-1) + ", %r15\n"
        s += "\tcmpq\t$" + str(threshold) + ", %r15\n"
        s += "\tmovq\t$.J" + str(index) + "_" + str(i) + ", %" + return_reg + "\n"
        s += "\tjl\t" + str(func_name)+"\n"
        s += ".J"+ str(index) + "_" + str(i) + ":\n"
    s += "\tsubq\t$1, %r13\n"
    s += "\tjne .L" + str(index) + "_B\n"
    return s


# threshold0其实是icache的thride0，因为icache的outnumber=300，太小了，所以移到这里（废除，转到cpi2中）
def generate_jmp_block(index, threshold, max_value, outer_number, func_name="func1", return_reg="x30"):
    s = ""
    inner_number = 8
    inner_num_ins = 32
    s += load_number_to_reg(outer_number, "x13")
    s += load_number_to_reg(inner_number, "x12")
    # s += "\tldr x3, =0x5DEECE66D\n"
    s += load_number_to_reg(25214903917, "x3")
    s += f".L{index}_S:\n"
    s += "\tmov x0, #0\n"
    s += "\tmov x2, #0\n"
    for i in range(inner_num_ins):
        s += f".L{index}_{i}:\n"
        s += "\tmul x0, x0, x3\n"
        s += "\tadd x0, x0, #0xB\n"
        s += "\tand x0, x0, #0xFFFFFFFFFFFF\n"
        s += f"\tand x1, x0, #{max_value-1}\n"
        s += f"\tcmp x1, #{threshold}\n"
        if (i+2 < inner_num_ins):
            s += f"\tblt .L{index}_{i+2}\n"
        else:
            s += f"\tblt .L{index}_C\n"
    # s += f"\tb .L{index}_16\n"
    s += f".L{index}_C:\n"
    s += "\tadd x2, x2, #1\n"
    s += "\tcmp x2, x12\n"
    s += f"\tblt .L{index}_0\n"
    s += "\tsub x13, x13, #1\n"
    s += "\tcmp x13, #0\n"
    s += f"\tbgt .L{index}_S\n"
    # s += "\tmov x13, #0\n"

    # else:
    #     s += load_number_to_reg(outer_number, "x13")
    #     s += f".L{index}:\n"
    #     s += load_number_to_reg(32, "x12")
    #     s += f".L{index}IN:\n"
    #     s += f"\tbl {func_name}\n"
    #     s += "\tnop\n"
    #     s += "\tsub\tx12, x12, #1\n"
    #     s += "\tcmp\tx12, #0\n"
    #     s += f"\tbgt .L{index}IN\n"
    #     s += "\tsub\tx13, x13, #1\n"
    #     s += "\tcmp\tx13, #0\n"
    #     s += f"\tbgt .L{index}\n"

    return s



def file_block(index,outer_number, inner_number, stride, is_read=True):
    s = ""
    s += ".L" + str(index)+"_B:\n"
    s += "\tmovl\t$" + str(outer_number) + ", %edi\n"
    s += "\tmovl\t$" + str(inner_number) + ", %esi\n"
    s += "\tmovl\t$" + str(stride) + ",  %edx\n"
    if is_read:
        s += "\tcall fileread\n"
    else:
        s += "\tcall filewrite\n"
    return s


def file_begin(name="main.c"):
    s = "\t.arch armv8-a\n"
    return s

def file_end():
    s = ""
    return s


def func_begin(name, index=0):
    s = ""
    s += "\t.align\t2\n"
    s += "\t.global\t" + name + "\n"
    s += "\t.type\t" + name + ", %function\n"
    s += str(name) + ":\n"
    s += f".LFB{index}:\n"
    s += "\tstp\tx29, x30, [sp, -16]!\n"
    # s += "\t.cfi_startproc\n"
    # s += "\tsub\tsp, sp, #16\n"
    # s += "\t.cfi_def_cfa_offset 16\n"
    return s

def func_end(name, index=0):
    s = ""
    # s += "\tadd\tsp, sp, 16\n"
    s += "\tldp\tx29, x30, [sp], 16\n"
    s += "\tret\n"
    s += f".LFE{index}:\n"
    s += f"\t.size\t{name}, .-{name}\n"
    return s




def file_begin_old(name="main.c"):
    s = "\t.file\t" + '"' + name + '"' + "\n"
    return s

def file_end_old():
    s = '\t.ident\t"GCC: (GNU) 7.3.1 20180303 (Red Hat 7.3.1-5)"\n'
    s += '\t.section\t.note.GNU-stack,"",@progbits\n'
    return s

def func_begin_old(name, index):
    s = "\t.global\t" + name + "\n"
    s += "\t.type\t" + name + ", %function\n"
    s += str(name) + ":\n"
    s += ".LFB" + str(index) + ":\n"
    s += "\t.cfi_startproc\n"
    s += "\tsub\tsp, sp, #16\n"
    s += "\t.cfi_def_cfa_offset 16\n"
    return s

def func_end_old(name, index):
    s = "\tadd\tsp, sp, 16\n"
    s += "\t.cfi_def_cfa_offset 0\n"
    s += "\tret\n"
    s += "\t.cfi_endproc\n"
    s += ".LFE" + str(index) + ":\n"
    s += "\t.size\t" + str(name) + ", .-" + str(name) + "\n"
    return s





def generate_icache_block(index, outer_number):
    s = ""
    hex_0_15 = hex((outer_number >> 0) & 0xFFFF)[2:].zfill(4)
    hex_16_31 = hex((outer_number >> 16) & 0xFFFF)[2:].zfill(4)
    hex_32_47 = hex((outer_number >> 32) & 0xFFFF)[2:].zfill(4)
    hex_48_63 = hex((outer_number >> 48) & 0xFFFF)[2:].zfill(4)
    s += "\tmovz\tx13, #0x" + str(hex_0_15) + "\n"
    s += "\tmovk\tx13, #0x" + str(hex_16_31) + ", lsl #16\n"
    s += "\tmovk\tx13, #0x" + str(hex_32_47) + ", lsl #32\n"
    s += "\tmovk\tx13, #0x" + str(hex_48_63) + ", lsl #48\n"
    s += "\tb .L" + str(index) + "_OB\n"
    s += ".L" + str(index) + "_IB:\n"
    s += "\tbl func0\n"
    s += "\tnop\n"
    # s += "\tadd\tw12, w12, #1\n"
    # s += "\tcmp\tw12, #" + str(inner_number)+ "\n"
    # s += "\tbne .L" + str(index) + "_IB\n"
    s += "\tsub\tx13, x13, #1\n"
    s += "\tcmp\tx13, #0\n"
    s += "\tbeq .L" + str(index) + "_OE\n"
    s += ".L" + str(index) + "_OB:\n"
    s += "\tmov\tw12, 0\n"
    s += "\tb .L" + str(index) + "_IB\n"
    s += ".L" + str(index) + "_OE:\n"
    return s
