import json

# 读取 JSON 文件
with open('mashangpa_7_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 计算所有 current_array 的累加值
total_sum = 0
page_details = []

for page_key in sorted(data.keys(), key=lambda x: int(x)):
    page_data = data[page_key]
    current_array = page_data['current_array']
    page_sum = sum(current_array)
    total_sum += page_sum
    page_details.append({
        'page': page_key,
        'sum': page_sum,
        'count': len(current_array)
    })

# 打印每页详情
print("=" * 50)
print("每页 current_array 求和详情:")
print("=" * 50)
for detail in page_details:
    print(f"第 {detail['page']:>2} 页: {detail['sum']:>6} (共 {detail['count']} 个数字)")

# 打印总计
print("=" * 50)
print(f"所有页面总和: {total_sum}")
print(f"总页数: {len(data)}")
print(f"总数字个数: {sum(d['count'] for d in page_details)}")
print("=" * 50)
