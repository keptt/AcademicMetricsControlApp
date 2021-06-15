FROM centos:7


ENV ORACLE_HOME         "/usr/lib/oracle/client64"
ENV LD_LIBRARY_PATH     "${ORACLE_HOME}/lib"
ENV TNS_ADMIN           "${ORACLE_HOME}/network"
ENV NLS_LANG            "AMERICAN_AMERICA.UTF8"
ENV TMP_ORACLE          "/tmp/oracle"
ENV WORKDIR             "/app"
ENV LC_ALL              "en_US.UTF-8"
ENV LANG                "en_US.UTF-8"
ENV PATH                "${ORACLE_HOME}/bin:${PATH}"

ARG INIT=""


RUN yum update -y \
    && yum install -y zip unzip \
    && yum install -y wget \
    && yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel make \
    && cd /usr/src \
    && wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz \
    && tar xzf Python-3.7.9.tgz \
    && cd Python-3.7.9 \
    && ./configure --enable-optimizations \
    && make altinstall \
    && rm /usr/src/Python-3.7.9.tgz \
    && yum install -y zip unzip \
    && yum install -y libaio

RUN pip3.7 install fastapi uvicorn

COPY ./requirements.txt /app/requirements.txt

WORKDIR $WORKDIR

RUN pip3.7 install -r requirements.txt

COPY . $WORKDIR


# create dirs to which oracle client installation will be made

RUN if [ "$INIT" = "" ] ; \
    then : ; \
    else python3.7 db_init.py ; \
    fi


RUN adduser -u 99999 user && chmod -R 777 $WORKDIR

USER user

# create env var called init. call custom script in cmd that checks if INIT is defined - run init scripts that start up else - start up

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
