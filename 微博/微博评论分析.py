"""
微博评论数据分析脚本
====================
功能：对爬取的微博评论进行数据清洗、情感分析、主题聚类和可视化

分析模块：
- 数据清洗：处理缺失值、清洗表情符号、时间格式转换
- 情感分析：使用snownlp进行中文情感分析
- 主题聚类：使用LDA主题模型和关键词提取
- 可视化：词云、情感分布、主题分布、地区分布等
"""

import re
import warnings
from datetime import datetime

import jieba
import jieba.analyse
import matplotlib.pyplot as plt
import pandas as pd
from gensim import corpora
from gensim.models import LdaModel
from snownlp import SnowNLP
from wordcloud import WordCloud

# 忽略警告
warnings.filterwarnings('ignore')

# 设置matplotlib中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 数据清洗模块 ====================

def clean_text(text):
    """
    清洗评论文本
    
    参数:
        text: 原始评论文本
        
    返回:
        str: 清洗后的文本
    """
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text)
    
    # 移除微博表情符号 [xxx] 格式
    text = re.sub(r'\[.*?\]', '', text)
    
    # 移除话题标签 #xxx#
    text = re.sub(r'#.*?#', '', text)
    
    # 移除@用户
    text = re.sub(r'@[\w\u4e00-\u9fff]+', '', text)
    
    # 移除URL
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # 移除特殊字符，只保留中文、英文、数字和常见标点
    text = re.sub(r'[^\u4e00-\u9fff\w\s，。！？、；：""\'\'（）\-\.\!\?\,\;:\'"()]', '', text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def parse_weibo_time(time_str):
    """
    解析微博时间格式
    
    参数:
        time_str: 微博时间字符串，如 "Thu Sep 11 12:06:18 +0800 2025"
        
    返回:
        datetime: 解析后的datetime对象
    """
    if pd.isna(time_str) or time_str == '':
        return None
    
    try:
        # 微博时间格式
        dt = datetime.strptime(str(time_str), '%a %b %d %H:%M:%S %z %Y')
        return dt
    except:
        return None


def clean_data(df):
    """
    数据清洗主函数
    
    参数:
        df: 原始数据DataFrame
        
    返回:
        DataFrame: 清洗后的数据
    """
    print('=' * 50)
    print('开始数据清洗...')
    print(f'原始数据量: {len(df)} 条')
    
    # 复制数据
    df_clean = df.copy()
    
    # 1. 清洗评论文本
    df_clean['评论内容_清洗'] = df_clean['评论内容'].apply(clean_text)
    
    # 2. 解析时间
    df_clean['评论时间_解析'] = df_clean['评论时间'].apply(parse_weibo_time)
    df_clean['评论日期'] = df_clean['评论时间_解析'].apply(lambda x: x.strftime('%Y-%m-%d') if x else None)
    df_clean['评论小时'] = df_clean['评论时间_解析'].apply(lambda x: x.hour if x else None)
    
    # 3. 处理缺失值
    df_clean['地区'] = df_clean['地区'].fillna('未知')
    df_clean['性别'] = df_clean['性别'].fillna('未知')
    df_clean['点赞数'] = df_clean['点赞数'].fillna(0)
    
    # 4. 移除清洗后为空的评论
    df_clean = df_clean[df_clean['评论内容_清洗'] != '']
    
    # 5. 移除重复评论
    df_clean = df_clean.drop_duplicates(subset=['评论内容_清洗'], keep='first')
    
    print(f'清洗后数据量: {len(df_clean)} 条')
    print('=' * 50)
    
    return df_clean


# ==================== 情感分析模块 ====================

def analyze_sentiment(text):
    """
    分析单条文本的情感
    
    参数:
        text: 评论文本
        
    返回:
        float: 情感得分 0-1，越接近1越积极
    """
    if not text or text == '':
        return 0.5
    
    try:
        s = SnowNLP(text)
        return s.sentiments
    except:
        return 0.5


def get_sentiment_label(score):
    """
    根据情感得分返回情感标签
    
    参数:
        score: 情感得分
        
    返回:
        str: 情感标签
    """
    if score >= 0.6:
        return '积极'
    elif score <= 0.4:
        return '消极'
    else:
        return '中性'


def sentiment_analysis(df):
    """
    情感分析主函数
    
    参数:
        df: 数据DataFrame
        
    返回:
        DataFrame: 包含情感分析结果的数据
    """
    print('\n开始情感分析...')
    
    df_sentiment = df.copy()
    
    # 计算情感得分
    df_sentiment['情感得分'] = df_sentiment['评论内容_清洗'].apply(analyze_sentiment)
    
    # 获取情感标签
    df_sentiment['情感标签'] = df_sentiment['情感得分'].apply(get_sentiment_label)
    
    # 统计情感分布
    sentiment_counts = df_sentiment['情感标签'].value_counts()
    print(f'\n情感分布:')
    for label, count in sentiment_counts.items():
        print(f'  {label}: {count} 条 ({count/len(df_sentiment)*100:.1f}%)')
    
    return df_sentiment


# ==================== 主题聚类模块 ====================

# 停用词列表
STOPWORDS = set([
    '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
    '那', '她', '他', '它', '们', '这个', '那个', '什么', '怎么', '为什么', '哪', '哪里', '哪个', '吗', '呢', '啊', '吧', '哦', '嗯', '哈', '呀', '额',
    '微博', '评论', '转发', '用户', '今天', '明天', '昨天', '现在', '知道', '以为', '觉得', '感觉', '可以', '可能', '应该', '已经', '还是', '但是', '因为', '所以',
    '如果', '虽然', '或者', '而且', '不过', '一下', '一些', '一点', '这么', '那么', '多么', '如何', '谁', '几', '多少', '何', '此', '彼',
    '支持', '查', '约谈', '平台', '一个', '应该', '真的', '还是', '这种', '那个', '这个'
])


def tokenize(text):
    """
    中文分词
    
    参数:
        text: 文本
        
    返回:
        list: 分词结果
    """
    if not text:
        return []
    
    # jieba分词
    words = jieba.cut(text)
    
    # 过滤停用词和单字
    words = [w for w in words if w not in STOPWORDS and len(w) > 1 and not w.isdigit()]
    
    return words


def extract_keywords(df, top_n=20):
    """
    提取关键词
    
    参数:
        df: 数据DataFrame
        top_n: 返回前N个关键词
        
    返回:
        list: 关键词列表 [(词, 权重), ...]
    """
    print('\n提取关键词...')
    
    # 合并所有文本
    all_text = ' '.join(df['评论内容_清洗'].tolist())
    
    # 使用TF-IDF提取关键词
    keywords = jieba.analyse.extract_tags(all_text, topK=top_n, withWeight=True)
    
    print(f'\nTop {top_n} 关键词:')
    for word, weight in keywords:
        print(f'  {word}: {weight:.4f}')
    
    return keywords


def topic_modeling(df, num_topics=3):
    """
    LDA主题建模
    
    参数:
        df: 数据DataFrame
        num_topics: 主题数量
        
    返回:
        tuple: (LDA模型, 词典, 语料库)
    """
    print(f'\n进行LDA主题建模 (主题数: {num_topics})...')
    
    # 分词
    texts = df['评论内容_清洗'].apply(tokenize).tolist()
    
    # 过滤空文档
    texts = [text for text in texts if len(text) >= 2]
    
    if len(texts) < 10:
        print('数据量不足，跳过主题建模')
        return None, None, None
    
    # 创建词典和语料库
    dictionary = corpora.Dictionary(texts)
    
    # 过滤极端词频
    dictionary.filter_extremes(no_below=2, no_above=0.8)
    
    # 创建词袋模型
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # 训练LDA模型
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=10,
        alpha='auto'
    )
    
    # 打印主题
    print('\n主题聚类结果:')
    for idx, topic in lda_model.print_topics(num_words=8):
        print(f'\n主题 {idx + 1}:')
        # 解析主题词
        topic_words = re.findall(r'"([^"]+)"', topic)
        print(f'  关键词: {", ".join(topic_words)}')
    
    return lda_model, dictionary, corpus


