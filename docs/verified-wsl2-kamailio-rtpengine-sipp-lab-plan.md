# Verified WSL2 SIP Lab Plan for Etisalat -> Kamailio/RTPEngine -> Vapi

## Purpose

This document is the verified execution plan for building a local WSL2 lab that simulates:

- fake Etisalat carrier SIP ingress
- Kamailio SBC logic
- RTPEngine SDP/media anchoring
- fake Vapi upstream SBCs with dispatcher failover

## Related Documents

- [etisalat-vapi-sbc-solution-design.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/etisalat-vapi-sbc-solution-design.md) for the intended production architecture and solution design
- [implementation-evidence-log.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/implementation-evidence-log.md) for execution results and artifacts
- [proposal-safe-production-notes.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/proposal-safe-production-notes.md) for production-facing claim boundaries

It is based on the earlier `updated-wsl2-kamailio-rtpengine-sipp-lab-plan.md`, but corrected for the **actual machine state** on this system before implementation.

## Verified Environment

These checks were run on this machine before implementation:

- Windows host has `WSL2` installed
- default WSL distro is `Ubuntu`
- default WSL version is `2`
- distro version is `Ubuntu 24.04.4 LTS`
- WSL username is `dev`
- Ubuntu repositories expose:
  - `kamailio`
  - `kamailio-extra-modules`
  - `kamailio-utils-modules`
  - `kamcli`
  - `sngrep`
  - `rtpengine-daemon`
- Ubuntu 24.04 does **not** expose a package literally named `sipp`; the SIPp implementation is packaged as `sip-tester`

## Verified Corrections to the Prior Plan

### Package corrections

Use this package set on Ubuntu 24.04:

```bash
sudo apt update
sudo apt install -y \
  kamailio \
  kamailio-extra-modules \
  kamailio-utils-modules \
  kamcli \
  sip-tester \
  sngrep \
  tcpdump \
  net-tools \
  iproute2 \
  ngrep \
  python3 \
  python3-pip \
  netcat-openbsd \
  procps
```

Notes:

- `sip-tester` is the correct Ubuntu 24.04 package for SIPp.
- `kamailio-utils` should be replaced by `kamailio-utils-modules` and `kamcli`.
- `rtpengine` should **not** be installed as the default metapackage first in WSL2 because it pulls in `rtpengine-kernel-dkms` and related kernel-mode pieces that are not needed for this userspace lab.
- Prefer `rtpengine-daemon` for the WSL2 lab, or use a source build if the package path fails.

### RTPEngine correction for WSL2

Preferred WSL2 path:

```bash
sudo apt install -y rtpengine-daemon
```

Fallback:

- build the userspace daemon from source
- run with `--table=-1`
- do not target kernel forwarding in WSL2

### Filesystem layout correction

Use two locations:

- WSL runtime workspace: `/home/dev/sip-lab`
- Windows-visible docs and artifacts: `/mnt/c/Users/DELL/Downloads/sip-lab-wsl2`

Reason:

- runtime commands are more reliable in the Linux home directory
- logs, pcaps, config snapshots, and progress documents stay visible from Windows

## Scope

This lab is intended to prove:

- SIP INVITE routing from fake carrier to Kamailio
- ANI extraction from `P-Asserted-Identity`
- fallback ANI extraction from `From`
- `X-Original-Caller` and `X-Original_Caller` header injection
- conditional `From` rewrite
- preservation of the Vapi credential-style Request-URI
- routing through dispatcher `$du`
- rejection of untrusted source IPs
- Pike flood handling
- dispatcher failover from fake Vapi A to fake Vapi B
- RTPEngine SDP rewriting
- RTPEngine cleanup on CANCEL, BYE, and failover

This lab does **not** prove:

- real Etisalat signaling behavior
- real Etisalat ANI placement
- real Vapi credential acceptance
- AWS networking, Elastic IP, or security group behavior
- real carrier-cloud RTP behavior over the public internet

## Lab Topology

Loopback aliases inside WSL2:

```text
10.10.10.20  fake Etisalat carrier
10.10.10.10  Kamailio + RTPEngine SBC
10.10.10.41  fake Vapi SBC A
10.10.10.42  fake Vapi SBC B
10.10.10.99  fake untrusted source
```

Signaling path:

```text
Fake Etisalat SIPp UAC -> Kamailio SBC -> fake Vapi A/B
```

Media path:

```text
Fake Etisalat RTP -> RTPEngine -> fake Vapi RTP
```

## Artifact Strategy

The implementation must produce verifiable artifacts while it runs.

Required artifact classes:

- verified plan document
- implementation evidence log
- generated configs and scripts
- command outputs captured into text files where useful
- Kamailio logs
- RTPEngine logs
- SIPp traces
- packet captures where beneficial

Artifact root on Windows:

```text
C:\Users\DELL\Downloads\sip-lab-wsl2\evidence
```

WSL path:

```text
/mnt/c/Users/DELL/Downloads/sip-lab-wsl2/evidence
```

## Execution Phases

### Phase 1: Workspace bootstrap

Create:

- `/home/dev/sip-lab`
- `/home/dev/sip-lab/kamailio`
- `/home/dev/sip-lab/sipp`
- `/home/dev/sip-lab/tools`
- `/home/dev/sip-lab/run`
- `/mnt/c/Users/DELL/Downloads/sip-lab-wsl2/evidence`

