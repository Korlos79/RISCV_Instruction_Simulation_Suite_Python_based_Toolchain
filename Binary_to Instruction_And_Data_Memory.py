import time
dict_Reg = {
    'x0': 0,
    'x1': 0,
    'x2': 0x00003ffc,
    'x3': 0x00001800,
    'x4': 0,
    'x5': 0,
    'x6': 0,
    'x7': 0,
    'x8': 0,
    'x9': 0,
    'x10': 0,
    'x11': 0,
    'x12': 0,
    'x13': 0,
    'x14': 0,
    'x15': 0,
    'x16': 0,
    'x17': 0,
    'x18': 0,
    'x19': 0,
    'x20': 0,
    'x21': 0,
    'x22': 0,
    'x23': 0,
    'x24': 0,
    'x25': 0,
    'x26': 0,
    'x27': 0,
    'x28': 0,
    'x29': 0,
    'x30': 0,
    'x31': 0,
}
dict_Mem = {}
ProgramCounter = 0

def dec_to_bin(n):
    if n >= 0:
        return bin(n)[2:].zfill(32)
    else:
        n = abs(n)
        binary = bin(n)[2:].zfill(32)
        inverted = ''.join('1' if bit == '0' else '0' for bit in binary)
        binary_twos_complement = bin(int(inverted, 2) + 1)[2:].zfill(32)
        return binary_twos_complement
def bin_to_dec(binary_str):
    if isinstance(binary_str, int):
        binary_str = dec_to_bin(binary_str)
    if binary_str[0] == '1':
        return int(binary_str, 2) - (1 << 32)
    else:
        return int(binary_str, 2)
def bin_to_hex(binary_str):
    hex_str = ""
    for i in range(0, 32, 4):
        temp = binary_str[i:i + 4]
        hex_str += hex(int(temp, 2))[2:]
    return hex_str
def shift_right(val, shift_amount, s = 0):
    temp = dec_to_bin(sign_extend(val, 32))
    if  s :
        return temp[0]* shift_amount + str(dec_to_bin(val >> shift_amount)[2:])
    else:
        return '0'* shift_amount + str(dec_to_bin(val >> shift_amount)[2:])
def sign_extend(in_value, bits):
    sign_bit = 1 << (bits - 1)
    if in_value & sign_bit:
        return in_value - (1 << bits)
    return in_value
def print_dict_mem():
    if not dict_Mem:
        print("Memory is empty.")
        return
    min_addr = 0x2000
    max_addr = 0x2ffc
    addr = min_addr
    while addr <= max_addr:
        print(f"0x{addr:08x}", end = '    ')
        for i in range(8):
            byte0 = dict_Mem.get(addr + i*4, 0x00)
            byte1 = dict_Mem.get(addr + i*4 + 1, 0x00)
            byte2 = dict_Mem.get(addr + i*4 + 2, 0x00)
            byte3 = dict_Mem.get(addr + i*4 + 3, 0x00)
            word = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | byte0
            print(f"0x{word:08x}", end = ' ')
        print('\n', end ='')
        addr += 32

file_descriptors = {}
next_fd = 3



