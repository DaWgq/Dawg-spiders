import random
import time
from DrissionPage import ChromiumPage


def main():
    # 实例化浏览器对象
    page = ChromiumPage()

    # 开启监听，指定目标请求的 URL 特征
    page.listen.start("v2/comment/page")

    # 目标网址
    url = "https://www.xiaohongshu.com/explore/69c4b768000000002202ab38?xsec_token=ABzX56WxqcGA7VzmxWm2ofUQW6lC56J9B9-cvqmVgLBs0=&xsec_source=pc_feed"
    page.get(url)

    print("等待页面加载，请确保已经完成登录...")
    time.sleep(5)  # 留出一定时间加载页面或人工介入确认

    print("开始模拟向下滚动，并抓取评论数据...")
    all_comments = []

    # 模拟滚动抓取
    # 假设我们滚动 15 次，实际可根据是否还返回评论数据来判断是否到底
    for i in range(15):
        print(f"--- 正在进行第 {i + 1} 次下滑 ---")

        # 模拟页面向下滑动 (参数为滑动的像素，可根据实际情况调整)
        # 有时候小红书的评论在特定的容器里，如果全局滚动没反应，可以尝试滚动特定元素
        page.ele('.note-scroller').scroll.to_bottom()
        time.sleep(random.uniform(2.5, 3))

        # 等待目标数据包，超时时间设为 3 秒
        packet = page.listen.wait(timeout=3)

        if packet:
            try:
                # 获取并解析 JSON 响应
                resp_data = packet.response.body
                if "data" in resp_data and "comments" in resp_data["data"]:
                    comments = resp_data["data"]["comments"]
                    if not comments:
                        print("返回的评论数据为空，可能已经到底。")
                        break

                    for comment in comments:
                        nickname = comment.get("user_info", {}).get(
                            "nickname", "未知用户"
                        )
                        content = comment.get("content", "")
                        # 也可按需提取点赞数、时间、IP属地等: comment.get('like_count'), comment.get('ip_location')

                        print(f"用户: {nickname} | 评论: {content}")
                        all_comments.append({"nickname": nickname, "content": content})
            except Exception as e:
                print(f"解析数据包时发生错误: {e}")
        else:
            print("未监听到新的评论数据，可能需要等待或已经到底。")

        # 暂停一下，模拟人类真实的浏览速度，防止触发反爬
        time.sleep(1.5)

    print(f"抓取结束，共成功抓取 {len(all_comments)} 条首层评论！")


if __name__ == "__main__":
    main()
