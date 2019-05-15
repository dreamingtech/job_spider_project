import lxml
import requests
import re
from lxml import etree
from io import BytesIO
from PIL import Image


origin_url = "https://www.zhipin.com/gongsi/ba1fd0561b80a2121nBy0tS5EQ~~.html"

headers = {
    "Referer": origin_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
}
popup_captcha_url = "https://www.zhipin.com/captcha/popUpCaptcha?redirect={}".format(origin_url)

response = requests.get(popup_captcha_url, headers=headers)
html = etree.HTML(response.content.decode())
random_key_str = html.xpath('//img[@class="code"]/@src')[0]
print(random_key_str)
random_key = re.search(r"randomKey=(.*)", random_key_str).group(1)
headers = {
    "Referer": popup_captcha_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
}
captcha_url = "https://www.zhipin.com/captcha?randomKey={}".format(random_key)
response = requests.get(captcha_url, headers=headers)

Image.open(BytesIO(response.content)).show()