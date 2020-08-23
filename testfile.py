import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import random
import os

client = discord.Client()

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

url = 'https://docs.google.com/spreadsheets/d/1WI7W0KjLaebqQUuLpf7BqhPYEKnLa2ppNLEiXasOce4/edit#gid=0'

current_time = lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=9)


def is_moderator(member):
    return "운영진" in map(lambda x: x.name, member.roles)


@client.event
async def on_ready():
    global Harang
    await client.wait_until_ready()
    game = discord.Game("어몽어스와 연애")
    print("login: Amongus Main")
    print(client.user.name)
    print(client.user.id)
    print("---------------")
    await client.change_presence(status=discord.Status.online, activity=game)


async def get_spreadsheet(ws_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name("HarangTest-130d0649c09f.json", scope)
    auth = gspread.authorize(creds)

    if creds.access_token_expired:
        auth.login()

    try:
        worksheet = auth.open_by_url(url).worksheet(ws_name)
    except gspread.exceptions.APIError:
        print("API Error")
        return
    return worksheet


async def has_role(member, role):
    return role in map(lambda x: x.name, member.roles)


async def get_member_by_battletag(battletag):
    global harang
    harang = client.get_guild(406688488671543297)

    for member in harang.members:
        try:
            if member.nick.endswith(battletag):
                return member
        except:
            continue


async def get_opener(self):
    ws = await get_spreadsheet('temp1')
    return ws.cell(1, 1).value


async def is_spreadsheet_empty(sheetname):
    ws = await get_spreadsheet(sheetname)
    if ws.cell(1, 1).value is "":
        return True
    else:
        return False


@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel

    print('{} / {}: {}'.format(channel, author, content))

    if message.content.startswith(">>"):
        content = message.content
        content = content.split(">>")
        content = content[1]

        if content == '':
            return

        if content.startswith("어몽어스개최"):
            opener = content.split(" ")[0]
            time = content.split(" ")[1]
            desc = content[12:]

            # 개최될 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is False:
                await message.channel.send("이미 개최될 어몽어스가 있습니다")
                return

            ws = await get_spreadsheet('temp2')
            ws.resize(rows=1, cols=1)
            ws.append_row([author.mention])

            ws = await get_spreadsheet('temp1')
            ws.resize(rows=4, cols=1)

            ws.append_row([author.mention])
            ws.append_row([time])
            ws.append_row([desc])

            await message.channel.send("@everyone \n {} 어몽어스가 열립니다. \n 주최자 : {}".format(time, author.mention))
            return

        if content == "어몽어스신청":
            # 예정된 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is True:
                await message.channel.send("오늘은 예정된 어몽어스가 없습니다")
                return

            # 스크림 신청
            ws = await get_spreadsheet('temp2')
            try:
                ws.find(author.mention)
            except:
                ws.append_row([author.mention])
                await message.channel.send("어몽어스 신청이 완료되었습니다")
                return

            await message.channel.send("이미 신청되었습니다 >>어몽어스 로 명단에서 본인 이름을 확인하세요")
            return

        if content == "어몽어스신청취소":
            # 예정된 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is True:
                await message.channel.send("오늘은 예정된 어몽어스가 없습니다")
                return

            # 스크림 신청 취소
            ws = await get_spreadsheet('temp2')
            try:
                ws.find(author.mention)
            except:
                await message.channel.send("신청되지 않은 참가자입니다.")
                return

            cell = ws.find(author.mention)
            row = cell.row
            ws.delete_rows(row)

            await message.channel.send("어몽어스 신청 취소가 완료되었습니다")
            return

        if content == "어몽어스":
            # 예정된 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is True:
                await message.channel.send("오늘은 예정된 어몽어스가 없습니다")
                return

            # 스크림 정보를 보여주기 위한 작업
            ws = await get_spreadsheet('temp1')

            opener = ws.cell(1, 1).value
            time = ws.cell(2, 1).value
            desc = ws.cell(3, 1).value

            ws = await get_spreadsheet('temp2')
            participant = ws.col_values(1)

            # list에 \n 추가
            for index, value in enumerate(participant):
                participant[index] = participant[index] + '\n'

            # list to string and replace "," to ""
            participant = ','.join(participant)
            participant = participant.replace(",", "")

            counts = ws.row_count

            embed = discord.Embed(title="오늘의 어몽어스", description=desc, color=12745742)
            embed.add_field(name="시간", value=time, inline=False)
            embed.add_field(name="개최자", value=opener, inline=False)
            embed.add_field(name="참가자 {}명".format(counts), value=participant, inline=False)

            await channel.send(embed=embed)
            return

        if content.startswith("개최자변경"):
            # 예정된 스크림이 있는지 확인
            print("개최자 변경")
            result = await is_spreadsheet_empty('temp1')
            # is empty
            if result is True:
                await message.channel.send("오늘은 예정된 어몽어스가 없습니다")
                return

            # 새로운 개최자로 변경
            newopener = content.split(" ")[1]

            ws = await get_spreadsheet('temp1')
            ws.update_cell(1, 1, newopener)
            await message.channel.send("개최자 업데이트 완료")
            return

        if content.startswith("시간변경"):
            # 예정된 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is True:
                await message.channel.send("오늘은 예정된 어몽어스가 없습니다")
                return

            # 새로운 시간으로 업데이트
            newtime = content.split(" ")[1]

            ws = await get_spreadsheet('temp1')
            ws.update_cell(2, 1, newtime)
            await message.channel.send("시간 업데이트 완료")
            return

        if content == "어몽어스종료":
            # 종료할 스크림이 있는지 확인
            result = await is_spreadsheet_empty('temp1')
            if result is True:
                await message.channel.send("종료할 어몽어스가 없습니다")
                return

            # 종료 커맨드 날린 author 가 개최자 혹은 운영자인지 확인
            if author.mention != (await get_opener(author.mention)) and (not is_moderator(author)):
                await message.channel.send("어몽어스 개최자 또는 운영진만 내전을 종료할 수 있습니다.")
                return

            # 스크림 종료하는 작업 준비
            ws = await get_spreadsheet('temp1')
            ws.clear()
            ws.resize(rows=4, cols=1)

            ws = await get_spreadsheet('temp2')
            ws.resize(rows=1, cols=1)
            ws.clear()

            await message.channel.send("@everyone \n 어몽어스가 종료되었습니다")
            return

        if content == "어몽어스봇":
            embed = discord.Embed(title=":robot:어몽어스봇:robot:", description="어몽어스봇 온라인!", color=3066993)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/708306592465944591/723914634116988988/3b53af51b6da75d2.png")
            await channel.send(embed=embed)
            return


access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
