import streamlit as st
import os
import re
from PyPDF2 import PdfReader, PdfWriter
import zipfile
from io import BytesIO


# Télécharger le fichier PDF via Streamlit
pdf_file = st.file_uploader('Import PDF', type="pdf")

if pdf_file is not None:
    # Lire le contenu du fichier téléchargé
    pdf_file_path = pdf_file.name
    pdf_reader = PdfReader(BytesIO(pdf_file.read()))

    # Créer un fichier ZIP en mémoire
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        count = 0
        for page_num in range(len(pdf_reader.pages)):
            if count > 0:
                count -= 1
                continue

            pdf_writer = PdfWriter()
            page_obj = pdf_reader.pages[page_num]
            pdf_writer.add_page(page_obj)
            text = page_obj.extract_text()

            matched_text_array = re.findall(r"Etablissement\s+(\d{2})", text)
            if not matched_text_array:
                continue  

            matched_text = f"Etablissement {matched_text_array[0]}"

            i = page_num + 1
            while i < len(pdf_reader.pages):
                page_obj_next = pdf_reader.pages[i]
                text_next = page_obj_next.extract_text()
                matched_text_array_next = re.findall(r"Etablissement\s+(\d{2})", text_next)

                if not matched_text_array_next:
                    break

                matched_text_next = f"Etablissement {matched_text_array_next[0]}"
                if matched_text == matched_text_next:
                    i += 1
                    count += 1
                    pdf_writer.add_page(page_obj_next)
                else:
                    break

            # Créer le fichier PDF en mémoire
            output_filename = f"{matched_text.replace(' ', '_')}.pdf"
            pdf_bytes = BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)

            # Ajouter le fichier PDF au fichier ZIP
            zipf.writestr(output_filename, pdf_bytes.read())

    # Offrir le fichier ZIP pour téléchargement via Streamlit
    zip_buffer.seek(0)
    st.download_button('Télécharger le fichier ZIP', zip_buffer, file_name='Etat_des_couts_analytiques.zip')
