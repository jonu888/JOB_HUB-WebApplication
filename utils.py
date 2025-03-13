import os
import subprocess
from django.conf import settings

from django.utils.html import strip_tags
from weasyprint import HTML
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def render_to_latex(resume):
    # Common packages for all templates, including fontawesome5
    common_packages = "enumitem,geometry,hyperref,parskip,titlesec,multicol,graphicx,fontawesome5"

    # Template-specific configurations
    if resume.template == "elegant":
        # Elegant: Serif font, decorative lines, centered layout
        font_package = "mathpazo"  # Palatino font
        section_format = "\\titleformat{\\section}{\\large\\scshape\\bfseries}{\\thesection}{1em}{}[{\\vspace{0.5ex}\\titlerule[0.8pt]}]"
        section_spacing = "\\titlespacing*{\\section}{0pt}{2ex}{1ex}"
        line_thickness = "0.8pt"
        header_format = "\\begin{center} {\\Huge \\scshape \\textbf{" + resume.full_name + "}} \\\\[5pt] \\end{center}"

    elif resume.template == "modern":
        # Modern: Sans-serif font, minimalistic, two-column header
        font_package = "helvet"  # Helvetica font
        section_format = "\\titleformat{\\section}{\\large\\bfseries\\sffamily}{\\thesection}{1em}{}"
        section_spacing = "\\titlespacing*{\\section}{0pt}{1.5ex}{0.8ex}"
        line_thickness = "1pt"
        header_format = "{\\Huge \\sffamily \\textbf{" + resume.full_name + "}} \\\\ \\vspace{2pt} \\begin{tabular}{p{0.6\\textwidth} p{0.4\\textwidth}}"

    else:  # resume.template == "professional"
        # Professional: Classic font, formal table layout
        font_package = "times"  # Times New Roman font
        section_format = "\\titleformat{\\section}{\\large\\bfseries}{\\thesection}{1em}{}"
        section_spacing = "\\titlespacing*{\\section}{0pt}{1.5ex}{0.8ex}"
        line_thickness = "0.6pt"
        header_format = "{\\Huge \\textbf{" + resume.full_name + "}} \\\\ \\vspace{2pt} \\begin{tabular}{l r}"

    # Build the LaTeX template
    latex_template = f"""
\\documentclass[a4paper,10pt]{{article}}
\\usepackage{{{common_packages},{font_package}}}
\\geometry{{margin=0.8in}}
\\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\pagenumbering{{gobble}}
\\setlength{{\\parindent}}{{0pt}}
\\renewcommand{{\\labelitemi}}{{$\\bullet$}}
{section_format}
{section_spacing}
\\hypersetup{{colorlinks=false, pdfborder={{0 0 0}}}}

\\begin{{document}}

{header_format}
"""

    # Add header details with FontAwesome icons
    if resume.template == "elegant":
        latex_template += (
            f"\\faEnvelope\\ \\href{{mailto:{resume.email}}}{{Email}} & {resume.location} \\\\ "
            f"\\faGithub\\ {'' if not resume.github_url else f'\\href{{{resume.github_url}}}{{GitHub}}'} & {resume.phone} \\\\ "
            f"\\faLinkedin\\ {'' if not resume.linkedin_url else f'\\href{{{resume.linkedin_url}}}{{LinkedIn}}'} \\\\ "
            "\\end{center} \\noindent\\rule{\\linewidth}{" + line_thickness + "}\\\\"
        )
    elif resume.template == "modern":
        latex_template += (
            f"\\faEnvelope\\ \\href{{mailto:{resume.email}}}{{Email}} & \\faGithub\\ {'' if not resume.github_url else f'\\href{{{resume.github_url}}}{{GitHub}}'} \\\\ "
            f"{resume.location} & \\faLinkedin\\ {'' if not resume.linkedin_url else f'\\href{{{resume.linkedin_url}}}{{LinkedIn}}'} \\\\ "
            f"{resume.phone} & \\\\ \\end{{tabular}} \\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\"
        )
    else:  # professional
        latex_template += (
            f"\\faEnvelope\\ \\href{{mailto:{resume.email}}}{{Email}} & {resume.location} \\\\ "
            f"\\faGithub\\ {'' if not resume.github_url else f'\\href{{{resume.github_url}}}{{GitHub}}'} & {resume.phone} \\\\ "
            f"\\faLinkedin\\ {'' if not resume.linkedin_url else f'\\href{{{resume.linkedin_url}}}{{LinkedIn}}'} & \\\\ "
            "\\end{tabular} \\noindent\\rule{\\linewidth}{" + line_thickness + "}\\\\"
        )

    latex_template += """
\\section*{Summary}
"""
    latex_template += strip_tags(resume.summary).replace('\n', ' ') + " \\\\\n"  # Remove HTML tags and add line break
    latex_template += f"\\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\ \\section*{{Education}}\n"
    for edu in resume.education:
        if edu['degree']:
            latex_template += f"\\textbf{{{edu['degree']}}} \\\\ \\textit{{{edu['institution']}}} \\hfill \\textbf{{{edu['dates']}}} \\\\ CGPA: \\textbf{{{edu['cgpa']}}} \\\\\n"

    latex_template += f"\\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\ \\section*{{Experience}}\n"
    for exp in resume.experience:
        if exp['title']:
            latex_template += f"\\textbf{{{exp['title']}}} \\hfill \\textit{{{exp['company']}}} \\hfill \\textbf{{{exp['dates']}}} \\\\\n"
            if exp['details']:
                latex_template += "\\begin{itemize}[leftmargin=*,itemsep=0pt]\n"
                for detail in exp['details']:
                    latex_template += f"    \\item {strip_tags(detail).replace('\n', ' ')}\n"  # Remove HTML tags
                latex_template += "\\end{itemize}\n"

    latex_template += f"\\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\ \\section*{{Projects}}\n"
    for proj in resume.projects:
        if proj['title']:
            latex_template += f"\\underline{{\\textbf{{{proj['title']}}}}} {'\\hfill \\href{' + proj['url'] + '}{GitHub}' if proj['url'] else ''} \\\\\n {strip_tags(proj['description']).replace('\n', ' ')} \\\\\n"
            if proj['technologies']:
                latex_template += "\\begin{itemize}[leftmargin=*,itemsep=0pt]\n    \\item \\textbf{Technologies Used:} " + ", ".join(proj['technologies']) + "\n\\end{itemize}\n"

    latex_template += f"\\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\ \\section*{{Skills}}\n\\begin{{multicols}}{{2}}\n\\begin{{itemize}}[leftmargin=*,itemsep=0pt]\n"
    for skill in resume.skills:
        if skill['category']:
            latex_template += f"    \\item \\textbf{{{skill['category']}:}} {', '.join(skill['items'])}\n"
    latex_template += "\\end{itemize}\n\\end{multicols}\n"

    latex_template += f"\\noindent\\rule{{\\linewidth}}{{{line_thickness}}}\\\\ \\section*{{Languages}}\n\\begin{{itemize}}[leftmargin=*,itemsep=0pt]\n"
    for lang in resume.languages:
        if lang:
            latex_template += f"    \\item {lang}\n"
    latex_template += "\\end{itemize}\n"

    latex_template += "\\end{document}"
    
    return latex_template

def generate_pdf(resume):
    # Render the resume template to HTML
    html_content = render_to_string(f'templates/{resume.template}.html', {'resume': resume})
    
    # Create PDF using WeasyPrint
    html = HTML(string=html_content, base_url=settings.BASE_DIR)
    pdf = html.write_pdf()
    
    return pdf