import fitz  # PyMuPDF
import re
from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa CORS

app = Flask(__name__)
CORS(app)  # Aplica CORS a tu app

def extract_text_from_pdf(file):
    # Abre el archivo PDF desde un objeto de archivo
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        # Obtiene el texto de la primera página
        page = pdf[0]
        text = page.get_text("text")
    return text

def extract_contact_info(text):
    # Asumimos que el nombre podría estar en las primeras líneas del CV (esto es simplificado)
    name_match = re.search(r"(?<=\n)[A-Z][a-z]+(?:\s[A-Z][a-z]+)+", text)
    name = name_match.group(0) if name_match else None
    
    # Buscar el correo electrónico
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group(0) if email_match else None
    
    # Buscar el número de teléfono (formato común internacional y local)
    phone_match = re.search(r"\+?\d{1,4}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}", text)
    phone = phone_match.group(0) if phone_match else None

    return {
        "name": name,
        "email": email,
        "phone": phone
    }

@app.route('/procesar_pdf', methods=['POST'])
def procesar_pdf():
    if 'archivo_pdf' not in request.files:
        return jsonify({'error': 'No se envió un archivo'}), 400

    file = request.files['archivo_pdf']
    if file:
        text = extract_text_from_pdf(file)
        contact_info = extract_contact_info(text)
        return jsonify(contact_info)

    return jsonify({'error': 'No se pudo procesar el archivo'}), 500

if __name__ == '__main__':
    app.run(debug=True)
