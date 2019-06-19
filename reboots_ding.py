#!/bin/env python
# -*- coding:utf8 -*-

import socket
import urllib2
import urllib
import re
import json
import threading
import Queue
import time
import logging
import ConfigParser
import os

back_content = 'HTTP/1.x 200 ok\r\nContent-Type: text/html\r\n\r\n ok'


config = ConfigParser.ConfigParser()
config.read('./config.ini')

if config.has_section('log') and config.has_option('log','path'):
        path = config.get('log','path')
        if not os.path.exists(path):
                os.mkdir(path)
else:
        path = './'

log_first_name = time.strftime('%Y-%m-%d',time.localtime(time.time()))
log_name = path + '/' + log_first_name + '.log'
logger = logging.getLogger('ding')
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler(log_name)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


ding_queue = Queue.Queue()
msg_queue = Queue.Queue()


def dingding(tokenid, message):
	ding_url = "https://oapi.dingtalk.com/robot/send?access_token=" + tokenid
	subject = ''
	content = ''
	if message["status"] != "OK":
		subject = '告警'
		content = '告警主机: %s\n告警等级: %s\n告警信息: %s\n告警时间: %s\n' % (
			message['host'], message["level"], message["info"], message["time"])
	else:
		subject = "恢复"
		content = '恢复主机: %s\n恢复等级: %s\n恢复信息: %s\n恢复时间: %s\n' % (
			message['host'], message["level"], message["info"], message["time"])
 	header = {
            "Content-Type": "application/json",
            "charset": "utf-8"
 	}
 	data = {
            "msgtype": "text",
            "text": {
                "content": subject + "\n" + content
            },
            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": "false"
            }
 	}
        try:
 	    sendData = json.dumps(data)
 	    request = urllib2.Request(ding_url, data=sendData, headers=header)
 	    urlopen = urllib2.urlopen(request)
            return urlopen.read()
        except Exception,e:
            logger.error(e)

def set_message(msg):
	people = ''
	content = ''
	try:
	    body = msg.split('\r\n\r\n', 1)[1]
	    body = urllib.unquote(body)
            logger.info("获取消息成功: %s" % body)
	    for i in body.split('&', 1):
	    	if re.match('tos', i):
	    		people = i
		else:
		        content = i
            content = content.replace('+', ' ')
	    searchObj = re.search(
	    	r'\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]', content.split('=', 1)[1], re.M | re.I)
	    message = {'level': searchObj.group(1), 'status': searchObj.group(2), 'host': searchObj.group(
	    	3), 'tag': searchObj.group(4), 'info': searchObj.group(5), 'time': searchObj.group(6)}
            return message
        except Exception,e:
                logger.error(e)

def thread_msg(thread_id):
 	while True:
 		if not msg_queue.empty():
 			msg = msg_queue.get()
 			m = set_message(msg)
                        logger.info('解析消息成功: %s' %m)
 			ding_queue.put(m)
 		else :
                        logger.debug('msg_queue is empty ,wait ....')
 			time.sleep(10)

def thread_ding(arg):
 	to_id = arg
 	while True:
 		if not ding_queue.empty():
 			msg = ding_queue.get()
                        logger.info('开始发送消息: %s' %msg)
                        if msg:
 			    d_res = dingding(to_id, msg)
 			    logger.info('钉钉发送成功： %s' %d_res)
                        else:
                            logger.warning("获取消息失败 %s" % msg)
                            continue 
 		else:
                        logger.debug('ding_queue is empty,wait ....')
 			time.sleep(10)

def init(host=None,port=None):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	if host == None:
		host = socket.gethostname()
	if port == None:
		port = 10086
	s.bind((host,port))
	s.listen(5)
	return s

def get_msg(conn):
	msg = ''
	try:
	   data = conn.recv(2048)
	   msg += data
	   msg_queue.put(msg)
	   conn.sendall(back_content)
	   conn.close()
	except Exception,e:
	   logger.error(e)

if __name__ == '__main__':
    #tokenid='651799ff4d098ae5ae60d85ea9fc5e345604a26038aba75470ba6593012d1ffa'
    if config.has_section('default') and config.has_option('default','host'):
        host = config.get('default','host')
    else:
        host = None
    if config.has_section('default') and config.has_option('default','port'):
        port = config.getint('default','port')
    else:
        port = None
    if config.has_section('default') and config.has_option('default','tokenid'):
        tokenid = config.get('default','tokenid')
    else:
        logger.error('tokenid is empty')
    logger.info('start...')
    for x in range(0,5):
    	t = threading.Thread(target=thread_msg,args=(x,))
    	t.start()
    ok=init(host,port)
    logger.info('初始化成功：%s' %ok)
    t = threading.Thread(target=thread_ding,args=(tokenid,))
    t.start()
    while True:
        conn,addr = ok.accept()
        t = threading.Thread(target=get_msg,args=(conn,))
        t.start()


