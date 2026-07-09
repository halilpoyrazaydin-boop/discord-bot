import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

import os
TOKEN = os.environ.get("TOKEN", "MTUxNTg5NzI3MzQ1MDYzMTE4OA.GJQaiR.sDm1x-QW5immsE46AoYJjxyfgNqAg4hYe0dkaE")
ROBLOX_COOKIE = os.environ.get("ROBLOX_COOKIE", "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaBBAEGAEiHAoEZHVpZBIUMTU1MjYyMDg3MDA5MjI2ODU3MTUoAw.QhQXkucYEq8JeChDDF6hTv32fQXX0Tc_RYvvV8oMRtjAamtSFMlKMDWaznUUg6JSEsV3yc8wZIMNz3q1f5disClFsSA4fT6JUB-xHf3QaSbTIpmf0ZMJcRv-jbaFP0NX6q6jmHf7cwuu8qrZlOLCkOZ9Cv7o6_3geZhJCdI9oitS6zrB1eePolDHn6GSxv6gfXqBpbEjF-tz7abR0g1w0CzfgivegMOS7vs_5cBh-Ts1lIBfONSiKKg4tzqnbSuxWeaLhjkmJEH1v2XZZdbavm45CcDqXPCH0_5m6m4myQRq4pK00xuNIdZZN98WdTTZaI4uoQOYwK926yJy1sdqQ9KRM_DrCd79a6FzKHL71BBuOQyJqNtm1f6rZCkw-QEzMXjlczbKiqeyZraTyBCJq9nSqAOyzh-6wQO6-hoU8-ZjWZhJu-qrE7Ot-vNfhTxM6vGoISwQ154gZbxh4ahhoocdr26H3HUxXg-rsPX_hWLY7nid9ILhe4hWOIC4wyEzSRB4CBEWU7UlVeagD_59awmKT14BB_bGt-SD-DPsKyfjVGIHhvNEVL94aeX5Og3v1Tcy1zH6z9p0NrNLZ8V-Xo71QH1PcCrsBN_au_nx9m2Gy3f3EPPPpovNh2-lP76GQg7YFzEDT0tBJGs2Y2aZx0nZCJYCyy4i6Lc9ABIPxW8NOXQusTqFf3T9rnEeFPXPdpS-6gX67eBDEiE52h7O9WzQ013--WgsCiHtpqO8k3lxoXHp9aCWHT0fL0Hhx5nPtbn9SV8FeeE3do1jc87Sne0aYJ8KpfnuSILgGxUfoYp5IFHSrize_SIXAB-AI6ugmxIXls--cdkHs8n5tTzOfbM8U9OZJ3E4NY8nxrrD5C5psYZObHATVGWwjXnHfjV_AwQ6ybLTRbi9MJCE8CIgkh5CnsNtdcpFC-KhEwDCXrA.56dcoO3WHiDGIYZVUOKrkoGM1MI")
ROBLOX_GROUP_ID = 972348115
LOG_KANAL_ID = 1519328796275380325

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} olarak giris yapildi!")

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Komutlar guncellendi!")

# ─── ROBLOX FONKSİYONLARI ───────────────

async def csrf_al():
    headers = {"Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}"}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://auth.roblox.com/v2/logout", headers=headers) as r:
            return r.headers.get("x-csrf-token", "")

async def kullanici_id_al(username: str):
    async with aiohttp.ClientSession() as s:
        async with s.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username]}) as r:
            data = await r.json()
            if data.get("data"):
                return data["data"][0]["id"]
    return None

async def grup_rutbeleri_al():
    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://groups.roblox.com/v1/groups/{ROBLOX_GROUP_ID}/roles") as r:
            data = await r.json()
            return sorted([x for x in data.get("roles", []) if x["rank"] > 0], key=lambda x: x["rank"])

async def kullanici_rutbe_al(user_id: int):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://groups.roblox.com/v2/users/{user_id}/groups/roles") as r:
            if r.status == 200:
                data = await r.json()
                for g in data.get("data", []):
                    if g["group"]["id"] == ROBLOX_GROUP_ID:
                        return {"rank": g["role"]["rank"], "name": g["role"]["name"], "id": g["role"]["id"]}
    return {"rank": 0, "name": "Uye Degil", "id": 0}

