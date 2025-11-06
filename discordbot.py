import discord
from discord.ext import commands
import requests
import os
import psutil
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
    print(f"{bot.user} Online! Your Bot Is Ready.")

# 암호화폐 가격 조회 함수
def get_crypto_price(symbol):
    """CoinGecko API를 사용하여 암호화폐 가격 조회"""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd,krw"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get(symbol)  # .get()으로 안전하게 접근
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None
    except Exception as e:
        print(f"가격 조회 중 알 수 없는 오류: {e}")
        return None

# 코인 정보를 딕셔너리로 관리
COIN_MAP = {
    'btc': {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': '₿', 'color': 0xF7931A},
    'eth': {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'Ξ', 'color': 0x627EEA},
    'xrp': {'id': 'ripple', 'name': 'Ripple', 'symbol': '◈', 'color': 0x00AAE4},
    'doge': {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'Ð', 'color': 0xC2A633},
}

@bot.command(name='p', aliases=['price'])
async def crypto_price(ctx, coin_symbol: str = 'btc'):
    """지정한 암호화폐의 가격을 조회합니다. (예: !p eth)"""
    symbol = coin_symbol.lower()
    coin = COIN_MAP.get(symbol)
    
    if not coin:
        supported_coins = ", ".join(COIN_MAP.keys())
        await ctx.send(f"❌ 지원하지 않는 코인입니다. (지원 목록: {supported_coins})")
        return

    data = get_crypto_price(coin['id'])
    if data:

        usd = data.get('usd', 0)
        krw = data.get('krw', 0)
        
        usd_format = ",.4f" if symbol in ['xrp', 'doge'] else ",.2f"
        krw_format = ",.2f" if symbol in ['xrp', 'doge'] else ",.0f"

        embed = discord.Embed(title=f"{coin['symbol']} {coin['name']} ({symbol.upper()})", color=coin['color'])
        embed.add_field(name="USD", value=f"${usd:{usd_format}}", inline=True)
        embed.add_field(name="KRW", value=f"₩{krw:{krw_format}}", inline=True)
        await ctx.send(embed=embed)

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
        await ctx.send("도지코인 가격을 가져오는 중 오류가 발생했습니다.")

#system command
@bot.command(name="sys")
async def system_info(ctx):
    try:
        info = os.popen("uptime && free -h && df -h --output=source,size,used,avail,pcent /").read()
        await ctx.send(f"```{info}```")
    except Exception as e:
        await ctx.send(f"시스템 정보를 가져오는 중 오류가 발생했습니다: {e}")

# CPU
@bot.command(name="cpu")
async def cpu_usage(ctx):
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        color = "🟩" if cpu_percent < 30 else "🟨" if cpu_percent < 50 else "🟥"
        await ctx.send(f"CPU 사용률: {color} **{cpu_percent:.1f}%**")
    except Exception as e:
        await ctx.send(f"CPU 정보를 가져오는 중 오류가 발생했습니다: {e}")

# RAM 
@bot.command(name="ram")
async def ram_usage(ctx):
    try:
        mem = psutil.virtual_memory()
        usage = mem.percent
        color = "🟩" if usage < 50 else "🟨" if usage < 70 else "🟥"
        await ctx.send(f"RAM 사용률: {color} **{usage:.1f}%**")
    except Exception as e:
        await ctx.send(f"RAM 정보를 가져오는 중 오류가 발생했습니다: {e}")

# SWAP
@bot.command(name="swap")
async def swap_usage(ctx):
    try:
        swap = psutil.swap_memory()
        total_gb = swap.total / (1024 ** 3)
        used_gb = swap.used / (1024 ** 3)
        percent = swap.percent

        color = "🟩" if percent < 50 else "🟨" if percent < 70 else "🟥"
        await ctx.send(
            f"Swap 사용률: {color} **{percent:.1f}%** "
            f"({used_gb:.1f} GiB / {total_gb:.1f} GiB)"
        )
    except Exception as e:
        await ctx.send(f"Swap 정보를 가져오는 중 오류가 발생했습니다: {e}")

# DISK
@bot.command(name="disk")
async def disk_usage(ctx):
    try:
        disk = psutil.disk_usage('/')
        total_gb = disk.total / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)
        percent = disk.percent

        color = "🟩" if percent < 70 else "🟨" if percent < 90 else "🟥"
        await ctx.send(
            f"디스크 사용률: {color} **{percent:.1f}%** "
            f"({used_gb:.1f} GiB / {total_gb:.1f} GiB)"
        )
    except Exception as e:
        await ctx.send(f"디스크 정보를 가져오는 중 오류가 발생했습니다: {e}")

