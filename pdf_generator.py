from datetime import date
from fpdf import FPDF


def generate_pdf(topic):
    today = str(date.today())
    title = today + ": A brief overview of " + topic
    file = open("doc/content/" + today + "_" + topic + ".txt", "r")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 20, txt=title, ln=1, align='L')
    buffer = []
    is_references = False
    try:
        for line in file:
            buffer, is_references = write_new_line(buffer, line, pdf, is_references)
        pdf.output("doc/pdf/" + title + ".pdf")
    except Exception as ex:
        print("Error while generating pdf", ex)


LINE_MAX_LENGTH = 13


def write_new_line(buffer, line, pdf, is_references):
    if not line.startswith("https://"):
        words = line.split()
        if len(words) > 0:
            buffer.extend(words)
            if len(buffer) >= LINE_MAX_LENGTH:
                count = 0
                new_line = ""
                for count in range(len(buffer)):
                    if count == 0 or count % LINE_MAX_LENGTH != 0:
                        new_line += ' ' + buffer[count]
                    elif count != 0 and count % LINE_MAX_LENGTH == 0:
                        new_line += ' ' + buffer[count]
                        pdf.cell(200, 5, txt=new_line.encode('UTF-8').decode('latin-1'), ln=1, align='L')
                        new_line = ""
                        if (len(buffer) - count) < LINE_MAX_LENGTH:
                            break

                    count += 1

                buffer = buffer[count + 1:]
        else:
            new_line = ""
            for w in buffer:
                new_line += ' ' + w
            buffer = []
            pdf.cell(200, 5, txt=new_line.encode('UTF-8').decode('latin-1'), ln=1, align='L')
    else:
        if not is_references:
            pdf.cell(200, 10, txt='', ln=1, align='L')
            pdf.cell(200, 5, txt='References:', ln=1, align='L')
            is_references = True

        pdf.cell(200, 5, txt=line, ln=1, align='L')
    return buffer, is_references


#generate_pdf("artificial intelligence")
