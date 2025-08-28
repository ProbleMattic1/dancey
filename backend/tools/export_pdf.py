from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def export_pdf(comp, thumbs_dir, out_path):
    c = canvas.Canvas(out_path, pagesize=LETTER)
    W,H = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, H-72, f"{comp['title']} · {comp['bpm']} BPM · {comp['bars']} bars")
    y = H-110
    for step in comp['steps']:
        c.setFont("Helvetica", 12)
        c.drawString(72, y, f"{step['order']+1}. {step['move_id']} · {step['beats']} beats {'(mirrored)' if step.get('mirror') else ''}")
        for i in range(5):
            p = f"{thumbs_dir}/{step['move_id']}_{i}.png"
            try: c.drawImage(p, 72 + i*0.9*inch, y-0.8*inch, width=0.8*inch, height=0.8*inch)
            except: pass
        y -= 1.1*inch
        if y < 100: c.showPage(); y = H-72
    c.save()
