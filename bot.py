from import_ import *
user_state = {}
pending_replies = {}

MAIN_MENU_BUTTONS = [
    "EDO ijro",
    "E-huquqshunos",
    "Mahalla Ijro",
    "Elektron kluch",
    "Shartnomalar va toʻlovlar",
    "Eng koʻp beriladigan savollar"
]


@dp.message(Command("get_video"))
async def get_video_file_id(message: types.Message):
    if message.video:
        file_id = message.video.file_id
        await message.answer(f"Video file_id: {file_id}")
    else:
        await message.answer("Iltimos,  /get_video shu buyruq bilan birga yuboring.")
    

@dp.message(Command("get_phot"))
async def get_photo_file_id(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id  # Eng sifatli rasm
        await message.answer(f"Rasm file_id: {file_id}")
    else:
        await message.answer("Iltimos, /get_phot shu buyruq bilan birga yuboring.")



@dp.callback_query(F.data.in_(["yes", "no"]))
async def process_inline_buttons(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    if callback.data == "no":
        user_state[user_id] = {"step": "chat"}
        await callback.message.answer("Chat rejimidasiz. Xabar yozing, men uni admin ga yuboraman. Orqaga qaytish uchun /menu yozing.",reply_markup=ReplyKeyboardRemove())

    elif callback.data == "yes":
        user_state[user_id] = {"step": "main_menu"}
        await callback.answer() 
        await callback.message.answer(" /menu yozing.",reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@dp.message(F.reply_to_message)
async def admin_reply_handler(message: types.Message):
    reply_msg = message.reply_to_message  # butun Message obyekti
    msg_id = reply_msg.message_id         # faqat id

    user_id = r.get(msg_id)
    if not user_id:
        await message.reply("❌ User ID topilmadi — reply noto‘g‘ri formatda.")
        return

    try:
        if message.photo:
            await bot.send_photo(
                int(user_id),
                message.photo[-1].file_id,
                caption=message.caption or "",
                parse_mode="HTML"
            )
        elif message.text:
            await bot.send_message(
                int(user_id),
                message.text,
                parse_mode="HTML"
            )

        # Inline tugmani olib tashlash
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=msg_id,
            reply_markup=None
        )

        await message.reply("✅ Javob foydalanuvchiga yuborildi!")

    except Exception:
        import traceback
        error_text = traceback.format_exc()
        await message.reply(f"❌ Xatolik:\n<pre>{error_text}</pre>", parse_mode="HTML")

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Chat"), KeyboardButton(text="EDO ijro")],
            [KeyboardButton(text="E-huquqshunos"), KeyboardButton(text="Mahalla Ijro")],
            [KeyboardButton(text="Elektron kluch"), KeyboardButton(text="Shartnomalar va toʻlovlar")],
            [KeyboardButton(text="Eng koʻp beriladigan savollar")]
        ],
        resize_keyboard=True
    )


def get_lang_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    user_id = message.from_user.id
    user_state[user_id] = {"step": "choose_lang", "lang": "uz"}
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=get_lang_menu())
    await sync_to_async(User.objects.get_or_create)(username=user_id)


