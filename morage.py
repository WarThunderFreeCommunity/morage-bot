#--------------------------------------------------------------------------
#Импорты
import os
from dotenv import load_dotenv
load_dotenv()
#--------------------------------------------------------------------------
import disnake as dis
from disnake import Embed
from disnake.ext import commands
from colorama import Fore
import disnake
import asyncio
import sqlite3
import time
import datetime
from disnake import Button, ButtonStyle,SelectOption,SelectMenu,Embed
from random import randint
from pymongo import MongoClient
#--------------------------------------------------------------------------
bot = commands.Bot(command_prefix='C!', intents = disnake.Intents.all())
#--------------------------------------------------------------------------
#База Данных
#--------------------------------------------------------------------------
cluster = MongoClient("...")
moragedb = cluster.Morage.guilds
con = sqlite3.connect('base.db')
cursor = con.cursor()
#--------------------------------------------------------------------------
#Бд ивенты
#--------------------------------------------------------------------------

@bot.event
async def on_guild_remove(guild):
    moragedb.find_one_and_delete({"guild" : guild.id})

#--------------------------------------------------------------------------
#Логи
#--------------------------------------------------------------------------
@bot.event
async def on_guild_join(guild):
  guild = bot.get_guild(guild.id)

  integrations = await guild.integrations()

  for integration in integrations:
      if isinstance(integration, disnake.BotIntegration):
          if integration.application.user.name == bot.user.name:
              bot_inviter = integration.user
              post = {
                "guild" : guild.id, 
                "added" : bot_inviter.id,
                "logging" : "None",
                "channel" : "",
                "commander" : ""
              } 
              moragedb.insert_one(post)
              break
#--------------------------------------------------------------------------
#Эвенты
#--------------------------------------------------------------------------
@bot.event
async def on_ready():
  guilds = len(bot.guilds)
  print(f'{Fore.GREEN}Бот [ {bot.user} ] был запущен')
  print(f'{Fore.BLUE}https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot')
  cursor.execute( """CREATE TABLE IF NOT EXISTS users (
    server_id INT,
    bots_id TEXT,
    ride_mode INT
  )""")
  con.commit()
  for guild in bot.guilds:
    post = {
      "guild" : guild.id, 
      "logging" : "None",
      "channel" : "",
      "commander" : ""
    } 
    if moragedb.count_documents({"guild" : guild.id}) == 0:
      moragedb.insert_one(post)
#--------------------------------------------------------------------------
#Системное
#--------------------------------------------------------------------------
global bans
bans = {}
global time_bans
time_bans = {}
global bans_list
bans_list = {}
#--------------------------------------------------------------------------
global mutes
mutes = {}
global time_mutes
time_mutes = {}
global mutes_list
mutes_list = {}
#--------------------------------------------------------------------------
global channels
channels = {}
global time_channels
time_channels = {}
global channels_list
channels_list = {}
#--------------------------------------------------------------------------
global channels_create
channels_create = {}
global time_channels_create
time_channels_create = {}
global channels_create_list
channels_create_list = {}
#--------------------------------------------------------------------------
global everyones
everyones = {}
global time_everyones
time_everyones = {}
#--------------------------------------------------------------------------
global kicks
kicks = {}
global time_kicks
time_kicks = {}
#--------------------------------------------------------------------------
global roles_delete
roles_delete = {}
global time_roles_delete
time_roles_delete = {}
global roles_delete_list
roles_delete_list = {}
#--------------------------------------------------------------------------
global roles_create
roles_create = {}
global time_roles_create
time_roles_create = {}
global roles_create_list
roles_create_list = {}
#--------------------------------------------------------------------------
@bot.slash_command(name='info-bot',description='Посмотреть информацию о боте')
async def get_info(ctx):
  servers = len(bot.guilds)
  member = []
  for guild in bot.guilds:
    for members in guild.members:
      member.append(members.name)
  embed=Embed(title=None, description=f"**<:stats:1077905979653496852> | Статистика — {bot.user.name}**\n\n Задержка бота: ` {bot.latency * 1000:.0f} `\n Всего серверов: ` {servers} `\n Всего участников: ` {len(member)} `\n\n**<:info:1077905983860383804> | Информация  о боте**\n\n Дата создания: <t:1663513920:R>\n Версия бота: `1.0.0a`\n Версия Python: `3.11.2`\n Библиотека: `disnake 2.8.0`\n\n**<:useful:1077909503045017650> | Полезное: **\n\n> Используя кнопки ниже, вы можете посетить наши ресурсы, где можно ознакомиться с документацией бота, советами, или просто получить помощь.",color=0x2f3136)
  embed.set_thumbnail(url=bot.user.display_avatar)
  embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
  comp = [
    disnake.ui.Button(style=ButtonStyle.url,label='Website',url='https://morage.xyz'),
    disnake.ui.Button(style=ButtonStyle.url,label='Support',url='https://discord.gg/jCKxrhZGdm'),
    disnake.ui.Button(style=ButtonStyle.url,label='Invite',url='https://morage.xyz/invite')


  ]
  await ctx.send(embed=embed,components=comp)

#--------------------------------------------------------------------------
#Командер бота
#-------------------------------------------------------------------------- 

@bot.slash_command(name="bot-manager", description="Добавить / убрать роль управляющего ботом")
async def botcommander(inter : disnake.ApplicationCommandInteraction, роль : disnake.Role, действие : str = commands.Param(choices=["убрать", "назначить"], description="Выберите действие")):
  if действие == "убрать":
    if moragedb.find_one({"guild" : inter.guild.id})['commander'] == "":
      await inter.send(embed = disnake.Embed(title="<:erorr:1077885070582493254> | Ошибка", description="Вы хотите удалить роль командующего ботом, но она отсутсует.", colour=0x2f3136))  
    else:
      moragedb.update_one({"guild" : inter.guild.id}, 
      {"$set" : {"comander" : ""}})      
      embed = disnake.Embed(title="<:sucess:1077884984834142288> | Успешно", description=f"Вы добавили роль <@&{роль.id}> в список командующих ботом, теперь пользователи с этой ролью смогут выполнять все команды.",  colour=0x2f3136)
      embed.set_thumbnail(url = inter.user.display_avatar)
      await inter.send(embed=embed,ephemeral=1)  
      if moragedb.find_one({"guild" : inter.guild.id})['logging'] == "None":
        pass
      else:
        ch = bot.get_channel(int(moragedb.find_one({"guild" : inter.guild.id})['channel']))
        embed = disnake.Embed(title="<:edit:1078569880703467611> | Командующий изменён", colour=0x2f3136)
        embed.set_thumbnail(url = bot.user.avatar)
        embed.add_field(name="> Роль:", value=f"```{роль.id}```", inline=1)
        embed.add_field(name="> Добавил:", value=f"```{inter.author.id}```", inline=1)
        embed.add_field(name="> Действие:", value=f"```Добавление участника в белый список```", inline=0)
        embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>", inline=1)
        embed.add_field(name="> Канал:", value=f"<#{inter.channel.id}>", inline=1)
        embed.set_thumbnail(url = bot.user.display_avatar)
        await ch.send(embed = embed)       
