import sys
import asyncio
import discord
import csv

# --- asyncio hatalarını bastır ---
def suppress_asyncio_ssl_error(exc_type, exc_value, tb):
    if exc_type.__name__ == "RuntimeError" and "Event loop is closed" in str(exc_value):
        return  # kullanıcıya gösterme
    sys.__excepthook__(exc_type, exc_value, tb)
sys.excepthook = suppress_asyncio_ssl_error

# Windows için event loop fix
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Kullanıcıdan bilgileri al ---
TOKEN = input("Discord tokenini gir: ").strip()
GUILD_ID = input("Mesajları kopyalamak istediğin SUNUCU ID'sini gir: ").strip()
CHANNEL_ID = input("Belirli bir kanal ID'si girmek ister misin? (boş bırak = tüm kanallar): ").strip()

client = discord.Client()

async def fetch_messages_from_channel(channel):
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        messages.append([msg.author.name, msg.content])
    return messages

@client.event
async def on_ready():
    print(f"\n[+] Self-bot giriş yaptı: {client.user}")
    
    guild = client.get_guild(int(GUILD_ID))
    if not guild:
        print("[!] Sunucu bulunamadı! ID doğru mu?")
        await client.close()
        return

    all_messages = []

    if CHANNEL_ID:
        channel = guild.get_channel(int(CHANNEL_ID))
        if not channel:
            print("[!] Kanal bulunamadı! ID doğru mu?")
            await client.close()
            return
        
        print(f"[>] {guild.name} -> {channel.name} kanalından mesajlar çekiliyor...")
        msgs = await fetch_messages_from_channel(channel)
        all_messages.extend(msgs)
    else:
        print(f"[+] Kanal seçilmedi → {guild.name} sunucusundaki TÜM text kanalları çekilecek.")
        for channel in guild.text_channels:
            print(f"[>] {guild.name} -> {channel.name} kanalından mesajlar çekiliyor...")
            msgs = await fetch_messages_from_channel(channel)
            all_messages.extend(msgs)

    file_name = f"messages_{guild.id}.csv"
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["author", "message"])
        writer.writerows(all_messages)

    print(f"\n[+] {len(all_messages)} mesaj kaydedildi: {file_name}")
    await asyncio.sleep(1)  # düzgün kapanması için beklet
    try:
        await client.close()
    except RuntimeError:
        pass  # kapanış hatasını bastır

client.run(TOKEN)
