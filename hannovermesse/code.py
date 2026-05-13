from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.hannovermesse.de/en/search/?category=ep')
page.wait.doc_loaded()
div = page.ele('.grid-x search-snippet-list-items')
items = div.eles('.cell small-12')
for i in range(481):
    for item in items:
        # 跳过没有 data-cy='searchResultEntry' 属性的元素
        if not item.attr('data-cy') == 'searchResultEntry':
            continue
        href = item.ele('tag:a').attr('href')
        print( href)