#--------------------------------------------------------------------------
#Белый Список
#--------------------------------------------------------------------------
@bot.slash_command(name='wl',description='Покажет или добавит человека в вайт лист.')
async def wl(ctx, участник = None):
  if ctx.author.id == 966398661380669480 or ctx.author.id == 873222233751969822 or ctx.author.id == ctx.guild.owner.id or moragedb.find_one({"guild" : ctx.guild.id})['added']:
    if участник is None:
      if cursor.execute(f"SELECT bots_id FROM users WHERE server_id = {ctx.guild.id}").fetchone() == None:
        embed = disnake.Embed(title=" | Ошибка", description=f"{ctx.author.mention}, список аккаунтов находящихся в **Белом — списке** пуст.")
        embed.set_thumbnail(url=ctx.author.display_avatar)
        embed.set_footer(text="Добавьте пользователей используя /wl")
        await ctx.send(embed = embed, ephemeral = 1)
      else:
        list_bot = cursor.execute(f"SELECT bots_id FROM users WHERE server_id = {ctx.guild.id}").fetchone()[0]
        list_bot = list_bot.split(', ')
        for x in range(len(list_bot)):
          list_bot[x] = f'<:emoji_1:1045251058320015420> <@{list_bot[x]}>'
        if '<@ >' in list_bot:
          list_bot.remove('<@ >')
        elif '<@>' in list_bot: 
          list_bot.remove('<@>')
        list_bot = '\n'.join(list_bot)
        await ctx.send(f'<:emoji_1:1045251026430742588>Список аккаунтов:<:emoji_1:1045251026430742588> \n{list_bot} ',ephemeral = True)
        if list_bot == "<@>":
          embed = disnake.Embed(title=" | Ошибка", description=f"{ctx.author.mention}, список аккаунтов находящихся в **Белом — списке** пуст.")
          embed.set_thumbnail(url=ctx.author.display_avatar)
          embed.set_footer(text="Добавьте пользователей используя /wl")
          await ctx.send(embed = embed, ephemeral = 1)
    else:
      участник = участник.replace('<@', '').replace('>', '').replace(' ', '')
      if cursor.execute(f"SELECT bots_id FROM users WHERE server_id = {ctx.guild.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ({ctx.guild.id}, '{участник}', 0)")
        con.commit()
        embed = Embed(title = "<:sucess:1077884984834142288> | Успешно", description=f'Участник успешно добавлен в **Белый — список**',colour=0x2f3136)
        embed.set_thumbnail(url = ctx.author.display_avatar)
        embed.add_field(name="> Участник:", value=f"```{участник}```", inline=1)
        embed.add_field(name="> Действие:", value=f"```Добавление```")
        embed.set_footer(text="Используйте /wl_remove, чтобы убрать пользователя из белого списка.")
        await ctx.send(embed = embed,ephemeral = True)
      else:
        base = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(ctx.guild.id)).fetchone()[0]
        base = base.split(', ')
        if участник in base:
            embed2 = disnake.Embed(title="<:erorr:1077885070582493254> | Ошибка", description=f"{ctx.author.mention}, Вы пытаетесь добавить в **Белый — список** пользователя, который из без того уже находиться там.", colour=0x2f3136)
            embed2.set_thumbnail(url=ctx.author.display_avatar)
            embed2.set_footer(text="Вы можете удалить пользователя, используя /wl_remove")
            await ctx.send(embed = embed2,ephemeral = True)
            pass
        else:
          base.append(f'{участник}')
          base = ', '.join(base)
          cursor.execute("UPDATE users SET bots_id = '{}' WHERE server_id = {}".format(base, ctx.guild.id))
          con.commit()
          embed = Embed(title = "<:sucess:1077884984834142288> | Успешно", description=f'Участник успешно добавлен в **Белый — список**',colour=0x2f3136)
          embed.set_thumbnail(url = ctx.author.display_avatar)
          embed.add_field(name="> Участник:", value=f"```{участник}```", inline=1)
          embed.add_field(name="> Действие:", value=f"```Добавление```")
          embed.set_footer(text="Используйте /wl_remove, чтобы убрать пользователя из белого списка.")
          await ctx.send(embed = embed,ephemeral = True)
          if moragedb.find_one({"guild" : ctx.guild.id})['logging'] == "None":
            pass
          else:
            ch = bot.get_channel(int(moragedb.find_one({"guild" : ctx.guild.id})['channel']))
            embed = disnake.Embed(title="<:edit:1078569880703467611> | Вайт — лист изменён", colour=0x2f3136)
            embed.set_thumbnail(url = bot.user.avatar)
            embed.add_field(name="> Участник:", value=f"```{участник}```", inline=1)
            embed.add_field(name="> Добавил:", value=f"```{ctx.author.id}```", inline=1)
            embed.add_field(name="> Действие:", value=f"```Добавление участника в белый список```", inline=0)
            embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>", inline=1)
            embed.add_field(name="> Канал:", value=f"<#{ctx.channel.id}>", inline=1)
            embed.set_thumbnail(url = bot.user.display_avatar)
            # embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
            await ch.send(embed = embed)               
  else:
    embed4 = disnake.Embed(title=f"<:erorr:1077885070582493254> | Ошибка", description=f"{ctx.author.mention}, чтобы использовать эту команду вам необходимо быть **Создателем** данного Discord — сервера, или тот кто добавил бота на данный сервер.", colour=0x36393F)
    embed4.set_footer(text=f"Свяжитесь с владельцем сервера.")
    embed4.set_thumbnail(url = ctx.author.display_avatar)
    await ctx.send(embed = embed4,ephemeral = True)
