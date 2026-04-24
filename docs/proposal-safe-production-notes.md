# Proposal-Safe Production Notes

## Purpose

This document rewrites the earlier production notes into wording that is safe to use in a proposal.

## Related Documents

- [etisalat-vapi-sbc-solution-design.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/etisalat-vapi-sbc-solution-design.md) for the intended architecture and solution design
- [verified-wsl2-kamailio-rtpengine-sipp-lab-plan.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/verified-wsl2-kamailio-rtpengine-sipp-lab-plan.md) for the lab plan
- [implementation-evidence-log.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/implementation-evidence-log.md) for the validated evidence set

Rules used here:

- keep claims that are directly supported by the current lab code or packet traces
- mark production recommendations as recommendations, not proven facts
- avoid claiming a root cause or fix unless the lab has actually validated it

## Verified From The Current Lab

These points are directly supported by the current implementation and evidence set.

### 1. Caller-leg CANCEL behavior needs follow-up before production

Verified fact:

- in the isolated CANCEL test, the caller leg currently receives `408 Request Timeout`
- upstream still receives `CANCEL`, returns `200 OK` to the `CANCEL`, and then returns `487 Request Terminated`

Verified artifacts:

- [test06-cancel tshark summary](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/test06-cancel/tshark-summary.tsv)
- [test06-cancel Kamailio log](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/rtp/test06-cancel/kamailio.log)

Proposal-safe wording:

- The current lab cleanly proves upstream CANCEL propagation and RTPEngine cleanup, but the caller-leg final response is presently `408 Request Timeout` instead of a relayed `487`. This should be corrected and revalidated before production rollout.

Do not claim yet:

- that the cause is definitely trust-check ordering
- that moving the CANCEL block alone will fix it
- that a specific TM change is already proven

### 2. Dual custom ANI headers are still in discovery mode

Verified fact:

- the lab currently injects both `X-Original-Caller` and `X-Original_Caller`

Verified artifacts:

- [kamailio-lab.cfg](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/kamailio/kamailio-lab.cfg)
- [test01-pai tshark proof](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence/signaling/test01-pai/tshark-proof.txt)

Proposal-safe wording:

- The lab currently forwards both likely ANI header variants as a defensive discovery measure. Once Vapi confirms the canonical header name, production should standardize on a single form.

### 3. SIP transaction timers are intentionally lab-tuned

Verified fact:

- the current lab sets `fr_timer=3` and `fr_inv_timer=6`

Verified artifact:

- [kamailio-lab.cfg](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/kamailio/kamailio-lab.cfg)

Proposal-safe wording:

- The current timer values are intentionally aggressive for fast local failover testing. Production deployment should use internet-appropriate SIP timers rather than the lab values.

### 4. The current lab listens only on UDP 5060

Verified fact:

- the current Kamailio config exposes only `listen=udp:...:5060`

Verified artifact:

- [kamailio-lab.cfg](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/kamailio/kamailio-lab.cfg)

Proposal-safe wording:

- The lab is intentionally UDP-only. Production transport requirements should be confirmed with both Etisalat and Vapi, with TCP added if required or operationally preferred.

### 5. The lab does not model public-IP or Elastic-IP signaling behavior

Verified fact:

- the lab runs entirely on loopback addresses inside WSL2
- the current Kamailio config does not include public advertise settings or cloud-specific address handling

Proposal-safe wording:

- The lab validates signaling and media control logic locally, but it does not model AWS public-IP behavior. Production deployment will need explicit public/private address handling appropriate for an Elastic IP design.

### 6. The RTPEngine lab is single-interface

Verified fact:

- the RTPEngine lab runners bind a single interface/IP

Verified artifacts:

- [run_sdp_test.sh](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/run/run_sdp_test.sh)
- [run_cancel_test.sh](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/run/run_cancel_test.sh)

Proposal-safe wording:

- The lab validates SDP anchoring and rewrite behavior on a single local interface. Production deployment on AWS will require explicit media-address handling for public/private addressing.

### 7. Dispatcher health checking is disabled in the lab

Verified fact:

- `ds_ping_interval=0` in the current lab config

Verified artifact:

- [kamailio-lab.cfg](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/kamailio/kamailio-lab.cfg)

Proposal-safe wording:

- Dispatcher health checking is disabled in the lab to keep behavior deterministic. Production should enable endpoint health monitoring so failed upstream targets are detected before live calls are affected.

### 8. Pike currently runs before the trust-boundary check

Verified fact:

- `pike_check_req()` is evaluated before the source-IP trust check

Verified artifact:

- [kamailio-lab.cfg](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab/kamailio/kamailio-lab.cfg)

