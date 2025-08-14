from fpdf import FPDF


def generate_rdv_pdf(nom, date, heure, motif):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Confirmation de Rendez-vous", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nom : {nom}", ln=True)
    pdf.cell(200, 10, txt=f"Date : {date}", ln=True)
    pdf.cell(200, 10, txt=f"Heure : {heure}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Motif : {motif}")

    filename = f"rdv_{nom.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename
