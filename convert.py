# Đọc dữ liệu từ file txt gốc và ghi dữ liệu đã xử lý ra file mới
def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Tìm vị trí bắt đầu của đường dẫn
            path_start = line.find('InkData_word_processed_2')
            if path_start != -1:
                # Lấy phần đường dẫn từ vị trí bắt đầu đến hết
                processed_line = line[path_start:].split(',')[0]
                outfile.write(processed_line + '\n')

# Sử dụng file input và output
input_file = input()  # Thay bằng đường dẫn file input của mày
output_file = 'confirmed.txt'  # Thay bằng tên file output mà mày muốn

process_file(input_file, output_file)