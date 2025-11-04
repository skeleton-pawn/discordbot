import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
load_dotenv()

import requests

def get_coin_price(coin_id: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10).json()
        if coin_id in response and "usd" in response[coin_id]:
            price = response[coin_id]["usd"]
            
            # 소수점 자리수 조건부 적용
            if coin_id in ["bitcoin", "ethereum"]:
                return f"${int(price):,}"        # 정수만
            else:
                return f"${price:,.2f}"          # 소수점 2자리
        else:
            return None
    except Exception:
        return None

# === 디스코드 봇 ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} Online! Bot is Ready.")

#price command
@bot.command(name="btc")
async def btc_price(ctx):
    price = get_coin_price("bitcoin")
    if price:
        await ctx.send(f"현재 비트코인 가격: **{price} USD**")
    else:
        await ctx.send("비트코인 가격을 가져오는 중 오류가 발생했습니다.")

@bot.command(name="xrp")
async def xrp_price(ctx):
    price = get_coin_price("ripple")
    if price:
        await ctx.send(f"현재 리플(XRP) 가격: **{price} USD**")
    else:
        await ctx.send("리플 가격을 가져오는 중 오류가 발생했습니다.")

@bot.command(name="eth")
async def eth_price(ctx):
    price = get_coin_price("ethereum")
    if price:
        await ctx.send(f"현재 이더리움(ETH) 가격: **{price} USD**")
    else:
        await ctx.send("이더리움 가격을 가져오는 중 오류가 발생했습니다.")

@bot.command(name="doge")
async def doge_price(ctx):
    price = get_coin_price("dogecoin")
    if price:
        await ctx.send(f"현재 도지코인(DOGE) 가격: **{price} USD**")
    else:
        await ctx.send("도지코인 가격을 가져오는 중 오류가 발생했습니다.")

#system command
@bot.command(name="sys")
async def system_info(ctx):
    try:
        info = os.popen("uptime && free -h && df -h --output=source,size,used,avail,pcent /").read()
        await ctx.send(f"```{info}```")
    except Exception as e:
        await ctx.send(f"시스템 정보를 가져오는 중 오류가 발생했습니다: {e}")

@bot.command(name="uptime")
async def uptime(ctx):
    try:
        uptime_info = os.popen("uptime -p").read().strip()
        await ctx.send(f"서버 업타임: `{uptime_info}`")
    except Exception as e:
        await ctx.send(f"업타임 정보를 가져오는 중 오류가 발생했습니다: {e}")

# 존재하지 않는 명령 처리
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ '{ctx.message.content}' 명령은 존재하지 않습니다.")
    else:
        raise error

bot.run(os.getenv("DISCORD_TOKEN"))
