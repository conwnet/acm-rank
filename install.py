import os
if os.path.exists('database.db'):
    print('数据库已存在！如果要重新安装请手动删除database.db文件。')
else:
    from web import install
    install()
    print('安装完成！')
