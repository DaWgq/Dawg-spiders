import requests
from bs4 import BeautifulSoup
import csv

# 读取HTML文件
with open('code.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 找到"具有本属性的典型角色"部分
character_section = soup.find('h2', id='具有本属性的典型角色')
if character_section:
    # 找到该标题后的ul列表
    ul_tag = character_section.find_next('ul')
    
    if ul_tag:
        # 提取所有角色名称
        characters = []
        for li in ul_tag.find_all('li'):
            # 找到所有的<b>标签中的<a>标签
            bold_tags = li.find_all('b')
            for bold in bold_tags:
                a_tag = bold.find('a')
                if a_tag and a_tag.get('title'):
                    character_name = a_tag.get('title')
                    characters.append(character_name)
        
        # 保存到CSV文件
        with open('白发角色.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['角色名称'])  # 写入表头
            for char in characters:
                writer.writerow([char])
        
        print(f'成功提取 {len(characters)} 个角色名称')
        print('已保存到: 白发角色.csv')
        
        # 打印前几个角色作为示例
        print('\n前10个角色:')
        for i, char in enumerate(characters[:10], 1):
            print(f'{i}. {char}')
else:
    print('未找到角色列表部分')