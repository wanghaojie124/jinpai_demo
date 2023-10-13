from threading import Thread

from flask import Flask
from config import config
from controller.furnishings import furnishings


def create_app(config_name="development"):
    # 初始化
    app = Flask(__name__)

    # 导致指定的配置对象:创建app时，传入环境的名称
    app.config.from_object(config[config_name])

    # 注册所有蓝图
    register_blueprints(app)

    # 开启家居模块任务监听队列
    t = Thread(target=furnishings.run)
    t.start()
    return app


def register_blueprints(app):
    # 导入蓝图对象
    from app.api import api

    # 注册api蓝图,url_prefix为所有路由默认加上的前缀
    app.register_blueprint(api, url_prefix='/api/v1')
