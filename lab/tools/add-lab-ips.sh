#!/usr/bin/env bash
set -euo pipefail

sudo ip addr add 10.10.10.10/32 dev lo 2>/dev/null || true
sudo ip addr add 10.10.10.20/32 dev lo 2>/dev/null || true
sudo ip addr add 10.10.10.41/32 dev lo 2>/dev/null || true
sudo ip addr add 10.10.10.42/32 dev lo 2>/dev/null || true
sudo ip addr add 10.10.10.99/32 dev lo 2>/dev/null || true

ip -br addr show lo
