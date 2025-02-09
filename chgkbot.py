from pyrogram import Client
from pandas import read_excel
from datetime import datetime, timedelta
import time
import json

post_time_hours = 20
post_time_minutes = 00
messages_can_be_posted_without_timeout: int = 25
post_timeout: int = 12
seconds_in_minute = 60
output_line_length = 40

with open('credentials.json') as creds_file:
    creds = json.load(creds_file)
# # chat_id:int = creds["test_chat_id"]
chat_id: int = creds["chat_id"]
bot_api_id: int = creds["bot_api_id"]
bot_api_hash: str = creds["bot_api_hash"]


key_word: str = 'Ответ:'
error_text: str = 'n-a'
stop_word: str = 'break'
line_break = '\n'


def post_question(app, post_text, post_date, link):
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


def get_question_amount(question_dict):
    count: int = 0
    for question in question_dict:
        if (question == stop_word):
            break
        if type(question) == str:
            count += 1
    return count


def get_timeout(question_amount):
    if question_amount > messages_can_be_posted_without_timeout:
        return post_timeout
    return 0


def get_estimated_time(remaining_time, question_amount):
    # +2s for every question
    return remaining_time + question_amount * 2


def get_remaining_time(timeout, question_amount):
    return (question_amount - 1) * timeout


def get_expected_completion_time(estimated_time):
    return (datetime.now() + timedelta(seconds=estimated_time)).strftime('%Y-%m-%d %H:%M:%S')


def format_question_for_output_message(formatted_text):
    return formatted_text[0:output_line_length].replace(line_break, ' ')


def get_remaining_time_output(remaining_time):
    return f"~ {remaining_time//seconds_in_minute}m {remaining_time%seconds_in_minute}s left"


def main(app):
    df = read_excel('questions.xlsx', parse_dates=[
                    'Date'], usecols=['Date', 'Question'])
    dates = df['Date']
    question_dict: dict = df['Question']

    question_amount = get_question_amount(question_dict)
    timeout = get_timeout(question_amount)
    remaining_time = get_remaining_time(timeout, question_amount)
    estimated_time = get_estimated_time(remaining_time, question_amount)

    count: int = 0
    print(f"Number of questions: {question_amount}")
    print(
        f"Expected completion time: {get_expected_completion_time(estimated_time)}")

    for i in range(len(question_dict)):
        # if 'question' cell is empty, type == float
        if type(question_dict[i]) != str:
            continue

        if (question_dict[i] == stop_word):
            break

        post_time = dates[i].to_pydatetime().replace(
            hour=post_time_hours, minute=post_time_minutes)

        if post_time < datetime.now():
            print(f"WARNING !!! incorrect date (index = {i}): {post_time}")
            print(f"date in the past will cause immediate posting")
            break

        delimited_question_text = delimit_text(question_dict[i])

        if delimited_question_text == error_text:
            print(f"incorrect question formatting: index = {i}")
            continue

        link = get_link(delimited_question_text)

        formatted_question_text = format_question(delimited_question_text)

        post_question(app, formatted_question_text, post_time, link)

        count += 1

        print(
            f"{count}/{question_amount} -- {get_remaining_time_output(remaining_time)} -- #{i} scheduled for {post_time} -- '{format_question_for_output_message(formatted_question_text)}...'")

        remaining_time -= timeout

        # avoiding antispam timeout from TelegramAPI
        if count < question_amount:
            time.sleep(timeout)


if __name__ == '__main__':
    app = Client(name="chgk_bot_user", api_id=bot_api_id,
                 api_hash=bot_api_hash)
    app.start()
    main(app)
    app.stop()
