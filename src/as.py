#!/usr/bin/env python
#-*- coding:utf-8 -*-
# web crawler for artstation
# author : wangzhen <wangzhenjjcn@gmail.com> since 2019-03-15
import json
import os
import re
import sys
import threading
import time
import pygame
import requests
import logging
import argparse
import urllib.request
import urllib.error
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from functools import partial
 
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse

import pafy
import random
import math
import js2py

try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    print(f"python2.")
    import cookielib
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    print(f"python3.")
    import http.cookiejar as cookielib
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()

#global MINIMUM_SIZE,DOWNLOAD_DIR,CURRENT_PATH,LOG_FILE,LOG_FORMAT,HEADERS,LOG_LEVEL,logger
MINIMUM_SIZE = 10
DOWNLOAD_DIR = os.path.join(os.getcwd(), " ")
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_LEVEL = logging.INFO
LOG_FILE = 'download.log' or False
LOG_FORMAT = ''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'
}

download_path = "./downloads/"
tmp_path = download_path+"/tmp/"
base_url="https://www.artstation.com/"

# https://www.artstation.com/artwork/QzaRRx
# https://www.artstation.com/contests
# https://www.artstation.com/maddam
# https://www.artstation.com/maddam/store
# https://www.artstation.com/maddam/likes
# https://www.artstation.com/search/artists?q=kk
# https://www.artstation.com/artwork/LW84w

if not os.path.exists(download_path):
    os.mkdir(download_path)
if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)
 
webSession = requests.session()
webSession.cookies = cookielib.LWPCookieJar(filename=tmp_path+"cookie.txt")

defaultHeader = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache"}

ajaxheaders = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept-encoding': "gzip, deflate, br",
    'x-requested-with': "XMLHttpRequest",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache",
    'accept': "application/json, text/plain, */*; q=0.01",}

#global data_resault,data_download,data_playing