def decode(inst_bin : str):
    opcode = inst_bin[-7:]
    #R-type
    if opcode == '0110011':
        funct3 =  inst_bin[-15:-12]
        funct7 = inst_bin[:-25]
        rd = 'x' + str(int(inst_bin[-12:-7], 2))
        rs1 = 'x' + str(int(inst_bin[-20:-15], 2))
        rs2 = 'x' + str(int(inst_bin[-25:-20], 2))
        return {'opcode' : opcode, 'rd' : rd, 'rs1' : rs1, 'rs2' : rs2, 'funct3' : funct3, 'funct7' : funct7}
    #I-type (tru lenh load va jalr)
    elif opcode == '0010011':
        funct3 = inst_bin[-15:-12]
        rd = 'x' + str(int(inst_bin[-12:-7], 2))
        rs1 = 'x' + str(int(inst_bin[-20:-15], 2))
        if funct3 in ['001', '101']:
            imm = inst_bin[-25]*28 + inst_bin[-24:-20]
            funct7 = inst_bin[:-25]
            return {'opcode' : opcode, 'rd' : rd, 'rs1' : rs1, 'funct3' : funct3, 'funct7' : funct7, 'imm' : imm}
        imm = inst_bin[-32]*21 +inst_bin[-31:-20]
        return {'opcode' : opcode, 'rd' : rd, 'rs1' : rs1, 'funct3' : funct3, 'imm' : imm}
    #Cac lenh load va jalr
    elif opcode in ['0000011', '1100111']:
        funct3 = inst_bin[-15:-12]
        rd = 'x' + str(int(inst_bin[-12:-7], 2))
        rs1 = 'x' + str(int(inst_bin[-20:-15], 2))
        imm = inst_bin[-32]*21 +inst_bin[-31:-20]
        return {'opcode': opcode, 'rd': rd, 'rs1': rs1, 'funct3': funct3, 'imm': imm}
    #Cac lenh store
    elif opcode == '0100011':
        funct3 = inst_bin[-15:-12]
        imm = inst_bin[-32]*21 + inst_bin[-31:-25]+inst_bin[-12:-7]
        rs1 = 'x' + str(int(inst_bin[-20:-15], 2))
        rs2 = 'x' + str(int(inst_bin[-25:-20], 2))
        return {'opcode': opcode, 'rs1': rs1,  'rs2' : rs2,'funct3': funct3, 'imm': imm}
    #B-type
    elif opcode == '1100011':
        funct3 = inst_bin[-15:-12]
        rs1 = 'x' + str(int(inst_bin[-20:-15], 2))
        rs2 = 'x' + str(int(inst_bin[-25:-20], 2))
        imm = inst_bin[-32]*20 + inst_bin[-8] + inst_bin[-31:-25] + inst_bin[-12:-8] + '0'
        return {'opcode': opcode, 'rs1': rs1,  'rs2' : rs2,'funct3': funct3, 'imm': imm}
    #jal
    elif opcode == '1101111':
        rd = 'x' + str(int(inst_bin[-12:-7], 2))
        imm = inst_bin[-32]*12 + inst_bin[-20:-12] + inst_bin[-21] + inst_bin[-31:-21] + '0'
        return {'opcode': opcode, 'rd': rd, 'imm': imm}
    #U-type
    elif opcode in ['0110111', '0010111']:
        rd = 'x' + str(int(inst_bin[-12:-7], 2))
        imm = inst_bin[:-12] + '000000000000'
        return {'opcode': opcode, 'rd': rd, 'imm': imm}
    elif opcode == '1110011':
        return {'opcode' : opcode}
    return None