#--------------------------------------------------------------------------
@bot.slash_command(name= 'wl_remove',description='удалить человека из белого списка.')
async def wl_remove(ctx, участник = None):
      if ctx.author.id == 966398661380669480 or ctx.author.id == 873222233751969822 or ctx.author.id == ctx.guild.owner.id or moragedb.find_one({"guild" : ctx.guild.id})['added']:
        if участник is None:
          embed5 = Embed(title = "<:erorr:1077885070582493254> | Ошибка", description=f'{ctx.author.mention}, Вы не указали участника, которого хотите удалить из **Белого — списка**.',colour=0x2f3136)
          embed5.set_thumbnail(url = ctx.author.display_avatar)
          await ctx.send(embed = embed5,ephemeral = True)
        else:
          if cursor.execute(f"SELECT bots_id FROM users WHERE server_id = {ctx.guild.id}").fetchone() is None:
            embed6 = Embed(title=f"<:erorr:1077885070582493254> | Ошибка", description=f'{ctx.author.mention}, Вы хотите удалить пользователя из **Белого — списка**, но он пуст.',colour=0x2f3136)
            embed6.set_thumbnail(url = ctx.author.display_avatar)            
            await ctx.send(embed = embed6,ephemaral = True)
          else:
            участник = участник.replace('<@', '').replace('>', '').replace(' ', '')
            base = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(ctx.guild.id)).fetchone()[0]
            base = base.split(', ')
            try:
              base.remove(f'{участник}')
            except:
              pass
            base = ', '.join(base)
            cursor.execute("UPDATE users SET bots_id = '{}' WHERE server_id = {}".format(base, ctx.guild.id))
          con.commit()
          embed = disnake.Embed(title="<:sucess:1077884984834142288> | Успешно", description="Участник успешно убран из **Белого — списка**" ,colour=0x36393F)
          embed.set_thumbnail(url = ctx.author.display_avatar)
          embed.add_field(name="> Участник:", value=f"```{участник}```", inline=1)
          embed.add_field(name="> Действие:", value="```Удаление```")
          embed.set_footer(text="Используйте /wl, чтобы добавить пользователя в белый список.")
          await ctx.send(embed = embed, ephemeral=1)
          if moragedb.find_one({"guild" : ctx.guild.id})['logging'] == "None":
            pass
          else:
            ch = bot.get_channel(int(moragedb.find_one({"guild" : ctx.guild.id})['channel']))
            embed = disnake.Embed(title="<:edit:1078569880703467611> | Вайт — лист изменён", colour=0x2f3136)
            embed.set_thumbnail(url = bot.user.avatar)
            embed.add_field(name="> Участник:", value=f"```{участник}```", inline=1)
            embed.add_field(name="> Удалил:", value=f"```{ctx.author.id}```", inline=1)
            embed.add_field(name="> Действие:", value=f"```Удаление участника из белого списка```", inline=0)
            embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>", inline=1)
            embed.add_field(name="> Канал:", value=f"<#{ctx.channel.id}>", inline=1)
            embed.set_thumbnail(url = bot.user.display_avatar)
            # embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
            await ch.send(embed = embed)              
#--------------------------------------------------------------------------
      else:
        embed4 = disnake.Embed(title=f"<:erorr:1077885070582493254> | Ошибка", description=f"{ctx.author.mention}, чтобы использовать эту команду вам необходимо быть **Создателем** данного Discord — сервера, или тот кто добавил бота на данный сервер.", colour=0x36393F)
        embed4.set_footer(text=f"Свяжитесь с владельцем сервера.")
        embed4.set_thumbnail(url = ctx.author.display_avatar)
        await ctx.send(embed = embed4,ephemeral = True)
#--------------------------------------------------------------------------
# @bot.slash_command(name='база',description='Получить Базу Данных',guild_ids=[1044931892727787601])
# async def base(ctx):
#       embed12 = Embed(description=f'База получена',colour=0x2f3136)
#       embed12.set_author(name=f'Успешно',icon_url=str(f'https://media.discordapp.net/attachments/1030714278459752508/1037800788057149440/998972474635075677-1.png'),)
#       await ctx.send(embed = embed12)
#       if ctx.author.id == 640528346144309268 or ctx.author.id == 947586139911491635:
#         await ctx.send(file=disnake.File('ZloyKolt.db'))
#       else:
#         embed14 = Embed(description=f'**`Вы не обладатель бота!`**',colour=0x2f3136)
#         embed14.set_author(name=f'Ошибка',icon_url=str(f'https://media.discordapp.net/attachments/1030714278459752508/1037800787734175864/998972502518800423-1.png'),)
#         await ctx.send(embed = embed14,ephemeral = True)
#--------------------------------------------------------------------------
# Конфиг логов
#--------------------------------------------------------------------------
@bot.slash_command(name="logging", description="Назначте / Выключите канал логирования.")
@commands.has_permissions(administrator=True)
async def logging(inter:disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title=f"Настройка — {inter.guild.name}", description=f"{inter.author.mention}, Используя меню выбора ниже вы можете выбрать, что желаете сделать.",colour=0x36393F)
    embed.set_thumbnail(url = inter.user.display_avatar)
    await inter.send(embed=embed, ephemeral=1, components=disnake.ui.StringSelect(placeholder="Выберите необходимое вам действие", custom_id="меню",options=[
                disnake.SelectOption(
                        label="Выключить логгирование", description="Выключает логгирование на вашем сервере", emoji="<:icons_Wrong:859388130636988436>"
                    ),
                    disnake.SelectOption(
                        label="Назначить канал", description="Назначае канал логгирования на вашем сервере", emoji="<:icons_edit:859388129625374720>"
                    ),               
                ]
            ))
@logging.error
async def logging_erorr(self, ctx, error):
    embed = disnake.Embed(
        title=None,
        description=f"{ctx.author.mention}, Вы пытаетесь открыть меню конфигурации логгирования сервера, но для этого вам необходимо право `Администратор`, свяжитесь с администрацией сервера для решения проблемы.",
        colour=0x36393F
    )
    embed.set_thumbnail(url = ctx.author.display_avatar)
    await ctx.send(embed = embed, ephemeral = True) 
