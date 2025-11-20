FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake pkg-config libssl-dev libzmq3-dev libunbound-dev libsodium-dev \
    libunwind8-dev liblzma-dev libreadline6-dev libexpat1-dev libpgm-dev \
    qttools5-dev-tools libhidapi-dev libusb-1.0-0-dev \
    libprotobuf-dev protobuf-compiler libudev-dev libzstd-dev \
    libboost-chrono-dev libboost-date-time-dev libboost-filesystem-dev \
    libboost-locale-dev libboost-program-options-dev libboost-regex-dev \
    libboost-serialization-dev libboost-system-dev libboost-thread-dev \
    python3 python3-pip python3-all python3-pybind11 python3-pytest \
    ccache doxygen graphviz git curl autoconf libtool gperf nettle-dev libevent-dev \
    debhelper bison flex wget \
 && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/libexpat/libexpat/releases/download/R_2_4_8/expat-2.4.8.tar.bz2 \
 && tar -xf expat-2.4.8.tar.bz2 \
 && cd expat-2.4.8 \
 && ./configure --enable-static --disable-shared \
 && make -j$(nproc) && make install \
 && cd .. && rm -rf expat-2.4.8*

RUN wget https://www.nlnetlabs.nl/downloads/unbound/unbound-1.22.0.tar.gz \
 && tar xzf unbound-1.22.0.tar.gz \
 && cd unbound-1.22.0 \
 && ./configure --with-libexpat=/usr --with-ssl=/usr --enable-static-exe \
 && make -j$(nproc) && make install \
 && cd .. && rm -rf unbound-1.22.0*

RUN git config --global --add safe.directory '*'

WORKDIR /monero-python

COPY . .

RUN cd ./external/monero-cpp/external/monero-project/ \
 && git submodule update --init --force \
 && mkdir -p build/release \
 && cd build/release \
 && cmake -DSTATIC=ON -DBUILD_64=ON -DCMAKE_BUILD_TYPE=Release ../../ \
 && make wallet cryptonote_protocol \
 && cd ../../../../../../

RUN cd ./external/monero-cpp/ \
 && mkdir -p build \
 && cd build \
 && cmake .. \
 && cmake --build . \
 && make . \
 && cp libmonero-cpp* /usr/lib/ \
 && cd ../../../

RUN pip3 install . --break-system-packages

ENTRYPOINT ["./entrypoint.sh"]
