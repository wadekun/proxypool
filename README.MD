# Introduction
ProxyPool by python. Store in redis, use LIFO Queue.
（yingwenbuhao, couhe kanba ）

# Install Dependencies
you need install one of :  

* Libtesseract (Python bindings for the C API)
* Tesseract (wrapper: fork + exec)
* Cuneiform (wrapper: fork + exec)

for recognition of the digit in the ip or port image.
# run

## docker
```shell
> docker-compose build
> docker-compose up 
```

## virtualenv
```shell
> cd proxypool
> virtualenv --no-site-packages venv
> source venv/bin/activate
> pip install -r requirements.txt
> python proxypool.py 
```

# Configuration
you can add proxy config in 

`config.py` 
```json
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
```

```
name: proxy name
url：page url template
page_count: available proxy pages count
ip_xpath: ip text extract path by xpath
'ip_image': is ip node image ?
'port_xpath': port text extract path by xpath
'port_image': is port node image?
'is_image_url_relative': is iamge url relative?
'proxy_types': proxy types  
```