Proposal-safe wording:

- The current ordering applies Pike before the trust filter. That is acceptable for the lab, but production can choose either ordering based on operational preference.

### 9. TLS is not configured in the current lab

Verified fact:

- the current lab config contains no TLS listener or TLS signaling path

Proposal-safe wording:

- TLS is not part of the current lab scope. Production transport and encryption requirements should be confirmed with the carrier and Vapi during trunk onboarding.

## Recommended Proposal Version

If you want a concise proposal-ready version, use this wording:

1. The local lab has validated ANI extraction, header injection, trust-boundary enforcement, dispatcher failover, SDP anchoring, and upstream CANCEL propagation with packet-level evidence.
2. Some lab settings are intentionally optimized for fast simulation rather than production realism, including timer values, disabled dispatcher health checks, and loopback-only addressing.
3. Before production deployment, the design should be finalized for transport selection, public/private address handling, canonical custom ANI header naming, and caller-leg CANCEL final-response behavior.
4. The current CANCEL path proves upstream cleanup behavior, but the caller leg presently terminates with `408 Request Timeout`; this should be corrected and revalidated before release.

## What Not To Overclaim

- Do not say the current lab proves real Etisalat transport behavior.
- Do not say the current lab proves real Vapi credential acceptance.
- Do not say the root cause of the CANCEL `408` is fully known.
- Do not say a single config reorder is already proven to fix the CANCEL issue.
- Do not present lab timer values as production recommendations.

## Client-Facing Version

Use the following text when you need a short customer-facing section:

### Validated In Local Lab

We built and validated a local SIP lab that simulates the intended Etisalat -> SBC -> Vapi call flow and verified the behavior with packet-level traces. The lab successfully demonstrated ANI extraction, custom header forwarding, trust-boundary enforcement, dispatcher-based upstream failover, SDP/media anchoring through RTPEngine, and upstream CANCEL propagation with cleanup.

### Production Readiness Notes

The current lab is a strong functional proof of approach, but several items remain to be finalized for production deployment. These include transport selection with the carrier and Vapi, public/private address handling for AWS and Elastic IP operation, confirmation of the canonical ANI header name expected by Vapi, production-grade SIP timer and health-check values, and caller-leg final-response behavior for CANCEL handling.

### Recommended Deployment Position

The proposed production shape remains sound: a public-facing SBC layer on AWS, using Kamailio plus RTPEngine, positioned between the carrier and Vapi. The lab results reduce implementation risk by validating the core signaling and media-control logic ahead of carrier onboarding, while also making the remaining production tasks explicit and measurable.

### Suggested Proposal Sentence

We have already validated the core SIP signaling, routing, ANI handling, and media-anchoring logic in a packet-level local lab, and the remaining production work is focused on carrier-specific transport alignment, AWS public-addressing details, and final hardening of operational behaviors before go-live.

## AWS And Region-Specific Deployment Assumptions

These items are important for production planning and should not live only in the background research report.

### Target AWS shape

- The intended production region is `me-central-1`.
- The recommended deployment shape is one public-facing EC2 SBC running Kamailio and RTPEngine.
- The SBC should sit in a public subnet with an Internet Gateway path and an Elastic IP.
- This is a public-subnet design, not a private-subnet-plus-NAT design, because the SBC must receive inbound SIP from the carrier.

### Availability model

- The pragmatic first production model is active-passive, not active-active.
- Use one active node and one warm standby with the Elastic IP remapped during failover.
- New calls can recover quickly after failover; in-progress calls on the failed node should be treated as non-preserved.

### Region sizing note

- The earlier research replaced the original `t3.micro` assumption with current `me-central-1` alternatives.
- The recommended first-pass instance choices are `m7g.medium` or `m6g.medium`, with `m6i.large` or `m7i.large` as x86 fallbacks.
- Because instance-family availability is time-sensitive, this should be rechecked at deployment time.

### Vapi network assumptions to carry into production planning

- The earlier research used Vapi signaling IPs `44.229.228.186` and `44.238.177.138` as the upstream SIP targets.
- It also treated Vapi RTP as dynamic-address media with a published local UDP range of `40000-60000`.
- These values are useful for planning, but they should be revalidated during live deployment because provider networking guidance can change.

### Where the high-level design lives

- The canonical architecture and solution design now lives in:
  - [etisalat-vapi-sbc-solution-design.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/etisalat-vapi-sbc-solution-design.md)
- Use that file for architecture shape, traffic flows, deployment rationale, production readiness notes, and candidate implementation details.
- Use this file for the canonical production-facing summary and claim boundaries.
