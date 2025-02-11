REQ_FILE=requirements.txt
PROJECT=question_poster
SOURCE=chgkbot.py
VENV=venv
PYTHON=python3
VENV_PYTHON=${VENV}/bin/python3
PIP = $(VENV)/bin/pip

.PHONY: all freeze setup create_venv load_venv run clean

all: run


backup_req:
	cp ${REQ_FILE} ${REQ_FILE}.bak


${VENV}:
	${PYTHON} -m venv ${VENV}


setup: ${VENV} requirements.txt
	${PIP} install -r ${REQ_FILE}


freeze: backup_req
	${PIP} freeze > ${REQ_FILE}


run:
	${VENV_PYTHON} ${SOURCE}


autopep:
	${VENV_PYTHON} -m autopep8 --in-place ${SOURCE}


clean:
	rm -rf __pycache__
	rm -rf ${VENV}