@bot.listen("on_dropdown")
async def logging_listener(inter: disnake.MessageInteraction):
    if inter.values[0] == "Назначить канал":
        class ChannelChoose(disnake.ui.Modal):
            def __init__(self):
                components = [
                    disnake.ui.TextInput(
                        label="Введите айди канала ниже",
                        placeholder="Например: 1074725666433544303",
                        custom_id="channel",
                        style=disnake.TextInputStyle.short,
                        max_length=21,
                        min_length=17
                    )
                ]
                super().__init__(title="Изменение канала для логгирования", components=components, timeout=120)
            async def callback(self, inter: disnake.ModalInteraction):
                embed = disnake.Embed(title="<:sucess:1077884984834142288> | Успешно", description=f"{inter.user.mention}, Вы успешно изменили канал логгирования, теперь данный канал будет использоваться для логгирования информации о **всех** действиях нашего бота.", colour=0x36393F)
                embed.set_thumbnail(url = inter.user.display_avatar)
                for key, value in inter.text_values.items():
                    embed.add_field(
                        name="> Канал логгирования:",
                        value=f"<#{value[:1024]}>",
                        inline=False,
                    )
                await inter.response.send_message(embed=embed, ephemeral=1)
                if moragedb.find_one({"guild" : inter.guild.id})['logging'] == "None":
                  moragedb.update_one({"guild" : inter.guild.id}, 
                  {"$set" : {"channel" : int(value[:1024]), "logging" : "True"}})  
                else:                  
                  moragedb.update_one({"guild" : inter.guild.id}, 
                  {"$set" : {"channel" : int(value[:1024]), "logging" : "True"}})
                  # embed = disnake.Embed(title="<:edit:1077678930951164102> | Изменение сохранено", description=f"{inter.user.mention}, Вы успешно отключили логгирование на этом сервере.", colour=0x36393F)
                  # embed.set_thumbnail(url=inter.user.display_avatar)
                  # await inter.send(embed = embed, ephemeral=1)
                  try:
                    log_channel = inter.guild.get_channel(int(moragedb.find_one({"guild" : inter.guild.id})['channel']))
                    embed = disnake.Embed(title="<:edit:1077678930951164102> | Изменение Лога", description=f"Данный канал **будет** использоваться для логгирования всех действий бота на сервере.", colour=0x36393F)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Назначил:", value=f"{inter.user.mention}", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_footer(text="Теперь этот канал будет использоваться для логов")
                    await log_channel.send(embed = embed)
                  except:
                    pass                   
                                  
            async def on_error(self, error: Exception, inter: disnake.ModalInteraction):
                embed = disnake.Embed(
                    title=" | Ошибка",
                    description=f"{inter.user.mention}, что - то пошло не так, убедитесь что канал с таким айди существует на *этом* сервере, если же вы уверены что такой канал существует, и при этом вы видите это сообщение, пожалуйста, свяжииесь с разработчиком бота.",
                    colour=0x36393F
                )
                embed.set_thumbnail(url = inter.user.display_avatar)
                await inter.send(embed = embed, ephemeral=True)
        await inter.response.send_modal(modal = ChannelChoose())
    if inter.values[0] == "Выключить логгирование":
        embed = disnake.Embed(title="<:edit:1077678930951164102> | Изменение сохранено", description=f"{inter.user.mention}, Вы успешно отключили логгирование на этом сервере.", colour=0x36393F)
        embed.set_thumbnail(url=inter.user.display_avatar)
        await inter.send(embed = embed, ephemeral=1)
        try:
          log_channel = inter.guild.get_channel(int(moragedb.find_one({"guild" : inter.guild.id})['channel']))
          embed = disnake.Embed(title="<:edit:1077678930951164102> | Изменение Лога", description=f"Данный канал больше **не будет** использоваться как канал для логгирования действий бота.", colour=0x36393F)
          embed.set_thumbnail(url = bot.user.avatar)
          embed.add_field(name="> Отменил:", value=f"{inter.user.mention}", inline=1)
          embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
          embed.set_footer(text="Ранее этот канал использовался для логов")
          await log_channel.send(embed = embed)
        except:
          pass
        moragedb.update_one({"guild" : inter.guild.id}, 
        {"$set" : {"channel" : "", "logging" : "None"}})          
#--------------------------------------------------------------------------
@bot.event
async def on_guild_channel_delete(channel):
    global channels
    global channels_list
    global time_channels
    connectiont = True
    async for entry in channel.guild.audit_logs(limit=10):
      if connectiont:
        if entry.action == disnake.AuditLogAction.channel_delete and entry.target.id == channel.id:
          connectiont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              check = time_channels[f'{entry.user.id}_{channel.guild.id}']
            except:
              time_channels[f'{entry.user.id}_{channel.guild.id}'] = int(time.time())
            try:
              check = channels[f'{entry.user.id}_{channel.guild.id}']
            except:
              channels[f'{entry.user.id}_{channel.guild.id}'] = 1
            try:
              check = channels_list[f'{entry.user.id}_{channel.guild.id}']
              channels_list[f'{entry.user.id}_{channel.guild.id}'].append(channel)
            except:
              channels_list[f'{entry.user.id}_{channel.guild.id}'] = [channel]
            if int(time.time()) - time_channels[f'{entry.user.id}_{channel.guild.id}'] < 15 and entry.user.bot or int(time.time()) - time_channels[f'{entry.user.id}_{channel.guild.id}'] < 60 and not entry.user.bot:
              if channels[f'{entry.user.id}_{channel.guild.id}'] >= 4:
                try:
                  await channel.guild.ban(entry.user, reason = f'AntiCrash - Удаление каналов')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    change_channel = channels_list[f'{entry.user.id}_{channel.guild.id}'][0]
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Удаление каналов```", inline=1)
                    embed.add_field(name="> канал:", value=f"```Неизветсный, возможно удалён.```", inline=1)
                    embed.add_field(name="> Действие:", value="```Канал восстановлен, участник забанен.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    await channel.send(embed = embed)
                except:
                  pass
                loop = True
                popi = 0
                while loop:
                  try:
                    change_channel = channels_list[f'{entry.user.id}_{channel.guild.id}'][0]
                    if change_channel.type == disnake.ChannelType.text:
                      await channel.guild.create_text_channel(
                        name = change_channel.name,
                        category = change_channel.category,
                        position = change_channel.position,
                        topic = change_channel.topic,
                        slowmode_delay = change_channel.slowmode_delay,
                        nsfw = change_channel.nsfw,
                        overwrites = change_channel.overwrites,
                        reason = f'AntiCrash - Действие крашера {entry.user.name}'
                      )
                    elif change_channel.type == disnake.ChannelType.voice:
                      await channel.guild.create_voice_channel(
                        name = change_channel.name,
                        category = change_channel.category,
                        position = change_channel.position,
                        overwrites = change_channel.overwrites,
                        user_limit = change_channel.user_limit,
                        reason = f'AntiCrash - Действие крашера {entry.user.name}'
                      )
                    elif change_channel.type == disnake.ChannelType.category:
                      await channel.guild.create_category(
                        name = change_channel.name,
                        position = change_channel.position,
                        overwrites = change_channel.overwrites,
                        reason = f'AntiCrash - Действие крашера {entry.user.name}'
                      )
                  except:
                    pass
                  try:
                    change_channel = channels_list[f'{entry.user.id}_{channel.guild.id}'][0]
                    channels_list[f'{entry.user.id}_{channel.guild.id}'].pop(0)
                  except:
                    popi += 1
                    if popi == 2:
                      loop = False
