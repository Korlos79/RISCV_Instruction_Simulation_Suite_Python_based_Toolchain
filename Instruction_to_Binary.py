def int_to_bin(value, bits):
    return format(value, f'0{bits}b')
def binary_to_hex(binary_str): 
    hex_str = hex(int(binary_str, 2))
    return hex_str
def assemble_load(instruction, rd, imm, rs1):  
    opcode = '0000011'
    if instruction == "lb":
        funct3 = '000'  
    elif instruction == "lh":
        funct3 = '001'  
    elif instruction == "lw":
        funct3 = '010'  
    elif instruction == "lbu":
        funct3 = '100'  
    elif instruction == "lhu":
        funct3 = '101'  
    else:
        return "Lệnh không hợp lệ."
    imm_bin = int_to_bin(imm, 12)  
    rs1_bin = int_to_bin(rs1, 5)   
    rd_bin = int_to_bin(rd, 5)     
    return imm_bin + rs1_bin + funct3 + rd_bin + opcode
def assemble_store(instruction, rs1, rs2, imm):
    opcode = '0100011'
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    if instruction == 'sb':
        funct3 = '000'
    elif instruction == 'sh':
        funct3 = '001'
    elif instruction == 'sw':
        funct3 = '010'
    else:
        return "Lệnh không hợp lệ."
    imm_11_5_bin = int_to_bin(imm_11_5, 7)
    imm_4_0_bin = int_to_bin(imm_4_0, 5)
    rs1_bin = int_to_bin(rs1,5)
    rs2_bin = int_to_bin(rs2,5)
    return imm_11_5_bin + rs2_bin + rs1_bin + funct3 + imm_4_0_bin + opcode
def assemble_shift(instruction, rd, rs1, rs2, funct7=0):
    opcode = '0110011'
    if instruction == 'sll':
        funct3 = '001'
        funct7_bin = '0000000'
    elif instruction == 'srl':
        funct3 = '101'
        funct7_bin = '0000000'
    elif instruction == 'sra':
        funct3 = '101'
        funct7_bin = '0100000'
    else:
        return "Lệnh không hợp lệ."
    rs1_bin = int_to_bin(rs1, 5)      
    rd_bin = int_to_bin(rd, 5)        
    rs2_bin = int_to_bin(rs2, 5) # Thanh ghi rs2
    return funct7_bin + rs2_bin + rs1_bin + funct3 + rd_bin + opcode
def assemble_shift_immediate(instruction, rd, rs1, shamt):
    opcode = '0010011'
    if instruction == "slli":
        funct3 = '001'  
    elif instruction == "srli":
        funct3 = '101'  
    elif instruction == "srai":
        funct3 = '101'  
    else:
        return "Lệnh không hợp lệ."
    rs1_bin = int_to_bin(rs1, 5)   
    rd_bin = int_to_bin(rd, 5)    
    imm_bin = int_to_bin(shamt, 4)
    if instruction == "slli" or instruction == "srli":
        return '00000000' + imm_bin + rs1_bin + funct3 + rd_bin + opcode
    else:
        return '01000000' + imm_bin + rs1_bin + funct3 + rd_bin + opcode
def assemble_arithmetic(instruction, rd, rs1=None, rs2=None, imm=None):
    if instruction == "add":
        funct3 = '000'
        funct7 = '0000000'
        if rs1 is None or rs2 is None:
            return "Thiếu tham số rs1 hoặc rs2"
    elif instruction == "sub":
        funct3 = '000'
        funct7 = '0100000'
        if rs1 is None or rs2 is None:
            return "Thiếu tham số rs1 hoặc rs2"
    elif instruction == "addi":
        funct3 = '000'
        funct7 = ''
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None  
    elif instruction in ("lui", "auipc"):
        funct3 = ''
        funct7 = ''
        rs1 = None 
        rs2 = None  
        if imm is None:
            return "Thiếu tham số imm"
    else:
        return "Lệnh không hợp lệ."
    rd_bin = int_to_bin(rd, 5)
    rs1_bin = int_to_bin(rs1, 5) if rs1 is not None else ''
    rs2_bin = int_to_bin(rs2, 5) if rs2 is not None else ''
    if instruction == "addi":
        imm_bin = int_to_bin(imm, 12) 
    elif instruction in ("lui", "auipc"):    
        imm_bin = int_to_bin(imm, 20)
    else:
        imm_bin = ''
    if instruction == "addi":
        return imm_bin + rs1_bin + funct3 + rd_bin + '0010011'  
    elif instruction == "lui":
        return imm_bin + rd_bin + '0110111'  
    elif instruction == "auipc":
        return imm_bin + rd_bin + '0010111'  
    else:
        return funct7 + rs2_bin + rs1_bin + funct3 + rd_bin + '0110011'
