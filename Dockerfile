FROM ubuntu:18.04
MAINTAINER mikhailmironov@mikhailmironov.ru

ENV PLAYLIST http://91.92.66.82/trash/ttv-list/as.json
ENV DEBIAN_FRONTEND noninteractive
ENV LIVE_MEM_CACHE_SIZE 1000000000000

WORKDIR /opt/acestream
RUN apt-get update && \
apt-get install -y curl net-tools libssl1.0.0 libpython2.7 python-setupdocs python-apsw python-libxslt1 python-pip && pip install flask

# http://wiki.acestream.org/wiki/index.php/Download
RUN curl -O http://acestream.org/downloads/linux-beta/acestream_3.1.35_ubuntu_18.04_x86_64.tar.gz && \
tar -xf acestream_3.1.35_ubuntu_18.04_x86_64.tar.gz && \
rm acestream_3.1.35_ubuntu_18.04_x86_64.tar.gz

COPY ace-proxy.py ./
COPY index.html.j2 ./templates/


CMD while :; do find /tmp -type f -name "*.ts" -mmin +5 -delete && sleep 30; done & \
python ./ace-proxy.py & \
./start-engine --live-cache-type memory --live-mem-cache-size ${LIVE_MEM_CACHE_SIZE} --enable-profiler 1 --upload-limit 10 --client-console --http-port=6878 --log-stdout --log-stdout-level debug

EXPOSE 5000