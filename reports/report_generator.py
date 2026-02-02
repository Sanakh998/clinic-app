import datetime
import tempfile
import os
import webbrowser
from config.config import CLINIC_NAME

# ==========================================
# REPORT GENERATOR (PRINT)
# ==========================================


class ReportGenerator:
    @staticmethod
    def generate_patient_profile(patient, visits):
        """Generates a professional HTML file for printing."""
        # patient format: (id, name, phone, age, gender, address, notes, created)
        
        # Current time for footer
        print_time = datetime.datetime.now().strftime('%d-%b-%Y %I:%M %p')

        # Visit HTML Builder
        visits_html = ""
        if visits:
            for v in visits:
                # v format: (id, pid, date, comp, med, rem)
                # Hum medicines ko new line par dikhayenge agar wo comma separated hain
                meds_formatted = v[4].replace(',', '<br>&bull; ') if v[4] else "N/A"
                if v[4] and not v[4].startswith('<br>'):
                     meds_formatted = "&bull; " + meds_formatted

                visits_html += f"""
                <div class="visit-card">
                    <div class="visit-header">
                        <span class="visit-date">📅 Date: {v[2]}</span>
                        <span class="visit-id">Visit ID: #{v[0]}</span>
                    </div>
                    <div class="visit-body">
                        <div class="visit-row">
                            <div class="col-history">
                                <span class="label">Diagnosis / History</span>
                                <div class="value">{v[3]}</div>
                            </div>
                            <div class="col-meds">
                                <span class="label">Rx (Medicines)</span>
                                <div class="value meds-text">{meds_formatted}</div>
                            </div>
                        </div>
                        <div class="visit-footer-remarks">
                            <span class="label remarks">Remarks:</span> <span class="value remarks">{v[5]}</span>
                        </div>
                    </div>
                </div>
                """
        else:
            visits_html = '<div class="no-records">No visit history found for this patient.</div>'

        # Complete HTML Structure
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{CLINIC_NAME} - Patient Report</title>
            <style>
                :root {{
                    --primary-color: #0056b3; /* Medical Blue */
                    --primary-dark: #004494; /* Darker shade for hover */
                    --secondary-color: #f0f4f8;
                    --text-dark: #2c3e50;
                    --text-light: #5f6c7b;
                    --border-color: #e1e4e8;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #fff;
                    color: var(--text-dark);
                    margin: 0;
                    padding: 40px;
                    font-size: 14px;
                    line-height: 1.5;
                }}

                .report-container{{
                    max-width: 900px;
                    margin: auto;
                }}


                /* ----- NEW: Print Button Styles (Screen Only) ----- */

                .no-print-container {{
                    margin-bottom: 20px;
                }}
                .btn-print {{
                    background-color: var(--primary-color);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px; /* Space between icon and text */
                    font-family: inherit;
                    font-size: 14px;
                    font-weight: 600;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    transition: background-color 0.2s ease;
                }}
                .btn-print:hover {{
                    background-color: var(--primary-dark);
                }}
                .btn-print svg {{
                    width: 18px;
                    height: 18px;
                    fill: currentColor; /* SVG color matches text color (white) */
                }}
                /* -------------------------------------------------- */

                /* Header Design */
                .header-container {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 3px solid var(--primary-color);
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .clinic-info h1 {{
                    margin: 0;
                    color: var(--primary-color);
                    font-size: 28px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .clinic-info p {{
                    padding-left: 50px;                
                    margin: 5px 0 0;
                    color: var(--text-light);
                    font-size: 14px;
                }}
                .report-meta {{
                    text-align: center;
                }}
                .report-badge {{
                    background: var(--primary-color);
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }}

                /* Patient Info Section */
                .patient-section {{
                    background: var(--secondary-color);
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-left: 5px solid var(--primary-color);
                    display: flex;
                    flex-wrap: wrap;
                }}
                .info-group {{
                    flex: 1 1 25%; /* 4 columns */
                    margin-bottom: 10px;
                    min-width: 150px;
                }}
                .info-label {{
                    display: block;
                    font-size: 11px;
                    text-transform: uppercase;
                    color: var(--text-light);
                    font-weight: bold;
                    margin-bottom: 3px;
                }}
                .info-value {{
                    font-size: 15px;
                    font-weight: 600;
                    color: var(--text-dark);
                }}
                .info-full {{
                    flex: 1 1 100%;
                    padding-top: 10px;
                    border-top: 1px solid #dce1e6;
                }}

                /* Visits Section */
                .section-title {{
                    font-size: 18px;
                    color: var(--primary-color);
                    border-bottom: 1px solid var(--border-color);
                    padding-bottom: 5px;
                    margin-bottom: 20px;
                    font-weight: bold;
                }}

                .visit-card {{
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    margin-bottom: 10px;
                    overflow: hidden;
                    page-break-inside: avoid; /* Important for printing */
                }}
                .visit-header {{
                    background: #f8f9fa;
                    padding: 10px 15px;
                    border-bottom: 1px solid var(--border-color);
                    display: flex;
                    justify-content: space-between;
                    font-weight: bold;
                    color: var(--primary-color);
                }}
                .visit-body {{
                    padding: 10px 15px;
                }}
                .visit-row {{
                    display: flex;
                    gap: 20px;
                }}
                .col-history {{ flex: 1; border-right: 1px solid var(--border-color); padding-right: 15px; }}
                .col-meds {{ flex: 1; }}
                
                .label {{
                    font-weight: bold;
                    color: var(--text-light);
                    font-size: 12px;
                    display: block;
                    margin-bottom: 5px;
                    text-transform: uppercase;
                }}
                .value {{
                    font-size: 14px;
                }}
                .meds-text {{
                    color: #d63031; /* Reddish for medicines to stand out */
                    font-weight: 500;
                    line-height: 1.6;
                }}
                .visit-footer-remarks {{
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px dashed var(--border-color);
                    font-style: italic;
                    color: #555;
                }}

                .remarks {{
                    display: inline;
                }}
                
                .no-records {{
                    text-align: center;
                    padding: 40px;
                    color: var(--text-light);
                    font-style: italic;
                    background: var(--secondary-color);
                    border-radius: 8px;
                }}

                /* Footer */
                .footer {{
                    margin: 30px 80px 0;
                    text-align: center;
                    font-size: 11px;
                    color: #aaa;
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                }}

                /* Print Specifics */
                @media print {{
                    /* HIDE THE PRINT BUTTON ON PAPER */
                    .no-print-container {{
                        display: none !important;
                    }}
                    body {{ padding: 0; font-size: 12pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                    .patient-section {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                    .visit-header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                    .visit-card {{ break-inside: avoid; page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <div class="no-print-container">
                <button class="btn-print" onclick="window.print()">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 8h-1V3H6v5H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM8 5h8v3H8V5zm8 12v2H8v-2h8zm2-2v-2H6v2H4v-4c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v4h-2z"/><circle cx="18" cy="11.5" r="1"/></svg>
                    <span>Print Report</span>
                </button>
                </div>

                <div class="header-container">
                    <div class="clinic-info">
                        <h1>{CLINIC_NAME}</h1>
                        <p>Patient Medical Record System</p>
                    </div>
                    <div class="report-meta">
                        <div class="report-badge">Patient Report</div>
                        <p style="margin-top:5px; font-size:12px;">Printed: {print_time}</p>
                    </div>
                </div>

                <div class="patient-section">
                    <div class="info-group">
                        <span class="info-label">Patient Name</span>
                        <span class="info-value">{patient[1]}</span>
                    </div>
                    <div class="info-group">
                        <span class="info-label">Contact No</span>
                        <span class="info-value">{patient[2]}</span>
                    </div>
                    <div class="info-group">
                        <span class="info-label">Gender / Age</span>
                        <span class="info-value">{patient[4]} / {patient[3]} Yrs</span>
                    </div>
                    
                    <div class="info-group">
                        <span class="info-label">Address</span>
                        <span class="info-value">{patient[5]}</span>
                    </div>
                    <div class="info-full">
                        <span class="info-label" style="display: inline; font-style: italic;">Important Notes: </span>
                        <span class="info-value" style="font-size: 11px; font-style: italic;">{patient[6]}</span>
                    </div>
                </div>

                <div class="section-title">Visit History Log</div>
                {visits_html}

                <div class="footer">
                    <p>This is a computer-generated document. No signature required.</p>
                    <p>{CLINIC_NAME} &copy; {datetime.datetime.now().year}</p>
                </div>
            </div>

        </body>
        </html>
        """
        
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=".html")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            print(f"Error writing file: {e}")
            return

        # Open in browser
        webbrowser.open(f'file://{path}')
