from gradio_client import Client, handle_file
import shutil
import os
import subprocess
import time
import argparse


def generate_voiceover(texts, ref_audio, emotion_ref_audio, output_dir, api_url=None):
    if api_url is None:
        raise ValueError("api_url is required. Please provide the Index-TTS API URL.")
    if not os.path.exists(ref_audio):
        print(f"Error: Reference audio {ref_audio} not found.")
        return

    if not os.path.exists(emotion_ref_audio):
        print(f"Error: Emotion reference audio {emotion_ref_audio} not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    client = Client(api_url)
    print(f"Connected to {api_url}")

    for i, text in enumerate(texts):
        filename = f"{i + 1}.mp3"
        output_path = os.path.join(output_dir, filename)
        print(f"Generating {filename} for text: {text[:20]}...")

        try:
            result = client.predict(
                "Use emotion reference audio",
                handle_file(ref_audio),
                text,
                handle_file(emotion_ref_audio),
                0.85,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                "",
                False,
                120,
                True,
                0.8,
                30,
                0.8,
                0.0,
                3,
                10.0,
                1500,
                api_name="/gen_single",
            )

            wav_path = None
            if isinstance(result, dict) and "value" in result:
                wav_path = result["value"]
            elif isinstance(result, str):
                wav_path = result
            elif isinstance(result, tuple):
                wav_path = result[1]

            if not wav_path or not os.path.exists(wav_path):
                print(
                    f"Error: Invalid result or file not found for {filename}: {result}"
                )
                continue

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                wav_path,
                "-acodec",
                "libmp3lame",
                "-q:a",
                "2",
                output_path,
            ]
            subprocess.run(
                cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            print(f"Saved to {output_path}")

        except Exception as e:
            print(f"Failed to generate {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate voiceover using index-TTS interface"
    )
    parser.add_argument(
        "--texts",
        nargs="+",
        required=True,
        help="List of texts to generate voiceover for",
    )
    parser.add_argument(
        "--ref_audio",
        default="./resource/reference_audio/yb.wav",
        help="Path to reference audio",
    )
    parser.add_argument(
        "--emotion_ref_audio",
        default="./resource/emotion_reference_audio/speed.wav",
        help="Path to emotion reference audio",
    )
    parser.add_argument(
        "--output_dir", default="./out/voice/", help="Directory to save generated audio"
    )
    parser.add_argument(
        "--api_url",
        required=True,
        help="Index-TTS API URL",
    )

    args = parser.parse_args()

    generate_voiceover(
        texts=args.texts,
        ref_audio=args.ref_audio,
        emotion_ref_audio=args.emotion_ref_audio,
        output_dir=args.output_dir,
        api_url=args.api_url,
    )