@bot.command(name="info")
async def system_info(ctx):
    try:
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)

        # RAM 사용률
        mem = psutil.virtual_memory()
        ram_percent = mem.percent

        # 디스크 사용률 (루트 파티션 기준)
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        # 색상 (이모지) 지정
        def color(val, limits):
            green, yellow, red = limits
            if val < green:
                return "🟩"
            elif val < yellow:
                return "🟨"
            else:
                return "🟥"

        cpu_color = color(cpu_percent, (30, 50, 100))
        ram_color = color(ram_percent, (50, 70, 100))
        disk_color = color(disk_percent, (70, 90, 100))

        # 출력 포맷
        await ctx.send(
            f"📊 **System Info**\n"
            f"{cpu_color} CPU: **{cpu_percent:.1f}%**\n"
            f"{ram_color} RAM: **{ram_percent:.1f}%**\n"
            f"{disk_color} Disk: **{disk_percent:.1f}%**"
        )

    except Exception as e:
        await ctx.send(f"시스템 정보를 가져오는 중 오류가 발생했습니다: {e}")

# sever uptime
@bot.command(name="uptime")
async def uptime(ctx):
    try:
        uptime_info = os.popen("uptime -p").read().strip()
        await ctx.send(f"서버 업타임: `{uptime_info}`")
    except Exception as e:
        await ctx.send(f"업타임 정보를 가져오는 중 오류가 발생했습니다: {e}")

<<<<<<< HEAD
=======
@bot.command(name='info1')
async def system_info(ctx):
    """전체 시스템 정보 조회"""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    embed = discord.Embed(title="🖥️ 시스템 정보", description="서버의 전체 상태", color=0x2ecc71)
    embed.add_field(name="CPU", value=f"{cpu_percent}%", inline=True)
    embed.add_field(name="RAM", value=f"{ram.percent}%", inline=True)
    embed.add_field(name="Disk", value=f"{disk.percent}%", inline=True)
    
    await ctx.send(embed=embed)

# 서버 재부팅 명령어 (관리자 전용)
@bot.command(name='qreboot')
@commands.is_owner() # 봇 소유자만 실행 가능하도록 변경 
async def qreboot(ctx):

        embed = discord.Embed(

        title="⚠️ 서버 재부팅",
        description=f"5초 후 서버를 재부팅합니다.\n실행자: {ctx.author.mention}",
        color=0xff0000
    )
    await ctx.send(embed=embed)
    await asyncio.sleep(5)
    
    try:
        # sudoers 파일에 'username ALL=(ALL) NOPASSWD: /sbin/reboot' 와 같은 설정이 필요할 수 있습니다.
        result = subprocess.run(['sudo', 'reboot'], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        error_embed = discord.Embed(
            title="❌ 재부팅 실패",
            description=f"오류가 발생했습니다.\n```\n{e.stderr}\n```",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ 알 수 없는 오류",
            description=f"재부팅 중 예기치 않은 오류가 발생했습니다.\n`{e}`",
            color=0xff0000
        )
        await ctx.send(embed=error_embed)

@qreboot.before_invoke
async def ensure_owner(ctx):
    # 봇 애플리케이션 소유자 ID와 실행자 ID를 비교
    if not await bot.is_owner(ctx.author):
        await ctx.send("❌ 이 명령어를 사용할 권한이 없습니다.")
        raise commands.NotOwner("User is not the owner.")

@bot.command(name="com")
async def show_commands(ctx):
    embed = discord.Embed(
        title="📋 사용 가능한 명령어 목록",
        description="현재 이 봇에서 사용할 수 있는 주요 명령어들입니다.",
        color=discord.Color.orange()  # Orange color bar
    )

    embed.add_field(
        name="💰 코인 관련",
        value=(
            "`!btc` — 비트코인 가격 조회\n"
            "`!eth` — 이더리움 가격 조회\n"
            "`!xrp` — 리플 가격 조회\n"
            "`!doge` — 도지코인 가격 조회"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙️ 시스템 정보",
        value=(
            "`!cpu` — CPU 사용률 조회\n"
            "`!ram` — RAM 사용량 조회\n"
            "`!disk` — 디스크 사용량 조회\n"
            "`!info` — 전체 시스템 요약 정보\n"
            "`!uptime` — 서버 업타임 확인\n"
            "`!sys` — 기타 시스템 조회"

        ),
        inline=False
    )

    embed.set_footer(text="Designed by TK_Dominance😎System Bot v0.2")

    await ctx.send(embed=embed)

# 존재하지 않는 명령 처리
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ '{ctx.message.content}' 명령은 존재하지 않습니다.")
    else:
        raise error


bot.run(os.getenv("DISCORD_TOKEN"))