def assemble_logical(instruction, rd, rs1, rs2=None, imm=None):
    if instruction == "xor":
        funct3 = '100'
        funct7 = '0000000'
        if rs2 is None:
            return "Thiếu tham số rs2"
    elif instruction == "or":
        funct3 = '110'
        funct7 = '0000000'
        if rs2 is None:
            return "Thiếu tham số rs2"
    elif instruction == "and":
        funct3 = '111'
        funct7 = '0000000'
        if rs2 is None:
            return "Thiếu tham số rs2"
    elif instruction == "xori":
        funct3 = '100'
        funct7 = ''  
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None  
    elif instruction == "ori":
        funct3 = '110'
        funct7 = ''  
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None  
    elif instruction == "andi":
        funct3 = '111'
        funct7 = ''  
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None  
    
    else:
        return "Lệnh không hợp lệ."
    if instruction in ["xori", "ori", "andi"]:  
        imm_bin = int_to_bin(imm, 12)
    else:  
        imm_bin = ''
    rs1_bin = int_to_bin(rs1, 5)  
    rd_bin = int_to_bin(rd, 5)   
    if instruction in ["xori", "ori", "andi"]:  
        return imm_bin + rs1_bin + funct3 + rd_bin + '0010011'
    else:  
        rs2_bin = int_to_bin(rs2, 5)
        return funct7 + rs2_bin + rs1_bin + funct3 + rd_bin + '0110011'
def assemble_compare(instruction, rd, rs1, rs2=None, imm=None):
    if instruction == "slt":
        funct3 = '010'
        funct7 = '0000000'
        if rs2 is None:
            return "Thiếu tham số rs2"
    elif instruction == "slti":
        funct3 = '010'
        funct7 = ''  
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None 
    elif instruction == "sltu":
        funct3 = '011'
        funct7 = '0000000'
        if rs2 is None:
            return "Thiếu tham số rs2"
    elif instruction == "sltiu":
        funct3 = '011'
        funct7 = '' 
        if imm is None:
            return "Thiếu tham số imm"
        rs2 = None  
    else:
        return "Lệnh không hợp lệ."
    if instruction in ["slti", "sltiu"]:  
        rs2_bin = ''
        imm_bin = int_to_bin(imm, 12)
    else:  
        imm_bin = ''
        rs2_bin = int_to_bin(rs2, 5)
    rs1_bin = int_to_bin(rs1, 5)  
    rd_bin = int_to_bin(rd, 5)    
    if instruction in ["slti", "sltiu"]:  
        return imm_bin + rs1_bin + funct3 + rd_bin + '0010011'
    else:  
        return funct7 + rs2_bin + rs1_bin + funct3 + rd_bin + '0110011'
def assemble_branch(instruction, rs1, rs2, imm):
    opcode = '1100011' 
    if instruction == "beq":
        funct3 = '000'
    elif instruction == "bne":
        funct3 = '001'
    elif instruction == "blt":
        funct3 = '100'
    elif instruction == "bge":
        funct3 = '101'
    elif instruction == "bltu":
        funct3 = '110'
    elif instruction == "bgeu":
        funct3 = '111'
    else:
        return "Lệnh không hợp lệ."
    imm_12 = (imm >> 12) & 0x1  
    imm_10_5 = (imm >> 5) & 0x3F  
    imm_4_1 = (imm >> 1) & 0xF  
    imm_11 = (imm >> 11) & 0x1   
    imm_12_bin = int_to_bin(imm_12, 1)
    imm_10_5_bin = int_to_bin(imm_10_5, 6)
    imm_4_1_bin = int_to_bin(imm_4_1, 4)
    imm_11_bin = int_to_bin(imm_11, 1)
    rs1_bin = int_to_bin(rs1, 5) 
    rs2_bin = int_to_bin(rs2, 5)  
    return imm_12_bin + imm_10_5_bin + rs2_bin + rs1_bin + funct3 + imm_4_1_bin + imm_11_bin + opcode
def assemble_jal(instruction, rd, rs1=None, imm=None):
    if instruction == 'jal':
        imm_20 = (imm >> 20) & 0x1
        imm_10_1 = (imm >> 1) & 0x3FF
        imm_11 = (imm >> 11) & 0x1
        imm_19_12 = (imm >> 12) & 0xFF
        imm_20_bin = int_to_bin(imm_20, 1)
        imm_10_1_bin = int_to_bin(imm_10_1, 10)
        imm_11_bin = int_to_bin(imm_11, 1)
        imm_19_12_bin = int_to_bin(imm_19_12, 8)
        rd_bin = int_to_bin(rd, 5)
        return imm_20_bin + imm_10_1_bin + imm_11_bin + imm_19_12_bin + rd_bin + '1101111'
    elif instruction == 'jalr':
        funct3 = '000'
        imm_bin = int_to_bin(imm, 12)
        rs1_bin = int_to_bin(rs1, 5)  
        rd_bin = int_to_bin(rd, 5)
        return imm_bin + rs1_bin + funct3 + rd_bin + '1100111'  
