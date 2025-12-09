import re
import json
from typing import Dict, Any, List


def extract_gross_investments_in_renewables(pdf_path: str) -> Dict[str, Any]:
    text = get_page_text_containing(pdf_path, "Gross Investments (Eur Bn)")

    # 1️⃣ Total: "Investing Eur 21 Bn"
    total_match = re.search(
        r"Investing\s*(?:Eur|EUR|€)\s*~?\s*(\d+(?:[.,]\d+)?)\s*B[nN]",
        text, re.IGNORECASE)
    total = float(total_match.group(1).replace(",", ".")) if total_match else None

    labels = [
        "Offshore Wind",
        "Onshore Wind",
        "Solar PV",
        "Customers & Maintenance",
        "Storage",
    ]

    data: List[Dict[str, Any]] = []

    # 2️⃣ Extract ALL numbers that look like Bn values (ignoring 21 total)
    raw_nums = re.findall(
        r"~?\s*(\d+(?:[.,]\d+)?)\s*(?:Eur|EUR|€)?\s*B[nN]",
        text, re.IGNORECASE)

    # Convert & drop the total (21)
    nums = [float(n.replace(",", ".")) for n in raw_nums if float(n.replace(",", ".")) != total]

    # Defensive check
    while len(nums) < len(labels):
        nums.append(None)

    # 3️⃣ Assign numbers in correct visual order
    for label, num in zip(labels, nums):
        if num is not None:
            data.append({"label": label, "value_eur_bn": num})

    # 4️⃣ Summary
    if total and data:
        top_item = max(data, key=lambda x: x["value_eur_bn"])
        summary = (
            f"Gross investments in Renewable Power & Customers total ~{total:.0f} Bn EUR, "
            f"with {top_item['label']} being the largest segment."
        )
    else:
        summary = "Gross investments in Renewable Power & Customers could not be fully determined."

    return {
        "title": "Gross Investments in Renewable Power & Customers 2025-28",
        "total_investments_eur_bn": total,
        "data": data,
        "summary": summary,
    }

if __name__ == "__main__":
    pdf_path = "CMD25-strategic-plan-update.pdf"
    info = extract_gross_investments_in_renewables(pdf_path)
    print(json.dumps(info, indent=2))