class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('')
        self.master.geometry('')
        self.master.resizable(0,0)
        pageurl=" "
        getpagedata(pageurl)

    def createWidgets(self):
        self.top = self.winfo_toplevel()
        self.style = Style()


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        # if log_print:
        #     global print
        #     print = log_print
        max_workers = cpu_count()*4
        self.executor = futures.ThreadPoolExecutor(max_workers)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.root_path = None
        self.futures = []
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename=tmp_path+"cookie.txt")

    

    def log(self, message):
        print(message)

    def download_file(self, url, file_path, file_name):
        file_full_path = os.path.join(file_path, file_name)
        if os.path.exists(file_full_path):
            self.log('[Exist][image][{}]'.format(file_full_path))
        else:
            r = self.session.get(url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log('[Finish][image][{}]'.format(file_full_path))

    def download_video(self, id, file_path):
        file_full_path = os.path.join(file_path, "{}.{}".format(id, 'mp4'))
        if os.path.exists(file_full_path):
            self.log('[Exist][video][{}]'.format(file_full_path))
        else:
            video = pafy.new(id)
            best = video.getbest(preftype="mp4")
            r = self.session.get(best.url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.log('[Finish][video][{}]'.format(file_full_path))

    def download_project(self, hash_id):
        url = 'https://www.artstation.com/projects/{}.json'.format(hash_id)
        r = self.session.get(url)
        j = r.json()
        assets = j['assets']
        title = j['slug'].strip()
        # self.log('=========={}=========='.format(title))
        username = j['user']['username']
        for asset in assets:
            assert(self.root_path)
            user_path = os.path.join(self.root_path, username)
            os.makedirs(user_path, exist_ok=True)
            file_path = os.path.join(user_path, title)
            if not self.no_image and asset['has_image']:  # 包含图片
                url = asset['image_url']
                file_name = urlparse(url).path.split('/')[-1]
                try:
                    self.futures.append(self.executor.submit(self.download_file,
                                                                url, file_path, file_name))
                except Exception as e:
                    print(e)
            if not self.no_video and asset['has_embedded_player']:  # 包含视频
                player_embedded = asset['player_embedded']
                id = re.search(
                    r'(?<=https://www\.youtube\.com/embed/)[\w_]+', player_embedded).group()
                try:
                    self.futures.append(self.executor_video.submit(
                        self.download_video, id, file_path))
                except Exception as e:
                    print(e)

    def get_projects(self, username):
        data = []
        if username is not '':
            page = 0
            while True:
                page += 1
                url = 'https://www.artstation.com/users/{}/projects.json?page={}'.format(
                    username, page)
                r = self.session.get(url)
                if not r.ok:
                    err = "[Error] [{} {}] ".format(r.status_code, r.reason)
                    if r.status_code == 403:
                        self.log(err + "You are blocked by artstation")
                    elif r.status_code == 404:
                        self.log(err + "Username not found")
                    else:
                        self.log(err + "Unknown error")
                    break
                j = r.json()
                total_count = int(j['total_count'])
                if total_count == 0:
                    self.log("[Error] Please input right username")
                    break
                if page is 1:
                    self.log('\n==========[{}] BEGIN=========='.format(username))
                data_fragment = j['data']
                data += data_fragment
                self.log('\n==========Get page {}/{}=========='.format(page,
                                                                        total_count // 50 + 1))
                if page > total_count / 50:
                    break
        return data

    def download_by_username(self, username):
        data = self.get_projects(username)
        if len(data) is not 0:
            future_list = []
            for project in data:
                future = self.executor.submit(
                    self.download_project, project['hash_id'])
                future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(self, usernames, type):
        self.no_image = type == 'video'
        self.no_video = type == 'image'
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split('/')[-1]
            if username not in username_set:
                username_set.add(username)
                self.download_by_username(username)
        futures.wait(self.futures)
        self.log("\n========ALL DONE========")


def genUUid():
#############全########网######唯######一#######可######以######使######用#########精#####华#####在#######此#####
#   e = (new Date).getTime(),
#             window.performance && "function" == typeof window.performance.now && (e += performance.now()),
#             t = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(t) {
#                 var o;
#                 return o = (e + 16 * Math.random()) % 16 | 0,
#                 e = Math.floor(e / 16),
#                 ("x" === t ? o : 3 & o | 8).toString(16)
#             })
# performance.now()方法返回当前网页从performance.timing.navigationStart到当前时间之间的微秒数，其精度可达100万分之一秒。
# performance.now()近似等于Date.now()，但前者返回的是毫秒，后者返回的是微秒，后者的精度比前者高1000倍。
    aUUID = js2py.eval_js('function(){var e,t;return e=(new Date).getTime(),window.performance&&"function"==typeof window.performance.now&&(e+=performance.now()),t="xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(t){var o;return o=(e+16*Math.random())%16|0,e=Math.floor(e/16),("x"===t?o:3&o|8).toString(16)})};') 
    return aUUID()
#############全########网######唯######一#######可######以######使######用#########精#####华#####在#######此#####

def getpagedata(pageurl):
    print("URL:"+str(pageurl))
    # https://www.artstation.com/maddam
    # https://www.artstation.com/api/v2/cart/guest/count.json?cart_token=&visitor_uuid=xxxxxxxxxxxxxxxxxxxxxxxxxx
    # https://www.artstation.com/users/maddam/projects.json?page=1
    # webSession.cookies['visitor-uuid']=genUUid()
    # webSession.save()
    # webSession.cookies.set('visitor-uuid', genUUid(), path='/', domain='www.artstation.com')
    webSession.cookies.set_cookie(cookielib.Cookie(version=0,name='visitor-uuid',value=genUUid(),
                     domain='.artstation.com',
                    path='/',
                    port='80',port_specified=False,  
                    domain_specified=True,domain_initial_dot=False 
                     , path_specified=True,
                    secure=None, rest={},
                    expires=  None,
                    discard=False,comment=None, comment_url=None, rfc2109=False))
    # webSession.cookies.save()
    webSession.cookies.save()
    mainpage=openPage("https://www.artstation.com/",defaultHeader)
    pageone=openPage("https://www.artstation.com/maddam/projects.json?page=1",defaultHeader)
    # openPage("https://www.artstation.com/api/v2/cart/guest/count.json?cart_token=&visitor_uuid=",ajaxheaders)
    # if not pageone.ok:
    #     print("ERR CODE:"+str(pageone.status_code))
    #     return
    # j = pageone.json()
    # total_count = int(j['total_count'])
    # print("total_count:"+str(total_count))
    # print(pageone.cookies.values()) 
    # webSession.cookies.save()
    # print(pageone)



def openPage(url,webheader):
    print("Open:"+url)
    responseRes=webSession.get(url,  headers = webheader,verify=False ) 
    webSession.cookies.save()
    if not responseRes.ok:
        print("ERR CODE:"+str(responseRes.status_code))
        return 
    return responseRes
    # j = responseRes.json()
    # total_count = int(j['total_count'])
    # print("total_count:"+str(total_count))
    # print(responseRes.cookies.values()) 
    # webSession.cookies.save()
    # # responseRes.cookies.save()
    # print("")
    # print(f"statusCode = {responseRes.status_code}" +":"+url)
    # print(f"text = {responseRes.text}")
     



def word_align(_string, _length, _type='L'):
    __String=_string
    if len(_string)> _length/2 and _length>10:
        __String=_string[0:int(_length/2)-3]+"...."
    
    
    _str_len = len(str(__String))
    for _char in __String:
        if u'\u4e00' <= _char <= u'\u9fa5':
            _str_len += 1
    _space = _length-_str_len
    if _type == 'L':  
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space//2
        _right = _space-_left
    return ' '*_left + __String + ' '*_right

def is_nan(x):
    for s in x:
        if s==1 or s=="1": continue
        if s==2 or s=="2": continue
        if s==3 or s=="3": continue
        if s==4 or s=="4": continue
        if s==5 or s=="5": continue
        if s==6 or s=="6": continue
        if s==7 or s=="7": continue
        if s==8 or s=="8": continue
        if s==9 or s=="9": continue
        if s==0 or s=="0": continue
        if s=="." : continue
        return True
    return False


def downloadFile(path,filename,url):
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if not os.path.exists(path):
        os.mkdir(path)   
    if(url == None or "http" not in url):
        print("urlerr:"+str(url))
        return 3
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests':'1'}
    if  os.path.exists(path+filename):
        print("已存在：文件大小："+str(os.path.getsize(path+filename)))
        # if os.path.getsize(path+filename) < 1024000:
        #     print("小于1MB的重新下载中")
        # else:
        #     return 0    
    response = requests.get(url, headers=headers)
    try:
        with open((path+filename).encode('UTF-8').decode("UTF-8"), 'wb') as f:
            f.write(response.content)
            f.flush()
            f.close()
            return 0
    except Exception as e:
        print(e)
        pass



def closeWindow():
    try:
        print( 'killing...')
        time.sleep(1)
        sys.exit(0)
    except Exception as e:
        print(e)
        print( 'Going Die...')
        time.sleep(1)
        os._exit(0)
    finally:
        print( 'Finish Exit')



def set_logger():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if LOG_FILE:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setLevel(LOG_LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger




if __name__ == "__main__":
    top = Tk()
    top.protocol('WM_DELETE_WINDOW', closeWindow)
    Application(top).mainloop()
    try: top.destroy()
    except: pass
    