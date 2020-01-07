import os
from selenium import webdriver
import time
import urllib
import urllib.request
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

def getUrl(keyWord):
    isEn = all(ord(c) < 128 for c in keyWord)
    if (isEn):
        return 'https://www.google.com/search?q=' + keyWord + '&safe=strict&source=lnms&tbm=isch'
    else:
        return 'https://www.google.com/search?q=' + keyWord + '&safe=strict&hl=zh-CN&source=lnms&tbm=isch'


def crawler(key_word, out_dir):
    # 获得搜索页面url
    url = getUrl(key_word)
    # 打开浏览器
    driver = webdriver.Chrome()
    driver.get(url)
    # 存储高清图片的url
    output_set = set()
    # 储存图片的element
    element_set = set()

    print('开始爬取高清图片url！')

    pos = 0
    # 先将页面滚动到底部，显示出所有的图片
    for i in range(20):
        pos += 6000  # 每次下滚600
        js = "document.documentElement.scrollTop=%d" % pos
        driver.execute_script(js)
        # 收集所有图片的element
        for element in driver.find_elements_by_xpath('//div[@id="rg"]/div/div/a/img'):
            element_set.add(element)
        time.sleep(2)
        try:
            driver.find_element_by_xpath('/html/body/div/div/div/div/span/div/div/input').click()
        except:
            pass

    print('图片个数：', len(element_set))

    for element_i, element in enumerate(element_set):
        img_url = element.get_attribute('src')
        if img_url is not None:
            ActionChains(driver).click(element).perform()
            # 由于点击事件可能会打开新的窗口，需要关闭新的窗口
            handle = driver.current_window_handle  # 当前窗口
            handles = driver.window_handles  # 所有窗口
            for newhandle in handles:
                # 新打开的窗口
                if newhandle != handle:
                    driver.switch_to_window(newhandle)
                    driver.close()
                    driver.switch_to_window(handle)
            e1 = driver.find_element_by_xpath('//*[@id="irc-ss"]/div/div/div/div/a/div/img')
            hd_img_url = e1.get_attribute('src')
            if hd_img_url not in output_set:
                print(f'{element_i}:{hd_img_url}')
            output_set.add(hd_img_url)

    file = f'{out_dir}{key_word}_url.txt'
    with open(file, 'a+') as f:
        for val in output_set:
            f.write(str(val) + '\n')

    print('开始爬取高清图片！')

    for i, val in enumerate(output_set):
        try:
            if val is None:
                continue
            urllib.request.urlretrieve(str(val), f"{out_dir}/{i}.jpg")
            print(f'{val}: ok!')
        except Exception:
            print(f'{val}: error!')

    print('爬取完毕！')

    # 关闭浏览器
    driver.close()


if __name__ == '__main__':

    # 设置命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", type=str)
    parser.add_argument("--path", type=str)
    args = parser.parse_args()
    keyword = args.keyword
    out_dir = args.path
    print("关键字：", args.keyword)
    print("图片存储路径", args.path)

    # 不存在则创建目录
    if os.path.exists(args.path) == False:
        os.makedirs(args.path)

    # 开始爬虫
    crawler(args.keyword, args.path)

