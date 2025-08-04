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
 
fold_path = "/home/agilex/Documents/Ryu-Yang/Operating-Platform/dataset/"

def encode_video_frames(
    imgs_dir: Path | str,
    video_path: Path | str,
    fps: int,
    vcodec: Literal["libopenh264", "libx264"] = "libx264",
    pix_fmt: str = "yuv420p",
    g: int | None = 20,
    crf: int | None = 18,
    fast_decode: int = 1,
    log_level: Optional[str] = "error",
    overwrite: bool = False,
) -> None:
    """More info on ffmpeg arguments tuning on `benchmark/video/README.md`"""

    # 确保编码器列表已加载
    ensure_encoders_loaded()

    # 获取当前支持的编码器列表
    available_encoders = _AVAILABLE_ENCODERS

    # 用户指定的编码器是否可用
    if vcodec in available_encoders:
        pass  # 正常使用指定的编码器
    else:
        # 从支持的两个编码器中选择一个可用的
        supported_candidates = {"libopenh264", "libx264"} & set(available_encoders)

        if not supported_candidates:
            raise ValueError(
                "None of the supported encoders are available. "
                "Please ensure at least one of 'libopenh264' or 'libx264' is supported by your ffmpeg installation."
            )

        # 优先选择 libx264，否则选择 libopenh264
        selected_vcodec = "libx264" if "libx264" in supported_candidates else "libopenh264"

        # 发出警告
        warnings.warn(
            f"vcodec '{vcodec}' not available. Automatically switched to '{selected_vcodec}'.",
            UserWarning
        )

        vcodec = selected_vcodec

    # 剩余逻辑不变（略去，与原函数一致）
    video_path = Path(video_path)
    video_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_args = OrderedDict(
        [
            ("-f", "image2"),
            ("-r", str(fps)),
            ("-i", str(imgs_dir / "frame_%06d.jpg")),
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
def encode_depth_video_frames(
    imgs_dir: Path | str,
    video_path: Path | str,
    fps: int,
    vcodec: str = "ffv1",  # 使用无损编码
    pix_fmt: str = "gray16le",  # 单通道灰度
    overwrite: bool = False,
) -> None:
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
                            