import csv
import time
import random
import logging
from logging import lastResort
from urllib.parse import urljoin
import selenium
import requests
import bs4
from concurrent.futures import ThreadPoolExecutor

from pandas.tseries.holiday import next_monday
from statsmodels.sandbox.regression.penalized import next_odd

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def request_content(url, retries=3):
    """
    发送 HTTP 请求并返回网页内容。
    :param url: 目标 URL
    :param retries: 重试次数
    :return: 网页内容（字符串）或 None（如果请求失败）
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查状态码
            return response.text
        except requests.RequestException as e:
            logging.warning(f"请求失败: {e}, 重试中...")
            time.sleep(random.randint(2, 5))
    logging.error(f"无法获取页面内容: {url}")
    return None


def process_page(base_url, page, writer):
    """
    处理单个页面，抓取明星信息并写入 CSV 文件。
    :param base_url: 基础 URL
    :param page: 当前页码
    :param writer: CSV 写入器
    """
    page_url = base_url + str(page)
    logging.info(f"开始抓取页面: {page_url}")

    pre_soup = bs4.BeautifulSoup(request_content(page_url), 'html.parser')
    if not pre_soup:
        logging.warning(f"页面 {page_url} 请求失败")
        return

    star_list = pre_soup.find_all('a', class_='model-top__img model-top__img--video')
    video_quantity_list = pre_soup.find_all(class_='model-top__scene')

    quantity = []
    for video_quantity in video_quantity_list:
        b_tag = video_quantity.find('b')
        quantity.append(b_tag.text.strip() if b_tag else "N/A")

    for k, star in enumerate(star_list):
        star_info_url = star.get('href')
        star_info = bs4.BeautifulSoup(request_content(star_info_url), 'html.parser')
        if not star_info:
            logging.warning(f"明星详情页 {star_info_url} 请求失败")
            continue

        star_name = star_info.find('h1', class_='model__title')
        star_nation = star_info.find('a', class_='text-primary')
        table = star_info.find('table', class_='model__info')
        if table:
            # 找到第二个 tr 标签（索引从 0 开始）
            rows = table.find_all('tr')
            if len(rows) > 1:
                age_row = rows[1]  # 第二个 tr 标签
                # 找到 div class="fw-bold" 的标签
                age_div = age_row.find('div', class_='fw-bold')
                if age_div:
                    star_age = age_div.text.strip()
                else:
                    star_age = 'N/A'
            else:
                continue
        else:
            continue
        # star_age = star_info.find(class_='fw_bold')

        if star_name and star_nation and star_age:
            writer.writerow([
                star_name.text.strip(),
                star_age,
                star_nation.text.strip(),
                quantity[k],
                star_info_url
            ])
        else:
            logging.warning(f"未找到完整信息：{star_info_url}")
        time.sleep(random.randint(1, 3))  # 随机等待，避免被封禁

        video_page_list = star_info.find_all('a', class_='pagination__item __pagination_button')

        if not video_page_list:
            page_index = 1
            save_video_list(star_name.text.strip(), star_info_url, page_index)
        else:
            for video_page in video_page_list:
                next_page_index = video_page.findNext('a', class_='pagination__item __pagination_button')
                next_next_page_index = next_page_index.find_next_sibling('a',
                                                                         class_='pagination__item __pagination_button')
                if next_next_page_index == None:
                    pro_page_index = int(next_page_index['href'][-1])
                    break
            save_video_list(star_name.text.strip(), star_info_url, pro_page_index)

    logging.info(f"Page {page}/111 抓取完成。")


def clean_filename(filename):
    """清理文件名中的非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def save_video_list(star_name, star_info_url, page_index):
    # 清理文件名
    star_name = clean_filename(star_name)
    # 打开 CSV 文件
    with open(file=f"./Data/Show_list.csv", mode='a', encoding='utf-8', newline='') as vi:
        writer = csv.writer(vi)
        print(f"开始写入{star_name}的视频列表")
        # writer.writerow(['Video Name'])  # 写入表头
        for i in range(1, page_index + 1):
            # 获取当前页的内容
            star_info_url_sub = urljoin(star_info_url, str(i))  # 拼接 URL
            # print(star_info_url_sub)
            star_info_html = request_content(star_info_url_sub)
            if not star_info_html:
                print(f"无法获取页面: {star_info_url_sub}")

            star_info = bs4.BeautifulSoup(star_info_html, 'html.parser')
            video_list = star_info.find_all('div', class_='card-scene__text')
            # 如果没有视频列表，退出循环
            if not video_list:
                print(f"第 {star_info_url_sub} 页没有视频列表")
            # 写入视频名称
            for video in video_list:
                video_name = video.find('a').text.strip()

            # write-in actors
                video_page_url = video.find('div', class_='card-scene__text').find('a')['href']
                video_page_soup = bs4.BeautifulSoup(request_content(video_page_url), 'html.parser')
                actors = video_page_soup.find_all('a', class_='text-primary')
                actor_name_ally = []
                for actor in actors:
                    actor_name = actor.text.strip()
                    actor_name_ally.append(actor_name)
                actor_name_str = ', '.join(actor_name_ally)
                writer.writerow([star_name.strip(), video_name,actor_name_str])

            print(f"{star_name}----第 {i}/{page_index} 页视频列表已写入")
            time.sleep(random.randint(1, 3))  # 随机等待


def down_info(base_url):
    """
    主抓取函数，负责多线程抓取并保存数据。
    :param base_url: 基础 URL
    """
    with open("./Data/Star_Info.csv", mode="w", encoding="utf-8", newline='') as SI:
        #fieldnames = ['Name', 'Age', 'Nation', 'Video Quantity', 'Url']
        writer = csv.writer(SI)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_page, base_url, page, writer) for page in range(1, 2)]
            for future in futures:
                future.result()  # 等待所有任务完成


def main():
    """
    程序入口。
    """
    base_url = 'https://.com/models/page/'  # 基础 URL
    down_info(base_url)


if __name__ == '__main__':
    main()