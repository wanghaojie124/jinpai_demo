import json
import os
import time
from io import BytesIO
import base64
from queue import Queue

import requests
from PIL import Image

from config import furnishings_sd_api, furnishings_output, furnishings_max_px
from utils import my_makedirs, base64_to_image, cut_image


class Furnishings:

    def __init__(self):
        self.sn = None
        self.task_id = None
        self.task_queue = Queue()
        self.steps = 0

    def submit_task(self, params: dict):
        self.steps = 1
        self.task_id = params.get('task_id')
        url = furnishings_sd_api + "img2img"
        prompt = params.get("prompt")
        image_base64 = params.get('image')
        if "base64," not in image_base64:
            init_image_base64 = f"data:image/jpeg;base64,{params.get('image')}"
        else:
            init_image_base64 = image_base64

        image_b = BytesIO(base64.b64decode(init_image_base64.split(",")[-1]))
        _image = Image.open(image_b)

        width, height = cut_image(_image, furnishings_max_px)

        data = {
            "init_images": [init_image_base64],
            "steps": 20,
            "resize_mode": 0,
            "inpainting_fill": 1,
            "prompt": f"{prompt}, <lora:rishiv2_6000:0.7>, pt-houserishiv2-6000, no human,<lora:打光epiNoiseoffset_v2:1>",
            "negative_prompt": "EasyNegative, paintings, sketches, (worst quality:2), (low quality:2),"
                               " (normal quality:2), lowres, normal quality, ((monochrome)), "
                               "((grayscale)),Portrait,human,animal",
            "denoising_strength": 0.8,
            "cfg_scale": 6,
            "sampler_name": "DPM++ 2S a Karras",
            "override_settings": {
                "show_progress_every_n_steps": 5,
                "sd_model_checkpoint": "house_v2.safetensors [ebf8c003de]",
                "sd_vae": "Automatic"
            },
            "override_settings_restore_afterwards": False,
            "width": width,
            "height": height,
            "batch_size": 1,
            "alwayson_scripts": {
                "controlnet": {
                    "args": [
                        {
                            "weight": 0.9,
                            "input_image": init_image_base64,
                            "module": "seg_ofade20k",
                            "model": "control_v11p_sd15_seg [e1f51eb9]",
                            "resize_mode": "Crop and Resize",
                            "processor_res": 1502,
                            "threshold_a": 64,
                            "threshold_b": 64,
                            "guidance_start": 0,
                            "guidance_end": 1,
                            "control_mode": "Balanced",
                        }
                    ]
                }
            }
        }
        for i in range(1):
            response = requests.post(url, json=data).json()
            try:
                image = response.get("images")[0]
            except Exception as e:
                print(f"sd response: {response}")
                return

            save_path = my_makedirs(furnishings_output, self.task_id)
            filename = f"{self.task_id}_{i}.png"
            base64_to_image(image, os.path.join(save_path, filename))
            # 去除文件sd参数信息
            image_full_path = os.path.join(save_path, filename)
            image = Image.open(image_full_path)

            # next 3 lines strip exif
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)

            image_without_exif.save(image_full_path)
        self.steps = 0

    @staticmethod
    def get_progress():
        url = furnishings_sd_api + "progress"
        response = requests.get(url).json()
        progress = response.get('progress')
        return progress

    def run(self):
        while 1:
            params = self.task_queue.get()
            self.submit_task(params)
            time.sleep(1)


furnishings = Furnishings()