def execution(inst: dict, pc: int) -> int:
    a = inst
    opcode = a['opcode']
    cons = bin_to_dec(a.get('imm', '0'))
    cons2 = int(a.get('imm', '0'), 2)
    # R-type
    if opcode == '0110011':
        if a['rd'] == 'x0':
            return pc + 4
        if a['funct3'] == '000':
            if a['funct7'] == '0000000':
                dict_Reg[a['rd']] = (dict_Reg[a['rs1']] + dict_Reg[a['rs2']]) & 0xffffffff
            elif a['funct7'] == '0100000':
                dict_Reg[a['rd']] = (dict_Reg[a['rs1']] - dict_Reg[a['rs2']]) & 0xffffffff
        if a['funct3'] == '001':
            dict_Reg[a['rd']] = (dict_Reg[a['rs1']] << dict_Reg[a['rs2']]) & 0xffffffff
        if a['funct3'] == '010':
            dict_Reg[a['rd']] = (1 if (bin_to_dec(dict_Reg[a['rs1']]) < bin_to_dec(dict_Reg[a['rs2']])) else 0) & 0xffffffff
        if a['funct3'] == '011':
            dict_Reg[a['rd']] = 1 if (dict_Reg[a['rs1']] < dict_Reg[a['rs2']]) else 0
        if a['funct3'] == '100':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] ^ dict_Reg[a['rs2']]
        if a['funct3'] == '101':
            if a['funct7'] == '0000000':
                dict_Reg[a['rd']] = int(shift_right(dict_Reg[a['rs1']], dict_Reg[a['rs2']], 0), 2) & 0xffffffff
            elif  a['funct7'] == '0100000':
                dict_Reg[a['rd']] = int(shift_right(dict_Reg[a['rs1']], dict_Reg[a['rs2']], 1), 2) & 0xffffffff
        if a['funct3'] == '110':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] | dict_Reg[a['rs2']]
        if a['funct3'] == '111':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] & dict_Reg[a['rs2']]
    # I-type (tru lenh load va jalr)
    elif opcode == '0010011':
        if a['rd'] == 'x0':
            return pc + 4
        if a['funct3'] == '000':
            dict_Reg[a['rd']] = (dict_Reg[a['rs1']] + cons) & 0xffffffff
        if a['funct3'] == '001':
            dict_Reg[a['rd']] = (dict_Reg[a['rs1']] << cons2) & 0xffffffff
        if a['funct3'] == '010':
            dict_Reg[a['rd']] = (1 if (bin_to_dec(dict_Reg[a['rs1']]) < cons) else 0) & 0xffffffff
        if a['funct3'] == '011':
            dict_Reg[a['rd']] = 1 if (dict_Reg[a['rs1']] < cons2) else 0
        if a['funct3'] == '100':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] ^ cons
        if a['funct3'] == '101':
            if a['funct7'] == '0000000':
                dict_Reg[a['rd']] = int(shift_right(dict_Reg[a['rs1']], cons2, 0), 2) & 0xffffffff
            elif  a['funct7'] == '0100000':
                dict_Reg[a['rd']] = int(shift_right(dict_Reg[a['rs1']], cons2, 1), 2) & 0xffffffff
        if a['funct3'] == '110':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] | cons
        if a['funct3'] == '111':
            dict_Reg[a['rd']] = dict_Reg[a['rs1']] & cons
     # lui
    elif opcode == '0110111':
        if a['rd'] == 'x0':
            return pc + 4
        dict_Reg[a['rd']] = cons
    # auipc
    elif opcode == '0010111':
        if a['rd'] == 'x0':
            return pc + 4
        dict_Reg[a['rd']] = (pc+cons) & 0xffffffff
    #jalr
    elif opcode == '1100111':
        if a['rd'] == 'x0':
            pc = dict_Reg[a['rs1']] + cons
            return pc
        temp = dict_Reg[a['rd']]
        dict_Reg[a['rd']] = pc + 4
        pc = temp + cons
        return pc
    # B-type
    elif opcode == '1100011':
        rs1 = dict_Reg[a['rs1']]
        rs2 = dict_Reg[a['rs2']]
        if a['funct3'] == '000':
            if rs1 == rs2:
                pc += cons
                return pc
        if a['funct3'] == '001':
            if rs1 != rs2:
                pc += cons
                return pc
        if a['funct3'] == '100':
            if bin_to_dec(rs1) < bin_to_dec(rs2):
                pc += cons
                return pc
        if a['funct3'] == '101':
            if bin_to_dec(rs1) >= bin_to_dec(rs2):
                pc += cons
                return pc
        if a['funct3'] == '110':
            if rs1 < rs2:
                pc += cons
                return pc
        if a['funct3'] == '111':
            if rs1 >= rs2:
                pc += cons
                return pc
     # jal
    elif opcode == '1101111':
        if a['rd'] == 'x0':
            pc += cons
            return pc
        dict_Reg[a['rd']] = pc + 4
        pc += cons
        return pc
    # Cac lenh load lb, lh, lw, lbu, lhu
    elif opcode == '0000011':
        addr = dict_Reg[a['rs1']] + cons2
        if a['funct3'] == '000':  # Load byte (lb)
            val = dict_Mem.get(addr, 0)
            dict_Reg[a['rd']] = sign_extend(val, 8)
        elif a['funct3'] == '100':  # Load byte unsigned (lbu)
            val = dict_Mem.get(addr, 0)
            dict_Reg[a['rd']] = val & 0xff
        elif a['funct3'] == '001':  # Load halfword (lh)
            if addr % 2 != 0:
                raise ValueError(f"Địa chỉ halfword không hợp lệ: {addr}")
            byte0 = dict_Mem.get(addr, 0)
            byte1 = dict_Mem.get(addr + 1, 0)
            val = (byte1 << 8) | byte0
            dict_Reg[a['rd']] = sign_extend(val, 16)
        elif a['funct3'] == '101':  # Load halfword unsigned (lhu)
            if addr % 2 != 0:
                raise ValueError(f"Địa chỉ halfword không hợp lệ: {addr}")
            byte0 = dict_Mem.get(addr, 0)
            byte1 = dict_Mem.get(addr + 1, 0)
            val = (byte1 << 8) | byte0
            dict_Reg[a['rd']] = val & 0xffff
        elif a['funct3'] == '010':  # Load word (lw)
            if addr % 4 != 0:
                raise ValueError(f"Địa chỉ word không hợp lệ: {addr}")
            byte0 = dict_Mem.get(addr, 0)
            byte1 = dict_Mem.get(addr + 1, 0)
            byte2 = dict_Mem.get(addr + 2, 0)
            byte3 = dict_Mem.get(addr + 3, 0)
            val = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | byte0
            dict_Reg[a['rd']] = sign_extend(val, 8)
    # Cac lenh store sw, sb, sh
    elif opcode == '0100011':
        rs2 = dict_Reg[a['rs2']]
        addr = dict_Reg[a['rs1']] + cons2
        if a['funct3'] == '000':  # Store byte (sb)
            dict_Mem[addr] = rs2 & 0xFF
        elif a['funct3'] == '001':  # Store halfword (sh)
            if addr % 2 != 0:
                raise ValueError(f"Địa chỉ halfword không hợp lệ: {addr}")
            dict_Mem[addr] = rs2 & 0xFF
            dict_Mem[addr + 1] = (rs2 >> 8) & 0xFF
        elif a['funct3'] == '010':  # Store word (sw)
            if addr % 4 != 0:
                raise ValueError(f"Địa chỉ word không hợp lệ: {addr}")
            dict_Mem[addr] = rs2 & 0xFF
            dict_Mem[addr + 1] = (rs2 >> 8) & 0xFF
            dict_Mem[addr + 2] = (rs2 >> 16) & 0xFF
            dict_Mem[addr + 3] = (rs2 >> 24) & 0xFF
    #syscall
    elif opcode == '1110011':
        services = dict_Reg['x17']
        #Nhap xuat so nguyen
        if services == 1:
            print(bin_to_dec(dict_Reg['x10']))
        elif services == 5:
            dict_Reg['x10'] = int(input())
        #Nhap xuat char
        elif services == 11:
            print(chr(dict_Reg['x10']))
        elif services == 12:
            dict_Reg['x10'] = ord(input())
        #Nhap xuat string
        elif services == 8:
            addr_dst = dict_Reg['x10']
            number_of_char  = dict_Reg['x11']
            read_string = list(input())
            lenn = len(read_string)
            if lenn < number_of_char - 1:
                for i in range(lenn):
                    dict_Mem[addr_dst + i] = ord(read_string[i]) & 0xFF
                dict_Mem[addr_dst + lenn] = 0xa & 0xFF
            else:
                for i in range(number_of_char - 1):
                    dict_Mem[addr_dst + i] = ord(read_string[i]) & 0xFF
        elif services == 4:
            addr_src = dict_Reg['x10']
            while True:
                ki_tu = dict_Mem.get(addr_src, 0)
                if ki_tu == 0: break
                print(chr(ki_tu), end = '')
                addr_src += 1
            print('')
        #Ket thuc chuong trinh
        elif services == 10:
            print('---program is finished running (0)---')
            return -1
        #Thoi gian tu 1970 (ms)
        elif services == 30:
            c = int(time.time() * 1000)
            dict_Reg['x10'] = c - (c//(16**8))*(16**8)
            dict_Reg['x11'] = c//(16**8)
        #In ra dạng hexa
        elif services == 34:
            print('0x' + bin_to_hex(dec_to_bin(dict_Reg['x10'])))
        #In ra dạng bin
        elif services == 35:
            print(dec_to_bin(dict_Reg['x10']))
        #In int không dấu
        elif services == 36:
            print(dict_Reg['x10'])
        #Kết thúc chương trình với exit_code
        elif services == 93:
            exit_code = dict_Reg['x10']
            print(f'---program is finished running ({exit_code})---')
            return -1
        '''
        elif services == 1024:
            global next_fd
            try:
                path_address = dict_Reg['x10']
                flags = dict_Reg['x11']
                path = ''
                while True:
                    ki_tu = dict_Mem.get(path_address, 0)
                    if ki_tu == 0: break
                    path + chr(ki_tu)
                    path_address += 1
                mode = None
                if flags == 0:  # Read-only
                    mode = 'r'
                elif flags == 1:  # Write-only (create if not exist)
                    mode = 'w'
                elif flags == 9:  # Write-append
                    mode = 'a'
                else:
                    dict_Reg['x10'] = -1
                    return pc + 4
                file = open(path, mode)
                fd = next_fd
                file_descriptors[fd] = file
                next_fd += 1
                dict_Reg['x10'] = fd
            except Exception as e:
                dict_Reg['x10'] = -1
        '''
    pc += 4
    return pc

def Run(input_f):
    global ProgramCounter
    #Đọc file binary
    with open(input_f, 'r') as file:
        f = file.readlines()
    #Giải mã lệnh
    fhandle = {}
    addr = 0x0
    #Duyệt lệnh, gắn địa chỉ lệnh, decode
    for inst_bin in f:
        inst_bin = inst_bin.strip()
        fhandle[addr]  = decode(inst_bin)
        addr += 4
    i = ProgramCounter
    #Thực thi
    while  (i <= (addr - 4)) and (i >= 0):
        i = execution(fhandle[i], i)
        ProgramCounter = i
        #print(hex(i))
    ProgramCounter += 4

# Main
if __name__ == "__main__":
    input_file = 'D:\Python\output.txt'
    Run(input_file)
    print("RegFile: ")
    for key, value in dict_Reg.items():
        ans = dec_to_bin(value)
        #print(key, ans)
        print(key, bin_to_hex(ans))
        #print(key, value)
    print('pc = 0x', hex(ProgramCounter)[2:].zfill(8), sep = '')
    print("Memory: ")
    print_dict_mem()
