FROM golang:1.27.1-alpine3.24

WORKDIR /app

COPY . .

RUN go mod tidy
RUN go build -o app cmd/api/main.go

EXPOSE 8080

CMD [ "./app" ]