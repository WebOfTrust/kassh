FROM gleif/keri:latest

RUN apt-get update && apt-get install -y openssh-server

RUN mkdir /var/run/sshd

RUN echo 'root:PASSWORD' | chpasswd

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

EXPOSE 22

WORKDIR /usr/local/var
RUN mkdir kassh
COPY . kassh/

WORKDIR /usr/local/var/kassh

RUN pip install -r requirements.txt

CMD ["/usr/sbin/sshd", "-D"]