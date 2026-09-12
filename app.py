from flask import Flask, request
import os
import requests

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GH_TOKEN")
GITHUB_REPO = "Khanh-Trieu31/tbhoathinh3d-tracker"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
  data = request.get_json()

  if "callback_query" in data:
    callback_data = data["callback_query"]["data"]
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    query_id = data["callback_query"]["id"]

    if callback_data == "trigger_github":
      gh_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
      headers = {
          "Authorization": f"Bearer {GITHUB_TOKEN}",
          "Accept": "vnd.github+json",
      }
      payload = {"event_type": "kich-hoat-chay"}

      response = requests.post(gh_url, json=payload, headers=headers)

      # Trả phản hồi về Telegram để tắt hiệu ứng xoay vòng ở nút bấm
      requests.post(
          f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
          json={
              "callback_query_id": query_id,
              "text": (
                  "Đã kích hoạt GitHub thành công!"
                  if response.status_code == 204
                  else "Lỗi kích hoạt!"
              ),
          },
      )

  return "OK", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
