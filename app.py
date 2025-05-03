from flask import Flask, request, send_file
import tabula
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return 'No file part', 400
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            # Attempt to read all tables from the PDF
            list_of_dfs = tabula.read_pdf(filepath, pages='all', multiple_tables=True)

            if not list_of_dfs:
                os.remove(filepath)
                return 'No tables found in the PDF.', 400

            # Concatenate all extracted DataFrames into one
            combined_df = pd.concat(list_of_dfs, ignore_index=True)

            # Convert the DataFrame to CSV format
            csv_data = combined_df.to_csv(index=False)

            os.remove(filepath)
            return csv_data
        except Exception as e:
            os.remove(filepath)
            return f'Error during PDF processing: {str(e)}', 500
    return 'Invalid file format', 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run(debug=True)
