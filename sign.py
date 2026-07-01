import os
import requests
# ========== 从环境变量读取配置 ==========
DLS = os.getenv("DLS")
SCKEY = os.getenv("SCKEY")
# 调试打印
print(f"DEBUG: SCKEY 变量值 = {SCKEY}")
print(f"DEBUG: DLS 变量值 = {DLS[:10]}...")

def send_wechat_notice(title, content):
    """通过Server酱发送微信推送"""
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

# 【重点】用你抓包到的完整请求头，和 Access-Token 字段
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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 26_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.73(0x1800492d) NetType/4G Language/zh_CN",
        "Referer": "https://servicewechat.com/wxe11089c85860ec02/56/page-frame.html"
    }

def sign_in(token):
    """签到接口"""
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
    """获取抽奖次数"""
    url = "https://vip.ixiliu.cn/mp/activity.lottery.getUserInfoV2"
    headers = get_headers(token)
    params = {"snId": "478725928739072"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 200:
                # 👇 这里改成真实字段 draw_day_times（已修复）
                return data.get("data", {}).get("user", {}).get("draw_day_times", 0)
        return 0
    except:
        return 0

def lottery(token):
    """抽奖接口"""
    draw_count = get_draw_chance(token)
    if draw_count <= 0:
        return "ℹ️ 今日抽奖次数已用完"
    
    url = "https://vip.ixiliu.cn/mp/activity.lottery/draw"
    headers = get_headers(token)
    params = {"snId": "478725928739072", "channelSn": "0"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 200:
                prize = data.get("data", {}).get("prize", {}).get("prize_name", "未知奖品")
                return f"✅ 抽奖成功，获得: {prize}"
            else:
                return f"❌ 抽奖失败: {data.get('message', '未知错误')}"
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
        print(f"\n===== 账号[{idx}] =====")
        sign_result = sign_in(token)
        print(sign_result)
        lottery_result = lottery(token)
        print(lottery_result)
        total_result.append(f"账号{idx}:\n{sign_result}\n{lottery_result}")
    result_content = "\n\n".join(total_result)
    print(f"\n===== 运行汇总 =====\n{result_content}")
    send_wechat_notice("杜蕾斯签到脚本", result_content)