def process_file(input_filename, output_filename):
    try:
        with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
            for line in infile:
                line = line.replace('0x', '').strip()
                line = line.replace(',', '').replace('(', ' ').replace(')', '').strip()
                parts = line.split()
                if parts[0] in ['xor', 'xori']:
                    instruction = parts[0]   
                    registers = [p.replace('x', '') for p in parts[1:]] 
                    parts = [instruction] + registers  
                else:
                    line = line.replace('x', '')
                    parts = line.split()
                if len(parts) == 0:
                    continue
                start_line = 1
                instruction = parts[0]                
                if instruction in ["lb", "lh", "lw", "lbu", "lhu"]:
                    try:
                        rd = int(parts[1])
                        imm = int(parts[2])
                        rs1 = int(parts[3]) 
                        binary_code = assemble_load(instruction, rd, imm, rs1)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["sb", "sh", "sw"]:
                    try:
                        rs1 = int(parts[3]) 
                        rs2 = int(parts[1]) 
                        imm = int(parts[2])
                        binary_code = assemble_store(instruction, rs1, rs2, imm)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["sll", "srl", "sra"]:
                    try:
                        rd = int(parts[1])
                        rs1 = int(parts[2]) 
                        rs2 = int(parts[3]) 
                        binary_code = assemble_shift(instruction, rd, rs1, rs2)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["slli", "srli", "srai"]:
                    try:
                        rd = int(parts[1])
                        rs1 = int(parts[2]) 
                        shamt = int(parts[3]) 
                        binary_code = assemble_shift_immediate(instruction, rd, rs1, shamt)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["add", "sub", "addi", "lui", "auipc"]:
                    try:
                        if instruction == "addi":
                            rd = int(parts[1])
                            rs1 = int(parts[2])
                            imm = int(parts[3]) 
                            binary_code = assemble_arithmetic(instruction, rd, rs1=rs1, imm=imm)
                        elif instruction in ["lui", "auipc"]:
                            rd = int(parts[1])
                            imm = int(parts[2],16)                      
                            binary_code = assemble_arithmetic(instruction, rd, imm=imm)
                        else:
                            rd = int(parts[1])
                            rs1 = int(parts[2])
                            rs2 = int(parts[3]) 
                            binary_code = assemble_arithmetic(instruction, rd, rs1=rs1, rs2=rs2)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["xor", "or", "and", "xori", "ori", "andi"]:
                    try:
                        rd = int(parts[1])
                        rs1 = int(parts[2]) 
                        if instruction in ["xori", "ori", "andi"]:
                            imm = int(parts[3])
                            binary_code = assemble_logical(instruction, rd, rs1, imm=imm)
                        else:
                            rs2 = int(parts[3]) 
                            binary_code = assemble_logical(instruction, rd, rs1, rs2=rs2)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["slt", "slti", "sltu", "sltiu"]:
                    try:
                        rd = int(parts[1])
                        rs1 = int(parts[2]) 
                        if instruction in ["slti", "sltiu"]:
                            imm = int(parts[3])
                            binary_code = assemble_compare(instruction, rd, rs1, imm=imm)
                        else:
                            rs2 = int(parts[3])
                            binary_code = assemble_compare(instruction, rd, rs1, rs2=rs2)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
                    try:
                        rs1 = int(parts[1])
                        rs2 = int(parts[2])
                        LABEL = str(parts[3]) + ":"
                        imm = 4
                        with open("commands.txt", "r") as infile:
                            for index, line in enumerate(infile):
                                if index >= start_line and len(line) > 0 and line != LABEL:
                                        imm = imm + 4
                                elif line and line == LABEL:
                                        break                           
                        binary_code = assemble_branch(instruction, rs1, rs2, imm)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                elif instruction in  ["jal", "jalr"]:
                    try:
                        if instruction == 'jal':
                            if len(parts) == 3:
                                rd = int(parts[1]) 
                                LABEL = str(parts[2]) + ":"
                            else: 
                                rd = 1
                                LABEL = str(parts[1]) + ":"
                            imm = 4
                            with open("commands.txt", "r") as infile:
                                for index, line in enumerate(infile):
                                    if index >= start_line and len(line) > 0 and line != LABEL:
                                        imm = imm + 4
                                    elif line and line == LABEL:
                                        break
                            binary_code = assemble_jal(instruction, rd, rs1=None, imm=imm)
                        else:
                            rd = int(parts[1])
                            rs1 = int(parts[2])
                            imm = int(parts[3])
                            binary_code = assemble_jal(instruction, rd, rs1=rs1, imm=imm)
                    except Exception as e:
                        print(f"Lỗi khi xử lý lệnh {instruction}: {e}")
                        continue
                else:
                    print(f"Lệnh không hợp lệ: {instruction}")
                    continue
                outfile.write("- " + parts[0] + ": " + binary_code + " ----> " + binary_to_hex(binary_code) + "\n")
                print(f"Đã in mã máy thành công vào file machine_codes.txt!!")
    except Exception as e:
        print(f"Lỗi khi xử lý file: {e}")
input_filename = 'commands.txt'  
output_filename = 'machine_codes.txt'  
process_file(input_filename, output_filename)

