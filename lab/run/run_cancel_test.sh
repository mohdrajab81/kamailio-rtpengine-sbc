#!/usr/bin/env bash
set -euo pipefail

TEST_NAME="test06-cancel"
LAB_ROOT="$HOME/sip-lab"
TEST_DIR="$LAB_ROOT/run/$TEST_NAME"
ART_DIR="/mnt/c/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/$TEST_NAME"
DISPATCHER_FILE="$LAB_ROOT/kamailio/dispatcher.list"
DISPATCHER_BACKUP="$TEST_DIR/dispatcher.list.bak"

mkdir -p "$TEST_DIR" "$ART_DIR"
cd "$TEST_DIR"
find "$TEST_DIR" -mindepth 1 -maxdepth 1 -type f -delete 2>/dev/null || true
find "$ART_DIR" -mindepth 1 -maxdepth 1 -type f -delete 2>/dev/null || true

restore_dispatcher() {
    if [ -f "$DISPATCHER_BACKUP" ]; then
        cp "$DISPATCHER_BACKUP" "$DISPATCHER_FILE"
    fi
}

trap restore_dispatcher EXIT

"$LAB_ROOT/tools/cleanup.sh" >/dev/null 2>&1 || true
"$LAB_ROOT/tools/add-lab-ips.sh" >/dev/null

cp "$DISPATCHER_FILE" "$DISPATCHER_BACKUP"
cat > "$DISPATCHER_FILE" <<'EOF'
# setid destination                              flags priority attrs
1 sip:10.10.10.41:5070;transport=udp            0     10       duid=vapi-a
EOF

nohup sudo rtpengine \
  --interface=10.10.10.10 \
  --listen-ng=127.0.0.1:2223 \
  --listen-cli=127.0.0.1:9901 \
  --port-min=40000 \
  --port-max=40100 \
  --table=-1 \
  --foreground \
  --log-stderr > rtpengine.log 2>&1 &
RPID=$!

nohup sudo kamailio -DD -E -f "$LAB_ROOT/kamailio/kamailio-lab.cfg" > kamailio.log 2>&1 &
KPID=$!

nohup sipp -sf "$LAB_ROOT/sipp/vapi-delayed-cancel.xml" -i 10.10.10.41 -p 5070 -m 1 -trace_msg -trace_err > vapi-a.out 2>&1 &
APID=$!

nohup sudo tcpdump -ni lo -w signaling.pcap "udp port 5060 or udp port 5070 or udp port 5080 or udp port 5064 or udp portrange 40000-40100" > tcpdump.out 2>&1 &
TPID=$!

sleep 2

if ! ps -p "$RPID" >/dev/null 2>&1; then
    echo "rtpengine_failed_to_start"
    tail -n 80 rtpengine.log || true
    exit 1
fi

if ! ps -p "$KPID" >/dev/null 2>&1; then
    echo "kamailio_failed_to_start"
    tail -n 80 kamailio.log || true
    exit 1
fi

RC=0
sipp 10.10.10.10:5060 -sf "$LAB_ROOT/sipp/carrier-cancel.xml" -i 10.10.10.20 -p 5062 -m 1 -trace_msg -trace_err > carrier.out 2>&1 || RC=$?

sleep 2

sudo kill -INT "$TPID" >/dev/null 2>&1 || true
kill "$APID" >/dev/null 2>&1 || true
wait "$APID" || true
sudo pkill -f "kamailio -DD -E -f $LAB_ROOT/kamailio/kamailio-lab.cfg" >/dev/null 2>&1 || true
sudo pkill -f "rtpengine --interface=10.10.10.10" >/dev/null 2>&1 || true
sleep 1

tcpdump -nn -r signaling.pcap > pcap-summary.txt 2>&1 || true
tcpdump -A -s 0 -nn -r signaling.pcap > pcap-ascii.txt 2>&1 || true
cp -a "$TEST_DIR"/. "$ART_DIR"/

printf 'test_name=%s\n' "$TEST_NAME"
printf 'carrier_rc=%s\n' "$RC"
printf 'artifact_dir=%s\n' "$ART_DIR"
ls -1 "$ART_DIR"
