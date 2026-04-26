# WSL2 SIP Lab Implementation Evidence Log

## Purpose

This document records the useful outputs, decisions, corrections, and artifacts produced while implementing the WSL2 Kamailio/RTPEngine/SIPp lab.

## Related Documents

- [etisalat-vapi-sbc-solution-design.md](etisalat-vapi-sbc-solution-design.md) for architecture intent and solution design
- [wsl2-lab-build-record.md](wsl2-lab-build-record.md) for the rebuild guide, topology, and current test suite

## Artifact Roots

- Windows docs: `C:\Projects\kamailio-rtpengine-sbc\docs`
- Windows evidence: `C:\Projects\kamailio-rtpengine-sbc\evidence`
- WSL runtime: `/home/dev/sip-lab`
- WSL evidence mirror: `/mnt/c/Projects/kamailio-rtpengine-sbc/evidence`

## Log Format

Each entry should record:

- timestamp or execution order
- objective
- command
- key output
- result
- artifact path
- conclusion

## Entry 001: Baseline environment verification

Objective:

- verify that WSL2 is installed and suitable for the local lab

Commands:

```powershell
wsl.exe -l -v
wsl.exe --status
wsl.exe -d Ubuntu -- bash -lc "cat /etc/os-release"
wsl.exe -d Ubuntu -- bash -lc "whoami"
```

Key output:

```text
Ubuntu    Stopped    2
Default Distribution: Ubuntu
Default Version: 2
Ubuntu 24.04.4 LTS
dev
```

Result:

- success

Artifact path:

- recorded directly in this document

Conclusion:

- WSL2 is available
- Ubuntu 24.04.4 LTS is the target runtime
- implementation can proceed in distro `Ubuntu`

## Entry 002: Repository/package verification

Objective:

- verify which package names are valid on Ubuntu 24.04 before installation

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "apt-cache policy kamailio kamailio-extra-modules kamailio-utils-modules kamcli sngrep rtpengine-daemon"
wsl.exe -d Ubuntu -- bash -lc "apt-cache search sipp | sed -n '1,40p'"
wsl.exe -d Ubuntu -- bash -lc "apt-cache show sip-tester | sed -n '1,60p'"
wsl.exe -d Ubuntu -- bash -lc "apt-cache depends rtpengine | sed -n '1,80p'; echo '---'; apt-cache depends rtpengine-daemon | sed -n '1,80p'"
```

Key output:

```text
kamailio available
kamailio-extra-modules available
kamailio-utils-modules available
kamcli available
sngrep available
rtpengine-daemon available
```

```text
sip-tester - Performance testing tool for the SIP protocol
This software is distributed as SIPp by its authors.
```

```text
rtpengine depends on rtpengine-kernel-dkms and other extra components
rtpengine-daemon is the userspace part
```

Result:

- success

Artifact path:

- recorded directly in this document

Conclusion:

- the prior plan required corrections
- `sip-tester` is the correct Ubuntu 24.04 SIPp package
- `rtpengine-daemon` is the correct first RTPEngine path for WSL2

## Entry 003: Initial planning publication

Objective:

- publish the corrected implementation plan before changing the runtime environment

Output:

- created the initial verified plan material
- created this evidence log

Artifact path:

- [wsl2-lab-build-record.md](wsl2-lab-build-record.md)
- [implementation-evidence-log.md](implementation-evidence-log.md)

Result:

- success

Conclusion:

- documentation baseline is now established
- implementation can proceed with traceable checkpoints

## Entry 004: WSL runtime workspace bootstrap

Objective:

- create the Linux runtime workspace used for the lab

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "mkdir -p ~/sip-lab/kamailio ~/sip-lab/sipp ~/sip-lab/tools ~/sip-lab/run"
wsl.exe -d Ubuntu -- bash -lc "ls -la ~/sip-lab && find ~/sip-lab -maxdepth 1 -type d | sort"
wsl.exe -d Ubuntu -- bash -lc "sudo -n true; printf 'sudo-nopasswd=ok\n'"
```

Key output:

```text
/home/dev/sip-lab
/home/dev/sip-lab/kamailio
/home/dev/sip-lab/run
/home/dev/sip-lab/sipp
/home/dev/sip-lab/tools
sudo-nopasswd=ok
```

Result:

- success

Artifact path:

- recorded directly in this document

Conclusion:

- the runtime directory exists
- `sudo` works non-interactively, so installation and service start can proceed without an interactive password prompt

## Entry 005: Package installation

Objective:

- install the corrected dependency set for Ubuntu 24.04

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "sudo apt update | tee /mnt/c/Projects/kamailio-rtpengine-sbc/evidence/01-apt-update.log"
wsl.exe -d Ubuntu -- bash -lc "sudo apt install -y kamailio kamailio-extra-modules kamailio-utils-modules kamcli sip-tester sngrep tcpdump net-tools iproute2 ngrep python3 python3-pip netcat-openbsd procps | tee /mnt/c/Projects/kamailio-rtpengine-sbc/evidence/02-apt-install-base.log"
wsl.exe -d Ubuntu -- bash -lc "sudo apt install -y rtpengine-daemon | tee /mnt/c/Projects/kamailio-rtpengine-sbc/evidence/03-apt-install-rtpengine-daemon.log"
```

Key output:

```text
kamailio 5.7.4 installed
kamailio-extra-modules installed
kamailio-utils-modules installed
kamcli installed
sip-tester installed
sngrep installed
rtpengine-daemon installed
```

Result:

- success

Artifact path:

- [01-apt-update.log](../evidence/01-apt-update.log)
- [02-apt-install-base.log](../evidence/02-apt-install-base.log)
- [03-apt-install-rtpengine-daemon.log](../evidence/03-apt-install-rtpengine-daemon.log)

Conclusion:

- the package installation path works on this host
- `sip-tester` exposes the SIPp binary we need
- `rtpengine-daemon` installs cleanly in WSL2 without requiring DKMS

## Entry 006: Binary validation

Objective:

- verify the actual binary names and versions after install

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "command -v kamailio; command -v sipp; command -v rtpengine; command -v kamcmd"
wsl.exe -d Ubuntu -- bash -lc "kamailio -v | head -n 3"
wsl.exe -d Ubuntu -- bash -lc "sipp -v | head -n 5"
wsl.exe -d Ubuntu -- bash -lc "dpkg -l | egrep 'kamailio|sip-tester|sngrep|rtpengine'"
```

Key output:

```text
/usr/sbin/kamailio
/usr/bin/sipp
/usr/bin/rtpengine
/usr/sbin/kamcmd
kamailio 5.7.4
SIPp v3.7.2-TLS-SCTP-PCAP
```

Result:

- success

Artifact path:

- [04-binary-checks.txt](../evidence/04-binary-checks.txt)
- [05-dpkg-package-snapshot.txt](../evidence/05-dpkg-package-snapshot.txt)

Conclusion:

- the corrected package assumptions were right
- the executable command remains `sipp`, even though the package name is `sip-tester`

## Entry 007: Lab asset generation and Kamailio validation

Objective:

- create the lab source files, sync them into WSL, and verify the Kamailio config against the installed runtime

Outputs created:

- loopback IP helper
- cleanup helper
- sync helper
- RTP sender helper
- dispatcher list
- Kamailio lab config
- SIPp fake Vapi scenarios
- SIPp fake carrier scenarios

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "bash /mnt/c/Projects/kamailio-rtpengine-sbc/lab/tools/sync_lab_to_wsl.sh"
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/tools/add-lab-ips.sh"
wsl.exe -d Ubuntu -- bash -lc "sudo kamailio -c -f ~/sip-lab/kamailio/kamailio-lab.cfg"
```

Key output:

```text
Synced lab assets from /mnt/c/Projects/kamailio-rtpengine-sbc/lab to /home/dev/sip-lab
lo ... 10.10.10.10/32 10.10.10.20/32 10.10.10.41/32 10.10.10.42/32 10.10.10.99/32
config file ok, exiting...
Listening on udp: 10.10.10.10:5060
```

Result:

- success after one config fix

Artifact path:

- [06-sync-to-wsl.log](../evidence/06-sync-to-wsl.log)
- [07-loopback-ip-setup.txt](../evidence/07-loopback-ip-setup.txt)
- [08-kamailio-config-check.txt](../evidence/08-kamailio-config-check.txt)
- [kamailio-lab.cfg](../lab/kamailio/kamailio-lab.cfg)

Conclusion:

- the lab source files are in place
- the fake network IPs are active in WSL
- the generated Kamailio config is valid for this installed package set
- one failure-route reply misuse was caught and corrected during validation

## Entry 008: PAI ANI extraction and header injection

Objective:

- verify that an INVITE carrying `P-Asserted-Identity` is normalized and forwarded with the expected custom headers

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_single_call_test.sh test01-pai vapi-ok.xml carrier-pai.xml"
```

