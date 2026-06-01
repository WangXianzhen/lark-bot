# 飞书机器人

## 配置

1. 在 Railway 部署时设置环境变量：
   - LARK_APP_ID
   - LARK_APP_SECRET  
   - VERIFICATION_TOKEN（从飞书开放平台获取）

2. 在飞书开放平台配置请求地址为：`https://你的railway地址/event`

## 本地测试

```bash
pip install -r requirements.txt
python app.py
```

使用 ngrok 暴露本地端口进行测试。
