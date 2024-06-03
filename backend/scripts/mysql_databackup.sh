#!/bin/sh
set -eu

LINUX_USER=root
DUMP_CMD=/usr/bin/mysqldump
RECOVERY_CMD=/usr/bin/mysql
OUT_DIR=/root/backup/mysql
BACKUP_ENV=online  # online, qa

DB_HOST=rm-j6c6l4d77vec99bgp.mysql.rds.aliyuncs.com
DB_NAME=huace_nlp
DB_USER=huace
DB_PASS=Mhuace@nlp
DB_DUMP_TABLES='setting user user_object user_vector_database workflow workflow_workflowtag_through workflowrunschedule workflowtag workflowtemplate workflowtemplate_workflowtag_through'
DAYS=15

echo "---------------------------------- Date: `date +%Y-%m-%d` ----------------------------------"

if [ ! -d "$OUT_DIR" ]; then
    # 如果目录不存在，则创建目录
    mkdir -p "$OUT_DIR"
    echo "1 >>> 目录 $OUT_DIR 已创建。"
else
    echo "1 >>> 目录 $OUT_DIR 已存在。"
fi

DATE=`date +%Y%m%d`
BACKUP_NAME=$DB_NAME-$DATE.sql
OUT_SQL=$OUT_DIR/$BACKUP_NAME
PURE_TAR_NAME=$DB_NAME-$DATE.tar.gz
TAR_SQL=$OUT_DIR/$PURE_TAR_NAME   # tar -xzvf file.tar.gz

echo "2 >>> 备份文件名 OUT_SQL: $OUT_SQL, 压缩名： $TAR_SQL"

# mysqldump command to backup
echo "3 >>> 压缩命令：$DUMP_CMD -h $DB_HOST -u$DB_USER -p$DB_PASS --set-gtid-purged=OFF $DB_NAME $DB_DUMP_TABLES > $OUT_SQL"

# win mysqldump
#"$DUMP_CMD" -h $DB_HOST -u$DB_USER -p$DB_PASS --set-gtid-purged=OFF $DB_NAME $DB_DUMP_TABLES > $OUT_SQL
# linux mysqldump
$DUMP_CMD -h $DB_HOST -u$DB_USER -p$DB_PASS --set-gtid-purged=OFF $DB_NAME $DB_DUMP_TABLES > $OUT_SQL  # 执行备份命令

OK_MSG="$BACKUP_ENV:"
#ERROR_MSG=""

if [ $? -eq 0 ]; then
  echo "4 >>> 备份命令执行成功。"
  OK_MSG="$OK_MSG mysqldump执行成功"
else
  echo "4 >>> 备份命令执行失败。"
#  ERROR_MSG="mysqldump执行失败"
fi

#判断文件是否存在
if [ -e "$OUT_SQL" ]; then
  echo "4.1 >>> 备份文件：$OUT_SQL 已存在"
else
  echo "4.1 >>> 备份文件：$OUT_SQL 未发现，备份可能失败！"
fi

# online 将数据 恢复到测试环境数据库(rds)，如果是测试环境，就不需要
QA_DB_HOST=rm-j6c8w48l98to3i078.mysql.rds.aliyuncs.com
QA_DB_USER=huace
QA_DB_PASS=Mhuace@nlp
QA_DB_NAME=huace_nlp
if [ "$BACKUP_ENV" == 'online' ]; then
  echo "5 >>> 恢复命令: $RECOVERY_CMD -h $QA_DB_HOST -u$QA_DB_USER -p$QA_DB_PASS $QA_DB_NAME < $OUT_SQL"
  $RECOVERY_CMD -h $QA_DB_HOST -u$QA_DB_USER -p$QA_DB_PASS $QA_DB_NAME < $OUT_SQL
  echo "5 >>> $BACKUP_ENV 环境数据恢复到测试rds中"
  OK_MSG="$OK_MSG -> 数据恢复到 QA-RDS"
else
  echo "5 >>> $BACKUP_ENV 环境不需要恢复数据库(rds)"
fi

