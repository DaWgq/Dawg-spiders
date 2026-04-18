import time
from DrissionPage import ChromiumPage



page = ChromiumPage()
page.get('https://detail.tmall.com/item.htm?ali_refid=a3_430673_1006%3A1437060120%3AH%3A7aU93pdNaraC452XRx%2FSFA%3D%3D%3Afd0f626df0a50ab00af966fafdd5cd9c&ali_trackid=318_fd0f626df0a50ab00af966fafdd5cd9c&id=871198825462&loginBonus=1&mi_id=0000DYAWTxlYnaYB22cT4yaEoVFB6USZV7RLzO98Sp2SYpo&mm_sceneid=0_0_1699100096_0&priceTId=214784fa17746211361404627e1178&skuId=5869245090115&spm=a21n57.sem.item.5&utparam=%7B%22aplus_abtest%22%3A%22314a228ccb61869b22c4b8d32e70142a%22%7D&xxc=ad_ztc')
page.ele('查看全部评价').click()
page.wait.doc_loaded()
elements = page.eles('@@class:beautify-scroll-bar')
import time

# 1. 抓取页面上所有带有这个类的元素（因为可能有多个隐藏的干扰项）
element = page.eles('@@class:beautify-scroll-bar')

target_box = None
for ele in elements:
    # 【关键修正】这里使用 DrissionPage 专属的可见性判断语法
    if ele.states.is_displayed:
        target_box = ele
        break

if target_box:
    print("成功找到肉眼可见的评论框真身！")

    # 尝试方式 1：直接让这个元素内部向下滑动 1000 像素
    target_box.scroll.down(1000)
    time.sleep(1)

    # 尝试方式 2：如果方式 1 淘宝还是没反应，直接解除注释用下面的 JS 暴力滑动
    # page.run_js('arguments[0].scrollTop += 1000;', target_box)

    # 尝试方式 3：直接滚到底部触发加载
    # page.run_js('arguments[0].scrollTop = arguments[0].scrollHeight;', target_box)

else:
    print("没找到可见的评论框，请确认右侧弹窗是否已打开")