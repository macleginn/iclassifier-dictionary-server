FROM golang:1.21-bookworm

# RUN apt-get update
# RUN apt-get install python3 python3-pip git gcc -y
# RUN apt-get install python3-flask python3-gunicorn -y

RUN adduser iclassifier
RUN mkdir /home/iclassifier/src
RUN chmod 777 /home/iclassifier/src
USER iclassifier
ENV HOME /home/iclassifier

# Copy the data
COPY data/dictionary.sqlite $HOME/data/dictionary.sqlite
# Compile the server
COPY src/main.go $HOME/src
WORKDIR $HOME/src
RUN go mod init dictionary
RUN go get -u github.com/mattn/go-sqlite3
RUN go build -o $HOME/main main.go
WORKDIR $HOME
EXPOSE 30000
ENTRYPOINT ["./main"]
