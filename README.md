# SIP Lab WSL2

## Purpose

This project contains a verified local WSL2 lab for the Etisalat -> Kamailio/RTPEngine -> Vapi SIP flow, along with the current documentation set, lab sources, and captured evidence artifacts.

## Current Document Set

- [etisalat-vapi-sbc-solution-design.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/etisalat-vapi-sbc-solution-design.md)
  Canonical solution design, architecture, production readiness notes, security model, candidate configs, and validated lab findings.
- [verified-wsl2-kamailio-rtpengine-sipp-lab-plan.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/verified-wsl2-kamailio-rtpengine-sipp-lab-plan.md)
  Verified lab execution plan for the WSL2 implementation.
- [implementation-evidence-log.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/implementation-evidence-log.md)
  Execution record and evidence map for what the lab actually proved.
- [proposal-safe-production-notes.md](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/proposal-safe-production-notes.md)
  Safe production-facing wording, explicit claim boundaries, and remaining hardening items.
- [Kamailio-Etisalat-Vapi-Lab-Evidence.pdf](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs/Kamailio-Etisalat-Vapi-Lab-Evidence.pdf)
  Customer-facing evidence pack.

## Project Layout

- [docs](/C:/Users/DELL/Downloads/sip-lab-wsl2/docs)
  Current documentation set.
- [lab](/C:/Users/DELL/Downloads/sip-lab-wsl2/lab)
  Kamailio config, SIPp scenarios, lab runners, and helper scripts.
- [evidence](/C:/Users/DELL/Downloads/sip-lab-wsl2/evidence)
  Logs, pcaps, tshark outputs, and supporting artifacts captured from the validated tests.

## What The Lab Validates

- ANI extraction from `P-Asserted-Identity`
- fallback ANI extraction from `From`
- custom ANI header forwarding
- trust-boundary enforcement
- dispatcher-based failover behavior
- SDP rewrite and media anchoring behavior
- upstream `CANCEL` propagation and RTPEngine cleanup

## What Still Needs Production Confirmation

- carrier transport and signaling policy
- carrier source IP ranges
- carrier ANI placement in live traffic
- Vapi gateway and credential acceptance details
- production timer values and health-check settings
- final caller-leg `CANCEL` response behavior before release

## Usage

- Start with the high-level design if you need architecture context.
- Use the verified plan if you need to rebuild or rerun the lab.
- Use the evidence log and evidence tree for proof.
- Use the proposal-safe notes when writing customer-facing or approval-facing material.
