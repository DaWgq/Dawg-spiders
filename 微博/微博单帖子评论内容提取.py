"""
微博评论爬虫脚本
================
功能：自动滚动微博页面，抓取评论数据并保存到Excel

数据字段：
- 用户名：评论者的微博昵称
- 评论内容：评论文本（纯文本格式）
- 地区：评论来源地区（如"浙江"、"广东"）
- 性别：评论者性别（男/女/未知）
- 点赞数：该评论的点赞数量
- 评论时间：评论发布时间
"""

import json
import random
import time
from datetime import datetime

import pandas as pd
from DrissionPage import ChromiumPage

# ==================== 全局变量 ====================

# 存储所有已解析的评论数据
all_comments = []

# 用于去重的评论ID集合，避免重复抓取同一条评论
seen_ids = set()


# ==================== 数据解析函数 ====================

def parse_comment(item):
    """
    解析单条评论数据
    
    参数:
        item: 单条评论的JSON数据字典
        
    返回:
        dict: 包含用户名、评论内容、地区、性别等字段的字典
        None: 如果该评论已存在（重复）则返回None
    """
    # 获取评论唯一ID，用于去重判断
    comment_id = item.get('idstr', '')
    if comment_id in seen_ids:
        return None  # 已存在，跳过
    seen_ids.add(comment_id)
    
    # 获取用户信息对象
    user = item.get('user', {})
    
    # 提取地区信息
    # source字段格式如"来自浙江"，需要去掉"来自"前缀
    source = item.get('source', '')
    region = source.replace('来自', '') if source else ''
    
    # 性别转换：微博API中 'm' 表示男性，'f' 表示女性
    gender_map = {'m': '男', 'f': '女'}
    gender = gender_map.get(user.get('gender', ''), '未知')
    
    # 返回解析后的数据字典
    return {
        '用户名': user.get('screen_name', ''),
        '评论内容': item.get('text_raw', item.get('text', '')),  # 优先使用纯文本格式
        '地区': region,
        '性别': gender,
        '点赞数': item.get('like_counts', 0),
        '评论时间': item.get('created_at', '')
    }


def parse_response(body):
    """
    解析HTTP响应数据
    
    参数:
        body: 响应体，可以是字符串或已解析的字典
        
    返回:
        list: 解析后的评论列表
    """
    comments = []
    try:
        # 判断响应体类型，字符串需要JSON解析
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        # 从响应数据中获取评论列表
        # 微博评论API返回格式：{"ok": 1, "data": [评论列表]}
        comment_list = data.get('data', [])
        
        # 逐条解析评论
        for item in comment_list:
            comment = parse_comment(item)
            if comment:
                comments.append(comment)
    except Exception as e:
        print(f'解析出错: {e}')
    
    return comments


# ==================== 主程序 ====================

# 创建浏览器页面对象（使用DrissionPage库）
page = ChromiumPage()

# 开启网络请求监听，过滤包含'buildComments'的请求（微博评论接口）
page.listen.start('buildComments')

# 访问目标微博页面
page.get('https://weibo.com/2656274875/5209661390462819')

# 等待页面完全加载
time.sleep(3)

# ==================== 爬取参数配置 ====================

# 最大滚动次数限制，防止无限循环
max_scrolls = 50

# 连续无新数据的计数器
no_new_data_count = 0

# 连续多少次无新数据时停止爬取
max_no_new_data = 5

# ==================== 主循环：滚动页面抓取评论 ====================

for i in range(max_scrolls):
    print(f'\n--- 第 {i + 1} 次滚动 ---')
    
    # 检测是否已加载全部评论（页面底部出现"已加载全部评论"提示）
    if page.ele('text:已加载全部评论', timeout=0.5):
        print('\n已加载全部评论，停止抓取')
        break
    
    # 滚动到页面底部，触发评论加载
    page.scroll.to_bottom()
    
    # 检测是否出现"点击加载更多"按钮，如有则点击
    load_more = page.ele('text:点击加载更多', timeout=0.5)
    if load_more:
        print('发现"点击加载更多"按钮，正在点击...')
        load_more.click()
        time.sleep(1)  # 点击后等待加载

    # 等待并捕获评论接口的响应数据
    try:
        # 等待监听的请求响应，超时5秒
        resp = page.listen.wait(timeout=5)
        
        if resp:
            # 获取响应体内容
            body = resp.response.body
            
            # 解析响应数据
            comments = parse_response(body)
            
            # 打印解析到的每条评论信息（便于调试和观察进度）
            for c in comments:
                print(f"用户名: {c['用户名']} | 内容: {c['评论内容'][:30]}... | 地区: {c['地区']} | 性别: {c['性别']}")
            
            if comments:
                # 将本批评论添加到总列表
                all_comments.extend(comments)
                print(f'本批解析 {len(comments)} 条评论，累计 {len(all_comments)} 条')
                no_new_data_count = 0  # 重置无数据计数器
            else:
                print('未解析到新评论')
                no_new_data_count += 1
        else:
            print('未捕获到新数据')
            no_new_data_count += 1
            
    except Exception as e:
        print(f'等待超时或出错: {e}')
        no_new_data_count += 1
    
    # 判断是否连续多次无新数据，若是则停止
    if no_new_data_count >= max_no_new_data:
        print(f'\n连续 {max_no_new_data} 次无新数据，停止抓取')
        break
    
    # 随机延迟，模拟人工操作，降低被封风险
    delay = random.uniform(1.5, 3.0)
    time.sleep(delay)


# ==================== 数据保存 ====================

if all_comments:
    # 将评论列表转换为DataFrame
    df = pd.DataFrame(all_comments)
    
    # 生成带时间戳的文件名
    filename = f'微博评论_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    # 保存到Excel文件（不包含行索引）
    df.to_excel(filename, index=False)
    
    print(f'\n抓取完成，共 {len(all_comments)} 条评论，已保存到 {filename}')
else:
    print('\n未抓取到任何评论')
