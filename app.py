import io
import os
import tempfile
import zipfile

from flask import Flask, abort, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)


def split_pdf_to_dir(pdf_path, output_dir, max_mb):
    if max_mb <= 0:
        raise ValueError("O tamanho maximo deve ser maior que zero.")

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    if num_pages == 0:
        raise ValueError("O PDF nao tem paginas.")

    size_bytes = os.path.getsize(pdf_path)
    max_bytes = int(max_mb * 1024 * 1024)
    avg_page_bytes = max(size_bytes // num_pages, 1)
    pages_per_part = max(1, max_bytes // avg_page_bytes)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    part = 1
    page_index = 0
    output_files = []

    while page_index < num_pages:
        writer = PdfWriter()
        added = 0
        while added < pages_per_part and page_index < num_pages:
            writer.add_page(reader.pages[page_index])
            added += 1
            page_index += 1

        output_path = os.path.join(output_dir, f"{base_name}_parte{part}.pdf")
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
        output_files.append(output_path)
        part += 1

    return output_files


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if "pdf_file" not in request.files:
        abort(400, "Arquivo PDF nao enviado.")

    pdf_file = request.files["pdf_file"]
    if not pdf_file or not pdf_file.filename:
        abort(400, "Arquivo PDF invalido.")

    try:
        max_mb = float(request.form.get("max_mb", "0"))
    except ValueError:
        abort(400, "Tamanho maximo invalido.")

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(pdf_path)

        try:
            parts = split_pdf_to_dir(pdf_path, temp_dir, max_mb)
        except Exception as exc:
            abort(400, f"Erro ao dividir o PDF: {exc}")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for part_path in parts:
                zipf.write(part_path, arcname=os.path.basename(part_path))
        zip_buffer.seek(0)

        base_name = os.path.splitext(os.path.basename(pdf_file.filename))[0]
        zip_name = f"{base_name}_partes.zip"
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=zip_name,
        )


if __name__ == "__main__":
    app.run(debug=True)
