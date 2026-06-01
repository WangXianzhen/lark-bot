import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# 飞书 Webhook 验证 token（从环境变量或配置文件获取）
VERIFICATION_TOKEN = ""  # 填入你的 Verification Token
ENCRYPT_KEY = ""  # 如果启用了加密，填入

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 处理验证 URL（可选）
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        print(f"收到消息: {json.dumps(data, ensure_ascii=False)}")
        
        # 处理事件
        event = data.get('event', {})
        event_type = data.get('event_type', '')
        
        if event_type == 'im.message.receive_v1':
            message = event.get('message', {})
            content = json.loads(message.get('content', '{}'))
            text = content.get('text', '')
            chat_id = message.get('chat_id', '')
            message_id = message.get('message_id', '')
            
            print(f"收到消息: {text}")
            
            # 这里调用 AI 处理，回复消息
            # 你可以接入 Claude API 等
            reply = f"收到：{text}"
            
            # 回复消息
            self.reply_message(chat_id, reply)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"code": 0}).encode())
    
    def reply_message(self, chat_id, text):
        cmd = f'''export PATH="$HOME/bin:$PATH" && lark-cli im +messages-send --chat-id "{chat_id}" --text "{text}"'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"回复结果: {result.stdout} {result.stderr}")
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"机器人服务运行在 http://0.0.0.0:{PORT}")
    server.serve_forever()
