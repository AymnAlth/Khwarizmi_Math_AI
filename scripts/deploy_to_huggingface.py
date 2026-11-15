"""
Al-Khwarizmi Neuro-Symbolic Math AI - Hugging Face Automated Deployment
Uploads the application and neuro-symbolic reasoning engine to Hugging Face Spaces
and/or Hugging Face Model Hub with automatic Git/CI/CD tracking.
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, login

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEPLOY_DIR = PROJECT_ROOT / "deploy" / "hf_space"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy Al-Khwarizmi Math AI to Hugging Face")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (Write permission)")
    parser.add_argument("--space_name", type=str, default="Khwarizmi-Math-AI", help="Name of the Hugging Face Space")
    parser.add_argument("--upload_model", action="store_true", help="Also upload LoRA and GGUF model artifacts to HF Models Hub")
    return parser.parse_args()


def main():
    args = parse_args()
    token = args.token or os.environ.get("HF_TOKEN")

    print("=" * 65)
    print("   🧮 Al-Khwarizmi Math AI - Hugging Face Deployment Pipeline")
    print("=" * 65)

    if not token:
        print("[!] No Hugging Face token provided via --token or HF_TOKEN environment variable.")
        token = input("👉 Please paste your Hugging Face Access Token (Write permissions): ").strip()

    if not token:
        print("[-] Deployment aborted: A Hugging Face token is required.")
        sys.exit(1)

    print("[*] Authenticating with Hugging Face...")
    try:
        login(token=token, add_to_git_credential=True)
        api = HfApi(token=token)
        user_info = api.whoami()
        username = user_info["name"]
        print(f"[✓] Successfully authenticated as: @{username}")
    except Exception as e:
        print(f"[-] Authentication failed: {e}")
        sys.exit(1)

    # 1. Create or verify Hugging Face Space
    space_id = f"{username}/{args.space_name}"
    print(f"\n[*] Step 1: Configuring Hugging Face Space: {space_id}...")
    try:
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            private=False,
            exist_ok=True,
        )
        print(f"[✓] Space repository confirmed: https://huggingface.co/spaces/{space_id}")
    except Exception as e:
        print(f"[-] Failed to create/verify Space: {e}")
        sys.exit(1)

    # 2. Upload Space application files
    print(f"\n[*] Step 2: Uploading application files from {DEPLOY_DIR}...")
    try:
        api.upload_folder(
            folder_path=str(DEPLOY_DIR),
            repo_id=space_id,
            repo_type="space",
            commit_message="feat(deploy): deploy production Khwarizmi Math AI to Hugging Face Spaces",
        )
        print("[✓] All deployment files uploaded successfully!")
    except Exception as e:
        print(f"[-] Error uploading Space files: {e}")
        sys.exit(1)

    # 3. Optional: Upload model artifacts
    if args.upload_model:
        model_id = f"{username}/Khwarizmi-Math-1.5B"
        print(f"\n[*] Step 3: Creating Model Hub Repository: {model_id}...")
        try:
            api.create_repo(repo_id=model_id, repo_type="model", private=False, exist_ok=True)
            sft_dir = ARTIFACTS_DIR / "qwen_khwarizmi_sft"
            if sft_dir.exists():
                print(f"[*] Uploading LoRA Adapters from {sft_dir}...")
                api.upload_folder(
                    folder_path=str(sft_dir),
                    repo_id=model_id,
                    repo_type="model",
                    commit_message="weights: upload QLoRA fine-tuned adapter weights",
                )
                print(f"[✓] LoRA weights live at: https://huggingface.co/{model_id}")
        except Exception as e:
            print(f"[!] Warning uploading model weights: {e}")

    # Final summary
    clean_space_name = args.space_name.lower().replace("_", "-")
    direct_api_url = f"https://{username.lower()}-{clean_space_name}.hf.space"
    space_page_url = f"https://huggingface.co/spaces/{space_id}"

    print("\n" + "=" * 65)
    print("   🎉 DEPLOYMENT COMPLETE! YOUR AI IS LIVE ON THE CLOUD!")
    print("=" * 65)
    print(f"🔗 Public Space Web UI : {space_page_url}")
    print(f"⚡ Direct Mobile REST API: {direct_api_url}/api/v1/solve")
    print(f"🩺 API Health Endpoint  : {direct_api_url}/api/v1/health")
    print("=" * 65)
    print("\n💡 Future Updates:")
    print("Whenever you make any changes or improvements in the future, simply re-run:")
    print("    python scripts/deploy_to_huggingface.py")
    print("And Hugging Face will update the live site and API within seconds without downtime!")
    print("=" * 65)


if __name__ == "__main__":
    main()
