#!/usr/bin/env bash

pushd `dirname $0` > /dev/null
BASE_DIR=`pwd -P`
popd > /dev/null

#############
# Functions
#############
function logging {
    echo "[INFO] $*"
}

function build_venv {
    if [ ! -d env375 ]; then
        virtualenv env375
    fi
    . env375/bin/activate

    pip3 install -r requirements.txt
}

function rebuild_db {
	logging "Clean"

	HOSTNAME="127.0.0.1" #数据库信息
	PORT="3306"
	USERNAME="root"
	PASSWORD="12345678"
	DBNAME="mysqldb"  #数据库名称
	
	#删除数据库
	delete_sql="drop database ${DBNAME}"
	mysql -h${HOSTNAME}  -P${PORT}  -u${USERNAME} -p${PASSWORD} ${DBNAME} -e "${delete_sql}"
	#创建数据库
	create_db_sql="create database IF NOT EXISTS ${DBNAME}"
	mysql -h${HOSTNAME}  -P${PORT}  -u${USERNAME} -p${PASSWORD} -e "${create_db_sql}"


	# rm -rf "${BASE_DIR}/mysite/db.sqlite3"
	rm -rf "${BASE_DIR}/mysite/account/migrations/0001_initial.py"
		
	# logging "makemigrations" "account"
	python "${BASE_DIR}/mysite/manage.py" "makemigrations" "account"

	# logging "migrate"
	python "${BASE_DIR}/mysite/manage.py" "migrate"

	# logging "initdb.py"
	python "${BASE_DIR}/mysite/initdb.py"
}

function launch_webapp {
    cd ${BASE_DIR}/mysite
    python "manage.py" "runserver"
}

#############
# Main
#############
cd ${BASE_DIR}
OPT_ENV_FORCE=$1

if [ "${OPT_ENV_FORCE}x" == "-fx" ];then
    python "${BASE_DIR}/manage.py" "clean"
fi

python "${BASE_DIR}/manage.py" "prepare"
build_venv

if [ "${OPT_ENV_FORCE}x" == "-ix" ];then
    rebuild_db
fi

launch_webapp
