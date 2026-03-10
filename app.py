import io
import re
from typing import List

import pandas as pd
import streamlit as st


st.set_page_config(page_title="ID Chunker", page_icon="📦", layout="centered")

st.title("ID Chunker to Excel")
st.write(
    "Paste a comma-separated or line-separated list of IDs. "
    "This app will group them into chunks (default 50 per cell) and export an Excel file."
)


def parse_ids(raw_text: str) -> List[str]:
    """Extract IDs from pasted text.

    Accepts comma-separated, newline-separated, or mixed input.
    Keeps only non-empty cleaned tokens.
    """
    parts = re.split(r"[\n,]+", raw_text)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned


def chunk_list(items: List[str], chunk_size: int) -> List[List[str]]:
    """Split a list into chunks of size chunk_size."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def build_excel(chunks: List[List[str]]) -> bytes:
    """Create an Excel file with one chunk per cell in column A."""
    rows = [{"Grouped IDs": ", ".join(chunk)} for chunk in chunks]
    df = pd.DataFrame(rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Grouped_IDs")
        ws = writer.sheets["Grouped_IDs"]
        ws.column_dimensions["A"].width = 140
    output.seek(0)
    return output.getvalue()


sample_text = "602975372198393, 603201931684354, 603066640267085"
raw_text = st.text_area(
    "Paste your IDs here",
    height=280,
    placeholder=sample_text,
)

chunk_size = st.number_input(
    "How many IDs per cell?",
    min_value=1,
    max_value=10000,
    value=50,
    step=1,
)

if st.button("Process IDs", type="primary"):
    ids = parse_ids(raw_text)

    if not ids:
        st.error("Please paste at least one ID.")
    else:
        chunks = chunk_list(ids, int(chunk_size))

        preview_df = pd.DataFrame(
            {
                "Cell #": list(range(1, len(chunks) + 1)),
                "Count in Cell": [len(chunk) for chunk in chunks],
                "Grouped IDs": [", ".join(chunk) for chunk in chunks],
            }
        )

        st.success(f"Found {len(ids)} IDs and created {len(chunks)} grouped cells.")
        st.dataframe(preview_df, use_container_width=True)

        excel_bytes = build_excel(chunks)
        st.download_button(
            label="Download Excel File",
            data=excel_bytes,
            file_name="grouped_ids.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        txt_output = "\n".join([", ".join(chunk) for chunk in chunks])
        st.download_button(
            label="Download TXT Version",
            data=txt_output,
            file_name="grouped_ids.txt",
            mime="text/plain",
        )

st.markdown("---")
st.caption("Tip: you can paste comma-separated, line-separated, or mixed IDs.")
