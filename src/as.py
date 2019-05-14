#!/usr/bin/env python
#-*- coding:utf-8 -*-


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
    'accept-encoding': "gzip, deflate",
    'x-requested-with': "XMLHttpRequest",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache",
    'accept': "application/json, text/javascript, */*; q=0.01",}

#global data_resault,data_download,data_playing



class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('')
        self.master.geometry('')
        self.master.resizable(0,0)


    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        
        


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
