#!/usr/bin/env python
#-*- coding:utf-8 -*-
# web crawler for artstation
# author : wangzhen <wangzhenjjcn@gmail.com> since 2019-03-15

import http.client

conn = http.client.HTTPSConnection("www.artstation.com")

headers = {
    'accept': "application/json, text/plain, */*",
    'dnt': "1",
    'x-csrf-token': "UTihJ+nY4G45ze6lRmW9BEV//wv3oXotk3N1FAzjfFMyi3CaMxP/NTVvT/Zs3imZjxPZZvVE0m2AX8ZqIWBBNA==",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    }

conn.request("GET", "/users/ijm86/projects.json?page=1", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))