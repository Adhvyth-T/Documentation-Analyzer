import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from utils import (
    fetch_and_clean,
    chunk_text,
    create_vector_store,
    analyze_style,
    analyze_readability,
    analyze_structure,
    analyze_completeness,
    extract_json_objects
)
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import os
import json

load_dotenv()

class AnalysisRequest(BaseModel):
    url: str
    analysis_type: Optional[str] = "readability"
    model: Optional[str] = None

class DocumentationAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-r1-0528:free")
        
    def analyze(self, url: str, analysis_type: str = "all", model: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            text = fetch_and_clean(url)
            chunks = chunk_text(text)
            db = create_vector_store(chunks)

            analysis_func_map = {
                "readability": analyze_readability,
                "structure": analyze_structure,
                "completeness": analyze_completeness,
                "style": analyze_style
            }

            query_map = {
                "readability": "Analyze readability for a non-technical marketer",
                "structure": "Evaluate document structure and flow",
                "completeness": "Check for completeness of information and examples",
                "style": "Analyze for Microsoft Style Guide compliance"
            }

            results = {}
            for atype, func in analysis_func_map.items():
                query = query_map[atype]
                docs = db.similarity_search(query, k=2)

                atype_results = []
                for doc in docs:
                    raw_analysis = func(
                        doc.page_content,
                        self.api_key,
                        model or self.default_model
                    )
                    parsed_json = extract_json_objects(raw_analysis)
                    atype_results.append(parsed_json[0] if parsed_json else {"raw": raw_analysis})

                results[atype] = atype_results

            return {
                "status": "success",
                "url": url,
                "analysis_type": "all",
                "results": results
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }

def to_html(report: dict) -> str:
    if report["status"] == "error":
        return f"<h1>Analysis Failed</h1><p><b>Error:</b> {report['error']}</p>"

    results = report["results"]
    sections_html = ""

    for section, findings in results.items():
        rows = ""
        for i, result in enumerate(findings):
            formatted = (
                json.dumps(result, indent=2, ensure_ascii=False)
                if not isinstance(result, str)
                else result
            )
            rows += f"<tr><td>{i+1}</td><td><pre>{formatted}</pre></td></tr>"

        section_table = f"""
        <h2>{section.capitalize()} Analysis</h2>
        <table>
            <thead><tr><th>#</th><th>Analysis Result</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """
        sections_html += section_table

    return f"""
    <html>
    <head>
        <title>Documentation Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
            th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            h2 {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <h1>Documentation Analysis Report</h1>
        <p><b>URL:</b> {report['url']}</p>
        {sections_html}
    </body>
    </html>
    """

def run_analysis_gui():
    def on_analyze():
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a documentation URL.")
            return

        btn_analyze.config(state="disabled")
        try:
            analyzer = DocumentationAnalyzer()
            report = analyzer.analyze(url)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_path = Path("output")
            base_path.mkdir(exist_ok=True)

            json_path = base_path / f"report_{timestamp}.json"
            html_path = base_path / f"report_{timestamp}.html"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(to_html(report))

            messagebox.showinfo("Success", f"Analysis complete!\n\nSaved to:\n- {json_path}\n- {html_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            btn_analyze.config(state="normal")

    root = tk.Tk()
    root.title("Documentation Analyzer")

    tk.Label(root, text="Enter Documentation URL:").pack(pady=5)
    url_entry = tk.Entry(root, width=80)
    url_entry.pack(padx=10, pady=5)

    btn_analyze = tk.Button(root, text="Analyze", command=on_analyze)
    btn_analyze.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_analysis_gui()
