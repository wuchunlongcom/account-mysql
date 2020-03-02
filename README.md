### 使用mysql数据库     


### 一、 运行
``` 
1、运行：./start.sh 
2、运行并初始化数据：./start.sh -i
```

### 二、 提交
```
1、使用mysql数据库
2、env375可以删除
```




### 备注
```
一、解决django版本问题
如果报错：django2.2/mysql ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3
解决方法：https://blog.csdn.net/weixin_33127753/article/details/89100552
#安装pymysql
pip install pymysql

#__init__.py
import pymysql
pymysql.install_as_MySQLdb()

第一种：
django降到2.1.4版本就OK了

第二种（仍使用django 2.2版本）：
 ...
 
二、解决安装gevent安装报错
安装xcode
 $ xcode-select --install
 
三、env375可以删除。
```