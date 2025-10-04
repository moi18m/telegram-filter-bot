import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8064115424:AAFsjX14yB7bkU_6Qwszp2Lgvu5BOgwzUJU"
ADMIN_ID = 664521950
user_data = {}

# دالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ دخلنا دالة /start")
    keyboard = []
    os.makedirs("filters", exist_ok=True)
    files = sorted([f for f in os.listdir("filters") if f.startswith("filter_") and f.endswith(".jpg")])
    for i in range(1, len(files) + 1):
        keyboard.append([InlineKeyboardButton(f"فلتر رقم {i}", callback_data=f"filter_{i}")])
    keyboard.append([InlineKeyboardButton("🔁 إعادة اختيار الفلتر", callback_data='restart')])
    if update.message.from_user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("➕ إضافة فلتر جديد", callback_data='add_filter')])
        keyboard.append([InlineKeyboardButton("🗑️ حذف فلتر", callback_data='delete_filter')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر الفلتر الي يعجبك", reply_markup=reply_markup)

    # إرسال الفلاتر وحدة وحدة
    for i, filename in enumerate(files, start=1):
        path = f"filters/{filename}"
        try:
            with open(path, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=f"فلتر رقم {i}")
                print(f"📤 أرسلنا فلتر رقم {i}")
        except Exception as e:
            print(f"❌ خطأ أثناء إرسال الفلتر {filename}: {e}")

# دالة اختيار الفلتر
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selected_filter = query.data.replace('_', ' ')
    if query.data == 'restart':
        await start(update, context)
        return
    if query.data == 'add_filter':
        await add_filter_handler(update, context)
        return
    if query.data == 'delete_filter':
        await delete_filter_handler(update, context)
        return
    if query.data.startswith('remove_'):
        await remove_filter_handler(update, context)
        return
    user_data[user_id] = {'filter': selected_filter}
    print(f"📝 خزّنا الفلتر للمستخدم {user_id}: {selected_filter}")
    await query.message.reply_text(f"أرسل صورتك الشخصية حتى أطبق {selected_filter}")
    username = query.from_user.username or "بدون يوزر"
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 المستخدم {query.from_user.full_name} (@{username}) اختار {selected_filter}"
    )

# دالة إضافة فلتر جديد
async def add_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📤 أرسل صورة الفلتر الجديد الآن")
    user_data[ADMIN_ID] = {'adding_filter': True}
    print("🛠️ الأدمن طلب إضافة فلتر جديد")

# دالة حفظ الفلتر الجديد
async def save_new_filter(update: Update):
    os.makedirs("filters", exist_ok=True)
    existing = [f for f in os.listdir("filters") if f.startswith("filter_") and f.endswith(".jpg")]
    next_index = len(existing) + 1
    new_path = f"filters/filter_{next_index}.jpg"
    try:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(new_path)
        await update.message.reply_text(f"✅ تم حفظ الفلتر الجديد باسم: filter_{next_index}.jpg")
        print(f"🆕 أضفنا فلتر جديد: {new_path}")
    except Exception as e:
        await update.message.reply_text("❌ فشل حفظ الفلتر الجديد")
        print(f"❌ خطأ أثناء حفظ الفلتر الجديد: {e}")
    user_data[ADMIN_ID]['adding_filter'] = False

# دالة حذف الفلاتر
async def delete_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    os.makedirs("filters", exist_ok=True)
    files = sorted([f for f in os.listdir("filters") if f.startswith("filter_") and f.endswith(".jpg")])
    if not files:
        await query.message.reply_text("🚫 ماكو فلاتر حالياً للحذف")
        return
    keyboard = []
    for f in files:
        keyboard.append([InlineKeyboardButton(f"❌ حذف {f}", callback_data=f"remove_{f}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("اختر الفلتر اللي تريد تحذفه:", reply_markup=reply_markup)

# دالة تنفيذ الحذف
async def remove_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    filename = query.data.replace("remove_", "")
    path = f"filters/{filename}"
    if os.path.exists(path):
        os.remove(path)
        await query.message.reply_text(f"✅ تم حذف الفلتر: {filename}")
        print(f"🗑️ حذفنا الفلتر: {filename}")
    else:
        await query.message.reply_text("❌ الملف غير موجود")
        print(f"🚫 حاولنا نحذف فلتر غير موجود: {filename}")

# دالة استلام صورة المستخدم
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📥 دخلنا دالة photo_handler")
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "بدون يوزر"
    if user_id not in user_data or 'filter' not in user_data[user_id]:
        await update.message.reply_text("❗ لازم تختار فلتر أول قبل ما ترسل الصورة")
        return
    selected_filter = user_data[user_id]['filter']
    try:
        photo_file = await update.message.photo[-1].get_file()
        os.makedirs("received", exist_ok=True)
        photo_path = f"received/user_{user_id}.jpg"
        await photo_file.download_to_drive(photo_path)
        await update.message.reply_text(f"✅ تم استلام الصورة، راح أطبق {selected_filter} وأرجعلك النتيجة")
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"📸 المستخدم {update.message.from_user.full_name} (@{username}) أرسل صورة\nID: {user_id}\nفلتر مطلوب: {selected_filter}"
        )
        print("📤 تم إرسال الصورة للأدمن بنجاح")
    except Exception as e:
        await update.message.reply_text("❌ ما قدرت أحفظ الصورة")
        print(f"❌ خطأ أثناء تحميل الصورة: {e}")

# دالة استلام الصورة المعدلة من الأدمن
async def edited_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🛠 دخلنا دالة edited_photo_handler")
    if update.message.from_user.id != ADMIN_ID:
        return
    if not update.message.caption:
        await update.message.reply_text("أضف تعليق يحتوي على ID المستخدم حتى أرجعله الصورة")
        return
    try:
        target_id = int(update.message.caption.strip())
        await context.bot.send_photo(
            chat_id=target_id,
            photo=update.message.photo[-1].file_id,
            caption="✅ هاي صورتك بعد التعديل"
        )
        await update.message.reply_text("📤 تم إرسال الصورة المعدلة للمستخدم")
        print(f"📤 رجعنا الصورة المعدلة للمستخدم {target_id}")
    except Exception as e:
        await update.message.reply_text("❌ ما قدرت أرسل الصورة المعدلة")
        print(f"❌ فشل إرسال الصورة المعدلة: {e}")

# دالة توجيه الصور حسب المرسل
async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.message.from_user.id
    print(f"📡 دخلنا photo_router - المرسل: {sender_id}")
    if sender_id == ADMIN_ID and user_data.get(ADMIN_ID, {}).get('adding_filter'):
        await save_new_filter(update)
    elif sender_id == ADMIN_ID and update.message.caption:
        await edited_photo_handler(update, context)
    else:
        await photo_handler(update, context)

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_router))  # ← هذا السطر هو الإضافة المهمة
app.run_polling()
