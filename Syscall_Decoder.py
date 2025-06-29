import os
import struct

class SyscallSimulator:
    def __init__(self):
        self.registers = {'name_buffer': bytearray(50)}  
        self.memory = {}  
        self.labels = {}  
        self.output = []  
        self.files = {}  # Để lưu trữ các file đang mở.
        self.file_counter = 3  # File descriptors bắt đầu từ 3 (0 là stdin, 1 là stdout, 2 là stderr).
        self.exit_flag = False

        # Các thanh ghi dấu chấm động (floating point registers)
        self.fp_registers = {f'f{i}': 0.0 for i in range(32)}

    def _log(self, message):
        """Ghi log đầu ra"""
        self.output.append(str(message))

    def _get_string(self, address):
        """Lấy chuỗi từ bộ nhớ tại địa chỉ đã cho"""
        result = []
        if address == 'name_buffer':  
            return bytes(self.registers['name_buffer']).decode('ascii').rstrip('\x00')

        while address in self.memory and self.memory[address] != '\0':
            result.append(self.memory[address])
            address += 1
        return ''.join(result)

    def _get_float(self, address):
        """Lấy giá trị dấu chấm động từ bộ nhớ"""
        return struct.unpack('f', bytes(self.memory[address:address + 4]))[0]

    def _set_float(self, address, value):
        """Lưu giá trị dấu chấm động vào bộ nhớ"""
        float_bytes = struct.pack('f', value)
        for i in range(4):
            self.memory[address + i] = float_bytes[i]

    def _process_syscall(self):
        """Xử lý các syscall"""
        syscall = self.registers.get('a7', 0)

        if syscall == 4:  # Print string
            address = self.registers.get('a0', 0)
            string = self._get_string(address)
            self._log(string)

        elif syscall == 1:  # Print integer
            value = self.registers.get('a0', 0)
            self._log(str(value))

        elif syscall == 5:  # Read integer input
            try:
                value = int(input("Nhập số nguyên: "))
                self.registers['a0'] = value
            except ValueError:
                self._log("Lỗi nhập số nguyên")
                self.registers['a0'] = 0

        elif syscall == 8:  # Read string input
            max_length = self.registers.get('a1', 50)
            input_str = input("Nhập chuỗi: ")[:max_length - 1]
            name_buffer = bytearray(input_str.encode('ascii') + b'\x00')
            name_buffer = name_buffer[:max_length]
            self.registers['name_buffer'] = name_buffer

        elif syscall == 11:  # Print character
            char = chr(self.registers.get('a0', 0))
            self._log(char)

        elif syscall == 12:  # Read a single character
            char = input("Nhập một ký tự: ")[0]
            self.registers['a0'] = ord(char)

        elif syscall == 10:  # Exit the program
            self._log("Kết thúc chương trình")
            self.exit_flag = True

        elif syscall == 2:  # Open file
            filename = self._get_string(self.registers.get('a0', 0))
            mode = self.registers.get('a1', 0)
            try:
                if mode == 0:  # Read-only
                    file = open(filename, 'r')
                elif mode == 1:  # Write-only
                    file = open(filename, 'w')
                elif mode == 2:  # Read-Write
                    file = open(filename, 'r+')
                self.files[self.file_counter] = file
                self.registers['a0'] = self.file_counter
                self.file_counter += 1
            except Exception as e:
                self._log(f"Lỗi mở tệp: {e}")
                self.registers['a0'] = -1

        elif syscall == 3:  # Close file
            fd = self.registers.get('a0', 0)
            if fd in self.files:
                self.files[fd].close()
                del self.files[fd]
                self.registers['a0'] = 0
            else:
                self._log("Lỗi đóng tệp")
                self.registers['a0'] = -1

        elif syscall == 4:  # Write to file (stdout or file)
            fd = self.registers.get('a0', 0)
            data_addr = self.registers.get('a1', 0)
            length = self.registers.get('a2', 0)
            data = self._get_string(data_addr)[:length]

            if fd == 1:  # Standard output (stdout)
                self._log(data)
            elif fd in self.files:  # Write to file
                self.files[fd].write(data)
                self.registers['a0'] = length
            else:
                self._log("Lỗi ghi tệp")
                self.registers['a0'] = -1

        elif syscall == 5:  # Read from file
            fd = self.registers.get('a0', 0)
            buffer_addr = self.registers.get('a1', 0)
            length = self.registers.get('a2', 0)

            if fd in self.files:
                data = self.files[fd].read(length)
                for i in range(len(data)):
                    self.memory[buffer_addr + i] = data[i]
                self.registers['a0'] = len(data)
            else:
                self._log("Lỗi đọc tệp")
                self.registers['a0'] = -1

        elif syscall == 6:  # Seek (move file pointer)
            fd = self.registers.get('a0', 0)
            offset = self.registers.get('a1', 0)
            whence = self.registers.get('a2', 0)

            if fd in self.files:
                self.files[fd].seek(offset, whence)
                self.registers['a0'] = 0
            else:
                self._log("Lỗi di chuyển con trỏ tệp")
                self.registers['a0'] = -1

        elif syscall == 9:  # Memory allocation (mmap)
            size = self.registers.get('a0', 0)
            self.memory[self.file_counter] = bytearray(size)
            self.registers['a0'] = self.file_counter
            self.file_counter += 1

        elif syscall == 14:  # Load floating point number into register
            reg = self.registers.get('a0', 0)
            value = self.registers.get('a1', 0)
            self.fp_registers[f'f{reg}'] = struct.unpack('f', bytes([value, 0, 0, 0]))[0]
        
        return self.exit_flag

    def _process_instruction(self, instruction):
        """Xử lý các lệnh assembly"""
        parts = instruction.split()
        if not parts:
            return

        op = parts[0]

        try:
            if op == 'li':  
                reg = parts[1].rstrip(',')
                value = int(parts[2], 0)
                self.registers[reg] = value

            elif op == 'la': 
                reg = parts[1].rstrip(',')
                label = parts[2]
                self.registers[reg] = label

            elif op == 'mv':  
                dest = parts[1].rstrip(',')
                src = parts[2]
                self.registers[dest] = self.registers.get(src, 0)

            elif op == 'ecall':
                return self._process_syscall()

        except Exception as e:
            print(f"Lỗi xử lý lệnh: {instruction}")
            print(e)

    def load_assembly(self, file_path):
        """Tải và phân tích tệp assembly"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy tệp {file_path}")
            return False

        is_data = is_text = False
        mem_address = 0x1000

        for line in lines:
            line = line.strip()

            if line == '.data':
                is_data = True
                is_text = False
                continue
            elif line == '.text':
                is_data = False
                is_text = True
                continue

            if is_data and ':' in line and '.asciz' in line:
                label, string_content = line.split(':', 1)
                label = label.strip()
                string_value = string_content.split('"')[1]
                self.labels[label] = mem_address
                for char in string_value + '\0':
                    self.memory[mem_address] = char
                    mem_address += 1

            if is_text:
                if self._process_instruction(line):
                    break

        return True

    def run(self, input_file, output_file='syscall_output.txt'):
        """Chạy mô phỏng"""
        if not self.load_assembly(input_file):
            return

        while not self.exit_flag:
            pass  # Lặp qua các lệnh syscall cho đến khi thoát

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.output))
        self._log_registers(output_file)

    def _log_registers(self, output_file):
        """Ghi các giá trị thanh ghi dưới dạng hex và floating point vào file"""
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("\n\n--- Giá trị thanh ghi ---\n")
            for reg, value in self.registers.items():
                if isinstance(value, int):
                    f.write(f"{reg}: {value:08x}\n")
                else:
                    f.write(f"{reg}: Không có giá trị\n")

            for reg, value in self.fp_registers.items():
                f.write(f"{reg}: {value:.6f}\n")

    def _log_memory(self, output_file):
        """Ghi các giá trị bộ nhớ vào file"""
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("\n\n--- Bộ nhớ ---\n")
            for addr, value in self.memory.items():
                f.write(f"Địa chỉ {addr:08x}: {chr(value)}\n")

def simulate_syscall(input_file, output_file='syscall_output.txt'):
    simulator = SyscallSimulator()
    simulator.run(input_file, output_file)

if __name__ == "__main__":
    simulate_syscall("syscall_input.txt")