Key output:

```text
incoming INVITE ... PAI=sip:971501234567@etisalat.local
Extracted ANI=971501234567 FromUser=0555123456
INVITE sip:+97145550123@localcred.sip.vapi.ai SIP/2.0
From: <sip:971501234567@etisalat.local>;tag=1
X-Original-Caller: 971501234567
X-Original_Caller: 971501234567
```

Result:

- success

Artifact path:

- [test01-pai Kamailio log](../evidence/signaling/test01-pai/kamailio.log)
- [test01-pai tshark summary](../evidence/signaling/test01-pai/tshark-summary.tsv)
- [test01-pai tshark proof](../evidence/signaling/test01-pai/tshark-proof.txt)

Conclusion:

- PAI-based ANI extraction works
- `From` rewriting works when PAI is present
- both Vapi custom header variants are injected as intended

## Entry 009: From-only ANI fallback and config correction

Objective:

- verify fallback ANI extraction from the `From` user when `P-Asserted-Identity` is absent

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_single_call_test.sh test02-from-only vapi-ok.xml carrier-from-only.xml"
```

Key output:

```text
Initial issue observed during execution:
Extracted ANI=0 FromUser=971509876543 PAI=<null>

After config correction:
Extracted ANI=971509876543 FromUser=971509876543 PAI=<null>
From: <sip:971509876543@etisalat.local>;tag=1
X-Original-Caller: 971509876543
```

Result:

- success after config fix

Artifact path:

- [kamailio-lab.cfg](../lab/kamailio/kamailio-lab.cfg)
- [test02-from-only Kamailio log](../evidence/signaling/test02-from-only/kamailio.log)
- [test02-from-only tshark proof](../evidence/signaling/test02-from-only/tshark-proof.txt)

Conclusion:

- the first run exposed a real script/config bug caused by `$null` handling for `$var(ani)`
- switching to empty-string initialization and checks fixed the fallback path
- From-only ANI extraction is now verified

## Entry 010: Untrusted-source rejection

Objective:

- verify that non-Etisalat source IPs are rejected at the trust boundary

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_untrusted_test.sh"
```

Key output:

```text
INVITE from 10.10.10.99:5063
SIP/2.0 403 Forbidden
Rejected SIP from untrusted source 10.10.10.99:5063
```

Result:

- success

Artifact path:

- [test03-untrusted Kamailio log](../evidence/signaling/test03-untrusted/kamailio.log)
- [test03-untrusted tshark summary](../evidence/signaling/test03-untrusted/tshark-summary.tsv)
- [test03-untrusted tshark proof](../evidence/signaling/test03-untrusted/tshark-proof.txt)

Conclusion:

- the source-IP policy is active and blocks untrusted signaling before relay

## Entry 011: Pike flood handling

Objective:

- verify that repeated INVITEs from the trusted source trigger Pike rate limiting

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_pike_test.sh"
```

Key output:

```text
100 calls, 13 successful, 87 failed
SIP/2.0 503 Rate Limit Exceeded
PIKE blocked 10.10.10.20:5062
```

Result:

- success

Artifact path:

- [test04-pike Kamailio log](../evidence/signaling/test04-pike/kamailio.log)
- [test04-pike tshark summary](../evidence/signaling/test04-pike/tshark-summary.tsv)
- [test04-pike carrier output](../evidence/signaling/test04-pike/carrier.out)
- [test04-pike tshark metrics](../evidence/signaling/test04-pike/tshark-metrics.txt)

Conclusion:

- Pike protection is active
- the lab can demonstrate that trusted-source traffic is still rate-limited under flood conditions

## Entry 012: Dispatcher failover proof

Objective:

- verify that a `503` from the first fake Vapi peer causes Kamailio to retry the second peer

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_failover_test.sh"
```

Key output:

