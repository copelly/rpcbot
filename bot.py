import disnake, asyncio
from disnake.ext import commands
import json
import random
import sqlite3
from datetime import datetime, timedelta
import requests

intents = disnake.Intents.default()
intents.message_content = True  # 메시지 내용 인텐트 활성화
intents.members = True  # 멤버 인텐트 활성화
intents.presences = True  # 프레즌스 인텐트 활성화
bot = commands.Bot(command_prefix="!", intents=intents)

token = "" # 봇토큰
WEBHOOK_URL = ""

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, dict) or 'tokens' not in data:
                return {"tokens": []}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tokens": []}

def save_config(data):
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_active_rpc_count():
    """현재 활성 RPC 사용자 수 반환"""
    try:
        config = load_config()
        return sum(1 for t in config.get('tokens', []) if t.get('active'))
    except:
        return 0

async def update_bot_status():
    """봇의 활동 상태 업데이트"""
    while True:
        try:
            count = get_active_rpc_count()
            activity = disnake.Activity(type=disnake.ActivityType.watching, name=f"{count}명이 RPC 사용중")
            await bot.change_presence(status=disnake.Status.online, activity=activity)
            print(f"✅ 봇 상태 업데이트: {count}명이 RPC 사용중 (온라인)")
        except Exception as e:
            print(f"상태 업데이트 오류: {e}")
        await asyncio.sleep(60)  # 60초마다 업데이트


@bot.event
async def on_connect():
    """연결 직후 즉시 온라인 상태로 설정"""
    try:
        count = get_active_rpc_count()
        activity = disnake.Activity(type=disnake.ActivityType.watching, name=f"{count}명이 RPC 사용중")
        await bot.change_presence(status=disnake.Status.online, activity=activity)
        print("on_connect: presence set to online")
    except Exception as e:
        print(f"on_connect 오류: {e}")

