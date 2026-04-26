#!/usr/bin/env bash
set -euo pipefail

LAB_ROOT="$HOME/sip-lab"
EVID_ROOT="/mnt/c/Projects/kamailio-rtpengine-sbc/evidence"
TOOL="$LAB_ROOT/tools/write_tshark_views.sh"

run_signaling_test() {
    local test_name="$1"
    local vapi_scenario="$2"
    local carrier_scenario="$3"
    "$LAB_ROOT/run/run_single_call_test.sh" "$test_name" "$vapi_scenario" "$carrier_scenario"
}

printf '[1/7] test01-pai\n'
run_signaling_test "test01-pai" "vapi-ok.xml" "carrier-pai.xml"
"$TOOL" "pai" "$EVID_ROOT/signaling/test01-pai"

printf '[2/7] test02-from-only\n'
run_signaling_test "test02-from-only" "vapi-ok.xml" "carrier-from-only.xml"
"$TOOL" "from-only" "$EVID_ROOT/signaling/test02-from-only"

printf '[3/7] test03-untrusted\n'
"$LAB_ROOT/run/run_untrusted_test.sh"
"$TOOL" "untrusted" "$EVID_ROOT/signaling/test03-untrusted"

printf '[4/7] test04-pike\n'
"$LAB_ROOT/run/run_pike_test.sh"
"$TOOL" "pike" "$EVID_ROOT/signaling/test04-pike"

printf '[5/7] test-failover\n'
"$LAB_ROOT/run/run_failover_test.sh"
"$TOOL" "failover" "$EVID_ROOT/signaling/test-failover"

printf '[6/7] test05-sdp\n'
"$LAB_ROOT/run/run_sdp_test.sh"
"$TOOL" "sdp" "$EVID_ROOT/rtp/test05-sdp"

printf '[7/7] test06-cancel\n'
"$LAB_ROOT/run/run_cancel_test.sh"
"$TOOL" "cancel" "$EVID_ROOT/rtp/test06-cancel"
