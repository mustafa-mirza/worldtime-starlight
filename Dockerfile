FROM debian:buster
#FROM debian:bookworm
#RUN echo 'deb http://ftp.cn.debian.org/debian buster main' > /etc/apt/sources.list
RUN apt-get -y update --fix-missing
MAINTAINER Avocado

#Payment App installation:
COPY jre1.8.0_102/ /usr/lib/jvm/java-8-openjdk-amd64/jre/
RUN chmod -R 755 /usr/lib/jvm/java-8-openjdk-amd64/jre/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/jre

COPY target/spring-boot-world-time-0.0.1-SNAPSHOT.jar /
#COPY paymentOptionsVault-0.0.1-SNAPSHOT.war /

#-------------------------------------------------------------------------------------
#Plugin Installtion START
#-------------------------------------------------------------------------------------
ARG ADPL_PLUGIN_PACKAGE
RUN apt-get install -y net-tools procps
# ASP installation and configuration
#COPY avcdadpl_3.1.55.debian12_amd64.deb  /
COPY avcdadpl_3.1.55.debian10_amd64.deb  /

COPY metadata.json /
RUN export AVCD_METADATA_FILENAME=/metadata.json

#Manual Install ASP
#RUN apt-get install -y /avcdadpl_3.1.55.debian12_amd64.deb
RUN apt-get install -y /avcdadpl_3.1.55.debian10_amd64.deb
RUN /opt/avcd/bin/avocado container-enable

ENTRYPOINT [ "/opt/avcd/bin/avocado-docker-start.sh" ]
#-------------------------------------------------------------------------------------
#Plugin Installtion END
#-------------------------------------------------------------------------------------
# Replace <APPLICATION_START_COMMAND> with your Application start command in below entrypoint
CMD ["/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java", "-jar", "/spring-boot-world-time-0.0.1-SNAPSHOT.jar"]
