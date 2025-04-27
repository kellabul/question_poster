from pyrogram import Client
from pandas import read_excel, isnull as pd_isnull
from datetime import datetime, timedelta
import time
import json


POST_TIME_HOURS: int = 20
POST_TIME_MINUTES: int = 00
MESSAGE_AMOUNT_CAN_BE_POSTED_WITHOUT_TIMEOUT: int = 25
POST_TIMEOUT: int = 13
SECONDS_IN_MINUTE: int = 60
LOG_TEXT_LENGTH: int = 40
AVERAGE_TIME_ERROR: int = 4

KEY_WORD: str = 'Ответ:'
STOP_WORD: str = 'break'
EXCEL_FILE_PATH: str = 'questions.xlsx'
DATE_COLUMN_HEADER: str = 'Date'
QUESTION_COLUMN_HEADER: str = 'Question'
LINE_BREAK = '\n'


with open('credentials.json') as creds_file:
    creds = json.load(creds_file)
chat_id: int = creds["chat_id"]
bot_api_id: int = creds["bot_api_id"]
bot_api_hash: str = creds["bot_api_hash"]


def post_question(app, post_text, post_date, link):
    if link:
        post_text = post_text.replace(link+LINE_BREAK, '')
        app.send_photo(chat_id, link, caption=post_text,
                       schedule_date=post_date)
        return
    app.send_message(chat_id, post_text, schedule_date=post_date)


def delimit_text(question_text):
    if (KEY_WORD) in question_text:
        delimited_text = question_text.split(KEY_WORD)
        return delimited_text
    return ''


def format_question(delimited_text):
    return delimited_text[0] + '||' + KEY_WORD + delimited_text[1] + '||'


def get_link(delimited_text):
    lines = delimited_text[0].splitlines()
    for line in lines:
        if line.startswith('http://') or line.startswith('https://'):
            return line
    return ''


def get_question_amount(question_dict):
    count: int = 0
    for question in question_dict:
        if (question == STOP_WORD):
            break
        if type(question) == str:
            count += 1
    return count


def get_timeout(question_amount):
    if question_amount > MESSAGE_AMOUNT_CAN_BE_POSTED_WITHOUT_TIMEOUT:
        return POST_TIMEOUT
    return 0


def get_remaining_time(timeout, question_amount):
    return (question_amount - 1) * (timeout + AVERAGE_TIME_ERROR)


def get_expected_completion_time(remaining_time):
    return (datetime.now() + timedelta(seconds=remaining_time)).strftime('%Y-%m-%d %H:%M:%S')


def format_text_for_log(output_text):
    text_prefix = "'"
    text_postfix = "...'" if len(output_text) > LOG_TEXT_LENGTH else text_prefix
    return f"{text_prefix}{output_text[0:LOG_TEXT_LENGTH].replace(LINE_BREAK, ' ')}{text_postfix}"


def get_remaining_time_output_string(remaining_time):
    remaining_time_minutes = remaining_time//SECONDS_IN_MINUTE
    remaining_time_seconds = remaining_time % SECONDS_IN_MINUTE
    return f"~ {remaining_time_minutes:02d}m {remaining_time_seconds:02d}s left"


def main(app):
    df = read_excel(EXCEL_FILE_PATH, parse_dates=[
                    DATE_COLUMN_HEADER], usecols=[DATE_COLUMN_HEADER, QUESTION_COLUMN_HEADER])
    dates = df[DATE_COLUMN_HEADER]
    question_dict: dict = df[QUESTION_COLUMN_HEADER]

    question_amount: int = get_question_amount(question_dict)
    timeout: int = get_timeout(question_amount)
    remaining_time: int = get_remaining_time(timeout, question_amount)

    count: int = 0
    print(f"Number of questions: {question_amount}")
    print(f"Expected completion time: {get_expected_completion_time(remaining_time)}")

    for i in range(len(question_dict)):
        question_text = question_dict[i]

        # if question cell is empty, type == float
        if type(question_text) != str:
            continue

        if (question_text == STOP_WORD):
            break

        post_date = dates[i].to_pydatetime()

        if pd_isnull(post_date):
            print(f"WARNING !!! Date not set for question (index = {i}): {post_date}")
            break

        post_time = post_date.replace(hour=POST_TIME_HOURS, minute=POST_TIME_MINUTES)

        if post_time < datetime.now():
            print(f"WARNING !!! Incorrect date (index = {i}): {post_time}")
            print(f"Date in the past will cause immediate posting")
            break

        delimited_question_text = delimit_text(question_text)

        if not delimited_question_text:
            print(f"incorrect question format (index = {i}): {format_text_for_log(question_text)}")
            continue

        link = get_link(delimited_question_text)

        formatted_question_text = format_question(delimited_question_text)

        post_question(app, formatted_question_text, post_time, link)

        count += 1

        print(
            f"{count:02d}/{question_amount:02d} -- {get_remaining_time_output_string(remaining_time)} -- "
            f"#{i:02d} scheduled for {post_time} -- {format_text_for_log(formatted_question_text)}")

        remaining_time -= (timeout + AVERAGE_TIME_ERROR)

        # avoiding antispam timeout from TelegramAPI
        if count < question_amount:
            time.sleep(timeout)


if __name__ == '__main__':
    app = Client(name="chgk_bot_user", api_id=bot_api_id,
                 api_hash=bot_api_hash)
    app.start()
    main(app)
    app.stop()
