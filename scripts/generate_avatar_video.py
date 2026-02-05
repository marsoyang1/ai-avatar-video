import os
import json
import time
import urllib.request
import urllib.parse
import requests
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_FILE = os.path.join(BASE_DIR, "assets", "comfyui_workflow", "数字人.json")
DEFAULT_REF_IMG = os.path.join(BASE_DIR, "assets", "reference_person", "yb.jpg")
DEFAULT_AUDIO = "out/voice/5.mp3"
DEFAULT_OUTPUT_DIR = "out/tmp"


class ComfyUIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.client_id = "client_" + str(int(time.time()))

    def _request(self, endpoint, data=None, method="GET", is_binary=False):
        url = f"{self.base_url}{endpoint}"
        if data is not None and not is_binary:
            data = json.dumps(data).encode("utf-8")

        headers = {"Content-Type": "application/json"} if not is_binary else {}

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                if is_binary:
                    return response.read()
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"Request failed: {url}, Error: {e}")
            raise

    def upload_file(self, file_path, file_type="input"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        print(f"Uploading: {filename} ...")

        with open(file_path, "rb") as f:
            files = {"image": (filename, f)}
            data = {"type": file_type, "overwrite": "true"}
            response = requests.post(
                f"{self.base_url}/upload/image", files=files, data=data
            )

        if response.status_code == 200:
            result = response.json()
            uploaded_name = result.get("name")
            if result.get("subfolder"):
                uploaded_name = os.path.join(result.get("subfolder"), uploaded_name)
            print(f"Uploaded: {uploaded_name}")
            return uploaded_name
        else:
            raise Exception(f"Upload failed: {response.text}")

    def queue_prompt(self, workflow):
        print("Queuing prompt...")
        p = {"prompt": workflow, "client_id": self.client_id}
        result = self._request("/prompt", p, method="POST")
        prompt_id = result["prompt_id"]
        print(f"Prompt queued ID: {prompt_id}")
        return prompt_id

    def wait_for_completion(self, prompt_id, timeout=1200):
        print("Waiting for completion...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            history = self._request(f"/history/{prompt_id}")
            if prompt_id in history:
                print("Task completed!")
                return history[prompt_id]
            time.sleep(5)
        raise TimeoutError("Task timed out")

    def download_output(self, history_data, output_dir):
        outputs = history_data.get("outputs", {})
        downloaded_files = []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Debug: Full outputs keys: {list(outputs.keys())}")
        for node_id, node_output in outputs.items():
            print(f"Debug: Node {node_id} output keys: {list(node_output.keys())}")
            for key in ["gifs", "videos", "images"]:
                if key in node_output:
                    for item in node_output[key]:
                        print(f"Debug: Found {key} item: {item}")
                        self._download_file(item, output_dir, downloaded_files)

        return downloaded_files

    def _download_file(self, file_info, output_dir, downloaded_files):
        # filename = file_info["filename"]
        file_ext = os.path.splitext(file_info["filename"])[1]
        if not file_ext:
            file_ext = ".mp4"

        # Auto-increment filename logic: 1.mp4, 2.mp4 ...
        existing_files = [f for f in os.listdir(output_dir) if f.endswith(file_ext)]
        max_num = 0
        for f in existing_files:
            name_no_ext = os.path.splitext(f)[0]
            if name_no_ext.isdigit():
                try:
                    num = int(name_no_ext)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue

        new_filename = f"{max_num + 1}{file_ext}"

        subfolder = file_info.get("subfolder", "")
        file_type = file_info.get("type", "output")

        params = urllib.parse.urlencode(
            {
                "filename": file_info["filename"],
                "subfolder": subfolder,
                "type": file_type,
            }
        )

        print(f"Downloading: {file_info['filename']} -> {new_filename}...")
        file_data = self._request(f"/view?{params}", is_binary=True)
        save_path = os.path.join(output_dir, new_filename)
        with open(save_path, "wb") as f:
            f.write(file_data)
        print(f"Saved to: {save_path}")
        downloaded_files.append(save_path)


def update_workflow(workflow, image_name, audio_name, resolution="560x996"):
    found_image = False
    found_audio = False

    target_width = None
    target_height = None
    if resolution:
        try:
            if "x" in str(resolution):
                parts = str(resolution).lower().split("x")
                target_width = int(parts[0])
                target_height = int(parts[1])
            else:
                print(
                    f"⚠️ Warning: Invalid resolution format: {resolution}. Expected 'WIDTHxHEIGHT' (e.g., 1080x1920)"
                )
        except Exception as e:
            print(f"⚠️ Warning: Failed to parse resolution: {e}")

    for node_id, node in workflow.items():
        class_type = node.get("class_type")
        inputs = node.get("inputs", {})

        if class_type in ["LoadImage", "ImageLoader", "Load Image"]:
            inputs["image"] = image_name
            found_image = True

        if class_type in [
            "LoadAudio",
            "AudioLoader",
            "Load Audio",
            "ETN_LoadAudio",
            "VH_LoadAudio",
        ]:
            for key in ["audio", "path", "upload"]:
                if key in inputs:
                    inputs[key] = audio_name
                    found_audio = True
                    break

        # Update resolution for relevant nodes
        if target_width and target_height:
            if "width" in inputs and "height" in inputs:
                print(
                    f"Updating resolution for node {node_id} ({class_type}): {inputs['width']}x{inputs['height']} -> {target_width}x{target_height}"
                )
                inputs["width"] = target_width
                inputs["height"] = target_height

    if not found_image:
        print("⚠️ Warning: No image loader node found in workflow")
    if not found_audio:
        print("⚠️ Warning: No audio loader node found in workflow")

    return workflow


def generate_avatar_video(
    ref_img=DEFAULT_REF_IMG,
    ref_audio=DEFAULT_AUDIO,
    output_dir=DEFAULT_OUTPUT_DIR,
    api_url=None,
    resolution=None,
):
    if api_url is None:
        raise ValueError("api_url is required. Please provide the ComfyUI API URL.")

    if not os.path.exists(WORKFLOW_FILE):
        print(f"❌ Error: Workflow file missing: {WORKFLOW_FILE}")
        return

    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    client = ComfyUIClient(api_url)
    server_img = client.upload_file(ref_img)
    server_audio = client.upload_file(ref_audio)
    workflow = update_workflow(workflow, server_img, server_audio, resolution)
    prompt_id = client.queue_prompt(workflow)
    history = client.wait_for_completion(prompt_id)
    files = client.download_output(history, output_dir)

    if files:
        print(f"\nSuccess! Results in: {output_dir}")
        for f in files:
            print(f"   - {f}")
    else:
        print("\nNo output files found.")


if __name__ == "__main__":
    import io

    parser = argparse.ArgumentParser(description="Generate avatar video using ComfyUI")
    parser.add_argument(
        "ref_img", nargs="?", default=DEFAULT_REF_IMG, help="Path to reference image"
    )
    parser.add_argument(
        "ref_audio", nargs="?", default=DEFAULT_AUDIO, help="Path to reference audio"
    )
    parser.add_argument(
        "--output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save generated video",
    )
    parser.add_argument("--api_url", required=True, help="ComfyUI API URL")
    parser.add_argument("--resolution", help="Video resolution (e.g., 560x960),9:16,560×996,竖屏16:9,996×560,横屏1:1,746×746,4:3,862×646")

    args = parser.parse_args()

    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    generate_avatar_video(
        args.ref_img, args.ref_audio, args.output_dir, args.api_url, args.resolution
    )