Verification:

- `pwd`
- `ls -la`
- path snapshots copied into the evidence log

### Phase 2: Package installation

Install:

- Kamailio packages
- SIPp package via `sip-tester`
- trace tools
- `rtpengine-daemon` if installable

Verification:

- `kamailio -v`
- `sipp -v` if the binary name is `sipp`
- `command -v sipp`
- `command -v rtpengine`
- package list snapshot via `dpkg -l`

Artifact outputs:

- install transcript
- package availability notes

### Phase 3: Lab scripts and configs

Create:

- loopback alias script
- cleanup script
- dispatcher list
- Kamailio lab config
- SIPp scenarios
- RTP sender helper if needed

Verification:

- config files exist
- `kamailio -c -f ...` passes

Artifact outputs:

- config snapshots
- syntax-check output

### Phase 4: Signaling-only tests

Run:

- healthy fake Vapi test
- PAI ANI extraction test
- From-only fallback test
- untrusted-source rejection test
- Pike flood test
- dispatcher failover test

Verification:

- SIPp traces
- Kamailio logs
- expected response codes
- expected header manipulations

Artifact outputs:

- SIPp `-trace_msg` and `-trace_err`
- Kamailio terminal log capture
- optional pcap for signaling

### Phase 5: RTPEngine and SDP tests

Run:

- RTPEngine in userspace mode
- SDP rewrite test
- optional RTP packet flow proof
- CANCEL cleanup test

Verification:

- `rtpengine_offer` and `rtpengine_answer` visible in Kamailio logs
- rewritten `c=` and `m=` lines visible in signaling captures
- RTPEngine logs show offer/answer/delete behavior

Artifact outputs:

- RTPEngine log file
- SDP traces
- optional loopback pcap

## Evidence Capture Rules

For each execution phase:

1. record the exact command
2. record whether it succeeded or failed
3. capture short relevant output
4. record the artifact file path if output was saved externally
5. record the engineering conclusion

This is maintained in the peer document:

`C:\Users\DELL\Downloads\sip-lab-wsl2\docs\implementation-evidence-log.md`

## Initial Command Set

These are the first implementation commands to run in WSL:

```bash
mkdir -p ~/sip-lab/kamailio ~/sip-lab/sipp ~/sip-lab/tools ~/sip-lab/run
sudo -n true
sudo apt update
sudo apt install -y \
  kamailio \
  kamailio-extra-modules \
  kamailio-utils-modules \
  kamcli \
  sip-tester \
  sngrep \
  tcpdump \
  net-tools \
  iproute2 \
  ngrep \
  python3 \
  python3-pip \
  netcat-openbsd \
  procps
sudo apt install -y rtpengine-daemon
```

If `sudo -n true` fails:

- stop and request interactive user approval or password handling

If `rtpengine-daemon` install fails:

- continue with signaling phases first
- switch to the documented source-build fallback for userspace RTPEngine

## Success Criteria

The implementation is successful when all of the following are demonstrated with artifacts:

- Kamailio config syntax validates
- fake carrier can place a successful INVITE through fake Vapi A
- ANI from `P-Asserted-Identity` is extracted and forwarded in custom headers
- ANI fallback from `From` works
- untrusted source receives `403 Forbidden`
- flood test produces Pike blocking behavior
- dispatcher failover reaches fake Vapi B after fake Vapi A failure
- SDP toward fake Vapi is rewritten to the SBC media address/port
- SDP back toward fake carrier is rewritten to the SBC media address/port
- CANCEL path triggers cleanup behavior with evidence in logs

## Current Implementation Status

Current state on this machine:

- environment verification is complete
- corrected Ubuntu 24.04 package set is installed, including `rtpengine-daemon`
- WSL runtime workspace and Windows-visible evidence workspace are in place
- Kamailio config validates successfully with the installed modules
- signaling validation is complete for:
  - PAI ANI extraction
  - From-only ANI fallback
  - untrusted-source rejection
  - Pike blocking
  - dispatcher failover
- RTPEngine validation is complete for:
  - SDP rewriting
  - media anchoring evidence via SDP and RTPEngine logs
- CANCEL cleanup is validated for lab purposes:
  - RTPEngine delete is evidenced
  - the runner now isolates a single upstream peer
  - the observed caller-leg final response is `408 Request Timeout`, which should be reviewed before production use
- tshark-backed revalidation is complete:
  - all active tests were rerun
  - each test now has fresh `tshark` summaries or proofs in its evidence folder
  - current conclusions are based on packet-level validation as well as application logs

Representative artifact locations:

- [implementation-evidence-log.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/implementation-evidence-log.md)
- [revalidate_with_tshark.sh](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/run/revalidate_with_tshark.sh)
- [signaling failover proof](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/signaling/test-failover/pcap-summary.txt)
- [signaling failover tshark summary](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/signaling/test-failover/tshark-summary.tsv)
- [SDP rewrite proof](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/test05-sdp/pcap-ascii.txt)
- [SDP rewrite tshark proof](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/test05-sdp/tshark-proof.txt)
- [CANCEL cleanup proof](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/test06-cancel/rtpengine.log)
