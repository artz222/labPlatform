## 部署流程

### macos/linux 系统

1. git clone本代码仓库
2. 在电脑中安装python、uv（pip install uv）
3. cd backend
4. uv sync
5. 激活uv环境：
    a. cd backend
    b. source .venv/bin/activate
6. cd src
7. fastapi run main.py

### windows 系统

1. git clone本代码仓库
2. 在电脑中安装python、uv（pip install uv）
3. cd backend
4. uv sync
5. 激活uv环境：(使用git bash环境)
    a. cd backend
    b. source .venv/bin/activate
6. cd src
7. fastapi run main.py

windows系统也可以使用powershell环境进行uv环境激活，使用该命令：.venv\Scripts\Activate.ps1，但powershell默认不能运行脚本文件，可参考该文章：https://blog.csdn.net/weixin_41891519/article/details/107151565