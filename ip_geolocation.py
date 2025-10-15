#!/usr/bin/env python3
"""
IP Geolocation - simple CLI tool
Requirements: Python 3.7+
Usage: python3 ip_geolocation.py 8.8.8.8
This script queries public IP geolocation endpoints and normalizes results.
"""
import sys
import json
import urllib.parse
from urllib.request import urlopen, Request
from typing import Optional, Dict, Any

ENDPOINTS = [
    "https://ipinfo.io/{ip}/json",
    "https://ipapi.co/{ip}/json/",
    "http://ip-api.com/json/{ip}"
]

HEADERS = {"User-Agent": "ip-geoloc-cli/1.0"}

def fetch_one(url: str) -> Optional[Dict[str, Any]]:
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=8) as resp:
            data = json.load(resp)
            if isinstance(data, dict):
                return data
    except Exception as e:
        # silently skip endpoint failures
        return None
    return None

def fetch_ip(ip: str) -> Optional[Dict[str, Any]]:
    ip = ip.strip()
    for t in ENDPOINTS:
        url = t.format(ip=urllib.parse.quote(ip))
        data = fetch_one(url)
        if data:
            return data
    return None

def normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    # common keys across providers
    out['ip'] = data.get('ip') or data.get('query')
    out['hostname'] = data.get('hostname') or data.get('org')
    out['org'] = data.get('org') or data.get('company') or data.get('organization')
    out['city'] = data.get('city')
    out['region'] = data.get('region') or data.get('regionName')
    out['country'] = data.get('country')
    out['loc'] = data.get('loc')  # ipinfo uses lat,long
    out['timezone'] = data.get('timezone')
    # try to extract lat/lon
    if out['loc'] and isinstance(out['loc'], str) and ',' in out['loc']:
        lat, lon = out['loc'].split(',', 1)
        out['latitude'] = lat.strip()
        out['longitude'] = lon.strip()
    else:
        out['latitude'] = data.get('latitude') or data.get('lat')
        out['longitude'] = data.get('longitude') or data.get('lon')
    return out

def pretty_print(info: Dict[str, Any]) -> None:
    if not info:
        print("No information available.")
        return
    keys = ["ip", "hostname", "org", "city", "region", "country", "latitude", "longitude", "timezone"]
    for k in keys:
        v = info.get(k)
        if v:
            print(f"{k.capitalize():10}: {v}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ip_geolocation.py <IP or hostname>")
        sys.exit(1)
    target = sys.argv[1]
    raw = fetch_ip(target)
    if raw is None:
        print("Unable to retrieve information for", target)
        sys.exit(2)
    info = normalize(raw)
    pretty_print(info)

if __name__ == "__main__":
    main()