```text
10.10.10.10:5060 -> 10.10.10.41:5070 INVITE
10.10.10.41:5070 -> 10.10.10.10:5060 SIP/2.0 503 Service Unavailable
10.10.10.10:5060 -> 10.10.10.42:5080 INVITE
10.10.10.42:5080 -> 10.10.10.10:5060 SIP/2.0 200 OK
Destination failed, trying next destination
```

Result:

- success

Artifact path:

- [test-failover Kamailio log](../evidence/signaling/test-failover/kamailio.log)
- [test-failover signaling pcap](../evidence/signaling/test-failover/signaling.pcap)
- [test-failover tshark summary](../evidence/signaling/test-failover/tshark-summary.tsv)
- [test-failover tshark proof](../evidence/signaling/test-failover/tshark-proof.txt)

Conclusion:

- dispatcher failover is now proven with packet-level evidence
- the retry branch preserved the credential-style Request-URI and forwarded headers

## Entry 013: SDP rewrite and RTPEngine anchoring

Objective:

- verify that SDP is rewritten through the SBC media address and RTPEngine userspace path

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_sdp_test.sh"
```

Key output:

```text
Inbound SDP:
o=carrier 1 1 IN IP4 10.10.10.20
c=IN IP4 10.10.10.20
m=audio 5064 RTP/AVP 0

Outbound SDP:
o=carrier 1 1 IN IP4 10.10.10.10
c=IN IP4 10.10.10.10
m=audio 40036 RTP/AVP 0
a=rtcp:40037
```

Result:

- success

Artifact path:

- [test05-sdp Kamailio log](../evidence/rtp/test05-sdp/kamailio.log)
- [test05-sdp RTPEngine log](../evidence/rtp/test05-sdp/rtpengine.log)
- [test05-sdp signaling pcap](../evidence/rtp/test05-sdp/signaling.pcap)
- [test05-sdp tshark proof](../evidence/rtp/test05-sdp/tshark-proof.txt)

Conclusion:

- RTPEngine userspace integration is working
- SDP is being anchored to the SBC address and rewritten as intended
- this is sufficient proof of media anchoring for the local lab even though the Ubuntu SIPp build did not expose a convenient RTP generation flag for a richer payload-flow demo

## Entry 014: CANCEL cleanup behavior

Objective:

- verify that CANCEL triggers RTPEngine cleanup with an isolated single-peer upstream path

Implementation note:

- the cancel runner temporarily replaces the WSL runtime dispatcher list with a single fake Vapi destination so the trace is not polluted by normal failover testing

Command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "~/sip-lab/run/run_cancel_test.sh"
```

Key output:

```text
CANCEL matched transaction, deleting RTPEngine
rtpengine ... offer
rtpengine ... delete
10.10.10.10:5060 -> 10.10.10.41:5070 CANCEL sip:+97145550123@localcred.sip.vapi.ai
10.10.10.10:5060 -> 10.10.10.20:5062 SIP/2.0 200 canceling
10.10.10.41:5070 -> 10.10.10.10:5060 SIP/2.0 200 OK
10.10.10.41:5070 -> 10.10.10.10:5060 SIP/2.0 487 Request Terminated
10.10.10.10:5060 -> 10.10.10.20:5062 SIP/2.0 487 Request Terminated
```

Result:

- success

Artifact path:

- [test06-cancel Kamailio log](../evidence/rtp/test06-cancel/kamailio.log)
- [test06-cancel RTPEngine log](../evidence/rtp/test06-cancel/rtpengine.log)
- [test06-cancel tshark summary](../evidence/rtp/test06-cancel/tshark-summary.tsv)
- [test06-cancel tshark proof](../evidence/rtp/test06-cancel/tshark-proof.txt)

Conclusion:

- RTPEngine delete behavior is evidenced and the cleanup hook is firing
- the trace is now isolated to a single upstream peer and is repeatable
- the caller-side CANCEL transaction receives `200 canceling`
- the original INVITE transaction receives final `487 Request Terminated`
- the carrier SIPp scenario uses one Via branch across INVITE, CANCEL, and non-2xx ACK so the CANCEL matches the original INVITE transaction

## Entry 015: Tshark installation and Wireshark-style pcap verification

Objective:

