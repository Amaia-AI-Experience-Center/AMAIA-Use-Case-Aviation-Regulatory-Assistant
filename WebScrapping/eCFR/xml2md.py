import argparse
from bs4 import BeautifulSoup
import re
from pathlib import Path
from markdownify import markdownify as md
import xml.etree.ElementTree as ET

# ------------------------------------------------------------
# Markdown conversion from aggregated eCFR XML
# ------------------------------------------------------------

def indentar_html_listas(html: str) -> str:
    """
    Convert paragraphs beginning with markers like (a), (1), (i), (A), or (I)
    into properly nested unordered lists (<ul><li>...</li></ul>).

    This improves hierarchical readability before converting HTML to Markdown.
    Returns the transformed HTML string, ready for markdownify().
    """
    soup = BeautifulSoup(html, "html.parser")

    # Regex pattern to identify label markers at the start of a paragraph
    regex = re.compile(r'^\(([a-z0-9A-Z]+)\)\s*(.*)')

    # Stack used to manage nested <ul> tags (representing hierarchical depth)
    stack = []

    # Iterate over paragraph tags to detect and restructure list elements
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        m = regex.match(txt)

        if not m:
            # If paragraph does not begin with a list marker, close all active lists
            while stack:
                stack.pop()
            continue

        label, resto = m.groups()
        nivel = len(label)  # Approximate list depth based on marker length
        li_txt = f"({label}) {resto}"

        # Close deeper lists than the current one
        while len(stack) > nivel:
            stack.pop()

        # Create new <ul> levels if needed
        while len(stack) < nivel:
            ul = soup.new_tag("ul")
            if stack:
                stack[-1].append(ul)
            else:
                p.insert_before(ul)
            stack.append(ul)

        # Create and append a list item
        li = soup.new_tag("li")
        li.string = li_txt
        stack[-1].append(li)

        # Remove the original paragraph to prevent duplication
        p.decompose()

    return str(soup)


def main():
    """
    Main routine: parses input arguments, reads an eCFR XML document
    from a specified directory, restructures content, converts to Markdown,
    and writes the output file in the same directory.
    """
    parser = argparse.ArgumentParser(description="Convert eCFR XML into Markdown.")
    parser.add_argument(
        "--input-dir",
        default="output",
        help="Directory containing 'salida_completa.xml' (default: output)"
    )
    args = parser.parse_args()

    # ------------------------------------------------------------
    # Path setup
    # ------------------------------------------------------------
    input_dir = Path(args.input_dir)
    entrada_xml = input_dir / "salida_completa.xml"
    salida_md = input_dir / "salida_completa.md"

    if not entrada_xml.exists():
        raise FileNotFoundError(f"[-] Input file not found: {entrada_xml}")

    # ------------------------------------------------------------
    # Parse and convert XML to Markdown
    # ------------------------------------------------------------
    xml = entrada_xml.read_text(encoding="utf-8")
    root = ET.fromstring(xml)
    md_parts = ["# Complete eCFR Document\n"]

    for sec in root.findall("section"):
        ident = sec.get("id", "id?")
        html = ET.tostring(sec, encoding="unicode")

        # Normalize list indentation and structure
        html = indentar_html_listas(html)

        # Convert HTML section to Markdown text
        md_text = md(html, heading_style="atx", strip=["a"])

        md_parts.append(f"\n## Section {ident}\n")
        md_parts.append(md_text)

    # ------------------------------------------------------------
    # Write final Markdown output
    # ------------------------------------------------------------
    salida_md.write_text("\n".join(md_parts), encoding="utf-8")
    print(f"[+] Markdown successfully saved to: {salida_md.resolve()}")


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    main() # Ej python xml2md.py --in-dir ./output

import argparse
from bs4 import BeautifulSoup
import re
from pathlib import Path
from markdownify import markdownify as md
import xml.etree.ElementTree as ET

# ------------------------------------------------------------
# Markdown conversion from aggregated eCFR XML
# ------------------------------------------------------------

def indentar_html_listas(html: str) -> str:
    """
    Convert paragraphs beginning with markers like (a), (1), (i), (A), or (I)
    into properly nested unordered lists (<ul><li>...</li></ul>).

    This improves hierarchical readability before converting HTML to Markdown.
    Returns the transformed HTML string, ready for markdownify().
    """
    soup = BeautifulSoup(html, "html.parser")

    # Regex pattern to identify label markers at the start of a paragraph
    regex = re.compile(r'^\(([a-z0-9A-Z]+)\)\s*(.*)')

    # Stack used to manage nested <ul> tags (representing hierarchical depth)
    stack = []

    # Iterate over paragraph tags to detect and restructure list elements
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        m = regex.match(txt)

        if not m:
            # If paragraph does not begin with a list marker, close all active lists
            while stack:
                stack.pop()
            continue

        label, resto = m.groups()
        nivel = len(label)  # Approximate list depth based on marker length
        li_txt = f"({label}) {resto}"

        # Close deeper lists than the current one
        while len(stack) > nivel:
            stack.pop()

        # Create new <ul> levels if needed
        while len(stack) < nivel:
            ul = soup.new_tag("ul")
            if stack:
                stack[-1].append(ul)
            else:
                p.insert_before(ul)
            stack.append(ul)

        # Create and append a list item
        li = soup.new_tag("li")
        li.string = li_txt
        stack[-1].append(li)

        # Remove the original paragraph to prevent duplication
        p.decompose()

    return str(soup)


def main():
    """
    Main routine: parses input arguments, reads an eCFR XML document
    from a specified directory, restructures content, converts to Markdown,
    and writes the output file in the same directory.
    """
    parser = argparse.ArgumentParser(description="Convert eCFR XML into Markdown.")
    parser.add_argument(
        "--input-dir",
        default="output",
        help="Directory containing 'salida_completa.xml' (default: output)"
    )
    args = parser.parse_args()

    # ------------------------------------------------------------
    # Path setup
    # ------------------------------------------------------------
    input_dir = Path(args.input_dir)
    entrada_xml = input_dir / "salida_completa.xml"
    salida_md = input_dir / "salida_completa.md"

    if not entrada_xml.exists():
        raise FileNotFoundError(f"[-] Input file not found: {entrada_xml}")

    # ------------------------------------------------------------
    # Parse and convert XML to Markdown
    # ------------------------------------------------------------
    xml = entrada_xml.read_text(encoding="utf-8")
    root = ET.fromstring(xml)
    md_parts = ["# Complete eCFR Document\n"]

    for sec in root.findall("section"):
        ident = sec.get("id", "id?")
        html = ET.tostring(sec, encoding="unicode")

        # Normalize list indentation and structure
        html = indentar_html_listas(html)

        # Convert HTML section to Markdown text
        md_text = md(html, heading_style="atx", strip=["a"])

        md_parts.append(f"\n## Section {ident}\n")
        md_parts.append(md_text)

    # ------------------------------------------------------------
    # Write final Markdown output
    # ------------------------------------------------------------
    salida_md.write_text("\n".join(md_parts), encoding="utf-8")
    print(f"[+] Markdown successfully saved to: {salida_md.resolve()}")


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    main() # Ej: python xml2md.py --input-dir ./output