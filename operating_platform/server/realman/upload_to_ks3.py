from robot_data_uploader.collect_uploader import BaaiRobotDataUploader
from upload_to_nas import(
    get_today_date,
    get_yesterday_date,
    get_day_before_yesterday_date
)
import os
import json
 
fold_path = "/home/agilex/Documents/Ryu-Yang/Operating-Platform/dataset/"

def ffmpeg_encode():
    pass
    

def encode_and_upload():
    ffmpeg_encode_flag = True
    for i in range(3):
        if i == 0:
            date_data = get_today_date()
        elif i == 1:
            date_data = get_yesterday_date()
        elif i == 2:
            date_data = get_day_before_yesterday_date()
        print(date_data)
        directory_path = os.path.join(fold_path, date_data,'user')
        if not os.path.exists(directory_path):
            print("数据路径不存在")
            continue
        entries = os.listdir(directory_path) # 各任务列表
        # 筛选出子目录
        subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))] # 仅筛选目录
        try:
            for task_data_name in subdirectories: 
                each_task_path = os.path.join(directory_path,task_data_name)
                entries_1 = os.listdir(each_task_path) 
                subdirectories_1 = [entry for entry in entries_1 if os.path.isdir(os.path.join(each_task_path, entry))] # data images videos meta
                for task_part in subdirectories_1:
                    if task_part == "images":
                        each_images_path = os.path.join(each_task_path,task_data_name)
                        entries_2 = os.listdir(each_images_path)
                        subdirectories_2 = [entry for entry in entries_2 if os.path.isdir(os.path.join(each_images_path, entry))] # images.top/left/right
                        for camera_images in subdirectories_2:
                            if not ffmpeg_encode(camera_images):
                                ffmpeg_encode_flag = False
                if ffmpeg_encode_flag:
                    each_common_record_path = os.path.join(each_task_path,'meta','common_record.json')
                    with open(each_common_record_path,"r",encoding="utf-8") as f:
                        data = json.load(f)
                        task_id = data["task_id"] # 云平台任务id
                        machine_id = data["machine_id"]
                        task_name = data["task_name"]
                    upload(each_task_path)
        except Exception as e:
            print(str(e))
                            