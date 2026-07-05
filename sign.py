import os
import requests
import json

# ========== 从环境变量读取配置 ==========
DLS = os.getenv("DLS")
SCKEY = os.getenv("SCKEY")

# 调试打印
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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 26_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.73(0x1800492d) NetType/4G Language/zh_CN",
        "Referer": "https://servicewechat.com/wxe11089c85860ec02/56/page-frame.html"
    }

def sign_in(token):
    """签到接口"""
    url = "https://vip.ixiliu.cn/mp/sign/applyV2"
    headers = get_headers(token)
    try:
        res = requests.get(url, headers=headers)
        print(f"🔍 签到响应状态码: {res.status_code}")
        print(f"🔍 签到响应内容: {res.text[:500]}")  # 打印前500字符
        
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
    """获取抽奖次数 - 带详细调试"""
    url = "https://vip.ixiliu.cn/mp/activity.lottery.getUserInfoV2"
    headers = get_headers(token)
    params = {"snId": "468512040523264"}
    
    print(f"\n🔍 ===== 开始获取抽奖次数 =====")
    print(f"🔍 请求URL: {url}")
    print(f"🔍 请求参数: {params}")
    print(f"🔍 请求头: {headers}")
    
    try:
        res = requests.get(url, headers=headers, params=params)
        print(f"🔍 响应状态码: {res.status_code}")
        print(f"🔍 原始响应内容: {res.text}")
        
        if res.status_code == 200:
            data = res.json()
            print(f"🔍 解析后的JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("status") == 200:
                # 打印所有可能的字段路径
                print(f"\n🔍 开始查找 draw_day_times 字段...")
                print(f"🔍 data.keys(): {data.keys()}")
                
                # 检查 data 下的所有键
                for key in data.keys():
                    print(f"🔍 data['{key}'] 类型: {type(data[key])}")
                    if isinstance(data[key], dict):
                        print(f"🔍 data['{key}'].keys(): {data[key].keys()}")
                
                # 尝试多种路径获取 draw_day_times
                result_data = data.get("data", {})
                print(f"\n🔍 result_data 类型: {type(result_data)}")
                print(f"🔍 result_data 内容: {result_data}")
                
                if isinstance(result_data, dict):
                    # 打印所有键
                    print(f"🔍 result_data.keys(): {result_data.keys()}")
                    
                    # 方案1: 直接在 result_data 下
                    if "draw_day_times" in result_data:
                        value = result_data.get("draw_day_times", 0)
                        print(f"✅ 在 result_data 下找到 draw_day_times = {value}")
                        return value
                    
                    # 方案2: 在 result_data.user 下
                    if "user" in result_data and isinstance(result_data["user"], dict):
                        if "draw_day_times" in result_data["user"]:
                            value = result_data["user"].get("draw_day_times", 0)
                            print(f"✅ 在 result_data.user 下找到 draw_day_times = {value}")
                            return value
                    
                    # 方案3: 在 result_data.data 下
                    if "data" in result_data and isinstance(result_data["data"], dict):
                        if "draw_day_times" in result_data["data"]:
                            value = result_data["data"].get("draw_day_times", 0)
                            print(f"✅ 在 result_data.data 下找到 draw_day_times = {value}")
                            return value
                    
                    # 方案4: 搜索所有嵌套字典中的 draw_day_times
                    print("🔍 在所有嵌套字典中搜索 draw_day_times...")
                    def find_key_in_dict(obj, target_key):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key == target_key:
                                    return value
                                if isinstance(value, (dict, list)):
                                    result = find_key_in_dict(value, target_key)
                                    if result is not None:
                                        return result
                        elif isinstance(obj, list):
                            for item in obj:
                                result = find_key_in_dict(item, target_key)
                                if result is not None:
                                    return result
                        return None
                    
                    found_value = find_key_in_dict(data, "draw_day_times")
                    if found_value is not None:
                        print(f"✅ 在嵌套结构中找到 draw_day_times = {found_value}")
                        return found_value
                    
                    print("❌ 未在任何位置找到 draw_day_times 字段")
                    
                    # 打印所有字段名供参考
                    print("\n🔍 数据中所有字段名:")
                    def print_all_keys(obj, prefix=""):
                        if isinstance(obj, dict):
                            for key in obj.keys():
                                print(f"  {prefix}{key}")
                                if isinstance(obj[key], (dict, list)):
                                    print_all_keys(obj[key], prefix + "  ")
                        elif isinstance(obj, list) and len(obj) > 0:
                            print_all_keys(obj[0], prefix + "  [0]")
                    
                    print_all_keys(data)
                    
                return 0
            else:
                print(f"❌ 接口返回status不为200: {data.get('status')}")
                return 0
        else:
            print(f"❌ 请求失败，状态码: {res.status_code}")
            return 0
    except Exception as e:
        print(f"❌ 获取抽奖次数异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def lottery(token):
    """抽奖接口"""
    print(f"\n🔍 ===== 开始抽奖 =====")
    draw_count = get_draw_chance(token)
    print(f"🔍 获取到的抽奖次数: {draw_count}")
    
    if draw_count <= 0:
        return "ℹ️ 今日抽奖次数已用完"
    
    url = "https://vip.ixiliu.cn/mp/activity.lottery/draw"
    headers = get_headers(token)
    params = {"snId": "468512040523264", "channelSn": "0"}
    
    print(f"🔍 抽奖请求URL: {url}")
    print(f"🔍 抽奖请求参数: {params}")
    
    try:
        res = requests.get(url, headers=headers, params=params)
        print(f"🔍 抽奖响应状态码: {res.status_code}")
        print(f"🔍 抽奖响应内容: {res.text}")
        
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
        
        # 打印token前几位（安全起见）
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
