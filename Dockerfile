FROM weboftrust/keri:orig

RUN apt-get update && apt-get install -y openssh-server

RUN groupadd sftp_users

RUN mkdir /var/run/sshd
RUN mkdir -p /data
RUN chown -R root:sftp_users /data/
RUN echo 'root:PASSWORD' | chpasswd

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN echo $'Match Group sftp_users\n\tForceCommand internal-sftp' >> /etc/ssh/sshd_config

EXPOSE 22

WORKDIR /usr/local/var
RUN mkdir kassh
COPY . kassh/

WORKDIR /usr/local/var/kassh

RUN pip install -r requirements.txt

CMD ["/usr/sbin/sshd", "-D"]