FROM python:3.10-slim

# 设置 pip 国内镜像源（加速下载）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装常用库（根据实际需求增减）
RUN pip install pytest numpy pandas requests scipy matplotlib seaborn scikit-learn

# 可选：如果测试需要 Jupyter 或调试工具，可以添加，但会增加镜像体积
# RUN pip install jupyter ipython

# 设置工作目录
WORKDIR /app

# 默认命令
CMD ["pytest"]