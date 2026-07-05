import os
import requests
import json

DLS = os.getenv("DLS")
SCKEY = os.getenv("SCKEY")

print(f"DEBUG: SCKEY 变量值 = {SCKEY}")
print(f"DEBUG: DLS 变量值 = {DLS[:10] if DLS else 'None'}...")

def send_wechat_notice(title, content):
    if not SCKEY:
        print("⚠️ 未配置SCKEY，跳过推送")
        return
    try:
        url = f"https://sctapi.ftqq.com/{SCKEY}.send"
        params = {"title": title, "desp": content}
        res = requests.get(url, params=params)
        print(f"✅ 推送请求发送成功，服务器返回状态码: {res.status_code}")
    except Exception as e:
        print(f"❌ 推送请求失败: {e}")

def get_headers(token):
    return {
        "Host": "vip.ixiliu.cn",
        "Connection": "keep-alive",
        "Access-Token": token,
        "Enterprise-hash": "10006",
        "sid": "10006",
        "content-type": "application/json;charset=utf-8",
        "platform": "MP-WEIXIN",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.73(0x1800492d) NetType/4G Language/zh_CN",
        "Referer": "https://servicewechat.com/wxe11089c85860ec02/56/page-frame.html"
    }

def sign_in(token):
    url = "https://vip.ixiliu.cn/mp/sign/applyV2"
    headers = get_headers(token)
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 200:
                return "✅ 签到成功"
            elif data.get("message") == "今日已签到，请明日再来":
                return "ℹ️ 今日已签到"
            else:
                return f"❌ 签到失败: {data.get('message', '未知错误')}"
        else:
            return f"❌ 签到请求失败，状态码: {res.status_code}"
    except Exception as e:
        return f"❌ 签到请求异常: {str(e)}"

def get_draw_chance(token):
    """获取抽奖次数 - 从签到信息接口获取"""
    url = "https://vip.ixiliu.cn/mp/sign/infoV2"
    headers = get_headers(token)
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"🔍 签到信息返回: {json.dumps(data, ensure_ascii=False)[:300]}")
            # 签到信息接口返回的是签到数据，没有抽奖次数
            # 如果今天已签到，通常会有抽奖次数
            if data.get("status") == 200:
                # 尝试从数据中获取抽奖次数（如果有的话）
                return 1  # 默认返回1次
        return 0
    except Exception as e:
        print(f"❌ 获取抽奖次数异常: {e}")
        return 0

def lottery(token):
    """抽奖接口 - 使用正确的 snId"""
    # 使用抓包到的正确 snId
    sn_id = "478725928739072"
    url = f"https://vip.ixiliu.cn/mp/activity.lottery/draw"
    headers = get_headers(token)
    params = {"snId": sn_id, "channelSn": "0"}
    
    print(f"🔍 抽奖请求URL: {url}")
    print(f"🔍 抽奖请求参数: {params}")
    
    try:
        res = requests.get(url, headers=headers, params=params)
        print(f"🔍 抽奖响应状态码: {res.status_code}")
        print(f"🔍 抽奖响应内容: {res.text[:200]}")
        
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 200:
                prize = data.get("data", {}).get("prize", {}).get("prize_name", "未知奖品")
                return f"✅ 抽奖成功，获得: {prize}"
            else:
                # 处理错误信息
                msg = data.get("message", "未知错误")
                if "次数" in msg or "已用" in msg:
                    return f"ℹ️ {msg}"
                return f"❌ 抽奖失败: {msg}"
        else:
            return f"❌ 抽奖请求失败，状态码: {res.status_code}"
    except Exception as e:
        return f"❌ 抽奖请求异常: {str(e)}"

if __name__ == "__main__":
    if not DLS:
        print("❌ 未检测到环境变量DLS")
        send_wechat_notice("杜蕾斯签到脚本", "❌ 未检测到Token，请检查配置")
        exit()

    tokens = DLS.split("&")
    total_result = []
    
    for idx, token in enumerate(tokens, 1):
        print(f"\n{'='*50}")
        print(f"===== 账号[{idx}] =====")
        print(f"{'='*50}")
        print(f"🔍 Token前10位: {token[:10]}...")
        
        sign_result = sign_in(token)
        print(f"签到结果: {sign_result}")
        
        lottery_result = lottery(token)
        print(f"抽奖结果: {lottery_result}")
        
        total_result.append(f"账号{idx}:\n{sign_result}\n{lottery_result}")
    
    result_content = "\n\n".join(total_result)
    print(f"\n{'='*50}")
    print(f"===== 运行汇总 =====")
    print(f"{'='*50}")
    print(result_content)
    
    send_wechat_notice("杜蕾斯签到脚本", result_content)
