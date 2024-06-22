REQ_FILE=requirements.txt
PROJECT=question_poster
SOURCE_FILE=chgkbot.py
VENV=${PROJECT}_venv
EXEC=python3

.PHONY: all write_req download_req create_venv load_venv run

all: run

write_req:
	${EXEC} -m pip freeze > ${REQ_FILE}

download_req:
	${EXEC} -m pip install -r ${REQ_FILE}

create_venv:
	${EXEC} -m venv ${VENV}

run:
	${EXEC} ${SOURCE_FILE}