async def rutbe_degistir(user_id: int, role_id: int):
    headers = {"Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}", "Content-Type": "application/json"}
    headers["X-CSRF-TOKEN"] = await csrf_al()
    async with aiohttp.ClientSession() as s:
        async with s.patch(f"https://groups.roblox.com/v1/groups/{ROBLOX_GROUP_ID}/users/{user_id}", headers=headers, json={"roleId": role_id}) as r:
            return r.status == 200, await r.text()

# ─── RÜTBE SEÇİM MENÜSÜ ─────────────────

class RutbeMenu(discord.ui.Select):
    def __init__(self, rutbeler, kullanici_adi, hedef_id, sebep, islem):
        self.kullanici_adi = kullanici_adi
        self.hedef_id = hedef_id
        self.sebep = sebep
        self.islem = islem
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=f"Rank: {r['rank']}")
            for r in rutbeler[:25]
        ]
        super().__init__(placeholder="Rutbe sec...", options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        basari, hata = await rutbe_degistir(self.hedef_id, role_id)
        secilen = next((o.label for o in self.options if o.value == str(role_id)), "Bilinmiyor")
        if basari:
            basliklar = {"ver": "Rutbe Verildi", "terfi": "Rutbe Terfi", "tenzil": "Rutbe Tenzil"}
            renkler = {"ver": discord.Color.green(), "terfi": discord.Color.green(), "tenzil": discord.Color.orange()}
            embed = discord.Embed(title=basliklar.get(self.islem, "Rutbe Degistirildi"), color=renkler.get(self.islem, discord.Color.blue()))
            embed.add_field(name="Kullanici", value=self.kullanici_adi, inline=True)
            embed.add_field(name="Yeni Rutbe", value=secilen, inline=True)
            embed.add_field(name="Islemi Yapan", value=interaction.user.mention, inline=True)
            embed.add_field(name="Sebep", value=self.sebep, inline=False)
            embed.timestamp = discord.utils.utcnow()
            await interaction.response.edit_message(content="Rutbe basariyla degistirildi!", view=None)
            log_kanal = interaction.guild.get_channel(LOG_KANAL_ID)
            if log_kanal:
                await log_kanal.send(embed=embed)
            else:
                await interaction.channel.send(embed=embed)
        else:
            await interaction.response.edit_message(content=f"Hata: {hata}", view=None)

class RutbeView(discord.ui.View):
    def __init__(self, rutbeler, kullanici_adi, hedef_id, sebep, islem):
        super().__init__(timeout=60)
        self.add_item(RutbeMenu(rutbeler, kullanici_adi, hedef_id, sebep, islem))

# ─── SLASH KOMUTU ───────────────────────

async def rutbe_autocomplete(interaction: discord.Interaction, current: str):
    rutbeler = await grup_rutbeleri_al()
    return [
        app_commands.Choice(name=r["name"], value=r["name"])
        for r in rutbeler if current.lower() in r["name"].lower()
    ][:25]

async def rutbe_komutu(interaction: discord.Interaction, kullanici_adi: str, sebep: str, islem: str, rutbe_adi: str = ""):
    await interaction.response.defer(ephemeral=True)
    hedef_id = await kullanici_id_al(kullanici_adi)
    if not hedef_id:
        await interaction.followup.send(f"'{kullanici_adi}' adli kullanici bulunamadi!", ephemeral=True)
        return
    rutbeler = await grup_rutbeleri_al()
    if not rutbeler:
        await interaction.followup.send("Rutbeler alinamadi!", ephemeral=True)
        return
    mevcut = await kullanici_rutbe_al(hedef_id)

    # Eğer rutbe_adi verilmişse direkt ver
    if rutbe_adi:
        hedef_rutbe = next((r for r in rutbeler if r["name"].lower() == rutbe_adi.lower()), None)
        if not hedef_rutbe:
            await interaction.followup.send(f"'{rutbe_adi}' adli rutbe bulunamadi!", ephemeral=True)
            return
        basari, hata = await rutbe_degistir(hedef_id, hedef_rutbe["id"])
        if basari:
            basliklar = {"ver": "Rutbe Verildi", "terfi": "Rutbe Terfi", "tenzil": "Rutbe Tenzil"}
            renkler = {"ver": discord.Color.green(), "terfi": discord.Color.green(), "tenzil": discord.Color.orange()}
            embed = discord.Embed(title=basliklar.get(islem, "Rutbe Degistirildi"), color=renkler.get(islem, discord.Color.blue()))
            embed.add_field(name="Kullanici", value=kullanici_adi, inline=True)
            embed.add_field(name="Yeni Rutbe", value=hedef_rutbe["name"], inline=True)
            embed.add_field(name="Islemi Yapan", value=interaction.user.mention, inline=True)
            embed.add_field(name="Sebep", value=sebep, inline=False)
            embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(content="Rutbe basariyla degistirildi!", ephemeral=True)
            log_kanal = interaction.guild.get_channel(LOG_KANAL_ID)
            if log_kanal:
                await log_kanal.send(embed=embed)
            else:
                await interaction.channel.send(embed=embed)
        else:
            await interaction.followup.send(f"Hata: {hata}", ephemeral=True)
        return

    # Rutbe verilmemişse menü göster
    if islem == "terfi":
        secenekler = [r for r in rutbeler if r["rank"] > mevcut["rank"]]
    elif islem == "tenzil":
        secenekler = [r for r in rutbeler if r["rank"] < mevcut["rank"]]
    else:
        secenekler = rutbeler
    if not secenekler:
        await interaction.followup.send("Uygun rutbe yok!", ephemeral=True)
        return
    metin = f"**{kullanici_adi}** icin rutbe sec:\nMevcut: **{mevcut['name']}**"
    await interaction.followup.send(content=metin, view=RutbeView(secenekler, kullanici_adi, hedef_id, sebep, islem), ephemeral=True)

@bot.tree.command(name="rutbe-degistir", description="Roblox grubunda kisiye rutbe ver")
@app_commands.describe(kullanici_adi="Roblox kullanici adi", sebep="Sebep", rutbe_adi="Rutbe adi (yazmaya basla, oneriler cikar)")
@app_commands.autocomplete(rutbe_adi=rutbe_autocomplete)
@app_commands.checks.has_permissions(manage_roles=True)
async def rutbe_ver(interaction: discord.Interaction, kullanici_adi: str, sebep: str = "Belirtilmedi", rutbe_adi: str = ""):
    await rutbe_komutu(interaction, kullanici_adi, sebep, "ver", rutbe_adi)

@bot.tree.command(name="rutbe-terfi", description="Roblox grubunda kisiye terfi ver")
@app_commands.describe(kullanici_adi="Roblox kullanici adi", sebep="Sebep", rutbe_adi="Rutbe adi (yazmaya basla, oneriler cikar)")
@app_commands.autocomplete(rutbe_adi=rutbe_autocomplete)
@app_commands.checks.has_permissions(manage_roles=True)
async def rutbe_terfi(interaction: discord.Interaction, kullanici_adi: str, sebep: str = "Belirtilmedi", rutbe_adi: str = ""):
    await rutbe_komutu(interaction, kullanici_adi, sebep, "terfi", rutbe_adi)

@bot.tree.command(name="rutbe-tenzil", description="Roblox grubunda kisiyi tenzil et")
@app_commands.describe(kullanici_adi="Roblox kullanici adi", sebep="Sebep", rutbe_adi="Rutbe adi (yazmaya basla, oneriler cikar)")
@app_commands.autocomplete(rutbe_adi=rutbe_autocomplete)
@app_commands.checks.has_permissions(manage_roles=True)
async def rutbe_tenzil(interaction: discord.Interaction, kullanici_adi: str, sebep: str = "Belirtilmedi", rutbe_adi: str = ""):
    await rutbe_komutu(interaction, kullanici_adi, sebep, "tenzil", rutbe_adi)

bot.run(TOKEN)
