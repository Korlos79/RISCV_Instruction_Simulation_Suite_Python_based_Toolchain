def print_memory_section(data_memory, start_addr, end_addr):
    """In ra dữ liệu bộ nhớ từ địa chỉ start_addr đến end_addr."""
    result = ""
    for i in range(start_addr, end_addr + 1, 32):  # Duyệt đến end_addr (bao gồm cả nó)
        result += f"0x{i:08x}  "  # In địa chỉ bộ nhớ bắt đầu của nhóm 32 byte
        
        # In 8 giá trị 32-bit cho mỗi dòng
        for j in range(8):
            # Lấy giá trị tại địa chỉ i + j*4, nếu không có giá trị, mặc định là 0
            value = data_memory.get(i + j * 4, 0)
            
            # Kiểm tra nếu giá trị là kiểu chuỗi, cần chuyển thành số nguyên
            if isinstance(value, str):
                value = int(value, 16)  # Chuyển giá trị chuỗi hex thành số nguyên
            
            result += f"0x{value:08x} "  # In ra giá trị của từng 32-bit

        result += "\n"  # Chuyển xuống dòng mới
    return result


def decode_instruction(instruction, data_memory, registers, pc, labels):
    opcode = instruction & 0x7f
    rd = (instruction >> 7) & 0x1f
    funct3 = (instruction >> 12) & 0x7
    rs1 = (instruction >> 15) & 0x1f
    rs2 = (instruction >> 20) & 0x1f
    funct7 = (instruction >> 25) & 0x7f
    imm = instruction >> 20

    # Sign extension for 12-bit immediate
    if imm & 0x800:
        imm -= (1 << 12)

    # Lệnh LI (Load Immediate)
    # LI không phải là một lệnh RISC-V chuẩn, nhưng chúng ta có thể mô phỏng bằng cách sử dụng LUI và ADDI
    # Giả sử LI được thực hiện như sau:
    if opcode == 0x37:  # LUI opcode
        value = imm << 12
        registers[rd] = value
        return f"li x{rd}, {value}"  # Giả lập lệnh LI

    # AUIPC (Add Upper Immediate to PC)
    elif opcode == 0x17:
        value = imm << 12
        registers[rd] = value
        return f"auipc x{rd}, {value}"

    # JAL (Jump and Link)
    elif opcode == 0x6f:
        imm = ((instruction >> 21) & 0x3ff) | ((instruction >> 20) & 0x1) << 10 | \
              ((instruction >> 12) & 0xff) << 11 | (instruction & 0x80000000) >> 11
        registers[rd] = imm  # Giả sử chúng ta lưu giá trị này vào thanh ghi
        return f"jal x{rd}, {imm}"

    # JALR (Jump and Link Register)
    elif opcode == 0x67:
        imm = instruction >> 20
        registers[rd] = registers[rs1] + imm
        return f"jalr x{rd}, x{rs1}, {imm}"

    # I-type instructions
    if opcode == 0x13:
        if funct3 == 0x0:  # ADDI
            registers[rd] = registers[rs1] + imm
            return f"addi x{rd}, x{rs1}, {imm}"
        elif funct3 == 0x2:  # SLTI
            registers[rd] = 1 if registers[rs1] < imm else 0
            return f"slti x{rd}, x{rs1}, {imm}"
        elif funct3 == 0x3:  # SLTIU
            registers[rd] = 1 if registers[rs1] < imm else 0
            return f"sltiu x{rd}, x{rs1}, {imm}"
        elif funct3 == 0x4:  # XORI
            registers[rd] = registers[rs1] ^ imm
            return f"xori x{rd}, x{rs1}, {imm}"
        elif funct3 == 0x6:  # ORI
            registers[rd] = registers[rs1] | imm
            return f"ori x{rd}, x{rs1}, {imm}"
        elif funct3 == 0x7:  # ANDI
            registers[rd] = registers[rs1] & imm
            return f"andi x{rd}, x{rs1}, {imm}"

    # Lệnh BEQ (Branch if Equal)
    if opcode == 0x63 and funct3 == 0x0:  # BEQ (Branch Equal)
        imm = ((instruction >> 20) & 0x7fe) | ((instruction >> 7) & 0x1) << 11 | ((instruction >> 25) & 0x3ff) << 5
        if registers[rs1] == registers[rs2]:
            branch_target = pc + imm  # Địa chỉ nhảy
            label_name = f"label_{branch_target:08x}"  # Tạo tên nhãn
            if label_name in labels:
                branch_target = labels[label_name]  # Nếu có nhãn thì nhảy đến địa chỉ của nhãn
            return f"beq x{rs1}, x{rs2}, {imm} -> Jump to {label_name} at {hex(branch_target)}"

    return f"Unknown instruction: {hex(instruction)}"

# Giải mã file với các lệnh mới
def decode_file(input_file, output_file):
    data_memory = {}  # Bộ nhớ .data
    text_memory = {}  # Bộ nhớ .text
    registers = [0] * 32  # 32 thanh ghi, tất cả khởi tạo bằng 0
    pc = 0x00000000
    labels = {}  # Tạo dictionary để lưu trữ các nhãn và địa chỉ của chúng

    with open(input_file, 'r') as f:
        instructions = f.readlines()

    # Đọc và lưu nhãn vào dictionary
    valid_instructions = []
    for i, instruction in enumerate(instructions):
        instruction = instruction.strip()  # Loại bỏ các ký tự không cần thiết
        if instruction:  # Nếu dòng không trống
            try:
                # Kiểm tra xem chuỗi có phải là nhị phân hợp lệ không
                int(instruction, 2)  # Chuyển đổi chuỗi nhị phân thành số nguyên
                valid_instructions.append(instruction)
                # Thêm nhãn vào labels, giả sử nhãn có dạng label_xxxx
                if instruction.startswith("label_"):
                    label_name = instruction.split()[0]
                    labels[label_name] = pc
            except ValueError:
                print(f"Warning: Dòng không hợp lệ (không phải nhị phân): {instruction}")

    # Giải mã các lệnh hợp lệ
    decoded_instructions = []
    for instruction_str in valid_instructions:
        instruction = int(instruction_str, 2)
        decoded_instruction = decode_instruction(instruction, data_memory, registers, pc, labels)
        decoded_instructions.append(decoded_instruction)

        # Cập nhật PC sau mỗi lệnh
        pc += 4  # Giả sử mỗi lệnh có độ dài 4 byte (32-bit)

    # Ghi kết quả vào tệp đầu ra
    with open(output_file, 'w') as f:
        f.write("\n".join(decoded_instructions) + "\n")
        f.write("\n-- Registers --\n")
        f.write("\n".join([f"x{i}: 0x{registers[i]:08x}" for i in range(32)]))
        f.write("\n-- .text Memory --\n")
        f.write(print_memory_section(text_memory, 0x00000000, 0x00000fe0))
        f.write("\n-- .data Memory --\n")
        f.write(print_memory_section(data_memory, 0x00002000, 0x00002fe0))

# Run the program
decode_file('input_instructions.txt', 'decoded_instructions.txt')
