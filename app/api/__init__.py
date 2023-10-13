from flask import Blueprint

api = Blueprint('api', __name__)

# 末尾导入，避免循环导入依赖
from app.api import view
