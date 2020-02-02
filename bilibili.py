# asyncio
import time
import json
import asyncio
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Mode': 'navigate',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


cookies = { # 必须参数

}


# 使用到的URL
URL_ = {
    "aid2cid_url": "https://api.bilibili.com/x/player/pagelist?aid=71816014&jsonp=jsonp",
    "danmu_url": "https://api.bilibili.com/x/v2/dm/history?type=1&oid=124606776&date=2020-01-01"
}

# 视频aid信息
AV_ID = 71816014 # https://www.bilibili.com/video/av71816014?from=search&seid=1263844934261848070 
# 弹幕开始日期
DANMU_START_TIME = '2019-10-20'
# 弹幕结束日期
DANMU_END_TIME = '2020-01-30'
# 弹幕下载的原始文件存储位置及命名
DANMU_SOC_INFO = '/home/ubuntu/danmu_soc.csv'
# 弹幕本地处理后文件存储位置及命名
DANMU_FORMAT_INFO = '/home/ubuntu/danmu_include_name.csv'


def cookie_str2dict(str_):
    '''
    字符串形式的Cookie数据转为字典格式
    '''
    if str_:

        cookie_dict = {}

        for i in str_.split('; '):
            k, v = i.split('=')
            cookie_dict[k] = v

        return cookie_dict

    return None


def get_days(n):
    '''
    获取当前日期到之前n天的日期集合
    '''
    before_n_days = []
    for i in range(0, n)[::-1]:
        before_n_days.append(str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days
# days = get_days(10)


def date_range(beginDate, endDate):
    '''
    给定日期间隔，获取之间的日期集合
    '''
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates
# search_time=date_range("2019-10-20", "2020-01-25")


def aid2cid(aid):
    '''
    根据av号获取cid
    '''
    cid = []

    try:

        url = "https://api.bilibili.com/x/player/pagelist?aid={}&jsonp=jsonp".format(aid)

        d = requests.get(url)

        if d.status_code != 200:
            raise ValueError('aid转cid请求异常')

        info_ = json.loads(d.text)

        # {'code': 0,
        #  'data': [{'cid': 124600873,
        #    'dimension': {'height': 1080, 'rotate': 0, 'width': 1920},
        #    'duration': 96,
        #    'from': 'vupload',
        #    'page': 1,
        #    'part': 'shake it',
        #    'vid': '',
        #    'weblink': ''},
        #   {'cid': 124606776,
        #    'dimension': {'height': 1920, 'rotate': 0, 'width': 1080},
        #    'duration': 96,
        #    'from': 'vupload',
        #    'page': 2,
        #    'part': '竖屏离你更近',
        #    'vid': '',
        #    'weblink': ''}],
        #  'message': '0',
        #  'ttl': 1}

        if info_['code'] != 0:

            raise ValueError('aid转cid失败 %s' % info_['message'])

        video_data = info_['data']

        # 一个aid可能对于多个cid 这里取这个尺寸的 {'height': 1080, 'rotate': 0, 'width': 1920}
        cid.append(video_data[0]['cid'])

        cid = list(map(lambda x: x.get('cid'), video_data))

    except Exception as e:
        print('aid2cid error: %s' % e.message)

    print('aid2cid ok cid: %s' % cid)
    return cid


def danmu_url(cid, time_=None):
    '''
    弹幕url组装
    '''

    url = []

    if cid and isinstance(time_, list):

        url = list(map(lambda x : "https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date={}".format(cid, x), time_))

    return url


def request_danmu(url=None, url_list=None):
    
    if url:
        request_url(url=url, headers=headers, cookies=cookies)

    if url_list:
        for i in url_list:
            time.sleep(2)
            if not request_url(url=i, headers=headers, cookies=cookies):
                continue


def request_url(url, headers=None, cookies=None):

    state = True

    try:

        r = requests.get(url, headers=headers, cookies=cookies)

        if r.status_code != 200:

            raise ValueError('URL请求失败 %s' % r.status_code)

        if '"code":' in r.text:  # {"code":-101,"message":"账号未登录","ttl":1}
            r = json.loads(r.text)
            raise ValueError('返回状态异常 %s' % r['message'])
        
        r.encoding = 'utf-8' # r_data = str(r.content, 'utf-8')

        danmu_ = format_danmu(r.content)

        if danmu_:
            save_danmu(danmu_)
            print('url %s 处理成功' % url)

    except Exception as e:
        print('error: %s'%e)
        state = False

    return state


# 弹幕格式处理
def format_danmu(value):
    soup = BeautifulSoup(value, 'html.parser')
    result = soup.select('d')
    if len(result) == 0:
        return result
    all_list = []
    for item in result:
        info = item.get('p').split(",")
        info.append(item.string)
        info[4] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(info[4])))
        all_list.append(info)
    return all_list


# 弹幕数据存贮
def save_danmu(value, dress_=DANMU_SOC_INFO):

    data = pd.DataFrame(value)  

    data.to_csv(dress_, mode='a', header=False)


# 数据清洗
def clean_danmu(dress_):
    
    data = pd.read_csv(dress_, names=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']) # https://zhuanlan.zhihu.com/p/44503744

    _danmu_ = data['J']

    key_ = ['注意身体', '主意身体', '别看了', '放下']

    name_dict = {}

    for i in _danmu_:

        for k in key_:

            if not k in i:
                continue

            if i.startswith(k) or i.startswith('都')  or i.startswith('手中的') or i.startswith('各位'):
                continue

            name = i.split(k)[0]

            name = name.replace('你', '').replace(' ', '').replace('，', '')

            if name in name_dict:
                name_dict[name] += 1
            else:
                name_dict[name] = 0

    # 字典排序
    name_dict = sorted(name_dict.items(), key = lambda x: x[1], reverse=True)

    print(name_dict)

    save_danmu(name_dict, dress_=DANMU_FORMAT_INFO)


def main():

    cid_list = aid2cid(AV_ID)

    # 获取日期集合 弹幕的url中必须传的参数
    date_list= date_range(DANMU_START_TIME, DANMU_END_TIME)
    # date_list= date_range('2019-10-20', '2019-10-21')

    url_set = []

    for cid in cid_list:
        # 处理URL
        url_set.extend(danmu_url(cid, date_list))

    # 获取弹幕
    request_danmu(url_list=url_set)

    # 弹幕文件处理
    clean_danmu(DANMU_SOC_INFO)


if __name__ == '__main__':
    main()



