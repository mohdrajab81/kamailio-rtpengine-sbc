#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: write_tshark_views.sh <mode> <artifact_dir>"
    exit 1
fi

MODE="$1"
ART_DIR="$2"
PCAP="$ART_DIR/signaling.pcap"

if [[ ! -f "$PCAP" ]]; then
    echo "pcap_not_found: $PCAP"
    exit 1
fi

tshark -r "$PCAP" -Y 'sip' \
    -T fields -E header=y -E separator=$'\t' -E quote=d \
    -e frame.number -e frame.time_relative -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e _ws.col.Info \
    > "$ART_DIR/tshark-summary.tsv"

case "$MODE" in
    pai|from-only)
        tshark -r "$PCAP" \
            -Y 'sip.Method == "INVITE" && ip.src == 10.10.10.10' \
            -V > "$ART_DIR/tshark-proof.txt"
        ;;
    untrusted)
        tshark -r "$PCAP" \
            -Y 'sip && (ip.src == 10.10.10.99 || sip.Status-Code == 403)' \
            -V > "$ART_DIR/tshark-proof.txt"
        ;;
    pike)
        tshark -r "$PCAP" \
            -Y 'sip.Status-Code == 503' \
            -T fields -E header=y -E separator=$'\t' -E quote=d \
            -e frame.number -e frame.time_relative -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e _ws.col.Info \
            > "$ART_DIR/tshark-503.tsv"

        {
            printf 'carrier_invites='
            tshark -r "$PCAP" -Y 'sip.Method == "INVITE" && ip.src == 10.10.10.20' -T fields -e frame.number | wc -l
            printf 'blocked_503='
            tshark -r "$PCAP" -Y 'sip.Status-Code == 503' -T fields -e frame.number | wc -l
        } > "$ART_DIR/tshark-metrics.txt"
        ;;
    failover)
        tshark -r "$PCAP" \
            -Y 'sip && ((sip.Method == "INVITE" && ip.src == 10.10.10.10) || sip.Status-Code == 503 || sip.Status-Code == 180 || sip.Status-Code == 200)' \
            -V > "$ART_DIR/tshark-proof.txt"
        ;;
    sdp)
        tshark -r "$PCAP" \
            -Y 'sdp || (sip.Method == "INVITE" && sip.msg_hdr contains "Content-Type: application/sdp") || (sip.Status-Code == 200 && sip.msg_hdr contains "Content-Type: application/sdp")' \
            -V > "$ART_DIR/tshark-proof.txt"
        ;;
    cancel)
        tshark -r "$PCAP" \
            -Y 'sip && (sip.Method == "INVITE" || sip.Method == "CANCEL" || sip.Method == "ACK" || sip.Status-Code == 180 || sip.Status-Code == 200 || sip.Status-Code == 408 || sip.Status-Code == 487)' \
            -V > "$ART_DIR/tshark-proof.txt"
        ;;
    *)
        echo "unsupported_mode: $MODE"
        exit 1
        ;;
esac
