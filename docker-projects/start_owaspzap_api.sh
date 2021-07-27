docker run -u zap --name owasp-zap-api --restart always -p 8090:8090 -i owasp/zap2docker-stable \
zap.sh -daemon -host 0.0.0.0 -port 8090 -config api.addrs.addr.name=.* \
-config api.addrs.addr.regex=true -config api.disablekey=true -silent \
-addonupdate -nostdout  -quickprogress >> /dev/null 2>&1 &
