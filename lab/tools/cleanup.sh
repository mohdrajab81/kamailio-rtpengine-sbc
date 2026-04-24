#!/usr/bin/env bash
set +e

sudo pkill -f "sipp" 2>/dev/null || true
sudo pkill -f "kamailio" 2>/dev/null || true
sudo pkill -f "rtpengine" 2>/dev/null || true
sudo pkill -f "sngrep" 2>/dev/null || true
sudo pkill -f "tcpdump" 2>/dev/null || true

sudo ip addr del 10.10.10.10/32 dev lo 2>/dev/null || true
sudo ip addr del 10.10.10.20/32 dev lo 2>/dev/null || true
sudo ip addr del 10.10.10.41/32 dev lo 2>/dev/null || true
sudo ip addr del 10.10.10.42/32 dev lo 2>/dev/null || true
sudo ip addr del 10.10.10.99/32 dev lo 2>/dev/null || true

ss -lntup 2>/dev/null | egrep '(:5060|:5062|:5070|:5080|:2223|:9901|:40000|:40100)' || true
