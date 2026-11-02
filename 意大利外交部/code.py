import time

from DrissionPage import ChromiumPage
page = ChromiumPage()
page.get("https://prenotami.esteri.it/")
login_btn = page.ele('.button primary')
login_btn.click()
time.sleep(2)
page.ele('.form-control').input('123456')
time.sleep(5)
page.ele('#floatingLabelInput38').input('123456')
time.sleep(3)
page.ele('Next').click()