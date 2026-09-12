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
    data = request.get_json()
    print("Nhan du lieu tu Telegram:", data)  # In dữ liệu nhận được ra logs

    if "callback_query" in data:
      callback_query = data["callback_query"]
      callback_data = callback_query.get("data")
      chat_id = callback_query["message"]["chat"]["id"]
      query_id = callback_query["id"]

      if callback_data == "trigger_github":
        # Phản hồi Telegram trước
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
            json={
                "callback_query_id": query_id,
                "text": "🚀 Đang gọi GitHub...",
            },
        )

        # Gọi GitHub API
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
        print(
            "Phan hoi tu GitHub - Status Code:", gh_response.status_code
        )  # In mã trạng thái GitHub
        print("Noi dung phan hoi:", gh_response.text)  # In nội dung lỗi nếu có

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
    print("Loi xay ra trong webhook:", str(e))

  return jsonify({"status": "ok"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