def classify_topic(text, lda_model, dictionary):
    """
    对文本进行主题分类
    
    参数:
        text: 文本
        lda_model: LDA模型
        dictionary: 词典
        
    返回:
        int: 主题编号
    """
    if lda_model is None or dictionary is None:
        return -1
    
    words = tokenize(text)
    if not words:
        return -1
    
    bow = dictionary.doc2bow(words)
    if not bow:
        return -1
    
    topics = lda_model.get_document_topics(bow)
    if not topics:
        return -1
    
    # 返回概率最高的主题
    return max(topics, key=lambda x: x[1])[0]


# ==================== 可视化模块 ====================

def plot_sentiment_distribution(df, save_path=None):
    """
    绘制情感分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成情感分布图...')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 情感标签饼图
    sentiment_counts = df['情感标签'].value_counts()
    colors = {'积极': '#4CAF50', '中性': '#FFC107', '消极': '#F44336'}
    pie_colors = [colors.get(label, '#999') for label in sentiment_counts.index]
    
    axes[0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
                colors=pie_colors, explode=[0.02] * len(sentiment_counts), startangle=90)
    axes[0].set_title('情感分布', fontsize=14, fontweight='bold')
    
    # 情感得分直方图
    axes[1].hist(df['情感得分'], bins=20, color='#2196F3', edgecolor='white', alpha=0.7)
    axes[1].axvline(x=0.4, color='#F44336', linestyle='--', label='消极阈值')
    axes[1].axvline(x=0.6, color='#4CAF50', linestyle='--', label='积极阈值')
    axes[1].set_xlabel('情感得分', fontsize=12)
    axes[1].set_ylabel('评论数量', fontsize=12)
    axes[1].set_title('情感得分分布', fontsize=14, fontweight='bold')
    axes[1].legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_wordcloud(df, save_path=None):
    """
    绘制词云图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成词云图...')
    
    # 合并所有文本
    all_text = ' '.join(df['评论内容_清洗'].tolist())
    
    # 分词
    words = jieba.cut(all_text)
    words = [w for w in words if w not in STOPWORDS and len(w) > 1]
    text_for_cloud = ' '.join(words)
    
    # 生成词云
    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',  # Windows中文字体
        width=1000,
        height=600,
        background_color='white',
        max_words=100,
        colormap='viridis'
    ).generate(text_for_cloud)
    
    plt.figure(figsize=(12, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('评论词云', fontsize=16, fontweight='bold', pad=20)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_region_distribution(df, save_path=None):
    """
    绘制地区分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成地区分布图...')
    
    # 统计地区
    region_counts = df['地区'].value_counts().head(15)
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(range(len(region_counts)), region_counts.values, color='#3F51B5', alpha=0.8)
    plt.yticks(range(len(region_counts)), region_counts.index)
    plt.xlabel('评论数量', fontsize=12)
    plt.ylabel('地区', fontsize=12)
    plt.title('评论地区分布 Top 15', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # 添加数值标签
    for i, v in enumerate(region_counts.values):
        plt.text(v + 0.5, i, str(v), va='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_gender_distribution(df, save_path=None):
    """
    绘制性别分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成性别分布图...')
    
    gender_counts = df['性别'].value_counts()
    colors = {'男': '#2196F3', '女': '#E91E63', '未知': '#9E9E9E'}
    pie_colors = [colors.get(label, '#999') for label in gender_counts.index]
    
    plt.figure(figsize=(8, 6))
    plt.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
            colors=pie_colors, explode=[0.02] * len(gender_counts), startangle=90,
            textprops={'fontsize': 12})
    plt.title('评论者性别分布', fontsize=14, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_time_distribution(df, save_path=None):
    """
    绘制时间分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成时间分布图...')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 按小时分布
    hour_counts = df['评论小时'].dropna().astype(int).value_counts().sort_index()
    axes[0].bar(hour_counts.index, hour_counts.values, color='#00BCD4', alpha=0.8)
    axes[0].set_xlabel('小时', fontsize=12)
    axes[0].set_ylabel('评论数量', fontsize=12)
    axes[0].set_title('评论时间分布（按小时）', fontsize=14, fontweight='bold')
    axes[0].set_xticks(range(0, 24, 2))
    
    # 按日期分布
    date_counts = df['评论日期'].dropna().value_counts().sort_index()
    if len(date_counts) > 0:
        axes[1].bar(range(len(date_counts)), date_counts.values, color='#8BC34A', alpha=0.8)
        axes[1].set_xlabel('日期', fontsize=12)
        axes[1].set_ylabel('评论数量', fontsize=12)
        axes[1].set_title('评论时间分布（按日期）', fontsize=14, fontweight='bold')
        axes[1].set_xticks(range(len(date_counts)))
        axes[1].set_xticklabels(date_counts.index, rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_like_distribution(df, save_path=None):
    """
    绘制点赞分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成点赞分布图...')
    
    # 按点赞数排序
    top_likes = df.nlargest(15, '点赞数')[['用户名', '评论内容', '点赞数']].copy()
    top_likes['评论摘要'] = top_likes['评论内容'].apply(lambda x: x[:20] + '...' if len(str(x)) > 20 else x)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 点赞数直方图
    likes = df['点赞数'].dropna().astype(int)
    axes[0].hist(likes[likes < 200], bins=30, color='#FF5722', alpha=0.7, edgecolor='white')
    axes[0].set_xlabel('点赞数', fontsize=12)
    axes[0].set_ylabel('评论数量', fontsize=12)
    axes[0].set_title('点赞数分布', fontsize=14, fontweight='bold')
    
    # 热门评论Top15
    axes[1].barh(range(len(top_likes)), top_likes['点赞数'].values, color='#FF9800', alpha=0.8)
    axes[1].set_yticks(range(len(top_likes)))
    axes[1].set_yticklabels([f"{name}" for name in top_likes['用户名']], fontsize=9)
    axes[1].set_xlabel('点赞数', fontsize=12)
    axes[1].set_title('热门评论 Top 15', fontsize=14, fontweight='bold')
    axes[1].invert_yaxis()
    
    # 添加数值标签
    for i, v in enumerate(top_likes['点赞数'].values):
        axes[1].text(v + 10, i, str(int(v)), va='center', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


def plot_sentiment_by_region(df, save_path=None):
    """
    绘制各地区情感分布图
    
    参数:
        df: 数据DataFrame
        save_path: 保存路径
    """
    print('\n生成各地区情感分布图...')
    
    # 统计各地区情感
    region_sentiment = df.groupby('地区')['情感得分'].mean().sort_values(ascending=False).head(15)
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(range(len(region_sentiment)), region_sentiment.values, 
                    color=['#4CAF50' if v >= 0.5 else '#F44336' for v in region_sentiment.values], alpha=0.8)
    plt.yticks(range(len(region_sentiment)), region_sentiment.index)
    plt.xlabel('平均情感得分', fontsize=12)
    plt.ylabel('地区', fontsize=12)
    plt.title('各地区平均情感得分 Top 15', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
    
    # 添加数值标签
    for i, v in enumerate(region_sentiment.values):
        plt.text(v + 0.01, i, f'{v:.2f}', va='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f'  保存到: {save_path}')
    
    plt.close()


# ==================== 主程序 ====================

def analyze_weibo_comments(data_path, output_dir='分析结果'):
    """
    微博评论分析主函数
    
    参数:
        data_path: 数据文件路径（Excel）
        output_dir: 输出目录
    """
    import os
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print('\n' + '=' * 60)
    print('微博评论数据分析')
    print('=' * 60)
    
    # 读取数据
    print(f'\n读取数据: {data_path}')
    df = pd.read_excel(data_path)
    print(f'数据列: {df.columns.tolist()}')
    print(f'数据量: {len(df)} 条')
    
    # 1. 数据清洗
    df_clean = clean_data(df)
    
    # 2. 情感分析
    df_sentiment = sentiment_analysis(df_clean)
    
    # 3. 提取关键词
    keywords = extract_keywords(df_sentiment, top_n=30)
    
    # 4. 主题建模
    lda_model, dictionary, corpus = topic_modeling(df_sentiment, num_topics=3)
    
    # 添加主题标签
    if lda_model:
        df_sentiment['主题'] = df_sentiment['评论内容_清洗'].apply(
            lambda x: classify_topic(x, lda_model, dictionary) + 1
        )
    
    # 5. 可视化
    print('\n' + '=' * 60)
    print('生成可视化图表...')
    print('=' * 60)
    
    plot_sentiment_distribution(df_sentiment, f'{output_dir}/情感分布.png')
    plot_wordcloud(df_sentiment, f'{output_dir}/词云图.png')
    plot_region_distribution(df_sentiment, f'{output_dir}/地区分布.png')
    plot_gender_distribution(df_sentiment, f'{output_dir}/性别分布.png')
    plot_time_distribution(df_sentiment, f'{output_dir}/时间分布.png')
    plot_like_distribution(df_sentiment, f'{output_dir}/点赞分布.png')
    plot_sentiment_by_region(df_sentiment, f'{output_dir}/地区情感分布.png')
    
    # 6. 保存分析结果
    output_file = f'{output_dir}/微博评论分析结果.xlsx'
    
    # 转换datetime列为字符串以便保存到Excel
    df_save = df_sentiment.copy()
    if '评论时间_解析' in df_save.columns:
        df_save['评论时间_解析'] = df_save['评论时间_解析'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else ''
        )
    
    df_save.to_excel(output_file, index=False)
    print(f'\n分析结果已保存到: {output_file}')
    
    # 7. 生成分析报告
    print('\n' + '=' * 60)
    print('分析报告摘要')
    print('=' * 60)
    
    print(f'\n【基础统计】')
    print(f'  总评论数: {len(df_sentiment)} 条')
    print(f'  有效评论数: {len(df_clean)} 条')
    print(f'  平均点赞数: {df_sentiment["点赞数"].mean():.1f}')
    print(f'  最高点赞数: {df_sentiment["点赞数"].max():.0f}')
    
    print(f'\n【情感分析】')
    print(f'  平均情感得分: {df_sentiment["情感得分"].mean():.3f}')
    sentiment_counts = df_sentiment['情感标签'].value_counts()
    for label, count in sentiment_counts.items():
        print(f'  {label}评论: {count} 条 ({count/len(df_sentiment)*100:.1f}%)')
    
    print(f'\n【用户画像】')
    gender_counts = df_sentiment['性别'].value_counts()
    for label, count in gender_counts.items():
        print(f'  {label}: {count} 人 ({count/len(df_sentiment)*100:.1f}%)')
    
    top_regions = df_sentiment['地区'].value_counts().head(5)
    print(f'\n  热门地区: {", ".join([f"{r}({c})" for r, c in top_regions.items()])}')
    
    print(f'\n【热门关键词】')
    top_keywords = [w for w, _ in keywords[:10]]
    print(f'  {", ".join(top_keywords)}')
    
    print('\n' + '=' * 60)
    print('分析完成！')
    print('=' * 60)
    
    return df_sentiment


if __name__ == '__main__':
    # 分析已有的微博评论数据
    data_file = '微博评论_20260321_162316.xlsx'
    analyze_weibo_comments(data_file)
