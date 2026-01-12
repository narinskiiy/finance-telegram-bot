from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import os

TOKEN = os.environ.get("BOT_TOKEN")

def init_db():
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount REAL,
        note TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save(user_id, rtype, amount, note):
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (user_id, type, amount, note) VALUES (?, ?, ?, ?)",
        (user_id, rtype, amount, note)
    )
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Moliya bot\n\n"
        "/income summa izoh\n"
        "/expense summa izoh\n"
        "/summary"
    )

async def income(update, context):
    amount = float(context.args[0])
    note = " ".join(context.args[1:])
    save(update.effective_user.id, "income", amount, note)
    await update.message.reply_text("✅ Daromad qo‘shildi")

async def expense(update, context):
    amount = float(context.args[0])
    note = " ".join(context.args[1:])
    save(update.effective_user.id, "expense", amount, note)
    await update.message.reply_text("❌ Xarajat qo‘shildi")

async def summary(update, context):
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT type, SUM(amount)
    FROM records
    WHERE user_id=?
    GROUP BY type
    """, (update.effective_user.id,))
    rows = cur.fetchall()
    conn.close()

    text = "📊 Hisobot:\n"
    for t, s in rows:
        text += f"{t}: {s}\n"

    await update.message.reply_text(text)

init_db()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("income", income))
app.add_handler(CommandHandler("expense", expense))
app.add_handler(CommandHandler("summary", summary))
app.run_polling()
