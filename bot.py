import telebot
import os

TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(TOKEN)

FILENAME = "marks.txt"

class Subject:
    def __init__(self, name, credits, got=0.0, max=0.0, total_max=20.0):
        self.name = name
        self.credits = float(credits)
        self.got = float(got)
        self.max = float(max)
        self.total_max = float(total_max)

def load_subjects():
    if not os.path.exists(FILENAME):
        return []
    subjects = []
    with open(FILENAME, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                subjects.append(Subject(*parts))
    return subjects

def save_subjects(subjects):
    with open(FILENAME, "w") as f:
        for s in subjects:
            f.write(f"{s.name} {s.credits} {s.got} {s.max} {s.total_max}\n")

def show_table(subjects):
    if not subjects:
        return "No subjects yet."
    text = "📊 *YOUR RESULTS:*\n\n"
    sum_got_w, sum_max_w, sum_credits = 0, 0, 0
    for s in subjects:
        percent = (s.got / s.max * 100) if s.max > 0 else 0
        text += f"{s.name} — got {s.got}/{s.max} ({percent:.2f}%), credits: {s.credits}\n"
        sum_got_w += s.got * s.credits
        sum_max_w += s.max * s.credits
        sum_credits += s.credits
    if sum_credits > 0:
        avg_got = sum_got_w / sum_credits
        avg_max = sum_max_w / sum_credits
        text += f"\nYour mark: {avg_got:.2f} / 20\nMax possible: {avg_max:.2f} / 20"
    return text

# --- Commands ---

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg, "Welcome to Mark Manager!\nUse /add, /update, or /show")

@bot.message_handler(commands=["add"])
def add(msg):
    bot.reply_to(msg, "Send subject name and credits (e.g. 'Math 4')")
    bot.register_next_step_handler(msg, handle_add)

def handle_add(msg):
    try:
        name, credits = msg.text.split()
        subjects = load_subjects()
        subjects.append(Subject(name, credits))
        save_subjects(subjects)
        bot.reply_to(msg, f"✅ Added subject {name} ({credits} credits).")
    except:
        bot.reply_to(msg, "❌ Format error. Use 'Name Credits'.")

@bot.message_handler(commands=["update"])
def update(msg):
    bot.reply_to(msg, "Send update like 'Math 7/10'")
    bot.register_next_step_handler(msg, handle_update)

def handle_update(msg):
    try:
        parts = msg.text.split()
        name = parts[0]
        got, maxx = map(float, parts[1].split("/"))
        subjects = load_subjects()
        for s in subjects:
            if s.name == name:
                s.got += got
                s.max += maxx
                save_subjects(subjects)
                bot.reply_to(msg, f"✅ Updated {name}: now {s.got}/{s.max}")
                return
        bot.reply_to(msg, "❌ Subject not found.")
    except Exception as e:
        bot.reply_to(msg, "❌ Format error. Use 'Name got/max'.")

@bot.message_handler(commands=["show"])
def show(msg):
    subjects = load_subjects()
    result = show_table(subjects)
    bot.reply_to(msg, result, parse_mode="Markdown")

bot.polling()