# 文件大的话就压缩
cd $OUT_DIR
echo "  >>> 当前路径："
pwd
echo "  >>> 压缩命令：tar -czvf $PURE_TAR_NAME $BACKUP_NAME"

tar -czvf $PURE_TAR_NAME $BACKUP_NAME
#chown $LINUX_USER:$LINUX_USER $OUT_DIR/$TAR_SQL

if [ $? -eq 0 ]; then
  find $OUT_DIR -name $BACKUP_NAME -type f -delete
  echo "6 >>> 压缩执行成功，[ find $OUT_DIR -name $BACKUP_NAME -type f -delete ] 删除成功"
  OK_MSG="$OK_MSG -> 备份压缩成功"
else
  echo "6 >>> 压缩执行失败。"
fi

# 删除20天之前的文件
echo "7 >>> 删除20天前文件命令：find $OUT_DIR -name "$DB_NAME-*.tar.gz" -type f -mtime +$DAYS -exec rm {} \;"
find $OUT_DIR -name "$DB_NAME-*.tar.gz" -type f -mtime +$DAYS -exec rm {} \;

if [ $? -eq 0 ]; then
  echo "8 >>> 过期的SQL文件删除成功。"
else
  echo "8 >>> 删除过期SQL文件时发生错误。"
fi

# --------------------- 仅在 online 传输 ---------------------------------
# 将数据再次备份到目标机器
SRC_PATH=$TAR_SQL
DEST_USER=huace
DEST_HOST=192.168.191.56
DEST_PATH=/data0/backup/mysql

echo "9 >>> SCP命令：spawn scp $SRC_PATH $DEST_USER@$DEST_HOST:$DEST_PATH"
expect <<EOF
set timeout 1800
spawn scp $SRC_PATH $DEST_USER@$DEST_HOST:$DEST_PATH
expect {
  "(yes/no)?" {send "yes\r"; exp_continue }
  "password:" {send "huace@nlp\r" }
}
expect "100%"
expect eof
EOF

# 使用expect编写交互脚本
expect_script=$(cat << EOF
spawn ssh $DEST_USER@$DEST_HOST "test -e $DEST_PATH/$PURE_TAR_NAME && echo 'ok' || echo 'no'"
expect {
    "password:" {send -- "huace@nlp\r"; exp_continue}
    "ok"      {puts "File exists on remote host."; exit 0}
    "no"      {puts "File does not exist on remote host."; exit 1}
    timeout   {puts "SSH connection timed out."; exit 2}
    eof       {puts "Unexpected EOF during SSH session."; exit 3}
}
expect eof
EOF
)
# 通过expect执行脚本
testResult=$(expect -c "$expect_script")
echo "10 >>> expect testResult: $testResult"
expect_exit_code=$?
echo "退出状态码: $expect_exit_code"

# 判断expect脚本的执行结果
if [ $expect_exit_code -eq 0 ]; then
  echo "10 >>> expect 备份压缩文件传输到远程机器成功"
  OK_MSG="$OK_MSG -> 远程备份成功"
else
  echo "10 >>> expect 备份压缩文件传输到远程机器失败"
fi
# --------------------- 仅在 online 传输 ---------------------------------

# 测试发送 http 请求
QYWX_API="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=854273f8-3dd7-423a-a811-5d91d765e2e2" # prd
#QYWX_API="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2955df74-4d77-4411-ac6b-63479e5a925b"  # test
# 获取JSON响应并解析
data=$(cat << EOF
{
  "msgtype": "text",
  "text": {
    "content": "$OK_MSG",
    "mentioned_mobile_list": ["13601841820"]
  }
}
EOF
)
response=$(curl -X POST -H "Content-Type:application/json" -d "$data" $QYWX_API)
errcode=$(echo "$response" | jq '.errcode')

echo "$response"

# 检查errcode的值是否为0
if [ "$errcode" -eq 0 ]; then
  echo "请求成功，errcode为0"
else
  echo "请求返回errcode非0，值为: $errcode"
fi

printf "\n\n\n"

