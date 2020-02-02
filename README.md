# BiliDanmuGet
获取哔哩哔哩(bilibili)的视频弹幕


### 执行环境
python3


### 执行准备
根据需要设置av号等信息... 修改bilibili.py文件中的
1. cookies信息
	- coodies = {'必须':'必须'}
2. 视频aid信息
	- AV_ID = 71816014 # https://www.bilibili.com/video/av71816014?from=search&seid=1263844934261848070 
3. 弹幕开始日期
	- DANMU_START_TIME = '2019-10-20'
4. 弹幕结束日期
	- DANMU_END_TIME = '2020-01-30'
5. 弹幕下载的原始文件存储位置及命名
	- DANMU_SOC_INFO = '/home/ubuntu/danmu_soc.csv'
6. 弹幕本地处理后文件存储位置及命名 弹幕处理根据需求拓展代码
	- DANMU_FORMAT_INFO = '/home/ubuntu/danmu_include_name.csv'


### 执行命令
python3 bilibili.py


### 附件
1. danmu_soc.csv 视频 av71816014 [shake it ！冬日也要活力满满] 原始弹幕

2. danmu_include_name.csv 原始弹幕处理后提取姓名的信息