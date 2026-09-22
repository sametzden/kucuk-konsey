#!/usr/bin/env bash
# Uzak borsa MCP sunucusunu oturumdan ÖNCE uyandırır.
#
# Neden gerekli: sunucu kullanılmadığında sıfıra iniyor. İlk istek onu uyandırır, uyanana kadar
# öndeki yönlendirici "503 no available server" döner (ölçülen: ilk istek ~13 sn, sonrakiler <1 sn).
# Claude Code oturum açarken MCP sunucularına arka planda bağlanır; sunucu o an uykudaysa bağlantı
# kurulamaz ve mcp__borsa__* araçları o oturum boyunca HİÇ görünmez. Ajan "veriyi alamadım" değil,
# "aracı göremedim" durumuna düşer ve tekrar deneyemez. 22.09.2026'da tam olarak bu oldu.
#
# Kullanım:  ./scripts/uyandir.sh  &&  claude

set -uo pipefail

URL="${BORSA_MCP_URL:-https://borsa.surucu.dev/mcp}"
DENEME="${1:-6}"
kod=""

for ((i = 1; i <= DENEME; i++)); do
	kod=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" \
		-H 'Content-Type: application/json' \
		-H 'Accept: application/json, text/event-stream' \
		-d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
		--max-time 30)

	if [[ "$kod" == "200" ]]; then
		echo "✅ borsa sunucusu uyanık (HTTP 200, $i. denemede). Oturumu şimdi açabilirsin."
		exit 0
	fi

	echo "⏳ deneme $i/$DENEME: HTTP $kod — henüz uyanmadı, 5 sn sonra tekrar"
	sleep 5
done

echo "❌ borsa sunucusu $DENEME denemede uyanmadı (son yanıt: HTTP $kod)." >&2
echo "   Oturumu açabilirsin ama mcp__borsa__* araçları eksik olabilir; içeride /mcp ile doğrula." >&2
exit 1
