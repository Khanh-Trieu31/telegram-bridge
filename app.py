import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GH_TOKEN = os.environ.get("GH_TOKEN")

GITHUB_OWNER = "Khanh-Trieu31"
GITHUB_REPO = "tbhoathinh3d-tracker"


@app.route("/")
def home():
  return "Telegram-GitHub Bridge is running!"


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
  try:
    # Dùng force=True để ép Flask đọc chính xác dữ liệu JSON từ Telegram
    data = request.get_json(force=True, silent=True)
    print("DEBUG DATA:", data)

    if not data or "callback_query" not in data:
      return jsonify({"status": "ignored"}), 200

    callback_query = data["callback_query"]
    callback_data = callback_query.get("data")
    chat_id = callback_query["message"]["chat"]["id"]
    query_id = callback_query["id"]

    if callback_data == "trigger_github":
      # 1. Phản hồi Telegram để tắt xoay vòng nút bấm
      requests.post(
          f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
          json={
              "callback_query_id": query_id,
              "text": "🚀 Đang gọi GitHub...",
          },
      )

      # 2. Gửi tín hiệu gọi GitHub Actions
      gh_url = (
          f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
      )
      headers = {
          "Authorization": f"Bearer {GH_TOKEN}",
          "Accept": "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
      }
      payload = {"event_type": "kich-hoat-chay"}

      gh_response = requests.post(gh_url, json=payload, headers=headers)
      print("GH STATUS CODE:", gh_response.status_code)
      print("GH RESPONSE TEXT:", gh_response.text)

      # 3. Gửi thông báo kết quả về Telegram
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
                    "❌ Lỗi GitHub ("
                    f"{gh_response.status_code}): {gh_response.text}"
                ),
            },
        )

  except Exception as e:
    print("PYTHON ERROR:", str(e))

  return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