#--------------------------------------------------------------------------
                channels[f'{entry.user.id}_{channel.guild.id}'] = 0
              else:
                channels[f'{entry.user.id}_{channel.guild.id}'] = channels[f'{entry.user.id}_{channel.guild.id}'] + 1
            else:
              time_channels[f'{entry.user.id}_{channel.guild.id}'] = int(time.time())
              channels[f'{entry.user.id}_{channel.guild.id}'] = 1
#--------------------------------------------------------------------------
@bot.event
async def on_guild_channel_create(channel):
    global channels_create
    global channels_create_list
    global time_channels_create
    connectiont = True
    async for entry in channel.guild.audit_logs(limit=10):
      if connectiont:
        if entry.action == disnake.AuditLogAction.channel_create and entry.target.id == channel.id:
          connectiont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              check = time_channels_create[f'{entry.user.id}_{channel.guild.id}']
            except:
              time_channels_create[f'{entry.user.id}_{channel.guild.id}'] = int(time.time())
            try:
              check = channels_create[f'{entry.user.id}_{channel.guild.id}']
            except:
              channels_create[f'{entry.user.id}_{channel.guild.id}'] = 1
            try:
              channels_create_list[f'{entry.user.id}_{channel.guild.id}'].append(channel)
            except:
              channels_create_list[f'{entry.user.id}_{channel.guild.id}'] = [channel]
            if int(time.time()) - time_channels_create[f'{entry.user.id}_{channel.guild.id}'] < 15 and entry.user.bot or int(time.time()) - time_channels_create[f'{entry.user.id}_{channel.guild.id}'] < 60 and not entry.user.bot:
              if channels_create[f'{entry.user.id}_{channel.guild.id}'] >= 4:
                try:
                  await channel.guild.ban(entry.user, reason = 'AntiCrash - Создание каналов')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Создание каналов```", inline=1)
                    embed.add_field(name="> канал:", value=f"```Неизвестный, возможно удален.```", inline=1)
                    embed.add_field(name="> Действие:", value="```Канал удалён, участник забанен.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)                  
                except:
                  pass
                loop = True
                while loop:
                  try:
                    await channels_create_list[f'{entry.user.id}_{channel.guild.id}'][0].delete(reason = f'AntiCrash - Действие крашера {entry.user.name}')
                  except:
                    pass
                  try:
                    channels_create_list[f'{entry.user.id}_{channel.guild.id}'].pop(0)
                  except:
                    loop = False
                channels_create[f'{entry.user.id}_{channel.guild.id}'] = 0
              else:
                channels_create[f'{entry.user.id}_{channel.guild.id}'] = channels_create[f'{entry.user.id}_{channel.guild.id}'] + 1
            else:
              time_channels_create[f'{entry.user.id}_{channel.guild.id}'] = int(time.time())
              channels_create[f'{entry.user.id}_{channel.guild.id}'] = 1