@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def choose_language(message: Message):
    user_id = message.from_user.id
    lang = "uz" if "O'zbekcha" in message.text else "ru"
    user_state[user_id] = {"step": "waiting_for_name", "lang": lang}
    await message.answer(
        "Familiya va Ismingizni kiriting:" if lang == "uz" else "Введите фамилию и имя:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message()
async def universal_handler(message: Message):
    user_id = message.from_user.id
    # lang = "uz" if "O'zbekcha" in message.text else "ru"
    lang = user_state.get(user_id, {}).get("lang", "uz")
    # state = user_state.get(user_id, {})
    state = user_state.get(user_id, {"step": "main_menu"})
    step = state.get("step", "main_menu")


    # Ism bosqichi
    if step == "waiting_for_name" and message.text:
        user, _ = await sync_to_async(User.objects.get_or_create)(username=user_id)
        user.first_name = message.text
        user.password = str(random.randint(100000,999999))
        await sync_to_async(user.save)()
        user_state[user_id]["step"] = "waiting_for_phone"
        await message.answer(
            "Telefon raqamingizni quyidagi formatda yuboring:\nNamuna: 901234567" if lang == "uz"
            else "Введите номер телефона в формате: 901234567",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Telefon bosqichi
    if step == "waiting_for_phone" and message.text:
        phone_number = message.text.strip()
        cleaned_number = re.sub(r'[^\d+]', '', phone_number)
        if (cleaned_number.startswith('+998') and len(cleaned_number) == 12) or \
            (cleaned_number.startswith('998') and len(cleaned_number) == 12) or \
            (len(cleaned_number) == 9 and cleaned_number[0] in ['9', '8', '7']):
            formatted_number = '+998' + cleaned_number[-9:]
            user, _ = await sync_to_async(User.objects.get_or_create)(username=user_id)
            user.last_name = formatted_number
            await sync_to_async(user.save)()
            await message.answer(
                "Rahmat! Ma'lumotlaringiz qabul qilindi." if lang == "uz"
                else "Спасибо! Ваши данные приняты.",
                reply_markup=ReplyKeyboardRemove()
            )
            user_state[user_id] = {"step": "main_menu", "lang": lang}
            await message.answer(
                "👇 Menyudan kerakli bo'limni tanlang" if lang == "uz"
                else "👇 Выберите нужный раздел из меню",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer(
                "Noto'g'ri telefon raqam formati. Namuna:  901234567" if lang == "uz"
                else "Некорректный формат номера. Пример: 901234567"
            )
        return

    # Asosiy menyu
    if message.text == "/menu":
        user_state.setdefault(user_id, {"step": "main_menu", "lang": "uz"})
        user_state[user_id] = {"step": "main_menu"}
        await message.answer(
            "Asosiy menyu." if lang == "uz" else "Главное меню.",
            reply_markup=get_main_menu()
        )
        return

    # Chat va shartnoma state
    if message.text == "Chat":
        user_state[user_id]["step"] = "chat"
        await message.answer(
            "Chat rejimidasiz. Xabar yozing, men uni admin ga yuboraman. Orqaga qaytish uchun /menu yozing." if lang == "uz"
            else "Вы в режиме чата. Напишите сообщение, я отправлю его админу. Для возврата напишите /menu.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    if message.text == "Shartnomalar va toʻlovlar":
        user_state[user_id]["step"] = "shartnoma"
        await message.answer(
            "Shartnomalar rejimidasiz. Xabar yozing, men uni boshqa admin ga yuboraman. Orqaga qaytish uchun /menu yozing." if lang == "uz"
            else "Вы в режиме договоров. Напишите сообщение, я отправлю его другому админу. Для возврата напишите /menu.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Chat state: xabarlarni admin gruppaga yuborish
    if state.get("step") == "chat":
        username = (
            f"@{message.from_user.username}" if message.from_user.username 
            else message.from_user.full_name if message.from_user.full_name 
            else f"ID:{message.from_user.id}"
        )
        user_profile = f"<a href='tg://user?id={user_id}'>{username}</a>"
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Ответ не был написан.",
                        callback_data=f"reply_to_{user_id}"
                    )
                ]
            ]
        )
        caption = message.caption or "🖼 Фото"
        if message.photo:
            await message.answer("Rasmingiz chat Admin ga yuborildi." if lang == "uz" else "Ваше фото отправлено админу.")
            sent_msg = await bot.send_photo(
                SHARTNOMA,
                message.photo[-1].file_id,
                caption=f"{caption}\n\n👤 Отправитель: {user_profile}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            r.setex(sent_msg.message_id, 86400, json.dumps(user_id))
            return
        elif message.text:
            await message.answer("Xabaringiz chat Admin ga yuborildi." if lang == "uz" else "Ваше сообщение отправлено админу.")
            sent_msg = await bot.send_message(
                SHARTNOMA,
                text=f"{message.text}\n\n👤 Отправитель: {user_profile}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            r.setex(sent_msg.message_id, 86400, json.dumps(user_id))
            return

    # Shartnoma state: xabarlarni boshqa gruppaga yuborish
    if state.get("step") == "shartnoma":
        username = (
            f"@{message.from_user.username}" if message.from_user.username 
            else message.from_user.full_name if message.from_user.full_name 
            else f"ID:{message.from_user.id}"
        )
        user_profile = f"<a href='tg://user?id={user_id}'>{username}</a>"
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Ответ не был написан.",
                        callback_data=f"reply_to_{user_id}"
                    )
                ]
            ]
        )
        caption = message.caption or "🖼 Фото"
        if message.photo:
            await message.answer("Rasmingiz chat Admin ga yuborildi." if lang == "uz" else "Ваше фото отправлено админу.")
            sent_msg = await bot.send_photo(
                CHAT,
                message.photo[-1].file_id,
                caption=f"{caption}\n\n👤 Отправитель: {user_profile}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            r.setex(sent_msg.message_id, 86400, json.dumps(user_id))
            return
        elif message.text:
            await message.answer("Xabaringiz chat Admin ga yuborildi." if lang == "uz" else "Ваше сообщение отправлено админу.")
            sent_msg = await bot.send_message(
                CHAT,
                text=f"{message.text}\n\n👤 Отправитель: {user_profile}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            r.setex(sent_msg.message_id, 86400, json.dumps(user_id))
            return

    if message.text in MAIN_MENU_BUTTONS:
        q_type = message.text
        questions = await sync_to_async(list)(
            QuestionAnswer.objects.filter(type=q_type)
        )
        if not questions:
            await message.answer("Bu bo'limda savollar yo'q." if lang == "uz" else "В этом разделе нет вопросов.", reply_markup=get_main_menu())
            return
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=q.question)] for q in questions] + [[KeyboardButton(text="⬅️ Orqaga")]],
            resize_keyboard=True
        )
        user_state[user_id] = {"step": "questions", "lang": lang, "type": q_type, "questions": [q.question for q in questions]}
        await message.answer("Savolni tanlang:" if lang == "uz" else "Выберите вопрос:", reply_markup=keyboard)
        return

    if message.text == "⬅️ Orqaga":
        user_state[user_id]["step"] = "main_menu"
        await message.answer("Asosiy menyu." if lang == "uz" else "Главное меню.", reply_markup=get_main_menu())
        return

    # Savolga javob
    if state.get("step") == "questions" and message.text in state.get("questions", []):
        try:
            question_obj = await sync_to_async(QuestionAnswer.objects.get)(
                question=message.text, type=state["type"]
            )
            javob = clean_telegram_html(question_obj.answer) or "Javob mavjud emas."
            if question_obj.img:
                await message.answer_photo(question_obj.img)
            if question_obj.video:
                await message.answer_video(question_obj.video)
            for part in split_message(javob):
                await message.answer(part, parse_mode="HTML")
            await message.answer(
                "Javobdan qoniqtizmimi?" if lang == "uz" else "Вы довольны ответом?",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="Ha", callback_data="yes"),
                            InlineKeyboardButton(text="Yo'q", callback_data="no")
                        ]
                    ]
                )
            )
            user_state[user_id]["step"] = "main_menu"
            return
        except QuestionAnswer.DoesNotExist:
            await message.answer("Javob mavjud emas." if lang == "uz" else "Ответ отсутствует.")
            user_state[user_id]["step"] = "main_menu"
            return

    await message.answer("Iltimos, menyudan tanlang yoki /start buyrug‘ini bosing." if lang == "uz" else "Пожалуйста, выберите из меню или напишите /start.", reply_markup=get_main_menu())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="/start"),
        BotCommand(command="menu", description="/menu"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())