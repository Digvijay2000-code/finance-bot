from envparse import env
env.read_envfile()

BASEROW_TOKEN = env.str("BASEROW_TOKEN")
BASEROW_USERNAME = env.str("BASEROW_USERNAME")
BASEROW_PASSWORD = env.str("BASEROW_PASSWORD")
BOT_TOKEN = env.str("BOT_TOKEN")
PO_TABLE = env.int("PO_TABLE")
BOT_ACCESS_TABLE = env.int("BOT_ACCESS_TABLE")
WEBHOOK = env.bool("WEBHOOK")
WEBHOOK_PATH = env.str("WEBHOOK_PATH", default = "webhook")
WEBHOOK_URL = f'https://finance-1tpt-bot.onrender.com/{WEBHOOK_PATH}'