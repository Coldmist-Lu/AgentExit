import json

def load_multiple_json_objects(file_path):
    objs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        buffer = ''
        brace_count = 0

        for line in f:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            for char in line:
                buffer += char
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1

                if brace_count == 0 and buffer:
                    # 解析完整一个对象
                    try:
                        obj = json.loads(buffer)
                        objs.append(obj)
                    except json.JSONDecodeError as e:
                        print(f"解析错误: {e}")
                        print(f"出问题的数据块: {buffer}")
                        raise e
                    buffer = ''  # 清空继续下一个

        if buffer.strip() != '':
            print(f"警告: 文件末尾还有未解析的数据: {buffer}")

    return objs
