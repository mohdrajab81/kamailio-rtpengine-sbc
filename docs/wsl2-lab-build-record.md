# WSL2 SIP Lab — Build Record and Rebuild Guide

## Purpose

This document records how the local WSL2 SIP lab was built and how to rebuild it on a fresh
machine. It is the operational companion to the solution design and the evidence log.

Related documents:

- [etisalat-vapi-sbc-solution-design.md](etisalat-vapi-sbc-solution-design.md) — production
  architecture, design decisions, and lab validation summary
- [implementation-evidence-log.md](implementation-evidence-log.md) — packet-level artifacts and
  per-test conclusions

## Verified Environment

| Item | Value |
|---|---|
| Host OS | Windows 11 with WSL2 |
| WSL distro | Ubuntu 24.04.4 LTS |
| WSL username | `dev` |
| Kamailio package | `kamailio` (Ubuntu 24.04 repo), observed as 5.7.4 in evidence |
| RTPEngine package | `rtpengine-daemon` (userspace daemon, no kernel module) |
| SIPp package | `sip-tester` (Ubuntu 24.04 name; binary is `sipp`) |

Ubuntu 24.04 does not expose a package literally named `sipp`. The correct package name is
`sip-tester`.

Do not install the broad `rtpengine` metapackage in WSL2. It pulls in `rtpengine-kernel-dkms`
and DKMS build dependencies that are not needed for a userspace lab and can fail in WSL2.

## Filesystem Layout

Two locations are used intentionally:

| Location | Purpose |
|---|---|
| `/home/dev/sip-lab` | WSL runtime workspace — Kamailio, SIPp, and run scripts work reliably here |
| `/mnt/c/Users/DELL/Downloads/sip-lab-wsl2` | Windows-visible root — configs, evidence, and docs stay accessible from Windows |

Lab source files live under `sip-lab-wsl2/lab/`. Evidence artifacts are written under
`sip-lab-wsl2/evidence/`. The run scripts copy their output to both locations.

## Lab Topology

Loopback aliases on the WSL2 loopback interface:

```text
10.10.10.10   Kamailio SBC + RTPEngine
10.10.10.20   fake Etisalat carrier (SIPp UAC)
10.10.10.41   fake Vapi SBC A  (SIPp UAS, port 5070)
10.10.10.42   fake Vapi SBC B  (SIPp UAS, port 5080)
10.10.10.99   fake untrusted source (used only in trust-rejection test)
```

Signaling path:

```text
SIPp UAC (10.10.10.20) -> Kamailio (10.10.10.10:5060) -> SIPp UAS A or B
```

Media path (RTP tests only):

```text
SIPp UAC RTP -> RTPEngine (10.10.10.10, ports 40000-40100) -> SIPp UAS RTP
```

## Scope

### What the lab proves

- SIP INVITE routing from fake carrier through Kamailio to fake Vapi
- ANI extraction from `P-Asserted-Identity`
- ANI fallback from `From` when PAI is absent
- Injection of `X-Original-Caller` and `X-Original_Caller` custom headers
- Conditional `From` rewrite when PAI user differs from From user
- Preservation of the Vapi credential-style Request-URI through dispatcher `$du`
- Source-IP trust enforcement — untrusted source receives `403 Forbidden`
- Pike rate limiting — flood traffic produces `503 Rate Limit Exceeded`
- Dispatcher failover from Vapi A (returning 503) to Vapi B (returning 200 OK)
- RTPEngine SDP rewrite — `c=` and `m=` lines rewritten to SBC address/ports
- RTPEngine cleanup on CANCEL, BYE, and failover paths
- Caller-side CANCEL handling — CANCEL receives `200 canceling`, then the INVITE receives final `487 Request Terminated`

### What the lab does not prove

- Real Etisalat signaling, source IPs, transport, or ANI placement
- Real Vapi credential acceptance or inbound gateway matching
- AWS public/private address handling or Elastic IP behavior
- TLS signaling
- Production timer values (lab uses aggressive values for fast simulation)
- Dispatcher health probing (disabled in lab with `ds_ping_interval=0`)

## How to Rebuild on a Fresh WSL2 Machine

### Step 1 — Bootstrap workspace

```bash
mkdir -p ~/sip-lab/kamailio ~/sip-lab/sipp ~/sip-lab/tools ~/sip-lab/run
```

### Step 2 — Install packages

```bash
sudo apt update
sudo apt install -y \
  kamailio \
  kamailio-extra-modules \
  kamailio-utils-modules \
  kamcli \
  rtpengine-daemon \
  sip-tester \
  sngrep \
  tcpdump \
  tshark \
  net-tools \
  iproute2 \
  ngrep \
  python3 \
  python3-pip \
  netcat-openbsd \
  procps \
  curl \
  jq \
  ca-certificates
```

Package notes:

| Package | Why needed |
|---|---|
| `kamailio` + extra/utils modules | Core SBC and all required modules |
| `kamcli` | `kamcmd` CLI for dispatcher and pike inspection |
| `rtpengine-daemon` | Userspace RTPEngine daemon; do not use `rtpengine` metapackage |
| `sip-tester` | Provides the `sipp` binary for carrier and Vapi simulation |
| `tshark` | Packet-level evidence; used by `write_tshark_views.sh` and `revalidate_with_tshark.sh` |
| `python3` | Required for `send_rtp.py` and `generate_evidence_pdf.py` |
| `netcat-openbsd` | Manual SIP/UDP probing during development |
| `procps` | Provides `ps` used in run script health checks |

### Step 3 — Sync lab files from Windows

Run from WSL:

```bash
bash /mnt/c/Users/DELL/Downloads/sip-lab-wsl2/lab/tools/sync_lab_to_wsl.sh
```

This copies the lab configs, SIPp scenarios, and scripts into `~/sip-lab`.

### Step 4 — Verify Kamailio config syntax

```bash
kamailio -c -f ~/sip-lab/kamailio/kamailio-lab.cfg
```

This must pass before running any test.

### Step 5 — Run the full test suite

```bash
bash ~/sip-lab/run/revalidate_with_tshark.sh
```

This runs all seven tests in sequence and generates tshark evidence for each.

## Lab File Map

### Tools

| File | What it does |
|---|---|
| [lab/tools/add-lab-ips.sh](../lab/tools/add-lab-ips.sh) | Adds all five loopback aliases to the `lo` interface. Run once before starting any test. |
| [lab/tools/cleanup.sh](../lab/tools/cleanup.sh) | Kills all lab processes (sipp, kamailio, rtpengine, tcpdump) and removes loopback aliases. Run between tests or when the lab is in a dirty state. |
| [lab/tools/sync_lab_to_wsl.sh](../lab/tools/sync_lab_to_wsl.sh) | Copies lab source files from the Windows directory into `~/sip-lab` in WSL. |
| [lab/tools/send_rtp.py](../lab/tools/send_rtp.py) | Sends synthetic G.711-shaped RTP packets to a given IP and port. Used for manual RTP flow testing. Usage: `python3 send_rtp.py <dst_ip> <dst_port> <packet_count>` |
| [lab/tools/write_tshark_views.sh](../lab/tools/write_tshark_views.sh) | Generates tshark summaries and proof files from a test's pcap. Called by the revalidation runner after each test. |
| [lab/tools/generate_evidence_pdf.py](../lab/tools/generate_evidence_pdf.py) | Generates a PDF evidence report from collected artifact files. |

### Kamailio config and dispatcher

| File | What it does |
|---|---|
| [lab/kamailio/kamailio-lab.cfg](../lab/kamailio/kamailio-lab.cfg) | Full Kamailio lab config. Contains all routing logic, ANI extraction, trust checks, dispatcher, RTPEngine integration, and Pike. |
| [lab/kamailio/dispatcher.list](../lab/kamailio/dispatcher.list) | Dispatcher destination list pointing to fake Vapi A (10.10.10.41:5070) and fake Vapi B (10.10.10.42:5080). |

### SIPp scenarios

| File | Role |
|---|---|
| [lab/sipp/carrier-pai.xml](../lab/sipp/carrier-pai.xml) | Carrier UAC — sends INVITE with `P-Asserted-Identity` carrying ANI. |
| [lab/sipp/carrier-from-only.xml](../lab/sipp/carrier-from-only.xml) | Carrier UAC — sends INVITE with ANI only in `From`, no PAI. |
| [lab/sipp/carrier-pai-sdp.xml](../lab/sipp/carrier-pai-sdp.xml) | Carrier UAC with SDP — used in SDP rewrite tests. |
| [lab/sipp/carrier-cancel.xml](../lab/sipp/carrier-cancel.xml) | Carrier UAC — sends INVITE then CANCEL. |
| [lab/sipp/vapi-ok.xml](../lab/sipp/vapi-ok.xml) | Vapi UAS — accepts INVITE and returns `200 OK`. |
| [lab/sipp/vapi-503.xml](../lab/sipp/vapi-503.xml) | Vapi UAS — rejects INVITE with `503 Service Unavailable`. Used in failover test. |
| [lab/sipp/vapi-sdp-answer.xml](../lab/sipp/vapi-sdp-answer.xml) | Vapi UAS — accepts INVITE and returns `200 OK` with SDP answer. Used in SDP rewrite tests. |
| [lab/sipp/vapi-delayed-cancel.xml](../lab/sipp/vapi-delayed-cancel.xml) | Vapi UAS — delays response long enough for the carrier-side CANCEL to arrive. Used in CANCEL test. |

### Run scripts