def send_webhook(user_id, token_info, expiration_date):
    """webhook으로 등록 정보 전송"""
    try:
        embed = {
            "content": "🎉 새로운 RPC 라이센스 등록!",
            "embeds": [
                {
                    "title": "RPC 활성화",
                    "description": f"새로운 사용자가 RPC를 등록했습니다.",
                    "color": 3447003,
                    "fields": [
                        {
                            "name": "사용자 ID",
                            "value": f"`{user_id}`",
                            "inline": True
                        },
                        {
                            "name": "토큰",
                            "value": f"`{token_info.get('token', 'N/A')}`" if token_info.get('token') else "미설정",
                            "inline": True
                        },
                        {
                            "name": "만료 날짜",
                            "value": f"`{expiration_date}`",
                            "inline": True
                        },
                        {
                            "name": "상태",
                            "value": f"`{token_info.get('type', 'N/A')}`",
                            "inline": True
                        },
                        {
                            "name": "접두사",
                            "value": f"`{token_info.get('prefix', 'N/A')}`",
                            "inline": True
                        },
                        {
                            "name": "활성 RPC 수",
                            "value": f"`{get_active_rpc_count()}`",
                            "inline": True
                        }
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        requests.post(WEBHOOK_URL, json=embed)
    except Exception as e:
        print(f"webhook 전송 오류: {e}")

class Setting(disnake.ui.Modal):
    def __init__(self):

        components = [
        # disnake.ui.TextInput(
        #     label="비밀번호",
        #     placeholder="",
        #     required=True,
        #     style=disnake.TextInputStyle.short,
        #     min_length=1,
        #     max_length=20,
        #     custom_id="pw",
        # ),
        disnake.ui.TextInput(
            label="토큰",
            placeholder="",
            required=True,
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=130,
            custom_id="token",
        ),
        disnake.ui.TextInput(
            label="상태",
            placeholder="",
            required=True,
            value = "PLAYING",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=10,
            custom_id="type",
        ),
        disnake.ui.TextInput(
            label="접두사",
            placeholder="",
            required=True,
            value = "!",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=4,
            custom_id="prefix",
        )
        
        ]
        super().__init__(
            title=f"RPC 기본 설정",
            custom_id="setting1",
            components=components,
            timeout=10000
        )

class Photo(disnake.ui.Modal):
    def __init__(self):

        components = [
        # disnake.ui.TextInput(
        #     label="비밀번호",
        #     placeholder="",
        #     required=True,
        #     style=disnake.TextInputStyle.short,
        #     min_length=1,
        #     max_length=20,
        #     custom_id="pw",
        # ),
        disnake.ui.TextInput(
            label="큰사진",
            placeholder="",
            required=True,
            value = "https://cdn.discordapp.com/attachments/1459772893318873190/1479729093313564825/4.png?ex=69ad189b&is=69abc71b&hm=f38f0371e7f50ba10e3703392f84b9d81f611bdf3fdbbd6ec9227f554f092b4c",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="largeimage",
        ),
        disnake.ui.TextInput(
            label="작은사진",
            placeholder="",
            required=False,
            value = "https://cdn.discordapp.com/attachments/1459772893318873190/1479729093313564825/4.png?ex=69ad189b&is=69abc71b&hm=f38f0371e7f50ba10e3703392f84b9d81f611bdf3fdbbd6ec9227f554f092b4c",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="smallimage",
        ),
        disnake.ui.TextInput(
            label="큰사진 글자",
            placeholder="",
            required=True,
            value = "코펠 RPC",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=50,
            custom_id="largete",
        ),
        disnake.ui.TextInput(
            label="작은사진 글자",
            placeholder="",
            required=False,
            value = "코펠 RPC",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=50,
            custom_id="smallte",
        )
        
        ]
        super().__init__(
            title=f"RPC 사진 설정",
            custom_id="photo1",
            components=components,
            timeout=10000
        )

class Button(disnake.ui.Modal):
    def __init__(self):

        components = [
        # disnake.ui.TextInput(
        #     label="비밀번호",
        #     placeholder="",
        #     required=True,
        #     style=disnake.TextInputStyle.short,
        #     min_length=1,
        #     max_length=20,
        #     custom_id="pw",
        # ),
        disnake.ui.TextInput(
            label="상단버튼 (이름)",
            placeholder="",
            required=False,
            value = "https://discord.gg/copel",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="button1",
        ),
        disnake.ui.TextInput(
            label="하단버튼 (이름)",
            placeholder="",
            required=False,
            value = "무료봇",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="button2",
        ),
        disnake.ui.TextInput(
            label="상단버튼 (링크)",
            placeholder="",
            required=False,
            value = "https://discord.gg/copel",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=2000,
            custom_id="button1link",
        ),
        disnake.ui.TextInput(
            label="하단버튼 (링크)",
            placeholder="",
            required=False,
            value = "https://discord.gg/copel",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=2000,
            custom_id="button2link",
        )
        
        ]
        super().__init__(
            title=f"RPC 버튼 설정",
            custom_id="button1",
            components=components,
            timeout=10000
        )

class Ment(disnake.ui.Modal):
    def __init__(self):

        components = [
        # disnake.ui.TextInput(
        #     label="비밀번호",
        #     placeholder="",
        #     required=True,
        #     style=disnake.TextInputStyle.short,
        #     min_length=1,
        #     max_length=20,
        #     custom_id="pw",
        # ),
        disnake.ui.TextInput(
            label="상단멘트",
            placeholder="",
            required=False,
            value = "기모띠한 코펠",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="details",
        ),
        disnake.ui.TextInput(
            label="하단멘트",
            placeholder="",
            required=False,
            value = "섹시한 코펠",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=300,
            custom_id="state",
        ),
        disnake.ui.TextInput(
            label="상태메시지 + 제목",
            placeholder="",
            required=False,
            value = "귀여운 코펠입니다.",
            style=disnake.TextInputStyle.short,
            min_length=1,
            max_length=20,
            custom_id="name",
        )
        
        ]
        super().__init__(
            title=f"RPC 멘트 설정",
            custom_id="ment1",
            components=components,
            timeout=10000
        )



@bot.command()
async def 등록(ctx, license: str):
    conn = sqlite3.connect('license.db')
    cursor = conn.cursor()

    # 라이센스 조회 및 date 값을 가져옴
    cursor.execute('SELECT licenses, date FROM licenses WHERE licenses=?', (license,))
    result = cursor.fetchone()

    if result:
        licenses, date = result
        current_date = datetime.now()

        # date를 정수로 변환하고 현재 날짜에 더해서 만료 날짜 계산
        expiration_date = (current_date + timedelta(days=int(date))).strftime('%Y-%m-%d')

        # 라이센스 삭제
        cursor.execute('DELETE FROM licenses WHERE licenses=?', (license,))
        conn.commit()
        conn.close()

        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"tokens": []}

        # 안전장치: 파일이 dict가 아니거나 'tokens' 키가 없으면 초기화
        if not isinstance(data, dict) or 'tokens' not in data:
            data = {"tokens": []}


        new_entry = {
            "id": str(ctx.author.id),
            # "pw": license,
            "token": "",
            "prefix": "",
            "embed": False,
            "day": expiration_date,
            "type": "",
            "details": "",
            "state": "",
            "name": "",
            "largeimage": "",
            "smallimage": "",
            "largete": "",
            "smallte": "",
            "button1": "",
            "button2": "",
            "button2link": "",
            "active": False
        }


        data['tokens'].append(new_entry)

        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # webhook으로 정보 전송
        send_webhook(ctx.author.id, new_entry, expiration_date)

        await ctx.send(f'라이센스가 등록되었습니다. 만료 날짜: {expiration_date}')
    else:
        conn.close()
        await ctx.send('없는 라이센스입니다.')

@bot.slash_command(name='패널', description='RPC에 대한 설정하기')
async def 패널(interaction: disnake.ApplicationCommandInteraction):
    # 패널은 모든 사용자가 볼 수 있도록 허용합니다.
    # (버튼 동작은 눌른 사용자의 등록 정보를 기준으로 처리됩니다.)
    
    select = disnake.ui.Select(
        custom_id="testselect",
        placeholder="설정하려는 옵션을 선택해주세요.",
        options=[
            disnake.SelectOption(label="기본설정", description="RPC 기본설정 입니다.", emoji="🔧", value="setting"),
            disnake.SelectOption(label="멘트설정", description="RPC에 뜨는 멘트관련 설정입니다.", emoji="🔧", value="ment"),
            disnake.SelectOption(label="사진설정", description="RPC에 뜨는 사진관련 설정입니다.", emoji="🔧", value="photo"),
            disnake.SelectOption(label="버튼설정", description="RPC에 뜨는 버튼관련 설정입니다.", emoji="🔧", value="button"),
        ],
    )

    class StartStopView(disnake.ui.View):
        def __init__(self, user_id):
            super().__init__(timeout=None)
            self.user_id = str(user_id)
            config = load_config()
            user_config = next((u for u in config.get('tokens', []) if u.get('id') == self.user_id), None)
            self.active = user_config.get('active', False) if user_config else False

            # 선택 박스와 시작/중지 버튼 추가
            self.add_item(select)
            self.add_item(self.StartButton(self))
            self.add_item(self.StopButton(self))

        class StartButton(disnake.ui.Button):
            def __init__(self, parent):
                super().__init__(label="시작", style=disnake.ButtonStyle.success, custom_id="rpc_start")
                self.parent_view = parent

            async def callback(self, button_inter: disnake.MessageInteraction):
                if str(button_inter.user.id) != self.parent_view.user_id:
                    await button_inter.response.send_message("본인만 시작/중지할 수 있습니다.", ephemeral=True)
                    return

                config = load_config()
                user_config = next((u for u in config.get('tokens', []) if u.get('id') == self.parent_view.user_id), None)
                if user_config:
                    user_config['active'] = True
                    save_config(config)
                    # 즉시 상태 반영 시도
                    try:
                        count = get_active_rpc_count()
                        activity = disnake.Activity(type=disnake.ActivityType.watching, name=f"{count}명이 RPC 사용중")
                        await bot.change_presence(status=disnake.Status.online, activity=activity)
                    except Exception:
                        pass
                    await button_inter.response.send_message("RPC가 시작되었습니다.", ephemeral=True)
                else:
                    await button_inter.response.send_message("등록된 정보가 없습니다.", ephemeral=True)

        class StopButton(disnake.ui.Button):
            def __init__(self, parent):
                super().__init__(label="중지", style=disnake.ButtonStyle.danger, custom_id="rpc_stop")
                self.parent_view = parent

            async def callback(self, button_inter: disnake.MessageInteraction):
                if str(button_inter.user.id) != self.parent_view.user_id:
                    await button_inter.response.send_message("본인만 시작/중지할 수 있습니다.", ephemeral=True)
                    return

                config = load_config()
                user_config = next((u for u in config.get('tokens', []) if u.get('id') == self.parent_view.user_id), None)
                if user_config:
                    user_config['active'] = False
                    save_config(config)
                    # 즉시 상태 반영 시도
                    try:
                        count = get_active_rpc_count()
                        activity = disnake.Activity(type=disnake.ActivityType.watching, name=f"{count}명이 RPC 사용중")
                        await bot.change_presence(status=disnake.Status.online, activity=activity)
                    except Exception:
                        pass
                    await button_inter.response.send_message("RPC가 중지되었습니다.", ephemeral=True)
                else:
                    await button_inter.response.send_message("등록된 정보가 없습니다.", ephemeral=True)

    view = StartStopView(interaction.user.id)
    await interaction.response.send_message(embed=disnake.Embed(title="RPC 설정", description="RPC 설정 패널입니다.", color=0x2B2D31), ephemeral=False, view=view)

@bot.event
async def on_interaction(interaction: disnake.MessageInteraction):
    if interaction.type == disnake.InteractionType.component:
        if interaction.data.custom_id == "testselect":
            selected = interaction.data.values[0]
            
            if selected == 'setting':
                await interaction.response.send_modal(Setting())
                try:
                    modal_inter: disnake.ModalInteraction = await bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == "setting1" and i.author.id == interaction.author.id,
                        timeout=10000,
                    )

                except asyncio.TimeoutError:
                    return
                
                config = load_config()
                user_id = str(interaction.user.id)
                # pw = modal_inter.text_values["pw"]
                # 디버그: 로드된 ID 목록과 현재 사용자 ID 출력 (토큰은 출력하지 않음)
                try:
                    loaded_ids = [uc.get('id') for uc in config.get('tokens', [])]
                except Exception:
                    loaded_ids = []
                print(f"[DEBUG setting] loaded_ids={loaded_ids}, user_id={user_id}")

                for user_config in config.get('tokens', []):
                    # if user_config.get("id") == user_id and user_config.get("pw") == pw:
                    print(f"[DEBUG setting] checking stored_id={user_config.get('id')}")
                    if user_config.get("id") == user_id:
                        user_config['token'] = modal_inter.text_values["token"]
                        user_config['type'] = modal_inter.text_values["type"]
                        user_config['prefix'] = modal_inter.text_values["prefix"]
                        save_config(config)
                        await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)
                        return

                # await modal_inter.send("ID 또는 비밀번호가 일치하지 않습니다.", ephemeral=True)
                # await modal_inter.send("ID가 일치하지 않습니다.", ephemeral=True)
                # await modal_inter.send("설정이 업데이트되었습니다. (ID 체크 생략)", ephemeral=True)
                await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)

            if selected == 'ment':
                await interaction.response.send_modal(Ment())
                try:
                    modal_inter: disnake.ModalInteraction = await bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == "ment1" and i.author.id == interaction.author.id,
                        timeout=10000,
                    )

                except asyncio.TimeoutError:
                    return
                
                config = load_config()
                user_id = str(interaction.user.id)
                # pw = modal_inter.text_values["pw"]
                try:
                    loaded_ids = [uc.get('id') for uc in config.get('tokens', [])]
                except Exception:
                    loaded_ids = []
                print(f"[DEBUG ment] loaded_ids={loaded_ids}, user_id={user_id}")

                for user_config in config.get('tokens', []):
                    print(f"[DEBUG ment] checking stored_id={user_config.get('id')}")
                    # if user_config.get("id") == user_id and user_config.get("pw") == pw:
                    if user_config.get("id") == user_id:
                        user_config['details'] = modal_inter.text_values["details"]
                        user_config['state'] = modal_inter.text_values["state"]
                        user_config['name'] = modal_inter.text_values["name"]
                        save_config(config)
                        await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)
                        return

                # await modal_inter.send("ID 또는 비밀번호가 일치하지 않습니다.", ephemeral=True)
                # await modal_inter.send("ID가 일치하지 않습니다.", ephemeral=True)
                await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)

            if selected == 'photo':
                await interaction.response.send_modal(Photo())
                try:
                    modal_inter: disnake.ModalInteraction = await bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == "photo1" and i.author.id == interaction.author.id,
                        timeout=10000,
                    )

                except asyncio.TimeoutError:
                    return
                
                config = load_config()
                user_id = str(interaction.user.id)
                # pw = modal_inter.text_values["pw"]
                try:
                    loaded_ids = [uc.get('id') for uc in config.get('tokens', [])]
                except Exception:
                    loaded_ids = []
                print(f"[DEBUG photo] loaded_ids={loaded_ids}, user_id={user_id}")

                for user_config in config.get('tokens', []):
                    print(f"[DEBUG photo] checking stored_id={user_config.get('id')}")
                    # if user_config.get("id") == user_id and user_config.get("pw") == pw:
                    if user_config.get("id") == user_id:
                        user_config['largeimage'] = modal_inter.text_values["largeimage"]
                        user_config['smallimage'] = modal_inter.text_values["smallimage"]
                        user_config['largete'] = modal_inter.text_values["largete"]
                        user_config['smallte'] = modal_inter.text_values["smallte"]
                        save_config(config)
                        await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)
                        return

                # await modal_inter.send("ID 또는 비밀번호가 일치하지 않습니다.", ephemeral=True)
                # await modal_inter.send("ID가 일치하지 않습니다.", ephemeral=True)
                await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)

            if selected == 'button':
                await interaction.response.send_modal(Button())
                try:
                    modal_inter: disnake.ModalInteraction = await bot.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == "button1" and i.author.id == interaction.author.id,
                        timeout=10000,
                    )

                except asyncio.TimeoutError:
                    return
                
                config = load_config()
                user_id = str(interaction.user.id)
                # pw = modal_inter.text_values["pw"]
                try:
                    loaded_ids = [uc.get('id') for uc in config.get('tokens', [])]
                except Exception:
                    loaded_ids = []
                print(f"[DEBUG button] loaded_ids={loaded_ids}, user_id={user_id}")

                for user_config in config.get('tokens', []):
                    print(f"[DEBUG button] checking stored_id={user_config.get('id')}")
                    # if user_config.get("id") == user_id and user_config.get("pw") == pw:
                    if user_config.get("id") == user_id:
                        user_config['button1'] = modal_inter.text_values["button1"]
                        user_config['button2'] = modal_inter.text_values["button2"]
                        user_config['button1link'] = modal_inter.text_values["button1link"]
                        user_config['button2link'] = modal_inter.text_values["button2link"]
                        save_config(config)
                        await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)
                        return

                # await modal_inter.send("ID 또는 비밀번호가 일치하지 않습니다.", ephemeral=True)
                # await modal_inter.send("ID가 일치하지 않습니다.", ephemeral=True)
                await modal_inter.send("설정이 업데이트되었습니다.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        await bot.tree.sync()  
        print("Commands synced successfully!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # 주기적 업데이트 시작
    if not hasattr(bot, 'status_task_started'):
        bot.status_task_started = True
        print("🟢 봇 상태 업데이트 시작...")
        bot.loop.create_task(update_bot_status())

bot.run(token)
