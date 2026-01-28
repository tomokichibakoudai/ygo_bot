import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# -------------------------
# Google Sheets 認証
# -------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 環境変数から JSON を読み込む
json_str = os.environ["GOOGLE_CREDENTIALS"]
info = json.loads(json_str)

# JSON から直接認証情報を作成
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)

gs_client = gspread.authorize(creds)
sheet = gs_client.open(os.getenv("GOOGLE_SHEET")).sheet1


# -------------------------
# Discord Bot 設定
# -------------------------
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# -------------------------
# 日本語 → 内部形式 変換
# -------------------------
def convert_first(value):
    if value in ["先", "先攻"]:
        return "first"
    if value in ["後", "後攻"]:
        return "second"
    return None

def convert_result(value):
    if value in ["〇", "○", "勝ち"]:
        return "win"
    if value in ["×", "負け"]:
        return "lose"
    return None

# -------------------------
# 試合IDを自動生成
# -------------------------
def get_new_id():
    records = sheet.get_all_records()
    return len(records) + 1

# -------------------------
# BO1 記録
# -------------------------
@tree.command(name="b1", description="BO1の対戦を記録します")
async def b1(
    interaction: discord.Interaction,
    deck_a: int,
    deck_b: int,
    first: str,
    result: str,
    memo: str = ""
):
    first_conv = convert_first(first)
    result_conv = convert_result(result)

    if first_conv is None or result_conv is None:
        await interaction.response.send_message("入力形式が正しくありません（先/後・〇/×）。", ephemeral=True)
        return

    deckA_name = DECKS.get(deck_a, "Unknown")
    deckB_name = DECKS.get(deck_b, "Unknown")

    match_id = get_new_id()

    sheet.append_row([
        match_id,
        "BO1",
        interaction.user.name,
        deckA_name,
        deckB_name,
        first_conv,
        result_conv,
        memo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    await interaction.response.send_message(
        f"【BO1】記録しました\n"
        f"ID: {match_id}\n"
        f"{deckA_name} vs {deckB_name}（{first}）→ {result}\n"
        f"メモ: {memo}"
    )

# -------------------------
# BO3 記録
# -------------------------
@tree.command(name="b3", description="BO3の対戦を記録します")
async def b3(
    interaction: discord.Interaction,
    deck_a: int,
    deck_b: int,
    first: str,
    result: str,
    memo: str = ""
):
    first_conv = convert_first(first)
    result_conv = convert_result(result)

    if first_conv is None or result_conv is None:
        await interaction.response.send_message("入力形式が正しくありません（先/後・〇/×）。", ephemeral=True)
        return

    deckA_name = DECKS.get(deck_a, "Unknown")
    deckB_name = DECKS.get(deck_b, "Unknown")

    match_id = get_new_id()

    sheet.append_row([
        match_id,
        "BO3",
        interaction.user.name,
        deckA_name,
        deckB_name,
        first_conv,
        result_conv,
        memo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    await interaction.response.send_message(
        f"【BO3】記録しました\n"
        f"ID: {match_id}\n"
        f"{deckA_name} vs {deckB_name}（{first}）→ {result}\n"
        f"メモ: {memo}"
    )

# -------------------------
# 訂正コマンド
# -------------------------
@tree.command(name="edit", description="記録を訂正します")
async def edit(
    interaction: discord.Interaction,
    match_id: int,
    field: str,
    new_value: str
):
    records = sheet.get_all_records()

    for i, row in enumerate(records, start=2):  # 2行目からデータ
        if row["id"] == match_id:
            col_map = {
                "mode": 2,
                "user": 3,
                "deckA": 4,
                "deckB": 5,
                "first": 6,
                "result": 7,
                "memo": 8
            }

            if field not in col_map:
                await interaction.response.send_message("訂正できる項目は mode/user/deckA/deckB/first/result/memo です。")
                return

            col = col_map[field]

            # 日本語入力の変換
            if field == "first":
                new_value = convert_first(new_value)
            if field == "result":
                new_value = convert_result(new_value)

            sheet.update_cell(i, col, new_value)
            await interaction.response.send_message(f"ID {match_id} の {field} を {new_value} に更新しました。")
            return

    await interaction.response.send_message("指定したIDが見つかりません。")

# -------------------------
# Bot 起動
# -------------------------
@bot.event
async def on_ready():
    await tree.sync()
    print("Bot is ready")

bot.run(os.getenv("DISCORD_TOKEN"))