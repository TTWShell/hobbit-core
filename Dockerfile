FROM python:3.6.5


ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip -i https://pypi.doubanio.com/simple && \
    pip install -i https://pypi.doubanio.com/simple pytest pytest-cov flake8
