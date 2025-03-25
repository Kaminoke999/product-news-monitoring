import json
import os
import requests
from datetime import datetime
from typing import Dict, List

class NewsChecker:
    def __init__(self):
        self.slack_webhook = os.environ['SLACK_WEBHOOK_URL']
        self.config = self.load_config()

    def load_config(self) -> Dict:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_news(self) -> None:
        try:
            for source in self.config['news_sources']:
                response = requests.get(source['url'])
                if response.status_code == 200:
                    news_data = response.json()
                    self.process_news(news_data, source)
        except Exception as e:
            self.notify_error(str(e))

    def process_news(self, news_data: List[Dict], source: Dict) -> None:
        for item in news_data:
            if self.match_keywords(item['title'], source['keywords']):
                self.notify_slack(item, source)
                break

    def match_keywords(self, text: str, keywords: List[str]) -> bool:
        return any(keyword.lower() in text.lower() for keyword in keywords)

    def notify_slack(self, news_item: Dict, source: Dict) -> None:
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 新規リリース情報"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*製品名:*\n{source['name']}"},
                        {"type": "mrkdwn", "text": f"*担当者:*\n{source['members']}"},
                        {"type": "mrkdwn", "text": f"*タイトル:*\n{news_item['title']}"},
                        {"type": "mrkdwn", "text": f"*URL:*\n{news_item['url']}"}
                    ]
                }
            ]
        }
        
        requests.post(self.slack_webhook, json=message)

    def notify_error(self, error_message: str) -> None:
        message = {
            "text": f"⚠️ エラーが発生しました:\n{error_message}"
        }
        requests.post(self.slack_webhook, json=message)

if __name__ == "__main__":
    checker = NewsChecker()
    checker.check_news()
