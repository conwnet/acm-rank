import time, urllib.request, sqlite3

def auto_update():
    request = urllib.request.Request('http://127.0.0.1/updateall/password')
    for i in range(3):
        try:
            with urllib.request.urlopen(request, timeout=600):
                pass
            with sqlite3.connect('database.db') as db:
                db.execute("update `acmers` set `update_time`=? where `id`='0'", (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ))
                db.commit()
            return True
        except:
            pass
    return False

while True:
    if auto_update():
        print('all data have updated...')
    else:
        print('update faild...')
    time.sleep(21600)