#--------------------------------------------------------------------------
@bot.event
async def on_member_join(member):
    if cursor.execute("SELECT ride_mode FROM users WHERE server_id = {}".format(member.guild.id)).fetchone() is None:
      ride_mode = 0
    else:
      ride_mode = cursor.execute("SELECT ride_mode FROM users WHERE server_id = {}".format(member.guild.id)).fetchone()[0]
    if ride_mode == 1:
      try:
        await member.kick(reason = 'AntiRide mode ON')
      except:
        pass
    else:
      if member.bot:
        if member.public_flags.verified_bot or member.public_flags.verified_bot_developer:
          pass
        else:
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{member.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              await member.ban(reason = 'AntiCrash - Не верифицированный бот')
            except:
              pass
            connectiont = True
            async for entry in member.guild.audit_logs(limit=10):
              if connectiont:
                if entry.action == disnake.AuditLogAction.bot_add and entry.target.id == member.id:
                  connectiont = False
                  crash = False
                  if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone() is None:
                    crash = True
                  else:
                    list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone()[0]
                    list_bot = list_bot.split(', ')
                    list_bot.append(f'{bot.user.id}')
                    if f'{entry.user.id}' in list_bot:
                      pass
                    else:
                      crash = True
                  if crash:
                    try:
                      await entry.user.ban(reason = 'AntiCrash - Приглашение краш бота')
                      if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                        pass
                      else:
                        channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                        embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                        embed.set_thumbnail(url = bot.user.avatar)
                        embed.add_field(name="> Причина:", value="```Добавление неверифицированного бота```", inline=1)
                        embed.add_field(name="> Бот:", value=f"```Неизвестный, возможно забанен.```", inline=1)
                        embed.add_field(name="> Действие:", value="```Бот забанен, участник забанен.```", inline=0)
                        embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                        embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                        embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                        await channel.send(embed = embed)
                    except:
                      pass
#--------------------------------------------------------------------------
@bot.event
async def on_member_ban(guild, user):
    global bans
    global bans_list
    global time_bans
    connectiont = True
    await asyncio.sleep(0.5)
    async for entry in guild.audit_logs(limit=10):
      if connectiont:
        if entry.action == disnake.AuditLogAction.ban and int(entry.target.id) == int(user.id):
          connectiont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              check = time_bans[f'{entry.user.id}_{guild.id}']
            except:
              time_bans[f'{entry.user.id}_{guild.id}'] = int(time.time())
            try:
              check = bans[f'{entry.user.id}_{guild.id}']
              bans[f'{entry.user.id}_{guild.id}'] = bans[f'{entry.user.id}_{guild.id}'] + 1
            except:
              bans[f'{entry.user.id}_{guild.id}'] = 1
            try:
              check = bans_list[f'{entry.user.id}_{guild.id}']
              bans_list[f'{entry.user.id}_{guild.id}'].append(user)
            except:
              bans_list[f'{entry.user.id}_{guild.id}'] = [user]
            if int(time.time()) - time_bans[f'{entry.user.id}_{guild.id}'] < 15 and entry.user.bot or int(time.time()) - time_bans[f'{entry.user.id}_{guild.id}'] < 60 and not entry.user.bot:
              if bans[f'{entry.user.id}_{guild.id}'] >= 4:
                try:
                  await guild.ban(entry.user, reason = 'AntiCrash - Выдача банов')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Выдача банов```", inline=1)
                    embed.add_field(name="> Причина банов:", value=f"```Неизвестна```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен, забаненный разбанен.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)                  
                except:
                  pass
                loop = True
                while loop:
                  try:
                    baned_user = bans_list[f'{entry.user.id}_{guild.id}'][0]
                  except:
                    pass
                  try:
                    await guild.unban(baned_user, reason = f'AntiCrash - Действие крашера {entry.user.name}')
                  except:
                    pass
                  try:
                    invites = await guild.invites()
                    if invites == []:
                      link = await guild.text_channels[0].create_invite()
                    else:
                      link = invites[0]
                    await baned_user.create_dm()
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Возвращение", description=f"Вы были забанены по неизвестной причине, вы были разбанены анти - крашем, и можете вернуться на сервер нажав [здесь]({link})",colour=0x2f3136)
                    await baned_user.send(f'Вы были разбанены на этом сервере: {link}')
                  except:
                    pass
                  try:
                    bans_list[f'{entry.user.id}_{guild.id}'].pop(0)
                  except:
                    loop = False
                bans[f'{entry.user.id}_{guild.id}'] = 0
            else:
              time_bans[f'{entry.user.id}_{guild.id}'] = int(time.time())
#--------------------------------------------------------------------------
@bot.event
async def on_message(message):
    global everyones
    global time_everyones
    await bot.process_commands(message)
    if '@everyone' in message.content.lower() or '@here' in message.content.lower():
      if message.author.guild_permissions.mention_everyone or message.author.bot:
        crash = False
        if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(message.guild.id)).fetchone() is None:
          crash = True
        else:
          list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(message.guild.id)).fetchone()[0]
          list_bot = list_bot.split(', ')
          list_bot.append(f'{bot.user.id}')
          if f'{message.author.id}' in list_bot:
            pass
          else:
            crash = True
        if crash:
          try:
            check = everyones[f'{message.author.id}_{message.guild.id}']
          except:
            everyones[f'{message.author.id}_{message.guild.id}'] = 1
          try:
            check = time_everyones[f'{message.author.id}_{message.guild.id}']
          except:
            time_everyones[f'{message.author.id}_{message.guild.id}'] = int(time.time())
          if int(time.time())-time_everyones[f'{message.author.id}_{message.guild.id}'] < 15 and message.author.bot or int(time.time())-time_everyones[f'{message.author.id}_{message.guild.id}'] < 60 and not message.author.bot:
            if everyones[f'{message.author.id}_{message.guild.id}'] >= 2:
              try:
                await message.guild.ban(user = message.author, delete_message_days = 1, reason = 'AntiCrash - Многократное использование @everyone')
                if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                  pass
                else:
                  channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                  embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                  embed.set_thumbnail(url = bot.user.avatar)
                  embed.add_field(name="> Причина:", value="```Упоминание @everyone```", inline=1)
                  embed.add_field(name="> Причина:", value=f"```Неизвестна```", inline=1)
                  embed.add_field(name="> Действие:", value="```Участник забанен, сообщения очищены.```", inline=0)
                  embed.add_field(name="> Участник", value=f"<@{message.user.id}>", inline=1)
                  embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                  embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                  await channel.send(embed = embed)      
              except:
                try:
                  webs = await message.guild.webhooks()
                  for web in webs:
                    if web.id == message.webhook_id:
                      await message.guild.ban(user = message.guild.get_member(web.user.id), delete_message_days = 1, reason = 'AntiCrash - Использование @everyone через вебхук')
                      await web.delete()
                except disnake.errors.Forbidden:
                  pass
              everyones[f'{message.author.id}_{message.guild.id}'] = 0
            else:
              everyones[f'{message.author.id}_{message.guild.id}'] = everyones[f'{message.author.id}_{message.guild.id}'] + 1
          else:
            time_everyones[f'{message.author.id}_{message.guild.id}'] = int(time.time())
            everyones[f'{message.author.id}_{message.guild.id}'] = 1
#--------------------------------------------------------------------------
@bot.event
async def on_guild_role_delete(role):
    global roles_delete
    global time_roles_delete
    global roles_delete_list
    connectiont = True
    async for entry in role.guild.audit_logs(limit=10):
      if connectiont:
        if entry.action == disnake.AuditLogAction.role_delete and entry.target.id == role.id:
          connectiont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(role.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(role.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              roles_delete[f'{entry.user.id}_{role.guild.id}'] += roles_delete[f'{entry.user.id}_{role.guild.id}'] + 1
            except:
              roles_delete[f'{entry.user.id}_{role.guild.id}'] = 1
            try:
              check = time_roles_delete[f'{entry.user.id}_{role.guild.id}']
            except:
              time_roles_delete[f'{entry.user.id}_{role.guild.id}'] = int(time.time())
            try:
              check = roles_delete_list[f'{entry.user.id}_{role.guild.id}']
              roles_delete_list[f'{entry.user.id}_{role.guild.id}'].append(role)
            except:
              roles_delete_list[f'{entry.user.id}_{role.guild.id}'] = [role]
            if int(time.time())-time_roles_delete[f'{entry.user.id}_{role.guild.id}'] < 30:
              if roles_delete[f'{entry.user.id}_{role.guild.id}'] >= 3:
                try:
                  await entry.user.ban(reason = 'AntiCrash - Удаление ролей')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Удаление ролей```", inline=1)
                    embed.add_field(name="> Роли:", value=f"```Неизвестны```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен, роли восстановлены.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)      
                except:
                  pass
                loop = True
                while loop:
                  try:
                    role_ch = roles_delete_list[f'{entry.user.id}_{role.guild.id}'][0]
                    new_role = await role_ch.guild.create_role(
                      name = role_ch.name,
                      permissions = role_ch.permissions,
                      color = role_ch.color,
                      hoist = role_ch.hoist,
                      mentionable = role_ch.mentionable,
                      reason = f'AntiCrash - Действие крашера {entry.user.name}'
                    )
                    await role.guild.edit_role_positions(positions = {new_role: role_ch.position})
                  except:
                    pass
                  for role_member in role_ch.members:
                    try:
                      await role_member.add_roles(new_role, reason = f'AntiCrash - Действие крашера {entry.user.name}')
                    except:
                      pass
                  try:
                    roles_delete_list[f'{entry.user.id}_{role.guild.id}'].pop(0)
                  except:
                    loop = False
                roles_delete[f'{entry.user.id}_{role.guild.id}'] = 0
            else:
              time_roles_delete[f'{entry.user.id}_{role.guild.id}'] = int(time.time())
              roles_delete[f'{entry.user.id}_{role.guild.id}'] = 1
#--------------------------------------------------------------------------
@bot.event
async def on_guild_role_create(role):
    global roles_create
    global time_roles_create
    global roles_create_list
    connectiont = True
    async for entry in role.guild.audit_logs(limit=10):
      if connectiont:
        if entry.action == disnake.AuditLogAction.role_create and entry.target.id == role.id:
          connectiont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(role.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(role.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              roles_create[f'{entry.user.id}_{role.guild.id}'] += roles_create[f'{entry.user.id}_{role.guild.id}'] + 1
            except:
              roles_create[f'{entry.user.id}_{role.guild.id}'] = 1
            try:
              check = time_roles_create[f'{entry.user.id}_{role.guild.id}']
            except:
              time_roles_create[f'{entry.user.id}_{role.guild.id}'] = int(time.time())
            try:
              check = roles_create_list[f'{entry.user.id}_{role.guild.id}']
              roles_create_list[f'{entry.user.id}_{role.guild.id}'].append(role)
            except:
              roles_create_list[f'{entry.user.id}_{role.guild.id}'] = [role]
            if int(time.time())-time_roles_create[f'{entry.user.id}_{role.guild.id}'] < 30:
              if roles_create[f'{entry.user.id}_{role.guild.id}'] >= 3:
                try:
                  await entry.user.ban(reason = 'AntiCrash - Создания ролей')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Создание ролей```", inline=1)
                    embed.add_field(name="> Роли:", value=f"```Неизвестны```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен, роли удалены.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)   

                except:
                  pass
                loop = True
                while loop:
                  try:
                    role_ch = roles_create_list[f'{entry.user.id}_{role.guild.id}'][0]
                    new_role = await role_ch.guild.delete_role(
                      name = role_ch.name,
                      permissions = role_ch.permissions,
                      color = role_ch.color,
                      hoist = role_ch.hoist,
                      mentionable = role_ch.mentionable,
                      reason = f'AntiCrash - Действие крашера {entry.user.name}'
                    )
                    await role.guild.edit_role_positions(positions = {new_role: role_ch.position})
                  except:
                    pass
                  for role_member in role_ch.members:
                    try:
                      await role_member.add_roles(new_role, reason = f'AntiCrash - Действие крашера {entry.user.name}')
                    except:
                      pass
                  try:
                    roles_create_list[f'{entry.user.id}_{role.guild.id}'].pop(0)
                  except:
                    loop = False
                roles_create[f'{entry.user.id}_{role.guild.id}'] = 0
            else:
              time_roles_create[f'{entry.user.id}_{role.guild.id}'] = int(time.time())
              roles_create[f'{entry.user.id}_{role.guild.id}'] = 1
#--------------------------------------------------------------------------
@bot.event
async def on_guild_role_update(before, after):
    if before.permissions.administrator:
      pass
    else:
      if after.permissions.administrator:
        connectiont = True
        async for entry in before.guild.audit_logs(limit=10):
          if connectiont:
            if entry.action == disnake.AuditLogAction.role_update and entry.target.id == before.id:
              cont = False
              crash = False
              if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone() is None:
                crash = True
              else:
                list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone()[0]
                list_bot = list_bot.split(', ')
                list_bot.append(f'{bot.user.id}')
                if f'{entry.user.id}' in list_bot:
                  pass
                else:
                  crash = True
              if crash:
                try:
                  await entry.user.ban(reason = 'AntiCrash - Выдача право администратора для роли')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Изменение прав```", inline=1)
                    embed.add_field(name="> Изменение:", value=f"```Выдача права Администратор```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен, роль восстановлена.```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)                     
                except:
                  pass
                perm = after.permissions
                perm.administrator = False
                try:
                  await after.edit(permissions = perm)
                except:
                  pass
#--------------------------------------------------------------------------
@bot.event
async def on_member_update(before, after):
    global mutes
    global mutes_list
    global time_mutes
    if before.roles != after.roles and len(before.roles) < len(after.roles):
      cont = True
      async for entry in before.guild.audit_logs(limit=10):
        if cont:
          if entry.action == disnake.AuditLogAction.member_role_update and entry.target.id == before.id:
            cont = False
            crash = False
            if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone() is None:
              crash = True
            else:
              list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone()[0]
              list_bot = list_bot.split(', ')
              list_bot.append(f'{bot.user.id}')
              if f'{entry.user.id}' in list_bot:
                pass
              else:
                crash = True
            if crash:
              change_roles = after.roles
              for role in before.roles:
                try:
                  change_roles.remove(role)
                except:
                  pass
              kick = False
              for role in change_roles:
                if role.permissions.administrator:
                  try:
                    await entry.target.remove_roles(role)
                  except:
                    pass
                  kick = True
              if kick:
                try:
                  await entry.user.ban(reason = f'AntiCrash - Выдача роли с админкой для {entry.target.name}')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Выдача ролей```", inline=1)
                    embed.add_field(name="> Изменение:", value=f"```Выдана роль с правом Администратор```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен, получатель забанен.```", inline=0)
                    embed.add_field(name="> Получатель:", value=f"{entry.target.mention}")
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)   
                except:
                  pass
                try:
                  await entry.target.ban(reason = f'AntiCrash - Получение роли с админкой от {entry.user.name}')
                except:
                  pass
    elif before.current_timeout is None and after.current_timeout is not None:
      cont = True
      async for entry in before.guild.audit_logs(limit=10):
        if cont:
          if entry.action == disnake.AuditLogAction.member_update and entry.target.id == before.id:
            cont = False
            crash = False
            if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone() is None:
              crash = True
            else:
              list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(before.guild.id)).fetchone()[0]
              list_bot = list_bot.split(', ')
              list_bot.append(f'{bot.user.id}')
              if f'{entry.user.id}' in list_bot:
                pass
              else:
                crash = True
            if crash:
              try:
                check = time_mutes[f'{entry.user.id}_{before.guild.id}']
              except:
                time_mutes[f'{entry.user.id}_{before.guild.id}'] = int(time.time())
              try:
                check = mutes[f'{entry.user.id}_{before.guild.id}']
              except:
                mutes[f'{entry.user.id}_{before.guild.id}'] = 1
              try:
                check = mutes_list[f'{entry.user.id}_{before.guild.id}']
              except:
                mutes_list[f'{entry.user.id}_{before.guild.id}'] = [before]
              if int(time.time()) - time_mutes[f'{entry.user.id}_{before.guild.id}'] < 15 and entry.user.bot or int(time.time()) - time_mutes[f'{entry.user.id}_{before.guild.id}'] < 60 and not entry.user.bot:
                if mutes[f'{entry.user.id}_{before.guild.id}'] >= 4:
                  try:
                    await entry.user.ban(reason = f'AntiCrash - Выдача мута для {entry.target.name}')
                    if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                      pass
                    else:
                      channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                      embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                      embed.set_thumbnail(url = bot.user.avatar)
                      embed.add_field(name="> Причина:", value="```Выдача тайм-аута```", inline=1)
                      embed.add_field(name="> Изменение:", value=f"```Тайм-аут для участника```", inline=1)
                      embed.add_field(name="> Действие:", value="```Участник забанен, голос возвращен.```", inline=0)
                      embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                      embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                      embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                      await channel.send(embed = embed)   
                  except:
                    pass
                  for muted_member in mutes_list[f'{entry.user.id}_{before.guild.id}']:
                    try:
                      await muted_member.timeout(until = None, reason = f'AntiCrash - Жертва крашера {entry.user.name}')
                    except:
                      pass
                  time_mutes.pop(f'{entry.user.id}_{before.guild.id}')
                  mutes[f'{entry.user.id}_{before.guild.id}'] = 0
                  mutes_list.pop(f'{entry.user.id}_{before.guild.id}')
                else:
                  mutes[f'{entry.user.id}_{before.guild.id}'] = mutes[f'{entry.user.id}_{before.guild.id}'] + 1
                  mutes_list[f'{entry.user.id}_{before.guild.id}'].append(before)
              else:
                time_mutes[f'{entry.user.id}_{before.guild.id}'] = int(time.time())
                mutes[f'{entry.user.id}_{before.guild.id}'] = 1
                mutes_list[f'{entry.user.id}_{before.guild.id}'] = [before]
#--------------------------------------------------------------------------
@bot.event
async def on_webhooks_update(channel):
    cont = True
    async for entry in channel.guild.audit_logs(limit=10):
      if cont:
        if entry.action == disnake.AuditLogAction.webhook_create:
          cont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              await entry.user.ban(reason = 'AntiCrash - Создание вебхука')
            except:
              pass
            try:
              await entry.target.delete(reason = f'AntiCrash - Действие крашера {entry.user.name}')
            except:
              pass
        elif entry.action == disnake.AuditLogAction.webhook_delete:
          cont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(channel.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              await entry.user.ban(reason = 'AntiCrash - Удаление вебхука')
              if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                pass
              else:
                channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                embed.set_thumbnail(url = bot.user.avatar)
                embed.add_field(name="> Причина:", value="```Создание вебхука```", inline=1)
                embed.add_field(name="> Изменение:", value=f"```Создан вебхук```", inline=1)
                embed.add_field(name="> Действие:", value="```Участник забанен, вебхук удалён```", inline=0)
                embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                await channel.send(embed = embed)   
            except:
              pass
            try:
              await channel.create_webhook(
                name = entry.before.name,
                reason = f'AntiCrash - Действие крашера {entry.user.name}'
              )
            except:
              pass
#--------------------------------------------------------------------------
@bot.event
async def on_member_remove(member):
    global kicks
    global time_kicks
    cont = True
    async for entry in member.guild.audit_logs(limit=10):
      if cont:
        if entry.action == disnake.AuditLogAction.kick and entry.target.id == member.id:
          cont = False
          crash = False
          if cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone() is None:
            crash = True
          else:
            list_bot = cursor.execute("SELECT bots_id FROM users WHERE server_id = {}".format(member.guild.id)).fetchone()[0]
            list_bot = list_bot.split(', ')
            list_bot.append(f'{bot.user.id}')
            if f'{entry.user.id}' in list_bot:
              pass
            else:
              crash = True
          if crash:
            try:
              kicks[f'{entry.user.id}_{member.guild.id}'] += kicks[f'{entry.user.id}_{member.guild.id}'] + 1
            except:
              kicks[f'{entry.user.id}_{member.guild.id}'] = 1
#--------------------------------------------------------------------------
            try:
              check = time_kicks[f'{entry.user.id}_{member.guild.id}']
            except:
              time_kicks[f'{entry.user.id}_{member.guild.id}'] = int(time.time())
#--------------------------------------------------------------------------
            if int(time.time())-time_kicks[f'{entry.user.id}_{member.guild.id}'] < 30:
              if kicks[f'{entry.user.id}_{member.guild.id}'] >= 3:
                try:
                  await entry.user.ban(reason = f'AntiCrash - кик / чистка людей')
                  if moragedb.find_one({"guild" : channel.guild.id})['logging'] == "None":
                    pass
                  else:
                    channel = bot.get_channel(int(moragedb.find_one({"guild" : channel.guild.id})['channel']))
                    embed = disnake.Embed(title="<:nuke:1077854768166346752> | Сервер защищён", colour=0x2f3136)
                    embed.set_thumbnail(url = bot.user.avatar)
                    embed.add_field(name="> Причина:", value="```Кик / Чистка учасников```", inline=1)
                    embed.add_field(name="> Изменение:", value=f"```Участники кикнуты```", inline=1)
                    embed.add_field(name="> Действие:", value="```Участник забанен```", inline=0)
                    embed.add_field(name="> Участник", value=f"<@{entry.user.id}>", inline=1)
                    embed.add_field(name="> Время:", value=f"<t:{int(time.time())}:R>")
                    embed.set_image(url="https://media.discordapp.net/attachments/938792278737162281/988575297056145449/EmptyLittleShit.png")
                    await channel.send(embed = embed)   
                  
                except:
                  pass
                kicks[f'{entry.user.id}_{member.guild.id}'] = 0
            else:
              time_kicks[f'{entry.user.id}_{member.guild.id}'] = int(time.time())
              kicks[f'{entry.user.id}_{member.guild.id}'] = 1
#--------------------------------------------------------------------------
@wl.error
async def wl_error(ctx,error):
    print(error)
    pass

@wl_remove.error
async def wl_rem_er(ctx,error):
  print(error)
  pass
#--------------------------------------------------------------------------
@bot.on_error
async def on_error(error):
  pass
#--------------------------------------------------------------------------
async def start_loop():
    count = 0
    while True:
      if count < 86400:
        await asyncio.sleep(10800)
        count += 10800
      else:
        await asyncio.sleep(360)
        count += 360
      await bot.get_channel(973537182394490930).send(file=disnake.File('base.db'))
#--------------------------------------------------------------------------
#Токен
#--------------------------------------------------------------------------
bot.run(os.getenv('TOKEN'))
#--------------------------------------------------------------------------