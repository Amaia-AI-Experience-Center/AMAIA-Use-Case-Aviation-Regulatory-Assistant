import argparse
import re
import requests
from pathlib import Path
from urllib.parse import urlencode
from tqdm import tqdm
import keyboard
import threading

# Global flag used to stop execution when user presses 'q'
stop_after = False


def build_ecfr_api_url(title: int, chapter=None, subchapter=None, part=None) -> str:
    """
    Construct the eCFR API endpoint for the specified title and optional parameters.
    Example output:
        https://www.ecfr.gov/api/versioner/v1/versions/title-14.json?chapter=I&subchapter=C&part=21
    """
    base = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title}.json"
    params = {k: v for k, v in {"chapter": chapter, "subchapter": subchapter, "part": part}.items() if v}
    return base + ("?" + urlencode(params) if params else "")


def fetch_ecfr_json(api_url: str):
    """
    Perform a GET request to the eCFR API and return the parsed JSON response.
    Raises an exception if the request fails.
    """
    print(f"API: {api_url}")
    resp = requests.get(api_url, headers={"accept": "application/json"}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def fetch_full_text(date: str, title: str, part: str, section: str) -> str:
    """
    Fetch the full XML text of a given regulation section based on date, title, part, and section.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
    params = {"part": part}
    if section:
        params["section"] = f"{part}.{section}"

    resp = requests.get(url, params=params, headers={"Accept": "application/xml"}, timeout=60)
    resp.raise_for_status()
    return resp.text.strip()


def append_xml(identifier: str, xml_text: str, salida_xml: Path):
    """
    Append a section's XML content to the output document.
    Removes redundant XML declarations before writing.
    """
    xml_text = re.sub(r'<\?xml[^>]*\?>', '', xml_text).strip()
    with open(salida_xml, "a", encoding="utf-8") as f:
        f.write(f'<section id="{identifier}">\n')
        f.write(xml_text)
        f.write('\n</section>\n')


def main():
    """
    Main routine: handles argument parsing, API data retrieval, 
    XML aggregation, and graceful interruption (via 'q' key).
    """
    global stop_after

    # ------------------ Argument Parsing ------------------
    parser = argparse.ArgumentParser(description="Download and aggregate eCFR XML sections by Title/Part.")
    parser.add_argument("--title", type=int, required=True, help="Regulation title number (required).")
    parser.add_argument("--chapter", default=None, help="Optional chapter identifier.")
    parser.add_argument("--subchapter", default=None, help="Optional subchapter identifier.")
    parser.add_argument("--part", default=None, help="Optional part number.")
    parser.add_argument("--max", type=int, default=None, help="Limit the number of sections processed.")
    parser.add_argument("--output-dir", default="output", help="Directory to store the resulting XML (default: output).")
    args = parser.parse_args()

    # ------------------ Output Directory Setup ------------------
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output file path
    salida_xml = output_dir / "salida_completa.xml"

    # Remove existing output file if present
    if salida_xml.exists():
        salida_xml.unlink()

    # Initialize XML file with document header
    salida_xml.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<document>\n', encoding="utf-8")

    # ------------------ Fetch eCFR Metadata ------------------
    url = build_ecfr_api_url(args.title, args.chapter, args.subchapter, args.part)
    data = fetch_ecfr_json(url)
    entries = data.get("content_versions", [])

    if not entries:
        print("[-] No entries found for the specified parameters.")
        return

    print(f"[INFO] Total sections found: {len(entries)}")

    # Limit the number of sections if --max was specified
    if args.max:
        entries = entries[:args.max]
        print(f"[INFO] Processing limited to the first {len(entries)} sections.")

    print("Press 'q' to stop gracefully after the current download.\n")

    # ------------------ Keyboard Interrupt Thread ------------------
    def check_quit():
        """Wait for user to press 'q' to stop the process."""
        global stop_after
        keyboard.wait('q')
        stop_after = True

    threading.Thread(target=check_quit, daemon=True).start()

    # ------------------ Download and Write Sections ------------------
    try:
        for idx, entry in enumerate(tqdm(entries, desc="Downloading")):
            if stop_after:
                tqdm.write("[-] Interrupted by user (will stop after current request).")
                break

            identifier = entry.get("identifier")
            date = entry.get("date")
            title = entry.get("title")
            part, section = (identifier.split(".", 1) if "." in identifier else (identifier, None))

            try:
                xml_text = fetch_full_text(date, title, part, section)
                append_xml(identifier, xml_text, salida_xml)
                tqdm.write(f"[+] Added section {identifier}")
            except Exception as e:
                tqdm.write(f"[*-*] Error processing {identifier}: {e}")

    # ------------------ Finalization ------------------
    finally:
        with open(salida_xml, "a", encoding="utf-8") as f:
            f.write("</document>\n")

        print(f"\n[INFO] XML file successfully saved at: {salida_xml.resolve()}")


if __name__ == "__main__":
    main() # Ej: python eCFRconAPI.py --title 14 --chapter I --subchapter C --part 21
