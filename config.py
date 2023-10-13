from enum import Enum


class Config(object):

    # 每次请求结束后，自动提交数据库中的变动，该字段在flask-sqlalchemy 2.0之后已经被删除了（有bug）
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # 2.0之后新加字段，flask-sqlalchemy 将会追踪对象的修改并且发送信号。
    # 这需要额外的内存，如果不必要的可以禁用它。
    # 注意，如果不手动赋值，可能在服务器控制台出现警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 数据库操作时是否显示原始SQL语句，一般都是打开的，因为后台要日志
    SQLALCHEMY_ECHO = True


class DevelopmentConfig(Config):
    """
    配置文件中的所有的账号密码等敏感信息，应该避免出现在代码中，可以采用从环境变量中引用的方式，比如：
    username = os.environ.get('MYSQL_USER_NAME')
    password = os.environ.get('MYSQL_USER_PASSWORD')
    本文为了便于理解，将用户信息直接写入了代码里
    """
    DEBUG = True
    # 数据库URI
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:xxx@xxxx/xxx'


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}

# OSS配置
oss_config = {
    "secret_id": "AKIDyukP261lQoATebEgvENNjxztkWfgXHvR",
    "secret_key": "SiuwrlW5TksucIqFXdR3a61tkTCXklbE",
    "bucket": "innoverse-img-1311503813",
    "domain": "http://img1.comixai.online/",
    "public_domain": "https://innoverse-img-1311503813.cos.ap-beijing.myqcloud.com/"
}
oss_mj_path = "server/to_mj"  # 用于放置mj图生图需要的图片
oss_server_path = "server/result"  # 用于储存处最终生成的图片

# midjourney配置及出图文件夹配置
furnishings_output = "imgs/furnishings"
furnishings_max_px = 1920  # 家居场景生图的最大边长尺寸


# 自动化进程阶段
class Steps(Enum):
    DIS = 1  # dis分割
    MJ_IMG2IMG = 2  # 使用mj进行图生图
    MIX_PIPE = 3  # 擦除mj生图的主体，置入原有主体，并进行混合
    SD_MIX = 4  # 放入sd进行主体与背景混合
    DETAIL_TEXT = 5  # 文字细节修复
    ON_START = 0  # 任务未开始
    FINISH = -1  # 任务完成
    FAIL = -2  # 任务失败


step_name_dict = {
    1: "阶段1",
    2: "阶段2",
    3: "阶段3",
    4: "阶段4",
    5: "阶段5",
    0: "任务未开始",
    -1: "任务完成",
    -2: "任务失败"
}
# sd api配置
sd_api = "http://region-31.seetacloud.com:56849/sdapi/v1/"
# 家装sd api配置
furnishings_sd_api = "http://region-31.seetacloud.com:49428/sdapi/v1/"

# autodl代理配置
proxies = {
    "http": "http://localhost:7890",
    "https": "http://localhost:7890",
}


