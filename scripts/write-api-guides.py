#!/usr/bin/env python3
"""Regenerate current v2 guides from the authoritative contract."""
import json
from current_api import ROOT
from current_api_guides import write_guides
write_guides(json.loads((ROOT/'openapi/amlok.json').read_text()),json.loads((ROOT/'data/product-api-examples.json').read_text()),json.loads((ROOT/'data/api-reference-index.json').read_text()))
