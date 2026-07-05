import os
import requests
import json

# ========== 从环境变量读取配置 ==========
DLS = os.getenv("DLS")
SCKEY = os.getenv("SCKEY")

print(f"DEBUG: SCKEY 变量值 = {SCKEY}")
print(f"DEBUG: DLS 变量值 = {DLS[:10] if DLS else 'None'}...")

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

def get_headers(token):
    """请求头"""
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

def test_draw_api_paths(token):
    """测试不同的抽奖接口路径"""
    headers = get_headers(token)
    params = {"snId": "468512040523264"}
    
    # 可能的路径列表（按可能性排序）
    paths = [
        "/mp/lottery/getUserInfoV2",
        "/mp/activity/lottery/getUserInfoV2",
        "/mp/lottery/getUserInfo",
        "/mp/activity/lottery/getUserInfo",
        "/mp/lottery/userInfo",
        "/mp/activity.lottery/userInfo",
        "/mp/lottery/info",
        "/mp/activity/lottery/info",
        "/mp/lottery/getDrawTimes",
        "/mp/lottery/drawTimes",
        "/mp/user/lotteryInfo",
        "/mp/activity/lotteryInfo",
    ]
    
    print("\n🔍 ===== 开始探测抽奖接口路径 =====")
    
    for path in paths:
        url = f"https://vip.ixiliu.cn{path}"
        try:
            res = requests.get(url, headers=headers, params=params, timeout=5)
            status = res.status_code
            print(f"  测试路径: {path}")
            print(f"    状态码: {status}")
            
            if status == 200:
                try:
                    data = res.json()
                    print(f"    响应数据: {json.dumps(data, ensure_ascii=False)[:200]}")
                    # 检查是否包含 draw_day_times
                    if "draw_day_times" in str(data):
                        print(f"    ✅✅✅ 找到包含 draw_day_times 的路径！")
                        return path, data
                except:
                    print(f"    响应内容: {res.text[:100]}")
            else:
                print(f"    响应: {res.text[:50]}")
            print()
        except Exception as e:
            print(f"    请求失败: {e}")
            print()
    
    print("❌ 所有路径都测试完毕，未找到有效接口")
    return None, None

def get_draw_chance(token):
    """获取抽奖次数 - 自动探测路径"""
    # 先尝试测试所有路径
    valid_path, test_data = test_draw_api_paths(token)
    
    if valid_path:
        print(f"✅ 找到有效路径: {valid_path}")
        # 从测试数据中提取 draw_day_times
        if test_data:
            data = test_data
            if data.get("status") == 200:
                result_data = data.get("data", {})
                if isinstance(result_data, dict):
                    if "draw_day_times" in result_data:
                        return result_data.get("draw_day_times", 0)
                    if "user" in result_data:
                        return result_data.get("user", {}).get("draw_day_times", 0)
        return 0
    
    # 如果探测失败，尝试默认路径
    print("⚠️ 使用默认路径尝试...")
    url = "https://vip.ixiliu.cn/mp/lottery/getUserInfoV2"
    headers = get_headers(token)
    params = {"snId": "468512040523264"}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == 200:
                result_data = data.get("data", {})
                if isinstance(result_data, dict):
                    if "draw_day_times" in result_data:
                        return result_data.get("draw_day_times", 0)
                    if "user" in result_data:
                        return result_data.get("user", {}).get("draw_day_times", 0)
        return 0
    except:
        return 0

def lottery(token):
    """抽奖接口"""
    draw_count = get_draw_chance(token)
    print(f"🔍 获取到的抽奖次数: {draw_count}")
    
    if draw_count <= 0:
        return "ℹ️ 今日抽奖次数已用完"
    
    url = "https://vip.ixiliu.cn/mp/lottery/draw"
    headers = get_headers(token)
    params = {"snId": "468512040523264", "channelSn": "0"}
    
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
        print(f"\n{'='*50}")
        print(f"===== 账号[{idx}] =====")
        print(f"{'='*50}")
        
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
