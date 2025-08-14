from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove, InlineKeyboardMarkup,InlineKeyboardButton,  BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async
from aiogram.filters import Command
from aiogram.types import Message
import aiogram
import environ
import asyncio
import django
import random
import sys
import re
import os 
env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings') 
API_TOKEN = env.str('API_TOKEN')
SHARTNOMA =  -4980060633
CHAT =  -4947411477
django.setup()
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
from django.contrib.auth.models import User
from main.models import QuestionAnswer
from django.utils.html import strip_tags
from django.conf import settings



def clean_telegram_html(text):
    """
    Cleans HTML to only include Telegram-supported tags and handles special cases.
    """
    if not text:
        return ""
    
    # Telegram officially supported HTML tags
    ALLOWED_TAGS = [
        'b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del',
        'code', 'pre', 'a', 'tg-spoiler', 'tg-emoji', 'blockquote',
        'ul', 'ol', 'li', 'br', 'p'
    ]
    
    # First remove all unsupported tags completely
    text = re.sub(r'<(?!\/?({})[^>]*>)[^>]+>'.format('|'.join(ALLOWED_TAGS)), '', text)
    
    # Then remove all attributes from allowed tags (for security)
    text = re.sub(r'<(\w+)(?:\s+[^>]*)?>', r'<\1>', text)
    
    # Convert <p> tags to newlines
    text = re.sub(r'</?p[^>]*>', '\n', text)
    
    # Remove any remaining unsupported tags that might have been missed
    text = re.sub(r'<(?!\/?({})[^>]*>)[^>]+>'.format('|'.join(ALLOWED_TAGS)), '', text)
    
    return text.strip()

def split_message(text, max_length=4096):
    # Matnni 4096 belgidan oshmasdan bo'lib beradi
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

builder = InlineKeyboardBuilder()



