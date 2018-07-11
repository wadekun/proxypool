# /usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: config
# @Date: 2018-07-08 12:04

__author__ = 'Chuankun Liang'

proxies_config = [
    {
        'name': '快代理',
        'url': 'https://www.kuaidaili.com/free/intr/%d/',
        'page_count': 2390,
        'ip_xpath': '//*[@id="list"]/table/tbody/tr/td[1]/text()',
        'ip_image': False,
        'port_xpath': '//*[@id="list"]/table/tbody/tr/td[2]/text()',
        'port_image': False,
        'proxy_types': ['http', ]
    },
    {
        'name': '西刺代理',
        'url': 'http://www.xicidaili.com/wt/%d',
        'page_count': 1844,
        'ip_xpath': '//*[@id="ip_list"]/tr/td[2]/text()',
        'ip_image': False,
        'port_xpath': '//*[@id="ip_list"]/tr/td[3]/text()',
        'port_image': False,
        'proxy_types': ['http']
    },
    {
        'name': '米扑代理-开放代理',
        'url': 'https://proxy.mimvp.com/free.php?proxy=in_hp&sort=&page=%d',
        'page_count': 1,
        'ip_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-ip"]/text()',
        'ip_image': False,
        'port_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-port"]/img/@src',
        'port_image': True,
        'is_image_url_relative': True,
        'proxy_types': ['http', 'https']
    },
    {
        'name': '米扑代理-私密代理',
        'url': 'https://proxy.mimvp.com/freesecret.php?proxy=in_hp&sort=&page=%d',
        'page_count': 1,
        'ip_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-ip"]/text()',
        'ip_image': False,
        'port_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-port"]/img/@src',
        'port_image': True,
        'is_image_url_relative': True,
        'proxy_types': ['http', 'https']
    },
    {
        'name': '米扑代理-独享代理',
        'url': 'https://proxy.mimvp.com/freesole.php?proxy=in_hp&sort=&page=%d',
        'page_count': 1,
        'ip_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-ip"]/text()',
        'ip_image': False,
        'port_xpath': '//*[@id="mimvp-body"]/div[2]/div/table/tbody/td[@class="tbl-proxy-port"]/img/@src',
        'port_image': True,
        'is_image_url_relative': True,
        'proxy_types': ['http', 'https']
    },
]


# redis配置
# REDIS_STORE_ENABLE = True
REDIS_KEY_PREFIX = 'proxypool'
REDIS_HOST = 'redis'
REDIS_PORT = 6379

# 线程池配置
FETCH_THREAD_NUMBER = 3

