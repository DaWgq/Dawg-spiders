from DrissionPage import ChromiumPage
import time
import pandas as pd
import os

# 创建数据目录
os.makedirs('data', exist_ok=True)

page = ChromiumPage()
page.listen.start('client.action')
# 目标商品的链接
page.get('https://item.jd.com/100214216975.html?extension_id=eyJhZCI6IjY3OTQwIiwiY2giOiIyIiwic2t1IjoiMTAwMjE0MjE2OTc1IiwidHMiOiIxNzc0MDg0ODU0IiwidW5pcWlkIjoie1wiY2xpY2tfaWRcIjpcIjUzMWM5ZGRiLWFmOWItNDQ4Yi1iODIxLTExNjlkNmRkMTY5ZFwiLFwibWF0ZXJpYWxfaWRcIjpcIjgxMzcyNjgyNzI0NzA5NzEwNTNcIixcInBvc19pZFwiOlwiNjc5NDBcIixcInNpZFwiOlwiYmI5ZTUxZTUtYmVlNi00Y2QxLWJjODItNzU4ZGIxOGQzNTgwXCJ9In0%3D&jd_pop=531c9ddb-af9b-448b-b821-1169d6dd169d&abt=0')
page.wait.doc_loaded()
page.ele('text:全部评价').click()
page.wait.doc_loaded()

all_comments = []
scroll_count = 0
max_scroll = 50

while scroll_count < max_scroll:
    scroll_count += 1
    print(f'第 {scroll_count} 次滚动...')
    
    container = page.ele('._rateListContainer_1ygkr_45')
    container.scroll.down(1000)
    time.sleep(2)
    
    # 检测并点击展开更多评论
    expand_btn = page.ele('._hoverContent_1ygkr_111', timeout=0.5)
    if expand_btn:
        print('  发现展开按钮，点击展开更多评论')
        expand_btn.click()
        time.sleep(2)
    
    packet = page.listen.wait(timeout=5)
    if scroll_count == 1:
        print('  跳过第一个数据包')
        continue
    
    if packet and packet.response:
        try:
            data = packet.response.body
            floors = data.get('result', {}).get('floors', [])
            for floor in floors:
                if floor.get('mId') == 'commentlist-list':
                    comment_list = floor.get('data', [])
                    for item in comment_list:
                        info = item.get('commentInfo', {})
                        comment = {
                            '评论ID': info.get('commentId', ''),
                            '用户昵称': info.get('userNickName', ''),
                            '评论日期': info.get('commentDate', ''),
                            '评分': info.get('commentScore', ''),
                            '评分文本': info.get('commentScoreText', ''),
                            '评论内容': info.get('commentData', ''),
                            '点赞数': info.get('praiseCnt', ''),
                            '回复数': info.get('replyCnt', ''),
                            '产品规格': info.get('productSpecifications', ''),
                            '购买次数': info.get('buyCount', ''),
                            '图片数量': len(info.get('pictureInfoList', []))
                        }
                        all_comments.append(comment)
                        print(f"  [{comment['用户昵称']}] {comment['评论日期']} | 评分:{comment['评分']} | {comment['评论内容'][:30]}...")
                    print(f'  抓取到数据包，新增 {len(comment_list)} 条评论')
        except Exception as e:
            print(f'  解析数据包失败: {e}')
    
    scroll_top = container.run_js('return this.scrollTop')
    scroll_height = container.run_js('return this.scrollHeight')
    client_height = container.run_js('return this.clientHeight')
    
    if scroll_top + client_height >= scroll_height - 10:
        print('已滚动到底部')
        break

# 去重
df = pd.DataFrame(all_comments)
df = df.drop_duplicates(subset=['评论ID'])

# 保存Excel
output_file = f'./jd_comments_{time.strftime("%Y%m%d_%H%M%S")}.xlsx'
df.to_excel(output_file, index=False)
print(f'\n抓取完成！共 {len(df)} 条评论，已保存至 {output_file}')