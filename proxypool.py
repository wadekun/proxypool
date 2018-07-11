# -*- coding: utf-8 -*-

__author__ = 'Chuankun Liang'

"""
proxies pool
"""
import urllib2
from urlparse import urljoin, urlparse, parse_qs
import hashlib
import copy
import re
import time
import os
from config import proxies_config as proxies_configs, REDIS_HOST, REDIS_PORT, REDIS_KEY_PREFIX, FETCH_THREAD_NUMBER
import pickle
import redis
import logging
from lxml import etree
from PIL import Image
import pyocr
from pyocr import builders
import threadpool
logging.basicConfig()


class ProxyPool(object):
    """
    免费代理池，从配置中获取代理配置信息，并发分页抓取，并推送到redis队列（LIFO）。
    """
    def __init__(self):
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.redis_client = redis.Redis(connection_pool=pool)
        self.proxies_config_key = REDIS_KEY_PREFIX + '.proxies_configs'
        self.proxies_key = REDIS_KEY_PREFIX + '.proxies'
        self.logger = logging.getLogger('proxy_pool')
        self.logger.setLevel(logging.DEBUG)
        self.thread_pool = threadpool.ThreadPool(FETCH_THREAD_NUMBER)

    def _init_redis_config(self):
        if not self.redis_client.exists(self.proxies_config_key):  # 配置信息不存在
            for proxy in proxies_configs:
                encoded_proxy = pickle.dumps(proxy)
                self.redis_client.sadd(self.proxies_config_key, encoded_proxy)

    def _get_config_from_redis(self):
        """
        从redis获取代理配置，如果配置不存在则创建配置，上传redis
        :return:
        """
        if self.redis_client.scard(self.proxies_config_key) > 0:
            return pickle.loads(self.redis_client.spop(self.proxies_config_key))
        else:
            return None

    def _fetch(self):
        """
        抓取代理ip
        1. 从redis中获取代理配置
        2. 解析配置，抓取代理ip
        3. 验证代理ip，将验证后的代理ip放入redis队列（为了保证代理的可用性，采用LIFO队列）
        // TODO 并发爬取，每个代理列表的总页数已经配置，so，不需要判断爬取某个代理时什么时候返回。
        :return:
        """
        def download_img(img_url):
            save_path = os.path.join(os.path.dirname(__file__), 'imgs')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            img_data = urllib2.urlopen(img_url).read()
            file_name = hashlib.md5(img_url).hexdigest() + '.png'
            file_path = os.path.join(save_path, file_name)
            with open(file_path, 'wb+') as f:
                f.write(img_data)
            return file_path

        def convert_image_to_text(port_img_urls):
            port_img_paths = [download_img(img_url) for img_url in port_img_urls]
            recognizer = Recognizer()
            return [recognizer.image_to_text(img) for img in port_img_paths]

        def crawl_proxies_and_put_to_redis(proxy_url, proxy_config):
            self.logger.debug('start to crawl proxy url: %s' % proxy_url)
            opener = urllib2.build_opener()
            opener.addheaders = \
                [('User-agent',
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'),
                 ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                 ('Accept-Language', 'en')
                 ]

            urllib2.install_opener(opener)
            request = urllib2.Request(proxy_url)
            response = urllib2.urlopen(request)
            html = response.read()
            selector = etree.HTML(html)
            ips = selector.xpath(proxy_config['ip_xpath'])
            # if proxy_info['ip_image']:  # ip为图片, 下载ip图片，并转换为数字
            #     pass
            ports = selector.xpath(proxy_config['port_xpath'])
            if proxy_config['port_image']:  # 端口为图片，下载端口图片，并转换为数字
                port_img_urls = ports
                if proxy_config['is_image_url_relative']:
                    port_img_urls = [urljoin(proxy_config['url'], port_img_url) for port_img_url in ports]

                ports = convert_image_to_text(port_img_urls)

            if (not ips) or (not ports) or (len(ips) != len(ports)):
                # self.logger.debug('proxy %s fetch end.' % proxy_info['name'])
                self.logger.debug('proxy url: %s crawl finish.' % proxy_url)
                return

            ip_port_pairs = zip(ips, ports)
            for ip, port in ip_port_pairs:
                if ProxyPool.validate_proxy(ip, port):
                    self.logger.debug('put available proxy: %s' % ('http://' + ip + ':' + port))
                    self.put_proxy_to_redis('http://' + ip + ':' + port)

            self.logger.debug('proxy url: %s crawl finish.' % proxy_url)
            return ip_port_pairs

        while True:
            proxy_info = self._get_config_from_redis()
            if proxy_info is None:  # 如果获取的代理配置信息为空，则返回
                self.logger.debug('proxy config is null.')
                return
            self.logger.info('get proxy : %s' % proxy_info['name'])
            if '%d' in proxy_info['url']:  # 包含分页
                for page in range(1, proxy_info['page_count'] + 1):
                    url = proxy_info['url'] % page
                    time.sleep(1)  # 等待一秒
                    requests = threadpool.makeRequests(
                        crawl_proxies_and_put_to_redis,
                        [((url, copy.deepcopy(proxy_info), ), {})]
                    )
                    map(self.thread_pool.putRequest, requests)
                    # crawl_proxies_and_put_to_redis(url)
            else:
                crawl_proxies_and_put_to_redis(proxy_info['url'])

    def run(self):
        self._init_redis_config()
        self._fetch()
        self.thread_pool.wait()

    @staticmethod
    def validate_proxy(ip, port, proxy_type='http'):
        test_url = 'http://www.baidu.com'
        test_proxy_str = 'http://' + ip + ':' + port
        success_regex = re.compile(r'baidu.com')
        time_out = 3
        opener = urllib2.build_opener(urllib2.ProxyHandler({proxy_type: test_proxy_str}))
        # print 'use %s proxy: %s' % (proxy_type, test_proxy_str)
        urllib2.install_opener(opener)
        try:
            response = urllib2.urlopen(test_url, timeout=time_out)
        except:
            # print '%s connect failed' % test_proxy_str
            return False
        else:
            try:
                html = response.read()
                # print str
            except:
                # print '%s connect failed' % test_proxy_str
                return False
            if success_regex.search(html):
                # print '%s connect successful' % test_proxy_str
                return True
            else:
                # print '%s connect failed' % test_proxy_str
                return False

    def put_proxy_to_redis(self, proxy):
        """
        将代理ip放入redis队列(LIFO入队)
        :return:
        """
        self.redis_client.lpush(self.proxies_key, proxy)

    def get_proxy(self):
        """
        获取可用代理(LIFO出队)
        :return:
        """
        return self.redis_client.lpop(self.proxies_key)


class Recognizer(object):
    """
    图片识别器，识别端口、ip图片
    """
    def __init__(self):
        self.tools = pyocr.get_available_tools()
        self.logger = logging.getLogger('Recognizer')
        if len(self.tools) == 0:
            print("No OCR tool found")
            return
            # The tools are returned in the recommended order of usage
        self.tool = self.tools[0]
        self.logger.debug("Will use tool '%s'" % (self.tool.get_name()))
        # Ex: Will use tool 'libtesseract'

        self.langs = self.tool.get_available_languages()
        self.logger.debug("Available languages: %s" % ", ".join(self.langs))
        self.lang = self.langs[0]
        self.logger.debug("Will use lang '%s'" % self.lang)

    def image_to_text(self, image_path):
        txt = self.tool.image_to_string(
            Image.open(image_path),
            lang=self.lang,
            builder=pyocr.builders.TextBuilder()
        )
        return txt


if __name__ == '__main__':
    proxy_pool = ProxyPool()
    proxy_pool.run()
