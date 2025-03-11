kill `ps ax | grep main.py | awk '{print $1}'`
rm -rf db*
git checkout 1dd00d753422dd6519d66fda7c874139d41c0f54 -- db.sqlite3
nohup python3 main.py &> ~/nicegui.log &
