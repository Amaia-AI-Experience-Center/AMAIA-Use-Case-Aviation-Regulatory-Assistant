import os
import re
import hashlib
import argparse
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse


class MarkdownExtractor:
    """
    Class responsible for recursively downloading HTML pages,
    extracting the <main> content section, converting it to Markdown,
    and saving results in a structured folder tree.
    """

    def __init__(self, base_folder="output", max_depth=1):
        """
        Initialize the extractor.

        Parameters:
        - base_folder (str): root directory where all Markdown files will be saved.
        - max_depth (int): maximum recursion depth for following internal links.
        """
        self.base_folder = base_folder
        self.max_depth = max_depth
        self.visited_urls = set()
        os.makedirs(base_folder, exist_ok=True)

    def fetch_and_save(self, url: str, depth=0, parent_folder=None):
        """
        Fetch an HTML page, extract the <main> content (or similar section),
        convert it to Markdown, and optionally follow internal links up to
        a specified recursion depth.
        """

        normalized_url = self._normalize_url(url)
        print(f"\n[INFO] Processing (depth {depth}): {normalized_url}\n")

        # --------------------- HTTP Request ---------------------
        try:
            resp = requests.get(
                normalized_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"},
                allow_redirects=True,
                timeout=60
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"[-] Failed to download {normalized_url}: {e}")
            return

        final_url = self._normalize_url(resp.url)

        # Skip already visited URLs to prevent infinite loops
        if final_url in self.visited_urls:
            print(f"[SKIP] Already visited: {final_url}")
            return

        # --------------------- HTML Parsing ---------------------
        soup = BeautifulSoup(resp.text, "html.parser")

        # Attempt to locate the main content region (<main> preferred)
        main_content = (
            soup.find("main")
            or soup.find("div", class_="field-item")
            or soup.find("div", class_="content-block")
        )

        if not main_content:
            print("[WARN] No main content found in page.")
            return

        # --------------------- Internal Link Discovery ---------------------
        base_domain = urlparse(final_url).netloc
        links = []

        for a_tag in main_content.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith("#"):
                continue

            full_link = urljoin(final_url, href)
            norm_link = self._normalize_url(full_link)

            # Only follow links within the same domain
            if urlparse(norm_link).netloc != base_domain:
                continue
            if norm_link == final_url:
                continue

            links.append(norm_link)

        # --------------------- Content Cleanup ---------------------
        # Remove irrelevant layout elements to keep Markdown clean
        for tag in main_content.find_all(["nav", "header", "footer", "aside", "script", "style"]):
            tag.decompose()

        # --------------------- HTML → Markdown Conversion ---------------------
        markdown_text = md(str(main_content), heading_style="ATX", strip=["span"])
        # Optionally remove extra blank lines:
        # markdown_text = "\n".join(line.strip() for line in markdown_text.splitlines() if line.strip())

        # --------------------- File Path Construction ---------------------
        # Use short MD5 hash of the URL for folder naming to avoid long paths
        folder = self.base_folder if parent_folder is None else os.path.join(self.base_folder, parent_folder)
        hash_prefix = hashlib.md5(final_url.encode()).hexdigest()[:8]
        folder = os.path.join(folder, hash_prefix)
        os.makedirs(folder, exist_ok=True)

        # Generate safe filename from URL path
        filename = self._filename_from_url(final_url)
        filepath = os.path.join(folder, filename)

        # Fallback if path length exceeds Windows path limit (~240 chars)
        if len(filepath) > 240:
            short_hash = hashlib.md5(filepath.encode()).hexdigest()[:10]
            filepath = os.path.join(folder, f"{short_hash}.md")

        # --------------------- Save Markdown ---------------------
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"---\nsource: {final_url}\n---\n\n")
            f.write(markdown_text)

        print(f"[+] Saved: {filepath}")

        # Mark as visited after saving
        self.visited_urls.add(final_url)

        # --------------------- Recursive Link Processing ---------------------
        if depth < self.max_depth:
            for link in links:
                self.fetch_and_save(link, depth=depth + 1, parent_folder=hash_prefix)

    # ------------------------------------------------------------
    # Utility functions
    # ------------------------------------------------------------
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing query strings, anchors, and trailing slashes."""
        p = urlparse(url)
        return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")

    def _filename_from_url(self, url: str) -> str:
        """Create a safe Markdown filename from the URL path (last 50 chars)."""
        path = urlparse(url).path.strip("/") or "index"
        safe = re.sub(r'[<>:"/\\|?*]', "_", path)
        short = safe[-50:] if len(safe) > 50 else safe
        return f"{short}.md"


# ============================================================
# Command-line entry point
# ============================================================
def main():
    """
    Parse command-line arguments, initialize the MarkdownExtractor,
    and launch the extraction process for the given URL.
    """
    parser = argparse.ArgumentParser(
        description="Extract the <main> section of a webpage into Markdown and optionally follow internal links."
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=(
            "https://tc.canada.ca/en/corporate-services/acts-regulations/list-regulations/"
            "canadian-aviation-regulations-sor-96-433/standards/airworthiness-manual-chapter-533-"
            "aircraft-engines-canadian-aviation-regulations-cars"
        ),
        help="Starting URL to process."
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Maximum recursion depth for following internal links (default: 1)."
    )
    parser.add_argument(
        "--out",
        dest="base_folder",
        default="output",
        help="Base output directory where Markdown files are saved (default: output)."
    )

    args = parser.parse_args()

    # Initialize and run the extractor
    extractor = MarkdownExtractor(base_folder=args.base_folder, max_depth=args.depth)
    extractor.fetch_and_save(args.url)


# ============================================================
# Script entry point
# ============================================================
if __name__ == "__main__":
    main() # Ej: python PagBasicaRecursiva2md.py "https://example.com" --depth 1 --out "output"
