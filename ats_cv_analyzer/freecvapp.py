import streamlit as st
import docx2txt
import PyPDF2
import re
from collections import Counter
from fpdf import FPDF
import os
import glob
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime
import random
import spacy
import pandas as pd
from supabase import create_client, Client

# ------------------ Spacy NLP ------------------
nlp = spacy.load("en_core_web_sm")

# ------------------ PDF Class ------------------
from trademark_config import TRADEMARK_INFO

class PDF(FPDF):
    def footer(self):
        self.set_y(-20)
        self.set_font("DejaVu", size=8)
        self.set_text_color(100, 100, 100)
        current_year = datetime.now().year
        brand = TRADEMARK_INFO['brand_name']
        disclaimer = TRADEMARK_INFO['disclaimer']
        footer_text = f"© {current_year} {brand} | {disclaimer} | Page {self.page_no()}"
        self.cell(0, 8, footer_text, align="C")

# ------------------ Supabase Setup ------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
Admin = st.secrets["Admin"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Text Extraction ------------------
def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(file)
    else:
        return file.getvalue().decode("utf-8")

# ------------------ Job Keywords Loader ------------------
def detect_job_keywords(cv_name, folder="job_keywords"):
    base_name = cv_name.lower().replace(" ", "_")
    files = glob.glob(os.path.join(folder, "*.txt"))
    matched_file = None
    for file in files:
        job = os.path.splitext(os.path.basename(file))[0].lower()
        if job in base_name:
            matched_file = file
            break
    if not matched_file and files:
        matched_file = (
            os.path.join(folder, "software_engineer.txt")
            if os.path.exists(os.path.join(folder, "software_engineer.txt"))
            else files[0]
        )
    keywords = []
    if matched_file:
        with open(matched_file, "r") as f:
            keywords = [kw.strip() for kw in f.read().split(",") if kw.strip()]
    return keywords, matched_file, files

# ------------------ CV Analysis ------------------
def analyze_cv(text, job_keywords=None):
    text_lower = text.lower()
    result = {}
    result['sections'] = {
        'summary': bool(re.search(r'(summary|profile|about me)', text_lower)),
        'skills': bool(re.search(r'(skills|technologies|competencies)', text_lower)),
        'experience': bool(re.search(r'(experience|employment|work history)', text_lower)),
        'education': bool(re.search(r'(education|qualification|degree)', text_lower)),
        'contact': bool(re.search(r'(email|phone|contact)', text_lower)),
    }
    strengths, weaknesses = [], []
    for sec, exists in result['sections'].items():
        if exists:
            strengths.append(f"{sec.capitalize()} section is present.")
        else:
            weaknesses.append(f"{sec.capitalize()} section missing.")

    words = re.findall(r'\b\w+\b', text_lower)
    common_words = Counter(words).most_common(20)

    matched_keywords, missing_keywords = [], []
    if job_keywords:
        text_words = set(words)
        for kw in job_keywords:
            if kw.lower() in text_words:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

    total_sections = len(result['sections'])
    present_sections = sum(result['sections'].values())
    section_score = (present_sections / total_sections) * 50
    keyword_score = (len(matched_keywords) / len(job_keywords) * 50) if job_keywords else 0

    result.update({
        'strengths': strengths,
        'weaknesses': weaknesses,
        'common_words': common_words,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'ats_score': int(section_score + keyword_score),
    })
    return result

# ------------------ Keyword Suggestions ------------------
def suggest_keyword_usage(missing_keywords, cv_text):
    suggestions = []
    for kw in missing_keywords:
        if kw.lower() in cv_text.lower():
            continue
        suggestion = f"Consider including '{kw}' in your Skills or Experience section, e.g., 'Proficient in {kw}' or 'Worked on projects involving {kw}'."
        suggestions.append(suggestion)
    return suggestions

# ------------------ Rewriter Helpers ------------------
SECTION_TEMPLATES = {
    "summary": [
        "Professional with experience in {}.",
        "Skilled in {}.",
        "Accomplished in {}."
    ],
    "skills": [
        "Proficient in {}.",
        "Experienced with {}.",
        "Hands-on experience in {}."
    ],
    "experience": [
        "Developed expertise in {}.",
        "Led projects involving {}.",
        "Implemented solutions using {}.",
        "Collaborated with teams to optimize {}."
    ],
    "education": [
        "Completed {} degree.",
        "Graduated in {}.",
        "Certified in {}."
    ]
}

SECTION_HEADERS = {
    "summary": ["summary", "profile", "about me", "professional summary"],
    "skills": ["skills", "technologies", "competencies"],
    "experience": ["experience", "employment", "work history", "projects"],
    "education": ["education", "qualification", "degree", "academics"]
}

def detect_sections(cv_text):
    cv_text_lower = cv_text.lower()
    sections = {}
    for sec, headers in SECTION_HEADERS.items():
        for h in headers:
            pattern = r'{}[:\n]'.format(re.escape(h))
            match = re.search(pattern, cv_text_lower)
            if match:
                start = match.end()
                next_header_pos = len(cv_text)
                for other_sec, other_headers in SECTION_HEADERS.items():
                    if other_sec == sec:
                        continue
                    for oh in other_headers:
                        oh_match = re.search(r'{}[:\n]'.format(re.escape(oh)), cv_text_lower[start:])
                        if oh_match:
                            pos = start + oh_match.start()
                            if pos < next_header_pos:
                                next_header_pos = pos
                sections[sec] = cv_text[start:next_header_pos].strip()
                break
        if sec not in sections:
            sections[sec] = ""
    return sections

def inject_keywords(section_text, missing_keywords, section_type):
    bullets = []
    sentences = [s.strip() for s in re.split(r'[.\n]', section_text) if s.strip()]
    for sentence in sentences:
        sentence = re.sub(r"\bworked\b", "developed", sentence, flags=re.I)
        sentence = re.sub(r"\bresponsible\b", "led", sentence, flags=re.I)
        bullets.append(f"- {sentence}")
    for kw in missing_keywords:
        template = random.choice(SECTION_TEMPLATES.get(section_type, ["- {}"]))
        bullets.append(f"- {template.format(kw)}")
    return bullets

def professional_rewrite_cv(cv_text, job_keywords):
    sections = detect_sections(cv_text)
    rewritten_sections = {}
    for sec, text in sections.items():
        missing_keywords = [kw for kw in job_keywords if kw.lower() not in text.lower()]
        rewritten_sections[sec] = inject_keywords(text, missing_keywords, sec)
    final_cv = []
    for sec in ["summary", "skills", "experience", "education"]:
        if rewritten_sections[sec]:
            final_cv.append(sec.capitalize() + ":")
            final_cv.extend(rewritten_sections[sec])
            final_cv.append("")
    return "\n".join(final_cv)

# ------------------ PDF Helpers ------------------
def safe_multicell(pdf, text, line_height=8, indent=5):
    if not text:
        return
    x_start = pdf.get_x()
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin - indent
    pdf.set_x(pdf.l_margin + indent)
    pdf.multi_cell(usable_width, line_height, text)
    pdf.set_x(x_start)

# ------------------ PDF Report ------------------
def generate_pdf(analysis, cv_name="Uploaded_CV", job_keywords=None, rewritten_cv=None):
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
    pdf.add_font("DejaVu", "I", "fonts/DejaVuSans-Oblique.ttf", uni=True)
    pdf.add_font("DejaVu", "BI", "fonts/DejaVuSans-BoldOblique.ttf", uni=True)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "ATS CV Analysis Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, f"ATS-Friendliness Score: {analysis['ats_score']}%", ln=True)
    pdf.ln(5)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Strengths:", ln=True)
    pdf.set_font("DejaVu", "", 11)
    for s in analysis["strengths"]:
        safe_multicell(pdf, f"- {s}", indent=5)
    pdf.ln(3)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Weaknesses:", ln=True)
    pdf.set_font("DejaVu", "", 11)
    for w in analysis["weaknesses"]:
        safe_multicell(pdf, f"- {w}", indent=5)
    pdf.ln(3)

    if job_keywords:
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Keywords Analysis:", ln=True)
        pdf.set_font("DejaVu", "", 11)
        safe_multicell(pdf, f"Matched Keywords: {', '.join(analysis['matched_keywords'])}", indent=5)
        safe_multicell(pdf, f"Missing Keywords: {', '.join(analysis['missing_keywords'])}", indent=5)
        pdf.ln(3)

    if rewritten_cv:
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Professional Rewritten CV:", ln=True)
        pdf.set_font("DejaVu", "", 11)
        for line in rewritten_cv.split("\n"):
            safe_multicell(pdf, line, indent=5)
        pdf.ln(3)

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{cv_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# ------------------ Database Functions ------------------
def log_cv_analysis(cv_name, ats_score, matched_keywords, missing_keywords):
    data = {
        "cv_name": cv_name,
        "ats_score": ats_score,
        "matched_keywords": ",".join(matched_keywords),
        "missing_keywords": ",".join(missing_keywords),
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("analytics").insert(data).execute()

def save_subscriber(email, phone):
    data = {
        "email": email,
        "phone": phone if phone else None,
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("subscribers").insert(data).execute()

# ------------------ Frontend Helpers ------------------
def display_score(score):
    if not isinstance(score, (int, float)) or score < 0 or score > 100:
        score = 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "ATS Score"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#28a745"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

def display_keywords_chart(matched, missing):
    matched_count = len(matched) if matched else 0
    missing_count = len(missing) if missing else 0
    if matched_count + missing_count == 0:
        st.info("No keyword data to display chart.")
        return

    labels = ["Matched", "Missing"]
    sizes = [matched_count, missing_count]
    colors = ["#28a745", "#dc3545"]

    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 1}
    )
    ax.legend(wedges, labels, title="Keywords", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title("Keywords Match", fontsize=12, pad=10)
    ax.axis("equal")
    st.pyplot(fig)

def card(title, items, color):
    st.markdown(f"### {title}")
    if items:
        for i in items:
            st.markdown(
                f"<div style='background-color:{color}; padding:8px 12px; "
                f"border-radius:10px; margin-bottom:6px; font-size:15px;'>"
                f"• {i}</div>", unsafe_allow_html=True
            )
    else:
        st.info("None found")

import streamlit as st
from trademark_config import TRADEMARK_INFO

st.markdown(f"## 🌍 {TRADEMARK_INFO['brand_name']}")

st.markdown("### Trademark Classes")
for category, classes in TRADEMARK_INFO["classes"].items():
    st.markdown(f"**{category}**: {', '.join(classes)}")

st.info(TRADEMARK_INFO["disclaimer"])

# ------------------ Streamlit App ------------------
st.set_page_config(page_title="ATS CV Analyzer & Rewriter", layout="wide")
st.sidebar.image("https://dummyimage.com/200x60/000/fff&text=Tene+Africa", use_column_width=True)
uploaded_file = st.sidebar.file_uploader("📄 Upload a CV", type=["pdf","docx","txt"])

cv_name = None
job_keywords = []
if uploaded_file:
    cv_name = os.path.splitext(uploaded_file.name)[0]
    auto_keywords, auto_file, all_files = detect_job_keywords(cv_name)
    if all_files:
        file_options = {os.path.basename(f): f for f in all_files}
        default_choice = os.path.basename(auto_file) if auto_file else list(file_options.keys())[0]
        chosen_file = st.sidebar.selectbox("Select job keywords file", list(file_options.keys()), index=list(file_options.keys()).index(default_choice))
        kw_file = file_options[chosen_file]
        with open(kw_file, "r") as f:
            job_keywords = [kw.strip() for kw in f.read().split(",") if kw.strip()]
        st.sidebar.info(f"Using {len(job_keywords)} keywords from `{chosen_file}`")
    else:
        st.sidebar.warning("⚠️ No keyword files found")

# ------------------ Newsletter Signup ------------------
st.sidebar.markdown("### 📧 Join our Tene Africa Newsletter")
email = st.sidebar.text_input("Enter your email:")
phone = st.sidebar.text_input("Enter your phone number (optional):")

if st.sidebar.button("Sign Up"):
    if email and "@" in email:
        save_subscriber(email, phone)
        st.sidebar.success("✅ Thank you! You've been added to our list.")
    else:
        st.sidebar.error("❌ Please enter a valid email address.")

# ------------------ Admin Dashboard ------------------
st.sidebar.markdown("---")
admin_key = st.sidebar.text_input("Admin Access Key")

if admin_key == Admin:
    st.header("📊 Admin Analytics Dashboard")

    # CV Analytics
    response = supabase.table("analytics").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        st.write("Total CVs uploaded:", len(df))
        st.bar_chart(df['ats_score'])
        matched_total = sum(df['matched_keywords'].apply(lambda x: len(x.split(","))))
        missing_total = sum(df['missing_keywords'].apply(lambda x: len(x.split(","))))
        st.write(f"Total matched keywords: {matched_total}")
        st.write(f"Total missing keywords: {missing_total}")
    else:
        st.info("No analytics data available.")

    # Subscribers
    st.subheader("📧 Newsletter Subscribers")
    sub_resp = supabase.table("subscribers").select("*").execute()
    if sub_resp.data:
        subs_df = pd.DataFrame(sub_resp.data)
        st.dataframe(subs_df[["email", "phone", "timestamp"]])
    else:
        st.info("No subscribers yet.")

# ------------------ Main Dashboard ------------------
st.title("📊 ATS CV Analyzer & Professional Rewriter Dashboard")
with st.expander("ℹ️ About this App"):
    st.markdown("""
    ### 📄 ATS CV Analyzer & Optimizer

    This app helps job seekers improve their chances of passing **Applicant Tracking Systems (ATS)** 
    by analyzing their CVs against job descriptions and industry keywords.  

    **What it does:**
    - ✅ Extracts text from CVs (PDF/DOCX)  
    - 📊 Calculates an ATS score based on keyword matches  
    - 🔍 Highlights missing and matched keywords  
    - ✍️ Suggests improvements and rewrites sections professionally  
    - 📈 Provides detailed analytics and visualizations  
    - 💾 Generates a full PDF report of the analysis  

    **Extra Features:**
    - 📧 Newsletter signup (with optional phone number)  
    - 🛠 Admin dashboard to view analytics and subscribers  
    - ☁️ Powered by Supabase for secure cloud storage  

    ---
    ⚡ Developed by *Tene Africa* to help job seekers stand out in a competitive market.
    """)


if uploaded_file:
    text = extract_text(uploaded_file)
    analysis = analyze_cv(text, job_keywords=job_keywords)

    # Only log once per uploaded file
    if "logged_files" not in st.session_state:
        st.session_state.logged_files = set()

    if cv_name not in st.session_state.logged_files:
        log_cv_analysis(cv_name, analysis['ats_score'], analysis['matched_keywords'], analysis['missing_keywords'])
        st.session_state.logged_files.add(cv_name)

    try:
        display_score(analysis['ats_score'])
    except Exception as e:
        st.error(f"Unable to render ATS score chart: {e}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✅ Strengths", "⚠️ Weaknesses", "🔑 Keywords", "📋 Common Words", "✍️ Professional Rewritten CV"
    ])

    with tab1:
        card("Strengths", analysis["strengths"], "#e6ffe6")
    with tab2:
        card("Weaknesses", analysis["weaknesses"], "#ffe6e6")
    with tab3:
        st.subheader("🔑 Keywords Analysis")
        inner_tab1, inner_tab2, inner_tab3 = st.tabs(["✅ Matched", "❌ Missing", "💡 Suggestions"])
        with inner_tab1:
            if analysis["matched_keywords"]:
                for kw in analysis["matched_keywords"]:
                    st.markdown(f"<span style='background-color:#e6ffe6; padding:6px 10px; border-radius:8px; margin:4px; display:inline-block;'>{kw}</span>", unsafe_allow_html=True)
            else:
                st.info("No matched keywords")
        with inner_tab2:
            if analysis["missing_keywords"]:
                for kw in analysis["missing_keywords"]:
                    st.markdown(f"<span style='background-color:#ffe6e6; padding:6px 10px; border-radius:8px; margin:4px; display:inline-block;'>{kw}</span>", unsafe_allow_html=True)
            else:
                st.success("No missing keywords")
        with inner_tab3:
            suggestions = suggest_keyword_usage(analysis["missing_keywords"], text)
            if suggestions:
                for sug in suggestions:
                    st.markdown(f"<div style='background-color:#fff3cd; padding:8px 12px; border-radius:10px; margin-bottom:6px;'>{sug}</div>", unsafe_allow_html=True)
            else:
                st.success("No suggestions needed!")
        try:
            display_keywords_chart(analysis["matched_keywords"], analysis["missing_keywords"])
        except Exception as e:
            st.error(f"Unable to render keywords chart: {e}")
    with tab4:
        st.subheader("📋 Top 20 Frequent Words")
        if analysis["common_words"]:
            common_df = pd.DataFrame(analysis["common_words"], columns=["Word", "Count"])
            st.dataframe(common_df)
        else:
            st.info("No words extracted")
    with tab5:
        st.subheader("✍️ Professional Rewritten CV")
        rewritten_cv = professional_rewrite_cv(text, job_keywords)
        st.text_area("Rewritten CV:", rewritten_cv, height=400)
        st.download_button("📥 Download Rewritten CV", rewritten_cv, file_name=f"{cv_name}_rewritten.txt")
        pdf_report = generate_pdf(analysis, cv_name, job_keywords, rewritten_cv)
        with open(pdf_report, "rb") as f:
            st.download_button("📥 Download Full PDF Report", f, file_name=os.path.basename(pdf_report))
else:
    st.info("Please upload a CV to begin analysis.")
    

