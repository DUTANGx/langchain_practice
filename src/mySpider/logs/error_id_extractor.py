import re

''' 
tmp handle command
cat cryptohistoryhour.log | grep "429 Unknown Status" > tmp.log
'''

def extract_ids_from_log(file_path):
    # 存储提取的id
    id_list = set()
    
    # 打开日志文件并读取内容
    with open(file_path, 'r') as file:
        for line in file:
            # 使用正则表达式提取id
            ids = re.findall(r'id=(\d+)', line)
            # 将提取的id添加到列表中
            id_list.update([int(id) for id in ids])
    
    return id_list

# 日志文件的路径
log_file_path = 'tmp.log'

# 提取id
extracted_ids = extract_ids_from_log(log_file_path)

print(extracted_ids)