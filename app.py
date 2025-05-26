from flask import Flask, render_template, request, send_file
import os
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def pil_to_pdf_bytes(image):
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    return img_bytes.getvalue()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        label_pdf = request.files['label_pdf']
        company_logo = request.files['company_logo']
        client_logo = request.files['client_logo']

        if not label_pdf or not company_logo or not client_logo:
            return "All files are required."

        pdf_path = os.path.join(UPLOAD_FOLDER, label_pdf.filename)
        label_pdf.save(pdf_path)

        company_logo_img = Image.open(company_logo).resize((50, 50))
        client_logo_img = Image.open(client_logo).resize((50, 50))

        company_logo_bytes = pil_to_pdf_bytes(company_logo_img)
        client_logo_bytes = pil_to_pdf_bytes(client_logo_img)

        doc = fitz.open(pdf_path)
        for page in doc:
            for row in range(4):  # 4 rows of labels
                for col in range(3):  # 3 columns of labels
                    x = 50 + col * (200 + 20)
                    y = 50 + row * (150 + 20)

                    page.insert_image(
                        fitz.Rect(x + 10, y + 10, x + 60, y + 60),
                        stream=company_logo_bytes,
                        overlay=True
                    )
                    page.insert_image(
                        fitz.Rect(x + 130, y + 10, x + 180, y + 60),
                        stream=client_logo_bytes,
                        overlay=True
                    )

        output_filename = f"output_{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        doc.save(output_path)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
