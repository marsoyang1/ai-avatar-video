# AI Avatar Video Generator

[中文版本](./README_zh-CN.md)

This is a complete workflow project for generating AI avatar videos. It includes automated tools for copy generation, voice synthesis, video rendering, and final video merging.

## ✨ Features

- **Full Process Automation**: Covers copy, voice, video generation, and post-production merging.
- **Interactive Workflow**: Supports step-by-step confirmation and parameter adjustment to ensure generation quality.
- **Modular Design**: Each step (voice, video, merging) provides independent scripts that can be called separately.
- **Customizable**: Supports custom reference audio (voice cloning), emotional reference, and avatar images.
- **Multi-platform Support**: Supports multiple video aspect ratios (9:16, 16:9, etc.), adapting to different platforms like TikTok, YouTube Shorts, etc.

## 📂 Directory Structure

```
.
├── assets/                 # Resource files
│   ├── comfyui_workflow/   # ComfyUI workflow JSON
│   ├── emotion_reference_audio/ # Emotion reference audio
│   ├── reference_audio/    # Voice reference audio
│   └── reference_person/   # Avatar reference images
├── out/                    # Output directory (automatically created)
│   ├── voice/              # Generated audio clips
│   ├── tmp/                # Generated video clips
│   └── video/              # Final merged video
├── scripts/                # Python execution scripts
│   ├── generate_avatar_video.py   # Avatar video generation script (ComfyUI)
│   ├── generate_voiceover_local.py # Voice synthesis script (Index-TTS)
│   └── merge_videos.py            # Video merging script (FFmpeg)
├── SKILL.md                # Skill description document
└── README.md               # Project documentation
```

## 🛠️ Prerequisites

1. **Python Environment**: Python 3.8 or higher is required.
2. **FFmpeg**: System needs FFmpeg installed and configured in environment variables (for audio conversion and video merging).
3. **API Services**:
   - **Index-TTS**: Gradio service for voice synthesis.
   - **ComfyUI**: ComfyUI service for video generation (needs to load `assets/comfyui_workflow/digital_human.json` workflow).

## 📦 Installation

1. Clone this project:
   ```bash
   git clone <repository_url>
   cd ai-avatar-video
   ```

2. Install dependencies:
   ```bash
   pip install requests gradio_client
   ```

## 🚀 Usage Guide

You can run each module independently via Python scripts.

### 1. Voice Synthesis

Use `generate_voiceover_local.py` to generate audio clips.

```bash
python scripts/generate_voiceover_local.py \
  --texts "Hello everyone, this is a test video." "Welcome to the AI Avatar Generator." \
  --ref_audio "./assets/reference_audio/yb.wav" \
  --emotion_ref_audio "./assets/emotion_reference_audio/speed.wav" \
  --output_dir "./out/voice/task_001/" \
  --api_url "http://your-index-tts-api-url"
```

### 2. Video Generation

Use `generate_avatar_video.py` to generate video based on audio and image.

```bash
python scripts/generate_avatar_video.py \
  "./assets/reference_person/yb.jpg" \
  "./out/voice/task_001/1.mp3" \
  --output_dir "./out/tmp/task_001/" \
  --api_url "http://your-comfyui-api-url" \
  --aspect_ratio "9:16"
```

### 3. Video Merging

Use `merge_videos.py` to merge multiple video clips into a complete video.

```bash
python scripts/merge_videos.py \
  --input_dir "./out/tmp/task_001/" \
  --output_file "./out/video/final_video.mp4"
```

## 📄 License

This project is licensed under the terms specified in the LICENSE file.
