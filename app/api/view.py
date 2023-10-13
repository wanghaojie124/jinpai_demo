import os.path

from flask import request
from pre_request import pre, Rule
from pre_request.exception import ParamsValueError

from app.api import api
from config import furnishings_output
from controller.furnishings import furnishings
from utils import create_response, image2base64, list_full_path


@api.route(
    "/furnishings/submitImage",
    methods=["POST"]
)
def furnishings_task():
    rule = {
        "image": Rule(type=str, required=True),
        "prompt": Rule(type=str, required=True),
        "task_id": Rule(type=str, required=True),
    }
    try:
        params = pre.parse(rule=rule)
    except ParamsValueError as e:
        return create_response({}, 400, f"参数校验错误: {e.message}")

    task_id = params.get("task_id")
    furnishings.task_queue.put(params)

    return create_response({"task_id": task_id}, message="成功创建任务")


@api.route(
    "/furnishings/progress",
    methods=["GET"]
)
def furnishings_get_progress():
    task_id = request.args.get("task_id")
    if not task_id:
        return create_response({}, message=f"参数错误")
    dir_exist = os.path.exists(os.path.join(furnishings_output, task_id))
    current_task_id = furnishings.task_id
    task_dir = os.path.join(furnishings_output, task_id)

    if dir_exist:
        if list_full_path(task_dir) and (
                # 历史任务
                task_id != current_task_id or
                (       # 当前任务进行中时，防止图片未完全写入到文件，而进行文件读取导致图片内容缺失
                        task_id == current_task_id and furnishings.steps != 1
                )
        ):
            data = {
                "final_output": [],
                "step": -1,
                "step_name": "已完成"
            }
            try:
                output_dir = list_full_path(task_dir)
            except FileNotFoundError:
                return create_response({}, message=f"未查询到该task_id: {task_id}")
            for image in output_dir:
                filename = os.path.basename(image).split(".")[0]
                # image_url, _ = cos.upload_image(image, oss_server_path, f"{filename}.png")
                image_url = image2base64(image)
                data['final_output'].append(
                    {
                        "id": filename,
                        "image": image_url
                    }
                )
            return create_response(data)
        else:
            progress = furnishings.get_progress()
            return create_response(
                {
                    'progress': progress
                },
                message=f"当前任务进度：{progress * 100}%"
            )
    elif not dir_exist:
        if task_id == current_task_id:
            progress = furnishings.get_progress()
            return create_response(
                {
                    'progress': progress
                },
                message=f"当前任务进度：{progress * 100}%"
            )
        else:
            return create_response(
                {
                    'progress': 0
                },
                message=f"当前任务排队中"
            )


