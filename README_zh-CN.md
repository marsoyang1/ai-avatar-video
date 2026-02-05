# AI Avatar Video Generator

[English Version](./README.md)

这是一个用于生成 AI 数字人视频的完整工作流项目。它包含从文案生成、语音合成、视频渲染到最终视频合并的自动化工具。

## ✨ 功能特点

- **全流程自动化**：覆盖文案、语音、视频生成及后期合并。
- **交互式工作流**：支持分步确认和参数调整，确保生成质量。
- **模块化设计**：各个步骤（语音、视频、合并）均提供独立脚本，可单独调用。
- **支持自定义**：支持自定义参考音频（克隆音色）、情绪参考及数字人形象。
- **多平台适配**：支持多种视频比例（9:16, 16:9 等），适配抖音、视频号、B站等不同平台。

## 📂 目录结构

```
.
├── assets/                 # 资源文件
│   ├── comfyui_workflow/   # ComfyUI 工作流 JSON
│   ├── emotion_reference_audio/ # 情绪参考音频
│   ├── reference_audio/    # 音色参考音频
│   └── reference_person/   # 数字人参考图片
├── out/                    # 输出目录（自动创建）
│   ├── voice/              # 生成的音频片段
│   ├── tmp/                # 生成的视频片段
│   └── video/              # 最终合成的视频
├── scripts/                # Python 执行脚本
│   ├── generate_avatar_video.py   # 数字人视频生成脚本 (ComfyUI)
│   ├── generate_voiceover_local.py # 语音合成脚本 (Index-TTS)
│   └── merge_videos.py            # 视频合并脚本 (FFmpeg)
├── SKILL.md                # 技能描述文档
└── README.md               # 项目说明文档
```

## 🛠️ 前置要求

1. **Python 环境**: 需要安装 Python 3.8 或更高版本。
2. **FFmpeg**: 系统需安装 FFmpeg 并配置到环境变量中（用于音频转换和视频合并）。
3. **API 服务**:
   - **Index-TTS**: 用于语音合成的 Gradio 服务。
   - **ComfyUI**: 用于视频生成的 ComfyUI 服务（需加载 `assets/comfyui_workflow/数字人.json` 工作流）。

## 📦 安装

1. 克隆本项目：
   ```bash
   git clone <repository_url>
   cd ai-avatar-video
   ```

2. 安装依赖：
   ```bash
   pip install requests gradio_client
   ```

## 🚀 使用指南

你可以通过 Python 脚本独立运行各个模块。

### 1. 语音合成

使用 `generate_voiceover_local.py` 生成语音片段。

```bash
python scripts/generate_voiceover_local.py \
  --texts "大家好，这是一个测试视频。" "欢迎使用 AI 数字人生成工具。" \
  --ref_audio "./assets/reference_audio/yb.wav" \
  --emotion_ref_audio "./assets/emotion_reference_audio/speed.wav" \
  --output_dir "./out/voice/task_001/" \
  --api_url "http://your-index-tts-api-url"
```

### 2. 视频生成

使用 `generate_avatar_video.py` 根据语音和图片生成视频。

```bash
python scripts/generate_avatar_video.py \
  "./assets/reference_person/yb.jpg" \
  "./out/voice/task_001/1.mp3" \
  --output_dir "./out/tmp/task_001/" \
  --api_url "http://your-comfyui-api-url" \
  --aspect_ratio "9:16"
```

### 3. 视频合并

使用 `merge_videos.py` 将多个视频片段合并为一个完整视频。

```bash
python scripts/merge_videos.py \
  --input_dir "./out/tmp/task_001/" \
  --output_file "./out/video/final_video.mp4"
```

## 📄 许可证

本项目采用 LICENSE 文件中规定的许可证。
