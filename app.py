import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 飞书 Webhook 验证 token（从环境变量或配置文件获取）
VERIFICATION_TOKEN = os.environ.get("VERIFICATION_TOKEN", "")
ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY", "")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 处理飞书 URL 验证请求
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if 'challenge' in params:
            challenge = params['challenge'][0]
            response = {"challenge": challenge}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            print(f"URL 验证成功，challenge: {challenge}")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # 检查是否加密
        encrypt = self.headers.get('X-lark-encrypt', '')
        if encrypt:
            print("收到加密消息，需要配置 AES 解密")

        try:
            data = json.loads(body)
            print(f"收到消息: {json.dumps(data, ensure_ascii=False)}")

            # 处理飞书 URL 验证（url_verification 类型）
            if data.get('type') == 'url_verification':
                challenge = data.get('challenge', '')
                response = {"challenge": challenge}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                print(f"URL 验证成功，challenge: {challenge}")
                return

            # 处理事件
            event = data.get('event', {})
            event_type = data.get('event_type', '')

            if event_type == 'im.message.receive_v1':
                message = event.get('message', {})
                content = json.loads(message.get('content', '{}'))
                text = content.get('text', '')
                chat_id = message.get('chat_id', '')
                message_id = message.get('message_id', '')
                sender = event.get('sender', {})
                sender_id = sender.get('sender_id', {}).get('open_id', '')

                print(f"收到消息 from {sender_id}: {text}")

                # 这里调用 AI 处理，回复消息
                reply = f"收到：{text}"

                # 回复消息
                self.reply_message(chat_id, reply)

        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"code": 0}).encode())

    def reply_message(self, chat_id, text):
        app_id = os.environ.get("LARK_APP_ID", "")
        app_secret = os.environ.get("LARK_APP_SECRET", "")

        if not app_id or not app_secret:
            print("未配置 LARK_APP_ID 或 LARK_APP_SECRET")
            return

        # 使用 lark-cli 发送消息
        cmd = f'''export PATH="$HOME/bin:$PATH" && lark-cli im +messages-send --chat-id "{chat_id}" --text "{text}"'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"回复结果: {result.stdout} {result.stderr}")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 8000))
    print(f"机器人服务运行在 http://0.0.0.0:{PORT}")
    print(f"APP_ID: {os.environ.get('LARK_APP_ID', '未设置')}")
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()