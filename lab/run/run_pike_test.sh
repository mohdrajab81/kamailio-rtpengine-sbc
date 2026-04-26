#!/usr/bin/env bash
set -euo pipefail

TEST_NAME="test04-pike"
LAB_ROOT="$HOME/sip-lab"
TEST_DIR="$LAB_ROOT/run/$TEST_NAME"
ART_DIR="/mnt/c/Projects/kamailio-rtpengine-sbc/evidence/signaling/$TEST_NAME"

mkdir -p "$TEST_DIR" "$ART_DIR"
cd "$TEST_DIR"
find "$TEST_DIR" -mindepth 1 -maxdepth 1 -type f -delete 2>/dev/null || true
find "$ART_DIR" -mindepth 1 -maxdepth 1 -type f -delete 2>/dev/null || true

"$LAB_ROOT/tools/cleanup.sh" >/dev/null 2>&1 || true
"$LAB_ROOT/tools/add-lab-ips.sh" >/dev/null

nohup sudo kamailio -DD -E -f "$LAB_ROOT/kamailio/kamailio-lab.cfg" > kamailio.log 2>&1 &
KPID=$!
nohup sipp -sf "$LAB_ROOT/sipp/vapi-ok.xml" -i 10.10.10.41 -p 5070 -m 200 -trace_msg -message_file vapi-a_messages.log -trace_err -error_file vapi-a_errors.log > vapi-a.out 2>&1 &
APID=$!
nohup sipp -sf "$LAB_ROOT/sipp/vapi-ok.xml" -i 10.10.10.42 -p 5080 -m 200 -trace_msg -message_file vapi-b_messages.log -trace_err -error_file vapi-b_errors.log > vapi-b.out 2>&1 &
BPID=$!
nohup sudo tcpdump -ni lo -w signaling.pcap "udp port 5060 or udp port 5070 or udp port 5080" > /dev/null 2>&1 &
TPID=$!

sleep 2

if ! ps -p "$KPID" >/dev/null 2>&1; then
    echo "kamailio_failed_to_start"
    tail -n 80 kamailio.log || true
    exit 1
fi

RC=0
sipp 10.10.10.10:5060 -sf "$LAB_ROOT/sipp/carrier-pai.xml" -i 10.10.10.20 -p 5062 -m 100 -r 50 -rp 1000 -trace_err -error_file carrier_errors.log > carrier.out 2>&1 || RC=$?

sleep 2

sudo kill -INT "$TPID" >/dev/null 2>&1 || true
kill "$APID" >/dev/null 2>&1 || true
kill "$BPID" >/dev/null 2>&1 || true
wait "$APID" || true
wait "$BPID" || true
sudo pkill -f "kamailio -DD -E -f $LAB_ROOT/kamailio/kamailio-lab.cfg" >/dev/null 2>&1 || true
sleep 1

touch carrier_errors.log vapi-a_errors.log vapi-b_errors.log
cp -a "$TEST_DIR"/. "$ART_DIR"/

printf 'test_name=%s\n' "$TEST_NAME"
printf 'carrier_rc=%s\n' "$RC"
printf 'artifact_dir=%s\n' "$ART_DIR"
ls -1 "$ART_DIR"
