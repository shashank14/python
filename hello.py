import pdfplumber
import re
import json
from typing import Dict, Any


def get_page_text_containing(pdf_path: str, needle: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if needle in text:
                # normalize whitespace
                return " ".join(text.split())
    raise RuntimeError(f"Could not find '{needle}' in PDF")


def extract_gross_investments_by_geography(pdf_path: str) -> Dict[str, Any]:
    text = get_page_text_containing(pdf_path, "Gross Investments by geography")

    # Optional: keep this if you still want to inspect later
    # print("\n================ DEBUG TEXT ================\n")
    print(text)
    # print("\n============================================\n")

    # ---- 1) Total investments: "Gross investments reach Eur ~58 Bn" ----
    total_match = re.search(
        r"Gross investments reach\s+Eur\s*~?(\d+(?:\.\d+)?)\s*Bn",
        text,
        re.IGNORECASE,
    )
    if not total_match:
        # Fallback: generic "58 Eur Bn" or "Eur 58 Bn" if pattern changes
        total_match = re.search(
            r"~?\s*(\d+(?:\.\d+)?)\s*(?:Eur|EUR|€)?\s*Bn",
            text,
            re.IGNORECASE,
        )

    total = float(total_match.group(1)) if total_match else None

    # ---- 2) Percentages ----
    # We map "Other EU & Australia" using the Australia % we see in text: "Australia ~8%"
    patterns = {
        "United Kingdom": r"UK\s*~\s*(\d+(?:\.\d+)?)%",
        "United States": r"US\s*~\s*(\d+(?:\.\d+)?)%",
        "Iberia": r"Iberia\s*~\s*(\d+(?:\.\d+)?)%",
        "Brazil": r"Brazil\s*~\s*(\d+(?:\.\d+)?)%",
        # use just "Australia ~8%" for this bucket
        "Other EU & Australia": r"Australia\s*~\s*(\d+(?:\.\d+)?)%",
    }

    data = []
    perc_map = {}
    for label, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        val = float(m.group(1)) if m else None
        perc_map[label] = val
        data.append({"label": label, "value_percent": val})

    # ---- 3) Summary: UK + US combined ----
    uk = perc_map.get("United Kingdom") or 0.0
    us = perc_map.get("United States") or 0.0
    uk_us_share = uk + us
    approx_uk_us_eur = (
        round((total or 0.0) * uk_us_share / 100.0) if total is not None else None
    )

    if approx_uk_us_eur is not None:
        summary = (
            f"Approximately {uk_us_share:.0f}% of gross investments "
            f"(~{approx_uk_us_eur} Bn EUR) are allocated to the UK and US combined."
        )
    else:
        summary = "UK and US combined share could not be fully determined from the text."

    return {
        "title": "Gross Investments by Geography 2025-28",
        "total_investments_eur_bn": total,
        "data": data,
        "summary": summary,
    }


if __name__ == "__main__":
    pdf_path = "CMD25-strategic-plan-update.pdf"
    info = extract_gross_investments_by_geography(pdf_path)
    print(json.dumps(info, indent=2))