- install `tshark` in WSL and verify custom SIP header interpretation using the Wireshark dissector rather than only raw ASCII pcap output

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "sudo DEBIAN_FRONTEND=noninteractive apt update && sudo DEBIAN_FRONTEND=noninteractive apt install -y tshark"
wsl.exe -d Ubuntu -- tshark -r /mnt/c/Projects/kamailio-rtpengine-sbc/evidence/signaling/test01-pai/signaling.pcap -Y 'sip.Method == \"INVITE\" && ip.src==10.10.10.10' -V
```

Key output:

```text
Session Initiation Protocol (INVITE)
X-Original-Caller: 971501234567
Unrecognised SIP header (x-original-caller)
X-Original_Caller: 971501234567
Unrecognised SIP header (x-original_caller)
```

Result:

- success

Artifact path:

- [test01-pai tshark proof](../evidence/signaling/test01-pai/tshark-proof.txt)

Conclusion:

- `tshark` is now available in the WSL runtime for future pcap validation
- the second INVITE in `test01-pai` contains two distinct custom headers, not an accidental duplicate of one header
- Wireshark marks both as `Unrecognised SIP header` because they are custom extension headers, not because the SIP message is malformed

## Entry 016: Full tshark-backed revalidation pass

Objective:

- rerun the current lab suite and regenerate packet-level proof artifacts so every active conclusion is backed by fresh `tshark` output

Commands:

```powershell
wsl.exe -d Ubuntu -- bash -lc "bash /mnt/c/Projects/kamailio-rtpengine-sbc/lab/tools/sync_lab_to_wsl.sh && chmod +x ~/sip-lab/run/*.sh ~/sip-lab/tools/*.sh && ~/sip-lab/run/revalidate_with_tshark.sh"
```

Outputs created:

- [revalidate_with_tshark.sh](../lab/run/revalidate_with_tshark.sh)
- [write_tshark_views.sh](../lab/tools/write_tshark_views.sh)
- per-test `tshark-summary.tsv`
- per-test `tshark-proof.txt`
- `tshark-metrics.txt` and `tshark-503.tsv` for the Pike scenario

Key output:

```text
test01-pai carrier_rc=0
test02-from-only carrier_rc=0
test03-untrusted carrier_rc=1
test04-pike carrier_rc=1
test-failover carrier_rc=0
test05-sdp carrier_rc=0
test06-cancel carrier_rc=0

Pike tshark metrics:
carrier_invites=100
blocked_503=87

Failover tshark summary:
10.10.10.10 -> 10.10.10.41 INVITE
10.10.10.41 -> 10.10.10.10 503 Service Unavailable
10.10.10.10 -> 10.10.10.42 INVITE
10.10.10.42 -> 10.10.10.10 200 OK

SDP tshark proof:
carrier c=IN IP4 10.10.10.20 / m=audio 5064
forwarded c=IN IP4 10.10.10.10 / m=audio 40036 / a=rtcp:40037

Cancel tshark summary:
caller CANCEL
upstream CANCEL
caller-leg 200 canceling for CANCEL
upstream 200 OK
upstream 487 Request Terminated
caller-leg 487 Request Terminated
```

Result:

- success

Artifact path:

- [test01-pai tshark proof](../evidence/signaling/test01-pai/tshark-proof.txt)
- [test02-from-only tshark proof](../evidence/signaling/test02-from-only/tshark-proof.txt)
- [test03-untrusted tshark proof](../evidence/signaling/test03-untrusted/tshark-proof.txt)
- [test04-pike tshark metrics](../evidence/signaling/test04-pike/tshark-metrics.txt)
- [test-failover tshark summary](../evidence/signaling/test-failover/tshark-summary.tsv)
- [test05-sdp tshark proof](../evidence/rtp/test05-sdp/tshark-proof.txt)
- [test06-cancel tshark summary](../evidence/rtp/test06-cancel/tshark-summary.tsv)

Conclusion:

- the active lab results are now backed by fresh `tshark` artifacts rather than only SIPp traces and application logs
- the two intentional negative-path tests remain correct: `test03-untrusted` returns non-zero because the caller is rejected with `403`, and `test04-pike` returns non-zero because flood traffic is intentionally blocked with `503`
- header rewrite, trust-boundary enforcement, dispatcher failover, SDP anchoring, CANCEL final-response handling, and cancel cleanup all have packet-level proof in the current evidence set