| File | Test name | What it proves |
|---|---|---|
| [lab/run/run_single_call_test.sh](../lab/run/run_single_call_test.sh) | Generic runner | Accepts test name, Vapi scenario, and carrier scenario as arguments. Starts Kamailio, two Vapi UAS instances, tcpdump, sends the carrier call, collects artifacts. |
| [lab/run/run_failover_test.sh](../lab/run/run_failover_test.sh) | `test-failover` | Vapi A returns 503, Vapi B returns 200 OK. Proves dispatcher failover retries the second destination. |
| [lab/run/run_sdp_test.sh](../lab/run/run_sdp_test.sh) | `test05-sdp` | Starts RTPEngine in userspace mode alongside Kamailio. Proves SDP `c=` and `m=` lines are rewritten to the SBC address and port range. |
| [lab/run/run_cancel_test.sh](../lab/run/run_cancel_test.sh) | `test06-cancel` | Temporarily rewrites dispatcher to a single upstream peer using `vapi-delayed-cancel.xml`. Proves upstream CANCEL propagation, caller-side final `487`, and RTPEngine cleanup. Restores dispatcher on exit. |
| [lab/run/run_untrusted_test.sh](../lab/run/run_untrusted_test.sh) | `test03-untrusted` | Sends INVITE from `10.10.10.99` (not in trusted list). Proves source-IP rejection returns `403 Forbidden`. |
| [lab/run/run_pike_test.sh](../lab/run/run_pike_test.sh) | `test04-pike` | Sends 100 calls at 50 calls/second from the trusted source. Proves Pike blocks the flood with `503 Rate Limit Exceeded`. |
| [lab/run/revalidate_with_tshark.sh](../lab/run/revalidate_with_tshark.sh) | All tests | Runs all seven tests in sequence. After each test, calls `write_tshark_views.sh` to generate tshark evidence. Use this as the single revalidation entry point. |

## RTPEngine Startup Parameters

The RTP tests start RTPEngine directly with:

```bash
sudo rtpengine \
  --interface=10.10.10.10 \
  --listen-ng=127.0.0.1:2223 \
  --listen-cli=127.0.0.1:9901 \
  --port-min=40000 \
  --port-max=40100 \
  --table=-1 \
  --foreground \
  --log-stderr
```

`--table=-1` disables kernel forwarding mode. This is intentional — userspace-only mode is
sufficient for this lab and required for WSL2 where kernel module loading is not available.

## Success Criteria

The lab is considered valid when all of the following are demonstrated with artifacts:

- [x] Kamailio config syntax validates with `kamailio -c -f`
- [x] test01-pai: ANI extracted from `P-Asserted-Identity` and forwarded in custom headers
- [x] test02-from-only: ANI fallback from `From` works when PAI is absent
- [x] test03-untrusted: untrusted source receives `403 Forbidden`
- [x] test04-pike: flood traffic produces `503 Rate Limit Exceeded` blocks
- [x] test-failover: dispatcher retries Vapi B after Vapi A returns 503
- [x] test05-sdp: SDP `c=` and `m=` lines rewritten to SBC address in both directions
- [x] test06-cancel: upstream receives CANCEL, caller receives final `487 Request Terminated`, and RTPEngine session is cleaned up

## CANCEL Validation Detail

The CANCEL test currently shows:

```text
caller CANCEL
upstream CANCEL
caller leg: 200 canceling for CANCEL
upstream:   200 OK for CANCEL, then 487 Request Terminated
caller leg: 487 Request Terminated for INVITE
```

The carrier SIPp scenario uses the same Via branch for INVITE, CANCEL, and the non-2xx ACK.
This is required so Kamailio can match the CANCEL to the original INVITE transaction.

## Implementation Status

All success criteria above are currently met.

Tshark-backed revalidation has been completed for all tests. Each evidence folder contains
fresh tshark summaries and packet-level proof files generated by `revalidate_with_tshark.sh`.

Key artifact locations:

| Artifact | Path |
|---|---|
| PAI extraction proof | [evidence/signaling/test01-pai/tshark-proof.txt](../evidence/signaling/test01-pai/tshark-proof.txt) |
| From-only fallback proof | [evidence/signaling/test02-from-only/tshark-proof.txt](../evidence/signaling/test02-from-only/tshark-proof.txt) |
| Untrusted rejection proof | [evidence/signaling/test03-untrusted/tshark-proof.txt](../evidence/signaling/test03-untrusted/tshark-proof.txt) |
| Pike blocking metrics | [evidence/signaling/test04-pike/tshark-metrics.txt](../evidence/signaling/test04-pike/tshark-metrics.txt) |
| Pike 503 frame list | [evidence/signaling/test04-pike/tshark-503.tsv](../evidence/signaling/test04-pike/tshark-503.tsv) |
| Failover proof | [evidence/signaling/test-failover/tshark-summary.tsv](../evidence/signaling/test-failover/tshark-summary.tsv) |
| SDP rewrite proof | [evidence/rtp/test05-sdp/tshark-proof.txt](../evidence/rtp/test05-sdp/tshark-proof.txt) |
| CANCEL cleanup log | [evidence/rtp/test06-cancel/rtpengine.log](../evidence/rtp/test06-cancel/rtpengine.log) |
| CANCEL tshark summary | [evidence/rtp/test06-cancel/tshark-summary.tsv](../evidence/rtp/test06-cancel/tshark-summary.tsv) |
| Full evidence log | [docs/implementation-evidence-log.md](implementation-evidence-log.md) |
