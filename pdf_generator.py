from datetime import date
from fpdf import FPDF


def generate_pdf(topic):
    today = str(date.today())
    title = today + ": A brief overview of " + topic
    file = open("doc/content/" + today + "_" + topic + ".txt", "r")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 20, txt=title, ln=1, align='C')
    count = 2
    try:
        for line in file:
            line = ' '.join(line.split('\n'))
            pdf.cell(200, 5, txt=line.encode('UTF-8').decode('latin-1'), ln=count, align='C')
            count += 1
        pdf.output("doc/pdf/" + title + ".pdf")
    except Exception as ex:
        print("Error while generating pdf", ex)


#generate_pdf("artificial intelligence")
