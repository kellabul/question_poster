from pyrogram import Client
from pandas import read_excel
from datetime import datetime, timedelta
import time
import json

post_time_hours: int = 20
post_time_minutes: int = 00
messages_can_be_posted_without_timeout: int = 25
post_timeout: int = 12
seconds_in_minute: int = 60
log_text_length: int = 40
average_time_error: int = 2

key_word: str = 'Ответ:'
stop_word: str = 'break'
excel_file_path: str = 'questions.xlsx'
date_column_header: str = 'Date'
question_column_header: str = 'Question'
line_break = '\n'

with open('credentials.json') as creds_file:
    creds = json.load(creds_file)
chat_id: int = creds["chat_id"]
bot_api_id: int = creds["bot_api_id"]
bot_api_hash: str = creds["bot_api_hash"]


def post_question(app, post_text, post_date, link):
    if link:
        post_text = post_text.replace(link+line_break, '')
        app.send_photo(chat_id, link, caption=post_text,
                       schedule_date=post_date)
        return

    app.send_message(chat_id, post_text, schedule_date=post_date)


def delimit_text(question_text):
    if (key_word) in question_text:
        delimited_text = question_text.split(key_word)
        return delimited_text
    return ''


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


def get_remaining_time(timeout, question_amount):
    return (question_amount - 1) * timeout + question_amount * average_time_error


def get_expected_completion_time(remaining_time):
    return (datetime.now() + timedelta(seconds=remaining_time)).strftime('%Y-%m-%d %H:%M:%S')


def format_text_for_log(output_text):
    text_prefix = "'"
    text_postfix = "...'" if len(
        output_text) > log_text_length else text_prefix
    return f"{text_prefix}{output_text[0:log_text_length].replace(line_break, ' ')}{text_postfix}"


def get_remaining_time_output_string(remaining_time):
    remaining_time_minutes = remaining_time//seconds_in_minute
    remaining_time_seconds = remaining_time % seconds_in_minute
    return f"~ {remaining_time_minutes:02d}m {remaining_time_seconds:02d}s left"


def main(app):
    df = read_excel(excel_file_path, parse_dates=[
                    date_column_header], usecols=[date_column_header, question_column_header])
    dates = df[date_column_header]
    question_dict: dict = df[question_column_header]

    question_amount: int = get_question_amount(question_dict)
    timeout: int = get_timeout(question_amount)
    remaining_time: int = get_remaining_time(timeout, question_amount)

    count: int = 0
    print(f"Number of questions: {question_amount}")
    print(
        f"Expected completion time: {get_expected_completion_time(remaining_time)}")

    for i in range(len(question_dict)):
        # if question cell is empty, type == float
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

        if not delimited_question_text:
            print(
                f"incorrect question format (index = {i}): {format_text_for_log(question_dict[i])}")
            continue

        link = get_link(delimited_question_text)

        formatted_question_text = format_question(delimited_question_text)

        post_question(app, formatted_question_text, post_time, link)

        count += 1

        print(
            f"{count:02d}/{question_amount:02d} -- {get_remaining_time_output_string(remaining_time)} -- #{i:02d} scheduled for {post_time} -- {format_text_for_log(formatted_question_text)}")

        remaining_time -= (timeout + average_time_error)

        # avoiding antispam timeout from TelegramAPI
        if count < question_amount:
            time.sleep(timeout)


if __name__ == '__main__':
    app = Client(name="chgk_bot_user", api_id=bot_api_id,
                 api_hash=bot_api_hash)
    app.start()
    main(app)
    app.stop()
