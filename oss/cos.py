# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from config import oss_config
from utils import create_sn

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = oss_config.get("secret_id")
secret_key = oss_config.get("secret_key")
region = 'ap-beijing'
# COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None
scheme = 'https'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)


class Cos:

    def __init__(self):
        self.client = CosS3Client(config)

    def upload_image(self, image_path, save_path=None, filename=None):
        """
        向oss存储图片
        :param image_path: 本地图片路径
        :param save_path: oss上存储的路径
        :param filename: oss上存储的文件名
        :return url: 给前端防止跨域返回文件的访问路由
                public_url: 真实公网路由
        """
        if not filename:
            filename = create_sn()
        key = f'{save_path}/{filename}'
        response = self.client.upload_file(
            Bucket=oss_config["bucket"],
            Key=key,
            LocalFilePath=image_path,
            EnableMD5=False,
            progress_callback=None
        )
        url = oss_config['domain'] + key
        public_url = oss_config['public_domain'] + key
        return url, public_url


cos = Cos()


if __name__ == '__main__':
    cos.upload_image("../imgs/1280X1280.PNG", save_path="server")
