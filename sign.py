import os
import requests
import json

DLS = os.getenv("DLS")

# PushPlus 配置
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")
PUSHPLUS_TOPIC = os.getenv("PUSHPLUS_TOPIC")

print(f"DEBUG: PUSHPLUS_TOKEN 变量值 = {PUSHPLUS_TOKEN[:10] + '...' if PUSHPLUS_TOKEN else 'None'}")
print(f"DEBUG: PUSHPLUS_TOPIC 变量值 = {PUSHPLUS_TOPIC if PUSHPLUS_TOPIC else 'None'}")
print(f"DEBUG: DLS 变量值 = {DLS[:10] if DLS else 'None'}...")


def send_pushplus_notice(title, content):
    """
    PushPlus 推送通知
    """
    if not PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过推送")
        return

    url = "https://www.pushplus.plus/send"

    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    # 如果配置了群组 topic，则加入 topic
    if PUSHPLUS_TOPIC:
        data["topic"] = PUSHPLUS_TOPIC

    try:
        res = requests.post(url, json=data, timeout=15)

        print(f"✅ PushPlus 推送请求已发送，状态码: {res.status_code}")

        try:
            result = res.json()
            print(f"🔍 PushPlus 返回: {json.dumps(result, ensure_ascii=False)}")

            if result.get("code") == 200:
                print("✅ PushPlus 推送成功")
            else:
                print(f"❌ PushPlus 推送失败: {result.get('msg', '未知错误')}")
        except Exception:
            print(f"🔍 PushPlus 原始返回: {res.text}")

    except Exception as e:
        print(f"❌ PushPlus 推送请求异常: {e}")


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
    """签到接口"""
    url = "https://vip.ixiliu.cn/mp/sign/applyV2"
    headers = get_headers(token)

    try:
        res = requests.get(url, headers=headers, timeout=15)

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


def get_user_info(token):
    """获取用户信息，积分余额"""
    url = "https://vip.ixiliu.cn/mp/sign/infoV2"
    headers = get_headers(token)

    try:
        res = requests.get(url, headers=headers, timeout=15)

        if res.status_code == 200:
            data = res.json()
            print(f"🔍 签到信息返回: {json.dumps(data, ensure_ascii=False)[:500]}")

            if data.get("status") == 200:
                info = data.get("data", {})

                user_points = info.get("user_points", 0)
                points_name = info.get("points_name", "积分")
                signed_day_num = info.get("signed_day_num", 0)
                today_is_signed = info.get("today_is_signed", False)

                return {
                    "points": user_points,
                    "points_name": points_name,
                    "signed_days": signed_day_num,
                    "today_signed": today_is_signed
                }

        return None

    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None


def get_draw_chance(token):
    """获取抽奖次数"""
    return 1


def lottery(token):
    """抽奖接口"""
    sn_id = "478725928739072"
    url = "https://vip.ixiliu.cn/mp/activity.lottery/draw"
    headers = get_headers(token)
    params = {
        "snId": sn_id,
        "channelSn": "0"
    }

    print(f"🔍 抽奖请求URL: {url}")
    print(f"🔍 抽奖请求参数: {params}")

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)

        print(f"🔍 抽奖响应状态码: {res.status_code}")
        print(f"🔍 抽奖响应内容: {res.text[:200]}")

        if res.status_code == 200:
            data = res.json()

            if data.get("status") == 200:
                prize = data.get("data", {}).get("prize", {}).get("prize_name", "未知奖品")
                return f"✅ 抽奖成功，获得: {prize}"
            else:
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
        print("❌ 未检测到环境变量 DLS")
        send_pushplus_notice("杜蕾斯签到脚本", "❌ 未检测到 Token，请检查配置")
        exit()

    tokens = DLS.split("&")
    total_result = []
    total_points = 0

    for idx, token in enumerate(tokens, 1):
        token = token.strip()

        if not token:
            continue

        print(f"\n{'=' * 50}")
        print(f"===== 账号[{idx}] =====")
        print(f"{'=' * 50}")
        print(f"🔍 Token前10位: {token[:10]}...")

        # 1. 获取用户信息
        print("\n📊 获取用户信息...")
        user_info = get_user_info(token)

        if user_info:
            points = user_info.get("points", 0)
            points_name = user_info.get("points_name", "积分")
            signed_days = user_info.get("signed_days", 0)
            today_signed = user_info.get("today_signed", False)

            print(f"💰 当前{points_name}: {points}")
            print(f"📅 本月签到天数: {signed_days} 天")
            print(f"📌 今日签到状态: {'✅ 已签到' if today_signed else '❌ 未签到'}")

            total_points += points

            user_info_str = (
                f"💰 当前{points_name}: {points}\n"
                f"📅 本月签到: {signed_days}天\n"
                f"📌 今日: {'已签到' if today_signed else '未签到'}"
            )
        else:
            user_info_str = "⚠️ 获取用户信息失败"
            print("⚠️ 获取用户信息失败")

        # 2. 执行签到
        print("\n📝 执行签到...")
        sign_result = sign_in(token)
        print(f"签到结果: {sign_result}")

        # 3. 执行抽奖
        print("\n🎰 执行抽奖...")
        lottery_result = lottery(token)
        print(f"抽奖结果: {lottery_result}")

        # 4. 汇总
        total_result.append(
            f"## 账号 {idx}\n\n"
            f"{user_info_str}\n\n"
            f"{sign_result}\n\n"
            f"{lottery_result}"
        )

    result_content = "\n\n---\n\n".join(total_result)

    print(f"\n{'=' * 50}")
    print("===== 运行汇总 =====")
    print(f"{'=' * 50}")
    print(result_content)
    print(f"\n💰 账号总积分: {total_points}")

    send_content = result_content + f"\n\n---\n\n## 汇总\n\n💰 账号总积分: {total_points}"

    send_pushplus_notice("杜蕾斯签到脚本", send_content)
