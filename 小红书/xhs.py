from DrissionPage import ChromiumPage

page = ChromiumPage()
page.listen.start('comment/page')
url = 'https://www.xiaohongshu.com/explore/69b92ef1000000002003b1b2?xsec_token=ABwWbF-cllcq0GPYSqFaEfMWGKResNbRyE9UHZcrpTDME=&xsec_source=pc_cfeed'
page.get(url)
data = page.listen.wait().response.body
for i in range(10):
    print('正在加载第%d页评论...'%(i+1))
    page.scroll.down(1000)