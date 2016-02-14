# 说明

======
这是一个用来练手的由flask搭建的网站，前期大部分内容都参阅这个[flask mega tutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world),英文版需要翻墙，中文版在[这里](http://www.pythondoc.com/flask-mega-tutorial/index.html),并且原作者也把这个教程的代码放到github上了，在[这里](https://github.com/miguelgrinberg/microblog)。中文版的内容有写小地方的错误，大伙可以用我和作者github上的代码对应着纠错。

这个教程写的非常好，大家有兴趣可以试试。里面是采用openid登录，因为一些众所周知的原因，这个在天朝不太好用，所以我换掉了，后面也会陆陆续续增加一些功能。前端的话用的是bootstap的FLAT UI，完全照抄的。

[看看网站效果](http://115.28.23.216)
======
#快速建立一个你的网站

这个网站并不用于商业，只是纯粹练手而已，大家需要的话可以直接clone这个项目，几步轻松搭建网站。

#### clone项目到本地,你会得到一个名为flask_blog的文件夹。
> `$git clone https://github.com/Arnold-Hu/flask_blog.git`

#### 安装python，pip，并且安装wirtualenv作为虚拟环境（只介绍ubuntu下实现）
> 安装python：
> `$sudo apt-get install python python-dev python-pip python-virtualenv`

#### 进入flask_blog文件夹，建立虚拟环境，在虚拟环境中安装所需要的内容。
> 建立虚拟环境:
> `$virtualenv flask`(建议把环境叫这个名字，不然要改一些内容)

> 安装各种库：

> ```$source /flask/bin/activate
 $pip install -r requirements.txt
 $deactivate```

#### 增加个人配置

在根目录下新建文件夹名字为`/instance`

然后在这个文件夹中新建一个名字为`config.py`的文件，按下面的格式填上你的私密信息配置：
```
#coding:utf-8

SECRET_KEY = 'you-will-never-guess'

MAIL_SERVER = 'smtp.example.com.cn'
MAIL_PORT = 25                  #国内的邮箱代理基本上端口都是25,但是国外的比如gmail可能有所不同，具体需要上网查询
MAIL_USERNAME = 'example'       #你的邮箱帐号，不需要@以及后面的部分
MAIL_PASSWORD = 'example'       #你的邮箱密码
```

#### 建立数据库，运行程序
> 初始化数据库
> `$./db.create.py`


> 运行程序
> `$./run.py`

#### 看看效果

打开浏览器，输入localhost：5000,就ok了。

#### 开始部署

现在虽然已经可以在本地进行浏览，但是我知道能让大家欣赏才是一个网站的宿命，现在就介绍一下简单的部署。

1. 首先，你要有个服务器，推荐阿里云，学生身份还有优惠。如果你要直接用的话，可以直接clone这里的代码到服务器。

2. 然后，为了更好管理，在virtualenv环境下安装gunicorn
    ```
    $source flask/bin/activate
    (flask)$pip install gunicorn
    (flask)$ deactivate
    ```

3. 更改 run.py,把run.py文件更改如下：
    ```
    #!flask/bin/python
    #coding:utf-8
    from app import app
    from werkzeug.contrib.fixers import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app)

    if __name__ == "__main__":
        app.run()
    ```

4. 安装并配置nginx

    安装:`$apt-get install -y nginx-full`

    配置:备份并打开文件`~/etc/nginx/sites-available/default`

    把其中内内容如下配置：
    ```
    server{
        listen 80;
        server_name yourip; (比如我的就是115.28.23.216)
        access_log /home/flask_blog/logs/access.log;
        error_log /home/flask_blog/logs/error.log;(这两个日志文件要自己先创建，不然会报错)

        location / {
            proxy_pass http://127.0.0.1:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwardor;
        }
    }
    ```
    接着重启 nginx：`$sudo service nginx restart`

5. 启动应用

    回到网站目录： `cd ~/home/flask_blog`

    应用virtualenv环境： `source flask/bin/activate`

    启动: `(flask)$gunicorn -b 127.0.0.1:8080 run:app`

6. 现在就可以用浏览器访问或者用curl访问了。

#### 更新

如果要修改网站代码的话，可以先用`pkill gunicorn`杀死监听进程，然后再进行更改.

完毕后再如上启动：`(flask)$gunicorn -b 127.0.0.1:8080 run:app`

#### 其他
* 里面如果修改了数据库的模型，可以直接运行`db_migrate.py`迁移数据库。


