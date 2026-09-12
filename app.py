import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Lấy các biến môi trường đã cấu hình trên Render
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GH_TOKEN = os.environ.get("GH_TOKEN")  # GitHub Personal Access Token của bạn

# Thay thế các thông tin GitHub của bạn vào đây:
GITHUB_OWNER = "Khanh-Trieu31"  # Tên tài khoản GitHub của bạn
GITHUB_REPO = "tbhoathinh3d-tracker"  # Tên kho chứa dự án quét phim


@app.route("/")
def home():
  return "Telegram-GitHub Bridge is running!"


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
  data = request.get_json()

  # Kiểm tra xem người dùng có bấm vào inline button hay không
  if "callback_query" in data:
    callback_query = data["callback_query"]
    callback_data = callback_query.get("data")
    chat_id = callback_query["message"]["chat"]["id"]
    query_id = callback_query["id"]

    if callback_data == "trigger_github":
      # 1. Gửi phản hồi tức thì cho Telegram để nút bấm ngừng xoay vòng
      answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
      requests.post(
          answer_url,
          json={
              "callback_query_id": query_id,
              "text": "🚀 Đang kích hoạt GitHub chạy ngay lập tức...",
              "show_alert": False,
          },
      )

      # 2. Gửi tín hiệu gọi GitHub Actions qua repository_dispatch
      gh_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
      headers = {
          "Authorization": f"Bearer {GH_TOKEN}",
          "Accept": "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
      }
      payload = {"event_type": "kich-hoat-chay"}

      gh_response = requests.post(gh_url, json=payload, headers=headers)

      # 3. Gửi tin nhắn thông báo kết quả về Telegram
      msg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
      if gh_response.status_code == 204:
        requests.post(
            msg_url,
            json={
                "chat_id": chat_id,
                "text": "✅ Đã kích hoạt GitHub Actions thành công!",
            },
        )
      else:
        requests.post(
            msg_url,
            json={
                "chat_id": chat_id,
                "text": (
                    "❌ Kích hoạt thất bại từ GitHub: "
                    f"{gh_response.status_code}"
                ),
            },
        )

  return jsonify({"status": "ok"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
