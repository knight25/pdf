from flask import Flask, render_template, request, send_file
import pdfplumber
import pandas as pd
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['pdf']
    if file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        # Extract table from PDF using pdfplumber
        data = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    data.extend(table)

        if not data:
            return "No table data found in PDF.", 400

        # Convert to DataFrame and save to Excel
        df = pd.DataFrame(data)
        excel_filename = f"{uuid.uuid4().hex}.xlsx"
        excel_path = os.path.join(UPLOAD_FOLDER, excel_filename)
        df.to_excel(excel_path, index=False, header=False)

        return send_file(excel_path, as_attachment=True)

    return "Invalid file type. Please upload a PDF file.", 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
