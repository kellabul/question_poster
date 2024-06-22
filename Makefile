REQ_FILE=requirements.txt
PROJECT=question_poster
SOURCE_FILE=chgkbot.py
VENV=${PROJECT}_venv
PYTHON=python3

.PHONY: all write_req download_req create_venv load_venv run

all: run

write_req:
	${PYTHON} -m pip freeze > ${REQ_FILE}

download_req:
	${PYTHON} -m pip install -r ${REQ_FILE}

create_venv:
	${PYTHON} -m venv ${VENV}

run:
	${PYTHON} ${SOURCE_FILE}