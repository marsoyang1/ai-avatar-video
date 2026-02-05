import subprocess
import os
import argparse
import glob


def get_audio_duration(audio_path):
    """获取音频文件的时长（秒）"""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        print(f"  Audio duration: {duration:.2f}s")
        return duration
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  Failed to get audio duration: {e}")
        return None


def cut_video_to_duration(video_path, output_path, duration):
    """将视频截取到指定的时长（秒）"""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-t",
        str(duration),
        "-c",
        "copy",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  Cut video to {duration:.2f}s successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Failed to cut video {video_path}: {e}")
        return False


def find_audio_file(video_name, video_dir, audio_extensions):
    """查找音频文件"""
    base_name = os.path.splitext(video_name)[0]

    # 从视频路径提取项目名称
    # video_dir 格式: out/tmp/[项目名称]/
    video_dir_parts = os.path.normpath(video_dir).split(os.sep)

    # 尝试找到项目名称
    project_name = None
    if "tmp" in video_dir_parts:
        tmp_idx = video_dir_parts.index("tmp")
        if tmp_idx + 1 < len(video_dir_parts):
            project_name = video_dir_parts[tmp_idx + 1]

    if not project_name:
        # 如果找不到，尝试用视频文件名作为项目名称
        project_name = base_name

    print(f"  Project name: {project_name}")

    # 构建音频目录路径: out/voice/[项目名称]
    audio_dir = os.path.join("out", "voice", project_name)

    # 在音频目录查找
    if os.path.exists(audio_dir):
        for ext in audio_extensions:
            audio_path = os.path.join(audio_dir, base_name + ext)
            if os.path.exists(audio_path):
                print(f"  Found audio: {audio_path}")
                return audio_path

    # 如果都没找到，打印调试信息
    print(f"  No audio found for {video_name}")
    print(f"  Audio dir: {audio_dir}")
    if os.path.exists(audio_dir):
        audio_files = os.listdir(audio_dir)
        print(f"  Audio files in directory: {audio_files[:10]}")  # 只显示前10个
    else:
        print(f"  Audio directory does not exist: {audio_dir}")

    return None


def merge_videos(input_dir, output_file):
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        return

    video_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".mp4")])
    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    print(f"Found {len(video_files)} video files")

    # 支持的音频格式
    audio_extensions = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]

    temp_files = []
    list_file = os.path.join(input_dir, "filelist.txt")

    try:
        with open(list_file, "w", encoding="utf-8") as f:
            for video in video_files:
                print(f"\nProcessing: {video}")
                video_path = os.path.join(input_dir, video)

                # 查找音频文件
                audio_path = find_audio_file(video, input_dir, audio_extensions)

                if audio_path:
                    # 获取音频时长
                    duration = get_audio_duration(audio_path)
                    if duration is not None and duration > 0:
                        # 根据音频时长截取视频
                        temp_video = os.path.join(input_dir, f"temp_cut_{video}")
                        if cut_video_to_duration(video_path, temp_video, duration):
                            abs_path = os.path.abspath(temp_video)
                            f.write(f"file '{abs_path}'\n")
                            temp_files.append(temp_video)
                            continue

                # 如果没有找到音频文件或处理失败，使用原始视频
                abs_path = os.path.abspath(video_path)
                f.write(f"file '{abs_path}'\n")
                print(f"  Use original video (no audio or cut failed)")

        print(f"\nMerging {len(video_files)} videos into {output_file}...")

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c",
            "copy",
            output_file,
        ]

        subprocess.run(cmd, check=True)
        print(f"Successfully merged video: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Failed to merge videos: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(list_file):
            os.remove(list_file)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge video segments in a directory")
    parser.add_argument(
        "--input_dir", required=True, help="Directory containing video segments"
    )
    parser.add_argument(
        "--output_file", required=True, help="Path to save the merged video"
    )

    args = parser.parse_args()
    merge_videos(args.input_dir, args.output_file)
