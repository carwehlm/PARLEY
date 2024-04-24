FROM debian:bookworm

ENV PRISM_JAVAMAXMEM=4g \
    PRISM_JAVASTACKSIZE=1g

# architecture = [x86|arm]
ARG prism_version=4.8.1 \
    prism_arch=x86

RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && apt-get install -y \
                    wget \
                    nano \
                    git \
                    default-jdk \
                    maven \
                    python3 \
                    python3-numpy \
                    python3-seaborn \
                    python3-matplotlib \
                    python3-scipy \
                    python3-deap \
 && rm -rf /var/lib/apt/lists/*

# install prism
RUN wget -q -O - https://www.prismmodelchecker.org/dl/prism-${prism_version}-linux64-${prism_arch}.tar.gz | tar -xzf - -C /opt \
 && mv /opt/prism-* /opt/prism \
 && cd /opt/prism \
 && /opt/prism/install.sh \
 && ln -s /opt/prism/bin/prism /usr/local/bin/prism \
 && ln -s /opt/prism/bin/xprism /usr/local/bin/xprism \
 && ln -s /opt/prism/bin/ngprism /usr/local/bin/ngprism \
 && echo 'export PATH=${PATH}:/opt/prism/bin' >> ~/.bashrc
