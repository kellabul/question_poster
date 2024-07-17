from pyrogram import Client
from pandas import read_excel
from datetime import datetime
import time
import json

post_time_hours = 20
post_time_minutes = 00


with  open('credentials.json') as creds_file:
    creds = json.load(creds_file)
    
# # chat_id:int = creds["test_chat_id"]
chat_id:int = creds["chat_id"]
bot_api_id:int = creds["bot_api_id"]
bot_api_hash:str = creds["bot_api_hash"]


key_word: str = 'Ответ:'
error_text: str = 'n-a'


app = Client(name="chgk_bot_user", api_id=bot_api_id, api_hash=bot_api_hash)


df = read_excel('questions.xlsx', parse_dates=[
                   'Date'], usecols=['Date', 'Question'])
dates = df['Date']
question: dict = df['Question']

line_break = '\n'
messages_before_break = 10
seconds_to_sleep = 5


def post_question(post_text, post_date, link):
    if link != '':
        post_text = post_text.replace(link+line_break, '')
        app.send_photo(chat_id, link, caption=post_text,
                       schedule_date=post_date)
    else:
        app.send_message(chat_id, post_text, schedule_date=post_date)


def delimit_text(question_text):
    if (key_word) in question_text:
        delimited_text = question_text.split(key_word)
        return delimited_text
    return error_text


def format_question(delimited_text):
    return delimited_text[0] + '||' + key_word + delimited_text[1] + '||'


def get_link(delimited_text):
    lines = delimited_text[0].splitlines()
    for line in lines:
        if line.startswith('http://') or line.startswith('https://'):
            return line
    return ''


def main():
    for i in range(len(df.index)):
        # if 'question' cell is empty, type == float
        if type(question[i]) != str:
            continue

        post_time = dates[i].to_pydatetime().replace(
            hour=post_time_hours, minute=post_time_minutes)

        if post_time < datetime.now():
            print(f"--- !!! --- incorrect date (index = {i}): {post_time}")
            break

        delimited_question_text = delimit_text(question[i])

        if delimited_question_text == error_text:
            print(f"incorrect question formatting: index = {i}")
            continue

        link = get_link(delimited_question_text)

        formatted_text = format_question(delimited_question_text)

        post_question(formatted_text, post_time, link)

        print(f"Question #{i} was scheduled for {post_time} --- '{formatted_text[0:40].replace(line_break, ' ')}...'")

        # to avoid antispam timeout from TelegramAPI
        if ((i + 1) % messages_before_break == 0):
            time.sleep(seconds_to_sleep)


if __name__ == '__main__':
    app.start()
    main()
    app.stop()
