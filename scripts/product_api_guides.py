"""Compatibility entry point: regenerate the authoritative v2 guides."""
import json
from current_api import ROOT
from current_api_guides import write_guides

def generate():
    write_guides(json.loads((ROOT/"openapi/amlok.json").read_text()),json.loads((ROOT/"data/product-api-examples.json").read_text()),json.loads((ROOT/"data/api-reference-index.json").read_text()))

if __name__ == "__main__": generate()
