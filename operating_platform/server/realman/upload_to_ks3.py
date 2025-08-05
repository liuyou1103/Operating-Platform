from robot_data_uploader.collect_uploader import BaaiRobotDataUploader
from upload_to_nas import(
    get_today_date,
    get_yesterday_date,
    get_day_before_yesterday_date
)
import os
import json
import subprocess
from pathlib import Path
import requests
from collections import OrderedDict
 
fold_path = "/home/agilex/Documents/Ryu-Yang/Operating-Platform/dataset/"
fold_path = "/home/liuyou/Documents/test"
server_url="http://localhost:8080"
session = requests.Session()

def local_server_request(api_url,data):
    response = session.post(
        f"{server_url}/{api_url}",
        json=data
    )
    
def local_server_task_id_request(task_id):
    data = {
        "machine_id":str(task_id)
    }
    response = session.post(
        f"{server_url}/api/upload_task_id",
        json=data
    )
    
def read_common_record_json(each_task_path):
    each_common_record_path = os.path.join(each_task_path,'meta','common_record.json')
    with open(each_common_record_path,"r",encoding="utf-8") as f:
        data = json.load(f)
        task_id = data["task_id"] # 云平台任务id
        machine_id = data["machine_id"]
        task_name = data["task_name"]
    return task_id,task_name,machine_id

def read_info_json(each_task_path):
    each_info_path = os.path.join(each_task_path,'meta','info.json')
    with open(each_info_path,"r",encoding="utf-8") as f:
        data = json.load(f)
        fps = data["fps"] # fps      
    return fps

def get_img_video_path(each_task_path,camera_images,camera_images_path):
    img_path_list = []
    video_path_list = []
    entries = os.listdir(camera_images_path) # 各任务列表
    print(entries)
    # 筛选出子目录
    for episode_index in entries:
        img_path = os.path.join(camera_images_path, episode_index)
        video_name = episode_index + '.mp4'
        video_path = os.path.join(each_task_path,'videos',camera_images,video_name)
        img_path_list.append(img_path)
        video_path_list.append(video_path)
    if len(img_path_list) == len(video_path_list):
        return img_path_list, video_path_list
    else:
        print("path error")
        return [],[]
                    


def encode_video_frames(
    imgs_dir: Path | str,
    video_path: Path | str,
    fps: int,
    vcodec: str = "libx264",
    pix_fmt: str = "yuv420p",
    g: int | None = 2,
    crf: int | None = 18,
    fast_decode: int = 0,
    log_level: str | None = "error",
    overwrite: bool = False,
) -> None:
    try:
        """More info on ffmpeg arguments tuning on `benchmark/video/README.md`"""
        video_path = Path(video_path)
        imgs_dir = Path(imgs_dir)
        video_path.parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_args = OrderedDict(
            [
                ("-f", "image2"),
                ("-r", str(fps)),
                ("-i", str(imgs_dir / "frame_%06d.png")),
                ("-vcodec", vcodec),
                ("-pix_fmt", pix_fmt),
            ]
        )

        if g is not None:
            ffmpeg_args["-g"] = str(g)

        if crf is not None:
            ffmpeg_args["-crf"] = str(crf)

        if fast_decode:
            key = "-svtav1-params" if vcodec == "libsvtav1" else "-tune"
            value = f"fast-decode={fast_decode}" if vcodec == "libsvtav1" else "fastdecode"
            ffmpeg_args[key] = value

        if log_level is not None:
            ffmpeg_args["-loglevel"] = str(log_level)

        ffmpeg_args = [item for pair in ffmpeg_args.items() for item in pair]
        if overwrite:
            ffmpeg_args.append("-y")

        ffmpeg_cmd = ["ffmpeg"] + ffmpeg_args + [str(video_path)]
        # redirect stdin to subprocess.DEVNULL to prevent reading random keyboard inputs from terminal
        subprocess.run(ffmpeg_cmd, check=True, stdin=subprocess.DEVNULL)

        if not video_path.exists():
            raise OSError(
                f"Video encoding did not work. File not found: {video_path}. "
                f"Try running the command manually to debug: `{''.join(ffmpeg_cmd)}`"
            )
        return True
    except Exception as e:
        print(str(e))
        return False
    
def encode_depth_video_frames(
    imgs_dir: Path | str,
    video_path: Path | str,
    fps: int,
    vcodec: str = "ffv1",  # 使用无损编码
    pix_fmt: str = "gray16le",  # 单通道灰度
    overwrite: bool = False,
) -> None:
    try:
        """Encode depth images to video."""
        video_path = Path(video_path)
        imgs_dir = Path(imgs_dir)
        video_path.parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_args = [
            "ffmpeg",
            "-f", "image2",
            "-r", str(fps),
            "-i", str(imgs_dir / "frame_%06d.png"),
            "-vcodec", vcodec,
            "-pix_fmt", pix_fmt,
        ]
        
        if overwrite:
            ffmpeg_args.append("-y")
        
        ffmpeg_args.append(str(video_path))
        
        subprocess.run(ffmpeg_args, check=True, stdin=subprocess.DEVNULL)

        if not video_path.exists():
            raise OSError(f"Video encoding failed. File not found: {video_path}")
        return True
    except Exception as e:
        print(str(e))
        return False

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
                camera_save_folder = 'images'
                if camera_save_folder in subdirectories_1:
                    task_id,task_name,machine_id = read_common_record_json(each_task_path)
                    fps = read_info_json(each_task_path)
                    local_server_task_id_request(task_id)
                    
                    each_images_path = os.path.join(each_task_path,camera_save_folder)
                    entries_2 = os.listdir(each_images_path)
                    for camera_images in entries_2:
                        camera_images_path = os.path.join(each_images_path, camera_images)
                        if os.path.isdir(camera_images_path):
                            # 如果是目录，执行某些操作
                            print(f"{camera_images_path} 是一个目录")
                            img_list,video_list = get_img_video_path(each_task_path,camera_images,camera_images_path)
                            if 'depth' in camera_images:
                                if img_list:
                                    for i in range(len(img_list)) :
                                        if not encode_depth_video_frames(img_list[i],video_list[i],fps):
                                            ffmpeg_encode_flag = False
                            else:
                                if img_list:
                                    for i in range(len(img_list)) :
                                        print(img_list[i],video_list[i],fps)
                                        if not encode_video_frames(img_list[i],video_list[i],fps):
                                            ffmpeg_encode_flag = False                                   
                if ffmpeg_encode_flag:
                    pass
                    #upload(each_task_path)
        except Exception as e:
            print(str(e))
encode_and_upload()
                            