FROM python:3.6

ADD ./ /opt/knowschema
WORKDIR /opt/knowschema

ENV TZ=Asia/Shanghai \
  DEBIAN_FRONTEND=noninteractive

RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
  && echo ${TZ} > /etc/timezone \
  && dpkg-reconfigure --frontend noninteractive tzdata \
  && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache \
  chmod +x bin/manage \
  && pip install -r requirements/app.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["bin/manage", "start", "--daemon-off"]
