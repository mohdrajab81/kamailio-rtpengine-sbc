# SIP Lab WSL2

Local WSL2 lab validating the Etisalat -> Kamailio/RTPEngine -> Vapi SBC architecture,
with documentation, lab sources, and packet-level evidence artifacts.

## Documents

| File | Purpose |
| --- | --- |
| [docs/etisalat-vapi-sbc-solution-design.md](docs/etisalat-vapi-sbc-solution-design.md) | Production architecture, design decisions, candidate configs, security model, and lab validation summary. |
| [docs/wsl2-lab-build-record.md](docs/wsl2-lab-build-record.md) | Lab build record and rebuild guide — environment, topology, file map, test suite, and known issues. |
| [docs/implementation-evidence-log.md](docs/implementation-evidence-log.md) | Per-test execution record and packet-level evidence map. |

## Repository Layout

```text
docs/       Solution design, lab build record, evidence log
lab/
  kamailio/ Kamailio lab config and dispatcher list
  sipp/     SIPp carrier and Vapi UAS scenarios
  run/      Test runner scripts
  tools/    Loopback setup, cleanup, tshark, RTP helper, PDF generator
evidence/
  signaling/ Per-test artifacts for signaling-only tests
  rtp/       Per-test artifacts for RTPEngine and media tests
```

## What The Lab Validates

- ANI extraction from `P-Asserted-Identity` with fallback to `From`
- Custom ANI header injection (`X-Original-Caller` / `X-Original_Caller`)
- Conditional `From` rewrite when PAI differs from inbound `From`
- Source-IP trust enforcement — untrusted source receives `403 Forbidden`
- Pike rate limiting — flood traffic produces `503 Rate Limit Exceeded`
- Dispatcher failover from Vapi A (503) to Vapi B (200 OK)
- RTPEngine SDP rewrite and media anchoring
- Upstream `CANCEL` propagation and RTPEngine cleanup

## Known Lab Issue

The CANCEL test proves upstream teardown and RTPEngine cleanup, but the caller leg currently
receives `408 Request Timeout` instead of a relayed `487 Request Terminated`. This must be
resolved before production. See the solution design for investigation directions.

## What Still Needs Production Confirmation

- Etisalat signaling IP list and transport (UDP/TCP/TLS)
- Etisalat ANI placement in live traffic
- Vapi credential acceptance and inbound gateway matching
- AWS public/private address handling with Elastic IP
- Production SIP timer values and dispatcher health-check settings
- Canonical custom ANI header name confirmed by Vapi
- Caller-leg CANCEL final-response behavior

## How To Run The Lab

```bash
# Sync lab files from Windows into WSL runtime workspace
bash /mnt/c/Users/DELL/Downloads/sip-lab-wsl2/lab/tools/sync_lab_to_wsl.sh

# Verify Kamailio config syntax
kamailio -c -f ~/sip-lab/kamailio/kamailio-lab.cfg

# Run all seven tests with tshark revalidation
bash ~/sip-lab/run/revalidate_with_tshark.sh
```
