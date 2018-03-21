import logging

import requests
import json
import time
from bs4 import BeautifulSoup
import re

class Proxy():
    def __init__(self):
        self.MAX=5 #最大嗅探次数
        self.headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            "Referer":"https://www.lagou.com/jobs/list_Java?px=default&city=%E4%B8%8A%E6%B5%B7",
            "X-Anit-Forge-Code":"0",
            "X-Anit-Forge-Token":"None",
            "X-Requested-With":"XMLHttpRequest"
        }

    def getPage(self,url,data):
        FAILTIME=0 #访问失败次数
        try:
            result=requests.post(url,headers=self.headers,data=data)
            result.encoding = "utf-8"
            return result
        except:
            FAILTIME+=1
            if FAILTIME==self.MAX:
                print("访问错误")
                return ''


class Job:
    def __init__(self):
        self.datalist=[]

    def getJob(self,url,data):
        p=Proxy()
        result=p.getPage(url,data)
        result.encoding = "utf-8"
        result_dict=result.json()
        try:
            job_info = result_dict['content']['positionResult']['result']
            for info in job_info:
                print(info)
            return job_info
        except:
            print("发生解析错误")



if __name__ == '__main__':
    url="https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false&isSchoolJob=0"
    job = Job()
    all_page_info=[]
    for x in range(1,50):
        data = {
            "first": "false",
            "pn": x,
            "kd": "Java"
        }
        current_page_info=job.getJob(url,data)
        all_page_info.append(current_page_info)
        print("第%d页已经爬取成功"%x)

        time.sleep(10)


    # #输出json文件
    # out=json.dumps(all_page_info,ensure_ascii=False)
    # with open('info_from_lagou','w') as fp:
    #     fp.write(out)

