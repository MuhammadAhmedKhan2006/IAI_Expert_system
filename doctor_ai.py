import streamlit as st
import sqlite3
import datetime

st.set_page_config(page_title="IAI Medical Expert System", page_icon="🩺")
DB_NAME = "doctor_ai.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("CREATE TABLE IF NOT EXISTS consultations (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, symptoms TEXT, report_values TEXT, suggestion TEXT)")
    conn.commit(); conn.close()

def save_to_db(symptoms, report_values, suggestion):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO consultations (timestamp, symptoms, report_values, suggestion) VALUES (?, ?, ?, ?)", (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(symptoms), str(report_values), suggestion))
    conn.commit(); conn.close()

init_db()
s = st.session_state
if 'step' not in s:
    s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False; s.show_data = False

st.title("🩺 IAI Expert System: Medical Assistant")

conn = sqlite3.connect(DB_NAME)
db_count = conn.execute("SELECT COUNT(*) FROM consultations").fetchone()[0]
conn.close()
st.sidebar.write("📊 Saved consultations: " + str(db_count))
if st.sidebar.button("📂 View Saved Data", key="viewdata"):
    s.show_data = not s.show_data
    st.rerun()
if s.show_data:
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT id, timestamp, symptoms, report_values, suggestion FROM consultations ORDER BY id DESC").fetchall()
    conn.close()
    st.subheader("📂 Saved Consultations")
    if len(rows) == 0: st.write("Abhi koi data save nahi hua.")
    for r in rows:
        st.write("**#" + str(r[0]) + "** | " + str(r[1])); st.write("Symptoms: " + str(r[2])); st.write("Reports: " + str(r[3])); st.write("Suggestion: " + str(r[4])); st.divider()

step = s.step

# ================= START =================
if step == 'start':
    st.subheader("Aapko kya problem hai? (Select main complaint)")
    a, b, c = st.columns(3)
    if a.button("🤧 Cough / Fever", key="p1"): s.patient_data['main_complaint'] = "Cough/Fever"; s.step = 'cf1'; st.rerun()
    if b.button("💔 Chest Pain", key="p2"): s.patient_data['main_complaint'] = "Chest Pain"; s.step = 'cp1'; st.rerun()
    if c.button("🤢 Stomach Pain", key="p3"): s.patient_data['main_complaint'] = "Stomach Pain"; s.step = 'sp1'; st.rerun()
    d, e, f = st.columns(3)
    if d.button("🤕 Headache", key="p4"): s.patient_data['main_complaint'] = "Headache"; s.step = 'hd1'; st.rerun()
    if e.button("🦴 Joint Pain", key="p5"): s.patient_data['main_complaint'] = "Joint Pain"; s.step = 'jp1'; st.rerun()
    if f.button("🧴 Skin Problem", key="p6"): s.patient_data['main_complaint'] = "Skin Problem"; s.step = 'sk1'; st.rerun()
    g, h, i = st.columns(3)
    if g.button("🚻 Urinary Problem", key="p7"): s.patient_data['main_complaint'] = "Urinary Problem"; s.step = 'ur1'; st.rerun()
    if h.button("🗣️ Throat Problem", key="p8"): s.patient_data['main_complaint'] = "Throat Problem"; s.step = 'th1'; st.rerun()
    if i.button("🧍 Back Pain", key="p9"): s.patient_data['main_complaint'] = "Back Pain"; s.step = 'bp1'; st.rerun()

# ================= PATH 1: COUGH / FEVER (15 Qs) =================
elif step == 'cf1':
    st.subheader("🫁 [Cough/Fever] Q1: Kya aapko 2 hafte se zyada khansi (cough) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf1y"):
        s.patient_data['cough_2wk'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Cough more than 2 weeks: +15 risk"); s.step = 'cf2'; st.rerun()
    if c2.button("No / Nahi", key="cf1n"): s.patient_data['cough_2wk'] = "No"; s.step = 'cf2'; st.rerun()
elif step == 'cf2':
    st.subheader("🫁 Q2: Raat ko paseena (night sweats) ya wazan kam ho raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf2y"):
        s.patient_data['night_sweats_weight_loss'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Night sweats / weight loss: +15 risk"); s.step = 'cf3'; st.rerun()
    if c2.button("No / Nahi", key="cf2n"): s.patient_data['night_sweats_weight_loss'] = "No"; s.step = 'cf3'; st.rerun()
elif step == 'cf3':
    st.subheader("🫁 Q3: Khansi mein khoon (blood in cough) aata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf3y"):
        s.patient_data['blood_cough'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Blood in cough: +25 risk"); s.step = 'cf4'; st.rerun()
    if c2.button("No / Nahi", key="cf3n"): s.patient_data['blood_cough'] = "No"; s.step = 'cf4'; st.rerun()
elif step == 'cf4':
    st.subheader("🫁 Q4: Kya saans phoolti hai (breathlessness)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf4y"):
        s.patient_data['breathless'] = "Yes"
        if s.patient_data['blood_cough'] == "Yes": s.risk = max(s.risk + 40, 70); s.reasons.append("Breathlessness together with blood in cough: risk raised to at least 70"); s.step = 'end'
        else: s.risk = s.risk + 15; s.reasons.append("Breathlessness: +15 risk"); s.step = 'cf5'
        st.rerun()
    if c2.button("No / Nahi", key="cf4n"): s.patient_data['breathless'] = "No"; s.step = 'cf5'; st.rerun()
elif step == 'cf5':
    st.subheader("🫁 Q5: Kya bukhar 100.4°F se zyada hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf5y"):
        s.patient_data['fever_high'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Fever above 100.4F: +10 risk"); s.step = 'cf_plt'; st.rerun()
    if c2.button("No / Nahi", key="cf5n"): s.patient_data['fever_high'] = "No"; s.step = 'cf_plt'; st.rerun()
elif step == 'cf_plt':
    st.subheader("📋 Q6 (Report): Platelet count (normal 150000-450000)")
    plt = st.number_input("Apni report se platelet count likhein", min_value=0, max_value=1000000, value=250000, step=1000, key="plt_in")
    if st.button("Submit Report", key="plt_btn"):
        s.report_data['platelets'] = plt
        if plt < 20000: s.risk = max(s.risk + 60, 70); s.reasons.append("Platelets critically low (" + str(plt) + "): risk raised to at least 70"); s.step = 'end'
        elif plt < 150000: s.risk = s.risk + 15; s.reasons.append("Platelets low (" + str(plt) + "): +15 risk"); s.step = 'cf6'
        else: s.step = 'cf6'
        st.rerun()
elif step == 'cf6':
    st.subheader("🫁 Q7: Kya aapne TB ka test karwaya hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf6y"): s.patient_data['tb_test_done'] = "Yes"; s.step = 'cf7'; st.rerun()
    if c2.button("No / Nahi", key="cf6n"):
        s.patient_data['tb_test_done'] = "No"; s.risk = max(s.risk + 20, 40); s.reasons.append("Relevant test (TB) not done yet: risk raised to at least 40, test zaroori hai"); s.step = 'end'; st.rerun()
elif step == 'cf7':
    st.subheader("🫁 Q8: Kya TB test positive aaya?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf7y"):
        s.patient_data['tb_positive'] = "Yes"; s.risk = max(s.risk + 30, 40); s.reasons.append("Test report positive (needs doctor confirmation): risk raised to at least 40"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cf7n"): s.patient_data['tb_positive'] = "No"; s.step = 'cf8'; st.rerun()
elif step == 'cf8':
    st.subheader("🫁 Q9: Test negative aane ke bawajood kya symptoms abhi bhi hain? (False negative ho sakta hai)"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf8y"):
        s.patient_data['symptoms_despite_negative'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Symptoms continue despite negative test (false negative possible): +15 risk"); s.step = 'cf_mg'; st.rerun()
    if c2.button("No / Nahi", key="cf8n"): s.patient_data['symptoms_despite_negative'] = "No"; s.step = 'cf11'; st.rerun()
elif step == 'cf_mg':
    st.subheader("📋 Q10 (Report): Magnesium level (normal 1.7-2.2 mg/dL)")
    mg = st.number_input("Apni report se magnesium likhein", min_value=0.0, max_value=10.0, value=2.0, step=0.1, key="mg_in")
    if st.button("Submit Report", key="mg_btn"):
        s.report_data['magnesium'] = mg
        if mg < 1.7: s.risk = s.risk + 10; s.reasons.append("Magnesium low (" + str(mg) + "): +10 risk"); s.step = 'cf9'
        else: s.step = 'cf9'
        st.rerun()
elif step == 'cf9':
    st.subheader("🫁 Q11: Kya aap roz 6 ghante se kam sote hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf9y"):
        s.patient_data['sleep_less_6'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Sleep less than 6 hours: +10 risk"); s.step = 'cf10'; st.rerun()
    if c2.button("No / Nahi", key="cf9n"): s.patient_data['sleep_less_6'] = "No"; s.step = 'cf10'; st.rerun()
elif step == 'cf10':
    st.subheader("🫁 Q12: Kya bukhar ya peela/hara balgham (yellow-green phlegm) hai? (Body infection)"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf10y"):
        s.patient_data['infection_phlegm'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Fever / yellow-green phlegm (possible infection): +15 risk"); s.step = 'cf11'; st.rerun()
    if c2.button("No / Nahi", key="cf10n"): s.patient_data['infection_phlegm'] = "No"; s.step = 'cf11'; st.rerun()
elif step == 'cf11':
    st.subheader("🫁 Q13: Kya ghar mein koi TB ka mareez hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf11y"):
        s.patient_data['tb_contact'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("TB patient at home (contact risk): +15 risk"); s.step = 'cf12'; st.rerun()
    if c2.button("No / Nahi", key="cf11n"): s.patient_data['tb_contact'] = "No"; s.step = 'cf12'; st.rerun()
elif step == 'cf12':
    st.subheader("🫁 Q14: Kya aap smoking karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf12y"):
        s.patient_data['smoking'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Smoking: +5 risk"); s.step = 'cf13'; st.rerun()
    if c2.button("No / Nahi", key="cf12n"): s.patient_data['smoking'] = "No"; s.step = 'cf13'; st.rerun()
elif step == 'cf13':
    st.subheader("🫁 Q15: Kya khansi ke saath seene mein dard (chest pain) hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cf13y"):
        s.patient_data['chest_pain_with_cough'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Chest pain with cough: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cf13n"): s.patient_data['chest_pain_with_cough'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 2: CHEST PAIN (15 Qs) =================
elif step == 'cp1':
    st.subheader("💔 [Chest Pain] Q1: Kya seene mein pressure / squeezing (dabao) mehsoos hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp1y"):
        s.patient_data['pressure_pain'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Chest pressure / squeezing: +25 risk"); s.step = 'cp2'; st.rerun()
    if c2.button("No / Nahi", key="cp1n"): s.patient_data['pressure_pain'] = "No"; s.step = 'cp2'; st.rerun()
elif step == 'cp2':
    st.subheader("💔 Q2: Kya dard bazu, jabde (jaw) ya peeth tak phailta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp2y"):
        s.patient_data['pain_spreads'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Pain spreading to arm/jaw/back: +20 risk"); s.step = 'cp3'; st.rerun()
    if c2.button("No / Nahi", key="cp2n"): s.patient_data['pain_spreads'] = "No"; s.step = 'cp3'; st.rerun()
elif step == 'cp3':
    st.subheader("💔 Q3: Kya paseena, ulti jaisa mann (nausea) ya chakkar aa rahe hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp3y"):
        s.patient_data['sweat_nausea_dizzy'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Sweating / nausea / dizziness: +15 risk"); s.step = 'cp4'; st.rerun()
    if c2.button("No / Nahi", key="cp3n"): s.patient_data['sweat_nausea_dizzy'] = "No"; s.step = 'cp4'; st.rerun()
elif step == 'cp4':
    st.subheader("💔 Q4: Kya saans phoolti hai (breathlessness)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp4y"):
        s.patient_data['breathless'] = "Yes"
        if s.patient_data['pressure_pain'] == "Yes": s.risk = max(s.risk + 40, 70); s.reasons.append("Breathlessness together with chest pressure: risk raised to at least 70"); s.step = 'end'
        else: s.risk = s.risk + 10; s.reasons.append("Breathlessness: +10 risk"); s.step = 'cp5'
        st.rerun()
    if c2.button("No / Nahi", key="cp4n"): s.patient_data['breathless'] = "No"; s.step = 'cp5'; st.rerun()
elif step == 'cp5':
    st.subheader("💔 Q5: Kya dard 20 minute se zyada raha?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp5y"):
        s.patient_data['pain_over_20min'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Pain lasting more than 20 minutes: +20 risk"); s.step = 'cp_bp'; st.rerun()
    if c2.button("No / Nahi", key="cp5n"): s.patient_data['pain_over_20min'] = "No"; s.step = 'cp_bp'; st.rerun()
elif step == 'cp_bp':
    st.subheader("📋 Q6 (Report): Systolic BP (normal 90-139 mmHg)")
    bp = st.number_input("Apna systolic BP likhein", min_value=40, max_value=300, value=120, step=1, key="cpbp_in")
    if st.button("Submit Report", key="cpbp_btn"):
        s.report_data['chest_systolic_bp'] = bp
        if bp >= 180: s.risk = max(s.risk + 60, 70); s.reasons.append("BP very high (" + str(bp) + "): risk raised to at least 70"); s.step = 'end'
        elif bp < 90: s.risk = s.risk + 20; s.reasons.append("BP low (" + str(bp) + "): +20 risk"); s.step = 'cp_ecg'
        else: s.step = 'cp_ecg'
        st.rerun()
elif step == 'cp_ecg':
    st.subheader("📋 Q7 (Report): ECG ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Normal", key="cpecg_n"): s.report_data['ecg'] = "Normal"; s.step = 'cp6'; st.rerun()
    if c2.button("Abnormal", key="cpecg_a"):
        s.report_data['ecg'] = "Abnormal"; s.risk = max(s.risk + 30, 70); s.reasons.append("Abnormal ECG report: risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c3.button("ECG nahi hua", key="cpecg_x"):
        s.report_data['ecg'] = "Not done"
        if s.risk >= 40: s.reasons.append("ECG not done while risk is already high: urgent ECG and doctor visit needed"); s.step = 'end'
        else: s.step = 'cp6'
        st.rerun()
elif step == 'cp6':
    st.subheader("💔 Q8: Kya hilne-julne ya gehri saans lene par dard barh jata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp6y"):
        s.patient_data['worse_with_movement'] = "Yes"; s.reasons.append("Pain worse with movement: may be muscle strain (no risk added)"); s.step = 'cp7'; st.rerun()
    if c2.button("No / Nahi", key="cp6n"):
        s.patient_data['worse_with_movement'] = "No"; s.risk = s.risk + 10; s.reasons.append("Pain NOT related to movement: +10 risk"); s.step = 'cp7'; st.rerun()
elif step == 'cp7':
    st.subheader("💔 Q9: Kya aap roz aspirin ya blood thinner lete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp7y"):
        s.patient_data['aspirin_thinner'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Daily aspirin / blood thinner: +10 risk"); s.step = 'cp8'; st.rerun()
    if c2.button("No / Nahi", key="cp7n"): s.patient_data['aspirin_thinner'] = "No"; s.step = 'cp8'; st.rerun()
elif step == 'cp8':
    st.subheader("💔 Q10: Kya aapko diabetes (sugar) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp8y"):
        s.patient_data['diabetes'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Diabetes: +10 risk"); s.step = 'cp9'; st.rerun()
    if c2.button("No / Nahi", key="cp8n"): s.patient_data['diabetes'] = "No"; s.step = 'cp9'; st.rerun()
elif step == 'cp9':
    st.subheader("💔 Q11: Kya aapko high BP ki history hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp9y"):
        s.patient_data['high_bp_history'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("High BP history: +10 risk"); s.step = 'cp10'; st.rerun()
    if c2.button("No / Nahi", key="cp9n"): s.patient_data['high_bp_history'] = "No"; s.step = 'cp10'; st.rerun()
elif step == 'cp10':
    st.subheader("💔 Q12: Kya family mein kisi ko dil ki bimari hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp10y"):
        s.patient_data['family_heart'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Family history of heart disease: +10 risk"); s.step = 'cp11'; st.rerun()
    if c2.button("No / Nahi", key="cp10n"): s.patient_data['family_heart'] = "No"; s.step = 'cp11'; st.rerun()
elif step == 'cp11':
    st.subheader("💔 Q13: Kya aap smoking karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp11y"):
        s.patient_data['smoking'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Smoking: +5 risk"); s.step = 'cp12'; st.rerun()
    if c2.button("No / Nahi", key="cp11n"): s.patient_data['smoking'] = "No"; s.step = 'cp12'; st.rerun()
elif step == 'cp12':
    st.subheader("💔 Q14: Kya taangon ya pairon mein sujan (swelling) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp12y"):
        s.patient_data['leg_swelling'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Leg swelling: +10 risk"); s.step = 'cp13'; st.rerun()
    if c2.button("No / Nahi", key="cp12n"): s.patient_data['leg_swelling'] = "No"; s.step = 'cp13'; st.rerun()
elif step == 'cp13':
    st.subheader("💔 Q15: Kya seene ke dard ke saath behoshi (fainting) hui?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="cp13y"):
        s.patient_data['fainting'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Fainting with chest pain (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="cp13n"): s.patient_data['fainting'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 3: STOMACH PAIN (15 Qs) =================
elif step == 'sp1':
    st.subheader("🤢 [Stomach] Q1: Pet dard kab hota hai?"); c1, c2, c3 = st.columns(3)
    if c1.button("Khali pet (Empty)", key="sp1a"): s.patient_data['pain_timing'] = "Empty stomach"; s.step = 'sp2'; st.rerun()
    if c2.button("Khane ke baad", key="sp1b"): s.patient_data['pain_timing'] = "After eating"; s.step = 'sp3'; st.rerun()
    if c3.button("Hamesha (Always)", key="sp1c"): s.patient_data['pain_timing'] = "Always"; s.step = 'sp4'; st.rerun()
elif step == 'sp2':
    st.subheader("🤢 Q2: Kya khana khane se dard kam hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp2y"):
        s.patient_data['relieved_by_food'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Pain relieved by food (pattern doctor should check): +15 risk"); s.step = 'sp5'; st.rerun()
    if c2.button("No / Nahi", key="sp2n"): s.patient_data['relieved_by_food'] = "No"; s.step = 'sp5'; st.rerun()
elif step == 'sp3':
    st.subheader("🤢 Q3: Kya seene mein jalan (heartburn) hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp3y"): s.patient_data['heartburn'] = "Yes"; s.reasons.append("Pain after eating with heartburn: acidity is possible (no risk added)"); s.step = 'sp5'; st.rerun()
    if c2.button("No / Nahi", key="sp3n"): s.patient_data['heartburn'] = "No"; s.reasons.append("Pain after eating without heartburn: gas is possible (no risk added)"); s.step = 'sp5'; st.rerun()
elif step == 'sp4':
    st.subheader("🤢 Q4: Kya kala stool (black stool) ya khoon ki ulti (vomiting blood) hui?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp4y"):
        s.patient_data['black_stool_blood_vomit'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Black stool / vomiting blood (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp4n"): s.patient_data['black_stool_blood_vomit'] = "No"; s.step = 'sp5'; st.rerun()
elif step == 'sp5':
    st.subheader("🤢 Q5: Kya aap painkiller (ibuprofen / aspirin) use karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp5y"):
        s.patient_data['painkiller_use'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Painkiller (ibuprofen/aspirin) use: +10 risk"); s.step = 'sp_hb'; st.rerun()
    if c2.button("No / Nahi", key="sp5n"): s.patient_data['painkiller_use'] = "No"; s.step = 'sp_hb'; st.rerun()
elif step == 'sp_hb':
    st.subheader("📋 Q6 (Report): Hemoglobin (normal 12-17 g/dL)")
    hb = st.number_input("Apni report se hemoglobin likhein", min_value=0.0, max_value=25.0, value=13.0, step=0.1, key="hb_in")
    if st.button("Submit Report", key="hb_btn"):
        s.report_data['hemoglobin'] = hb
        if hb < 8: s.risk = max(s.risk + 40, 70); s.reasons.append("Hemoglobin very low (" + str(hb) + "): risk raised to at least 70"); s.step = 'end'
        elif hb < 12: s.risk = s.risk + 15; s.reasons.append("Hemoglobin low (" + str(hb) + "): +15 risk"); s.step = 'sp_stool'
        else: s.step = 'sp_stool'
        st.rerun()
elif step == 'sp_stool':
    st.subheader("📋 Q7 (Report): Stool test ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Normal", key="spst_n"): s.report_data['stool_test'] = "Normal"; s.step = 'sp6'; st.rerun()
    if c2.button("Blood / Infection", key="spst_a"):
        s.report_data['stool_test'] = "Blood/Infection found"; s.risk = s.risk + 20; s.reasons.append("Stool report shows blood / infection: +20 risk"); s.step = 'sp6'; st.rerun()
    if c3.button("Test nahi hua", key="spst_x"): s.report_data['stool_test'] = "Not done"; s.step = 'sp6'; st.rerun()
elif step == 'sp6':
    st.subheader("🤢 Q8: Kya bohat shadeed dard + pet sakht (rigid) + bukhar hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp6y"):
        s.patient_data['severe_rigid_fever'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Severe pain + rigid abdomen + fever (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp6n"): s.patient_data['severe_rigid_fever'] = "No"; s.step = 'sp7'; st.rerun()
elif step == 'sp7':
    st.subheader("🤢 Q9: Kya bagair wajah wazan kam ho raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp7y"):
        s.patient_data['weight_loss'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Unexplained weight loss: +15 risk"); s.step = 'sp8'; st.rerun()
    if c2.button("No / Nahi", key="sp7n"): s.patient_data['weight_loss'] = "No"; s.step = 'sp8'; st.rerun()
elif step == 'sp8':
    st.subheader("🤢 Q10: Kya baar baar ulti (repeated vomiting) ho rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp8y"):
        s.patient_data['repeated_vomiting'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Repeated vomiting: +10 risk"); s.step = 'sp9'; st.rerun()
    if c2.button("No / Nahi", key="sp8n"): s.patient_data['repeated_vomiting'] = "No"; s.step = 'sp9'; st.rerun()
elif step == 'sp9':
    st.subheader("🤢 Q11: Kya 3 din se zyada dast (diarrhea) hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp9y"):
        s.patient_data['diarrhea_3days'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Diarrhea more than 3 days: +10 risk"); s.step = 'sp10'; st.rerun()
    if c2.button("No / Nahi", key="sp9n"): s.patient_data['diarrhea_3days'] = "No"; s.step = 'sp10'; st.rerun()
elif step == 'sp10':
    st.subheader("🤢 Q12: Kya aankhein ya skin peeli (yellow) ho rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp10y"):
        s.patient_data['yellow_eyes_skin'] = "Yes"; s.risk = s.risk + 20; s.reasons.append("Yellow eyes / skin: +20 risk"); s.step = 'sp11'; st.rerun()
    if c2.button("No / Nahi", key="sp10n"): s.patient_data['yellow_eyes_skin'] = "No"; s.step = 'sp11'; st.rerun()
elif step == 'sp11':
    st.subheader("🤢 Q13: Kya aap zyada chai ya masaledar khana khate hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp11y"):
        s.patient_data['tea_spicy'] = "Yes"; s.reasons.append("Tea / spicy food habit: acidity is possible (no risk added)"); s.step = 'sp12'; st.rerun()
    if c2.button("No / Nahi", key="sp11n"): s.patient_data['tea_spicy'] = "No"; s.step = 'sp12'; st.rerun()
elif step == 'sp12':
    st.subheader("🤢 Q14: Kya thora sa khane ke baad hi pet bhara bhara lagta hai (bloating / early fullness)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp12y"):
        s.patient_data['early_fullness'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Bloating / early fullness: +10 risk"); s.step = 'sp13'; st.rerun()
    if c2.button("No / Nahi", key="sp12n"): s.patient_data['early_fullness'] = "No"; s.step = 'sp13'; st.rerun()
elif step == 'sp13':
    st.subheader("🤢 Q15: Kya family mein kisi ko pet / aant / jigar ki serious bimari rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sp13y"):
        s.patient_data['family_gi_disease'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Family history of stomach / bowel / liver disease: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sp13n"): s.patient_data['family_gi_disease'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 4: HEADACHE (15 Qs) =================
elif step == 'hd1':
    st.subheader("🤕 [Headache] Q1: Kya achanak sab se shadeed sar dard (thunderclap) hua?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd1y"):
        s.patient_data['thunderclap'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Sudden worst headache (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd1n"): s.patient_data['thunderclap'] = "No"; s.step = 'hd2'; st.rerun()
elif step == 'hd2':
    st.subheader("🤕 Q2: Kya bukhar + gardan akdi hui (stiff neck) + rash hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd2y"):
        s.patient_data['fever_neck_rash'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Fever + stiff neck + rash (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd2n"): s.patient_data['fever_neck_rash'] = "No"; s.step = 'hd3'; st.rerun()
elif step == 'hd3':
    st.subheader("🤕 Q3: Kya sar ke ek taraf dhadakta hua (throbbing) dard hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd3y"):
        s.patient_data['one_sided_throbbing'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("One-sided throbbing headache: +5 risk"); s.step = 'hd4'; st.rerun()
    if c2.button("No / Nahi", key="hd3n"): s.patient_data['one_sided_throbbing'] = "No"; s.step = 'hd6'; st.rerun()
elif step == 'hd4':
    st.subheader("🤕 Q4: Kya roshni ya awaaz se takleef (light/sound sensitivity) hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd4y"): s.patient_data['light_sound_sensitive'] = "Yes"; s.reasons.append("Throbbing + light/sound sensitivity: migraine-type pattern is possible (no risk added)"); s.step = 'hd5'; st.rerun()
    if c2.button("No / Nahi", key="hd4n"): s.patient_data['light_sound_sensitive'] = "No"; s.reasons.append("No light/sound sensitivity: tension-type pattern is possible (no risk added)"); s.step = 'hd6'; st.rerun()
elif step == 'hd5':
    st.subheader("🤕 Q5: Kya nazar ka masla, kamzori ya bolne mein dikkat hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd5y"):
        s.patient_data['vision_weakness_speech'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Vision / weakness / speech problem (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd5n"): s.patient_data['vision_weakness_speech'] = "No"; s.step = 'hd7'; st.rerun()
elif step == 'hd6':
    st.subheader("🤕 Q6: Kya dono taraf sar tight hai aur stress / tension hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd6y"): s.patient_data['both_sides_stress'] = "Yes"; s.reasons.append("Both-sided tight headache with stress: tension-type pattern is possible (no risk added)"); s.step = 'hd7'; st.rerun()
    if c2.button("No / Nahi", key="hd6n"): s.patient_data['both_sides_stress'] = "No"; s.step = 'hd7'; st.rerun()
elif step == 'hd7':
    st.subheader("🤕 Q7: Kya subah uthte waqt sar dard zyada hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd7y"):
        s.patient_data['worse_on_waking'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Headache worse on waking: +10 risk"); s.step = 'hd_sleep'; st.rerun()
    if c2.button("No / Nahi", key="hd7n"): s.patient_data['worse_on_waking'] = "No"; s.step = 'hd_sleep'; st.rerun()
elif step == 'hd_sleep':
    st.subheader("📋 Q8 (Input): Aap roz kitne ghante sote hain? (normal 7-9)")
    sl = st.number_input("Sleep hours likhein", min_value=0.0, max_value=24.0, value=7.0, step=0.5, key="sl_in")
    if st.button("Submit", key="sl_btn"):
        s.report_data['sleep_hours'] = sl
        if sl < 5: s.risk = s.risk + 15; s.reasons.append("Sleep less than 5 hours (" + str(sl) + "): +15 risk"); s.step = 'hd8'
        else: s.step = 'hd8'
        st.rerun()
elif step == 'hd8':
    st.subheader("🤕 Q9: Kya aap roz 8 ghante se zyada screen (mobile/computer) dekhte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd8y"):
        s.patient_data['screen_over_8h'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Screen time over 8 hours daily: +10 risk"); s.step = 'hd_bp'; st.rerun()
    if c2.button("No / Nahi", key="hd8n"): s.patient_data['screen_over_8h'] = "No"; s.step = 'hd_bp'; st.rerun()
elif step == 'hd_bp':
    st.subheader("📋 Q10 (Report): Systolic BP (normal 90-139 mmHg)")
    hbp = st.number_input("Apna systolic BP likhein", min_value=40, max_value=300, value=120, step=1, key="hdbp_in")
    if st.button("Submit Report", key="hdbp_btn"):
        s.report_data['head_systolic_bp'] = hbp
        if hbp >= 180: s.risk = max(s.risk + 40, 70); s.reasons.append("BP very high (" + str(hbp) + "): risk raised to at least 70"); s.step = 'end'
        elif hbp >= 140: s.risk = s.risk + 15; s.reasons.append("BP high (" + str(hbp) + "): +15 risk"); s.step = 'hd9'
        else: s.step = 'hd9'
        st.rerun()
elif step == 'hd9':
    st.subheader("🤕 Q11: Kya haal hi mein sar par chot (head injury) lagi?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd9y"):
        s.patient_data['head_injury'] = "Yes"; s.risk = s.risk + 30; s.reasons.append("Recent head injury: +30 risk"); s.step = 'hd10'; st.rerun()
    if c2.button("No / Nahi", key="hd9n"): s.patient_data['head_injury'] = "No"; s.step = 'hd10'; st.rerun()
elif step == 'hd10':
    st.subheader("🤕 Q12: Kya sar dard ke saath ulti jaisa mann (nausea) hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd10y"):
        s.patient_data['nausea'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Nausea with headache: +5 risk"); s.step = 'hd11'; st.rerun()
    if c2.button("No / Nahi", key="hd10n"): s.patient_data['nausea'] = "No"; s.step = 'hd11'; st.rerun()
elif step == 'hd11':
    st.subheader("🤕 Q13: Kya haal hi mein chai/coffee (caffeine) ki aadat change hui?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd11y"): s.patient_data['caffeine_change'] = "Yes"; s.reasons.append("Recent caffeine change: withdrawal headache is possible (no risk added)"); s.step = 'hd12'; st.rerun()
    if c2.button("No / Nahi", key="hd11n"): s.patient_data['caffeine_change'] = "No"; s.step = 'hd12'; st.rerun()
elif step == 'hd12':
    st.subheader("🤕 Q14: Kya aapki nazar kamzor hai ya chashma (glasses) ka number badla hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd12y"): s.patient_data['eyesight_problem'] = "Yes"; s.reasons.append("Eyesight problem: eye strain is possible (no risk added)"); s.step = 'hd13'; st.rerun()
    if c2.button("No / Nahi", key="hd12n"): s.patient_data['eyesight_problem'] = "No"; s.step = 'hd13'; st.rerun()
elif step == 'hd13':
    st.subheader("🤕 Q15: Kya aap hafte mein 3 ya zyada din sar dard ke liye painkiller lete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="hd13y"):
        s.patient_data['frequent_painkiller'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Frequent painkiller use for headache: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="hd13n"): s.patient_data['frequent_painkiller'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 5: JOINT PAIN (15 Qs) =================
elif step == 'jp1':
    st.subheader("🦴 [Joint Pain] Q1: Kya jodon (joints) mein dard 6 hafte se zyada se hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp1y"):
        s.patient_data['pain_6wk'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Joint pain more than 6 weeks: +10 risk"); s.step = 'jp2'; st.rerun()
    if c2.button("No / Nahi", key="jp1n"): s.patient_data['pain_6wk'] = "No"; s.step = 'jp2'; st.rerun()
elif step == 'jp2':
    st.subheader("🦴 Q2: Kya subah jodon mein akdan (morning stiffness) 30 minute se zyada rehti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp2y"):
        s.patient_data['morning_stiffness'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Morning stiffness over 30 minutes: +15 risk"); s.step = 'jp3'; st.rerun()
    if c2.button("No / Nahi", key="jp2n"): s.patient_data['morning_stiffness'] = "No"; s.step = 'jp3'; st.rerun()
elif step == 'jp3':
    st.subheader("🦴 Q3: Kya ek joint achanak laal, garam aur soojha hua hai (khaas kar angoothe ka)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp3y"):
        s.patient_data['sudden_red_swollen_joint'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Sudden red, swollen, warm joint: +15 risk"); s.step = 'jp4'; st.rerun()
    if c2.button("No / Nahi", key="jp3n"): s.patient_data['sudden_red_swollen_joint'] = "No"; s.step = 'jp4'; st.rerun()
elif step == 'jp4':
    st.subheader("🤒 Q4: Kya joint garam aur soojha hua hai AUR saath mein bukhar bhi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp4y"):
        s.patient_data['hot_joint_with_fever'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Hot swollen joint with fever (red flag, possible joint infection): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="jp4n"): s.patient_data['hot_joint_with_fever'] = "No"; s.step = 'jp5'; st.rerun()
elif step == 'jp5':
    st.subheader("🦴 Q5: Kya dard dono taraf ke jodon (jaise dono haath / dono ghutne) mein hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp5y"):
        s.patient_data['both_sides'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Pain in joints on both sides: +10 risk"); s.step = 'jp_ua'; st.rerun()
    if c2.button("No / Nahi", key="jp5n"): s.patient_data['both_sides'] = "No"; s.step = 'jp_ua'; st.rerun()
elif step == 'jp_ua':
    st.subheader("📋 Q6 (Report): Uric Acid (normal 3.5-7.2 mg/dL)")
    ua = st.number_input("Apni report se uric acid likhein", min_value=0.0, max_value=20.0, value=5.0, step=0.1, key="ua_in")
    if st.button("Submit Report", key="ua_btn"):
        s.report_data['uric_acid'] = ua
        if ua > 9: s.risk = s.risk + 20; s.reasons.append("Uric acid very high (" + str(ua) + "): +20 risk"); s.step = 'jp6'
        elif ua > 7.2: s.risk = s.risk + 10; s.reasons.append("Uric acid high (" + str(ua) + "): +10 risk"); s.step = 'jp6'
        else: s.step = 'jp6'
        st.rerun()
elif step == 'jp6':
    st.subheader("🦴 Q7: Kya aap zyada gosht, seafood ya sharab (alcohol) lete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp6y"):
        s.patient_data['purine_diet_alcohol'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("High meat / seafood / alcohol diet: +5 risk"); s.step = 'jp7'; st.rerun()
    if c2.button("No / Nahi", key="jp6n"): s.patient_data['purine_diet_alcohol'] = "No"; s.step = 'jp7'; st.rerun()
elif step == 'jp7':
    st.subheader("🦴 Q8: Kya dard kisi chot ya girne ke baad shuru hua?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp7y"):
        s.patient_data['injury_before'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Joint pain after injury / fall: +10 risk"); s.step = 'jp8'; st.rerun()
    if c2.button("No / Nahi", key="jp7n"): s.patient_data['injury_before'] = "No"; s.step = 'jp8'; st.rerun()
elif step == 'jp8':
    st.subheader("🦴 Q9: Kya joint hilane mein bohat mushkil hai ya joint ka shape tedha ho raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp8y"):
        s.patient_data['deformity_locking'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Joint locking / deformity: +15 risk"); s.step = 'jp_xr'; st.rerun()
    if c2.button("No / Nahi", key="jp8n"): s.patient_data['deformity_locking'] = "No"; s.step = 'jp_xr'; st.rerun()
elif step == 'jp_xr':
    st.subheader("📋 Q10 (Report): Joint X-Ray ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Normal", key="jpxr_n"): s.report_data['joint_xray'] = "Normal"; s.step = 'jp9'; st.rerun()
    if c2.button("Abnormal", key="jpxr_a"):
        s.report_data['joint_xray'] = "Abnormal"; s.risk = s.risk + 20; s.reasons.append("Abnormal joint X-Ray report: +20 risk"); s.step = 'jp9'; st.rerun()
    if c3.button("X-Ray nahi hua", key="jpxr_x"):
        s.report_data['joint_xray'] = "Not done"; s.reasons.append("X-Ray not done yet: imaging is advised by a doctor (no risk added)"); s.step = 'jp9'; st.rerun()
elif step == 'jp9':
    st.subheader("🦴 Q11: Kya raat ko dard neend se jaga deta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp9y"):
        s.patient_data['night_pain'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Night pain waking from sleep: +10 risk"); s.step = 'jp10'; st.rerun()
    if c2.button("No / Nahi", key="jp9n"): s.patient_data['night_pain'] = "No"; s.step = 'jp10'; st.rerun()
elif step == 'jp10':
    st.subheader("🦴 Q12: Kya aankhon mein lalpan, skin rash ya psoriasis bhi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp10y"):
        s.patient_data['eye_skin_signs'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Eye redness / skin rash with joint pain: +10 risk"); s.step = 'jp11'; st.rerun()
    if c2.button("No / Nahi", key="jp10n"): s.patient_data['eye_skin_signs'] = "No"; s.step = 'jp11'; st.rerun()
elif step == 'jp11':
    st.subheader("🦴 Q13: Kya family mein kisi ko arthritis ya gout hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp11y"):
        s.patient_data['family_arthritis'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Family history of arthritis / gout: +10 risk"); s.step = 'jp12'; st.rerun()
    if c2.button("No / Nahi", key="jp11n"): s.patient_data['family_arthritis'] = "No"; s.step = 'jp12'; st.rerun()
elif step == 'jp12':
    st.subheader("🦴 Q14: Kya aapka wazan zyada (overweight) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp12y"):
        s.patient_data['overweight'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Overweight (extra load on joints): +5 risk"); s.step = 'jp13'; st.rerun()
    if c2.button("No / Nahi", key="jp12n"): s.patient_data['overweight'] = "No"; s.step = 'jp13'; st.rerun()
elif step == 'jp13':
    st.subheader("🦴 Q15: Kya haath ya paon mein sunn hona (numbness) ya kamzori hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="jp13y"):
        s.patient_data['numbness_weakness'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Numbness / weakness in hands or feet: +15 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="jp13n"): s.patient_data['numbness_weakness'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 6: SKIN PROBLEM (15 Qs) =================
elif step == 'sk1':
    st.subheader("🧴 [Skin] Q1: Kya skin par kharish (itching) ho rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk1y"):
        s.patient_data['itching'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Skin itching: +5 risk"); s.step = 'sk2'; st.rerun()
    if c2.button("No / Nahi", key="sk1n"): s.patient_data['itching'] = "No"; s.step = 'sk2'; st.rerun()
elif step == 'sk2':
    st.subheader("🧴 Q2: Kya rash ya daane 2 hafte se zyada se hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk2y"):
        s.patient_data['rash_2wk'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Rash lasting more than 2 weeks: +10 risk"); s.step = 'sk3'; st.rerun()
    if c2.button("No / Nahi", key="sk2n"): s.patient_data['rash_2wk'] = "No"; s.step = 'sk3'; st.rerun()
elif step == 'sk3':
    st.subheader("🚨 Q3: Kya hothon / chehre / zubaan mein sujan hai AUR saans lene mein dikkat hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk3y"):
        s.patient_data['face_swelling_breathing'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Face / lip swelling with breathing difficulty (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sk3n"): s.patient_data['face_swelling_breathing'] = "No"; s.step = 'sk4'; st.rerun()
elif step == 'sk4':
    st.subheader("🚨 Q4: Kya skin par chhaale (blisters), skin chhilna ya muh mein zakhm bukhar ke saath hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk4y"):
        s.patient_data['blisters_peeling_fever'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Blisters / peeling skin / mouth sores with fever (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sk4n"): s.patient_data['blisters_peeling_fever'] = "No"; s.step = 'sk5'; st.rerun()
elif step == 'sk5':
    st.subheader("🧴 Q5: Kya rash mein pus (peep) ya dard hai, ya bukhar hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk5y"):
        s.patient_data['pus_infection'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Pus / painful rash (possible skin infection): +15 risk"); s.step = 'sk6'; st.rerun()
    if c2.button("No / Nahi", key="sk5n"): s.patient_data['pus_infection'] = "No"; s.step = 'sk6'; st.rerun()
elif step == 'sk6':
    st.subheader("🧴 Q6: Kya rash kisi nayi dawai, cream, sabun ya khane ke baad shuru hua?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk6y"):
        s.patient_data['new_trigger'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Rash started after new medicine / product / food: +5 risk"); s.step = 'sk_al'; st.rerun()
    if c2.button("No / Nahi", key="sk6n"): s.patient_data['new_trigger'] = "No"; s.step = 'sk_al'; st.rerun()
elif step == 'sk_al':
    st.subheader("📋 Q7 (Report): Allergy Test ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Negative", key="skal_n"): s.report_data['allergy_test'] = "Negative"; s.step = 'sk7'; st.rerun()
    if c2.button("Positive", key="skal_p"):
        s.report_data['allergy_test'] = "Positive"; s.risk = s.risk + 10; s.reasons.append("Allergy test positive: +10 risk"); s.step = 'sk7'; st.rerun()
    if c3.button("Test nahi hua", key="skal_x"):
        s.report_data['allergy_test'] = "Not done"; s.reasons.append("Allergy test not done: doctor may advise it (no risk added)"); s.step = 'sk7'; st.rerun()
elif step == 'sk7':
    st.subheader("🧴 Q8: Kya rash gol ring jaisa hai aur phail raha hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk7y"):
        s.patient_data['ring_shaped'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Ring-shaped spreading rash: fungal-type pattern is possible, +5 risk"); s.step = 'sk8'; st.rerun()
    if c2.button("No / Nahi", key="sk7n"): s.patient_data['ring_shaped'] = "No"; s.step = 'sk8'; st.rerun()
elif step == 'sk8':
    st.subheader("🧴 Q9: Kya kisi til (mole) ka size / rang badla hai ya koi zakhm bhar nahi raha?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk8y"):
        s.patient_data['mole_change_nonhealing'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Changing mole / non-healing sore: +25 risk, doctor checkup zaroori"); s.step = 'sk9'; st.rerun()
    if c2.button("No / Nahi", key="sk8n"): s.patient_data['mole_change_nonhealing'] = "No"; s.step = 'sk9'; st.rerun()
elif step == 'sk9':
    st.subheader("🧴 Q10: Kya aapki skin aksar sukhi / phati rehti hai ya eczema ki history hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk9y"): s.patient_data['dry_skin_eczema'] = "Yes"; s.reasons.append("Dry skin / eczema history: dryness-related rash is possible (no risk added)"); s.step = 'sk10'; st.rerun()
    if c2.button("No / Nahi", key="sk9n"): s.patient_data['dry_skin_eczema'] = "No"; s.step = 'sk10'; st.rerun()
elif step == 'sk10':
    st.subheader("🧴 Q11: Kya rash dhoop (sunlight) mein zyada barhta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk10y"):
        s.patient_data['sun_worsens'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Rash worsens in sunlight: +10 risk"); s.step = 'sk11'; st.rerun()
    if c2.button("No / Nahi", key="sk10n"): s.patient_data['sun_worsens'] = "No"; s.step = 'sk11'; st.rerun()
elif step == 'sk11':
    st.subheader("🧴 Q12: Kya rash ke saath jodon mein dard bhi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk11y"):
        s.patient_data['rash_with_joint_pain'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Rash with joint pain: +10 risk"); s.step = 'sk12'; st.rerun()
    if c2.button("No / Nahi", key="sk11n"): s.patient_data['rash_with_joint_pain'] = "No"; s.step = 'sk12'; st.rerun()
elif step == 'sk12':
    st.subheader("🧴 Q13: Kya ghar ya doston mein kisi aur ko bhi aisi hi khujli / rash hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk12y"):
        s.patient_data['contagious_contact'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Others around have similar rash (contagious cause possible): +5 risk"); s.step = 'sk13'; st.rerun()
    if c2.button("No / Nahi", key="sk12n"): s.patient_data['contagious_contact'] = "No"; s.step = 'sk13'; st.rerun()
elif step == 'sk13':
    st.subheader("🧴 Q14: Kya aap aajkal bohat stress mein hain ya neend poori nahi ho rahi?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk13y"):
        s.patient_data['stress_poor_sleep'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Stress / poor sleep: +5 risk"); s.step = 'sk14'; st.rerun()
    if c2.button("No / Nahi", key="sk13n"): s.patient_data['stress_poor_sleep'] = "No"; s.step = 'sk14'; st.rerun()
elif step == 'sk14':
    st.subheader("🧴 Q15: Kya aap bina doctor ki salah ke steroid cream lagate hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="sk14y"):
        s.patient_data['self_steroid_cream'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Using steroid cream without doctor advice: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="sk14n"): s.patient_data['self_steroid_cream'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 7: URINARY PROBLEM (15 Qs) =================
elif step == 'ur1':
    st.subheader("🚻 [Urinary] Q1: Kya peshab karte waqt jalan (burning) hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur1y"):
        s.patient_data['burning_urine'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Burning while urinating: +10 risk"); s.step = 'ur2'; st.rerun()
    if c2.button("No / Nahi", key="ur1n"): s.patient_data['burning_urine'] = "No"; s.step = 'ur2'; st.rerun()
elif step == 'ur2':
    st.subheader("🚻 Q2: Kya baar baar peshab aata hai ya jaldi jaane ki zaroorat hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur2y"):
        s.patient_data['frequency_urgency'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Frequent / urgent urination: +5 risk"); s.step = 'ur3'; st.rerun()
    if c2.button("No / Nahi", key="ur2n"): s.patient_data['frequency_urgency'] = "No"; s.step = 'ur3'; st.rerun()
elif step == 'ur3':
    st.subheader("🚻 Q3: Kya peshab mein khoon (blood in urine) aata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur3y"):
        s.patient_data['blood_urine'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Blood in urine: +25 risk"); s.step = 'ur4'; st.rerun()
    if c2.button("No / Nahi", key="ur3n"): s.patient_data['blood_urine'] = "No"; s.step = 'ur4'; st.rerun()
elif step == 'ur4':
    st.subheader("🚨 Q4: Kya peshab bilkul nahi aa raha ya bohat hi kam aa raha hai (poora din)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur4y"):
        s.patient_data['no_urine'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Very little / no urine output (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="ur4n"): s.patient_data['no_urine'] = "No"; s.step = 'ur5'; st.rerun()
elif step == 'ur5':
    st.subheader("🚨 Q5: Kya bukhar + kamar ke side mein shadeed dard + ulti ek saath hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur5y"):
        s.patient_data['fever_flank_vomit'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Fever + flank pain + vomiting (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="ur5n"): s.patient_data['fever_flank_vomit'] = "No"; s.step = 'ur6'; st.rerun()
elif step == 'ur6':
    st.subheader("🚻 Q6: Kya pet ke neeche (pelvic area) dard ya bhaari-pan hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur6y"):
        s.patient_data['lower_abdomen_pain'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Lower abdomen pain: +10 risk"); s.step = 'ur_cr'; st.rerun()
    if c2.button("No / Nahi", key="ur6n"): s.patient_data['lower_abdomen_pain'] = "No"; s.step = 'ur_cr'; st.rerun()
elif step == 'ur_cr':
    st.subheader("📋 Q7 (Report): Creatinine (normal 0.6-1.3 mg/dL)")
    cr = st.number_input("Apni report se creatinine likhein", min_value=0.0, max_value=20.0, value=1.0, step=0.1, key="cr_in")
    if st.button("Submit Report", key="cr_btn"):
        s.report_data['creatinine'] = cr
        if cr >= 4: s.risk = max(s.risk + 40, 70); s.reasons.append("Creatinine very high (" + str(cr) + "): risk raised to at least 70"); s.step = 'end'
        elif cr > 1.3: s.risk = s.risk + 20; s.reasons.append("Creatinine high (" + str(cr) + "): +20 risk"); s.step = 'ur_cul'
        else: s.step = 'ur_cul'
        st.rerun()
elif step == 'ur_cul':
    st.subheader("📋 Q8 (Report): Urine Culture ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Negative", key="urcul_n"): s.report_data['urine_culture'] = "Negative"; s.step = 'ur7'; st.rerun()
    if c2.button("Positive (Infection)", key="urcul_p"):
        s.report_data['urine_culture'] = "Positive"; s.risk = s.risk + 20; s.reasons.append("Urine culture shows infection: +20 risk"); s.step = 'ur7'; st.rerun()
    if c3.button("Test nahi hua", key="urcul_x"):
        s.report_data['urine_culture'] = "Not done"; s.reasons.append("Urine culture not done: doctor may advise it (no risk added)"); s.step = 'ur7'; st.rerun()
elif step == 'ur7':
    st.subheader("🚻 Q9: Kya aap roz 1.5 litre se kam pani peete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur7y"):
        s.patient_data['low_water'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Low water intake: +5 risk"); s.step = 'ur8'; st.rerun()
    if c2.button("No / Nahi", key="ur7n"): s.patient_data['low_water'] = "No"; s.step = 'ur8'; st.rerun()
elif step == 'ur8':
    st.subheader("🚻 Q10: Kya pehle kabhi pathri (kidney stone) ki history rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur8y"):
        s.patient_data['stone_history'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Kidney stone history: +10 risk"); s.step = 'ur9'; st.rerun()
    if c2.button("No / Nahi", key="ur8n"): s.patient_data['stone_history'] = "No"; s.step = 'ur9'; st.rerun()
elif step == 'ur9':
    st.subheader("🚻 Q11: Kya aapko diabetes (sugar) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur9y"):
        s.patient_data['diabetes'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Diabetes: +10 risk"); s.step = 'ur10'; st.rerun()
    if c2.button("No / Nahi", key="ur9n"): s.patient_data['diabetes'] = "No"; s.step = 'ur10'; st.rerun()
elif step == 'ur10':
    st.subheader("🚻 Q12: Kya peshab ka rang bohat gehra hai ya jhaag (foam) aata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur10y"):
        s.patient_data['dark_foamy_urine'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Dark or foamy urine: +10 risk"); s.step = 'ur11'; st.rerun()
    if c2.button("No / Nahi", key="ur10n"): s.patient_data['dark_foamy_urine'] = "No"; s.step = 'ur11'; st.rerun()
elif step == 'ur11':
    st.subheader("🚻 Q13: Kya raat ko baar baar peshab ke liye uthna padta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur11y"):
        s.patient_data['nocturia'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Frequent night-time urination: +5 risk"); s.step = 'ur12'; st.rerun()
    if c2.button("No / Nahi", key="ur11n"): s.patient_data['nocturia'] = "No"; s.step = 'ur12'; st.rerun()
elif step == 'ur12':
    st.subheader("🚻 Q14: Kya chehre ya pairon par sujan (swelling) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur12y"):
        s.patient_data['face_leg_swelling'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Face / leg swelling: +10 risk"); s.step = 'ur13'; st.rerun()
    if c2.button("No / Nahi", key="ur12n"): s.patient_data['face_leg_swelling'] = "No"; s.step = 'ur13'; st.rerun()
elif step == 'ur13':
    st.subheader("🚻 Q15: Kya family mein kisi ko kidney ki bimari hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="ur13y"):
        s.patient_data['family_kidney'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Family history of kidney disease: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="ur13n"): s.patient_data['family_kidney'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 8: THROAT PROBLEM (15 Qs) =================
elif step == 'th1':
    st.subheader("🗣️ [Throat] Q1: Kya gale mein dard (sore throat) 1 hafte se zyada se hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th1y"):
        s.patient_data['sore_throat_1wk'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Sore throat more than 1 week: +10 risk"); s.step = 'th2'; st.rerun()
    if c2.button("No / Nahi", key="th1n"): s.patient_data['sore_throat_1wk'] = "No"; s.step = 'th2'; st.rerun()
elif step == 'th2':
    st.subheader("🗣️ Q2: Kya kuch nigalne (swallowing) mein dard hota hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th2y"):
        s.patient_data['painful_swallowing'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Painful swallowing: +10 risk"); s.step = 'th3'; st.rerun()
    if c2.button("No / Nahi", key="th2n"): s.patient_data['painful_swallowing'] = "No"; s.step = 'th3'; st.rerun()
elif step == 'th3':
    st.subheader("🚨 Q3: Kya saans lene mein shadeed dikkat hai ya thook bhi nigal nahi pa rahe (munh se paani girna)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th3y"):
        s.patient_data['breathing_swallow_block'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Severe breathing trouble / cannot swallow saliva (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="th3n"): s.patient_data['breathing_swallow_block'] = "No"; s.step = 'th4'; st.rerun()
elif step == 'th4':
    st.subheader("🗣️ Q4: Kya bukhar 101°F se zyada hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th4y"):
        s.patient_data['fever_101'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Fever above 101F: +10 risk"); s.step = 'th5'; st.rerun()
    if c2.button("No / Nahi", key="th4n"): s.patient_data['fever_101'] = "No"; s.step = 'th5'; st.rerun()
elif step == 'th5':
    st.subheader("🗣️ Q5: Kya tonsils par safed daag ya pus (peep) nazar aati hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th5y"):
        s.patient_data['tonsil_pus'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("White spots / pus on tonsils (possible infection): +15 risk"); s.step = 'th6'; st.rerun()
    if c2.button("No / Nahi", key="th5n"): s.patient_data['tonsil_pus'] = "No"; s.step = 'th6'; st.rerun()
elif step == 'th6':
    st.subheader("🗣️ Q6: Kya gardan mein gilti (swollen glands) mehsoos hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th6y"):
        s.patient_data['neck_glands'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Swollen neck glands: +10 risk"); s.step = 'th_wbc'; st.rerun()
    if c2.button("No / Nahi", key="th6n"): s.patient_data['neck_glands'] = "No"; s.step = 'th_wbc'; st.rerun()
elif step == 'th_wbc':
    st.subheader("📋 Q7 (Report): WBC count (normal 4000-11000 /uL)")
    wbc = st.number_input("Apni report se WBC count likhein", min_value=0, max_value=100000, value=7000, step=100, key="wbc_in")
    if st.button("Submit Report", key="wbc_btn"):
        s.report_data['wbc'] = wbc
        if wbc >= 20000: s.risk = s.risk + 25; s.reasons.append("WBC very high (" + str(wbc) + "): +25 risk"); s.step = 'th7'
        elif wbc > 11000: s.risk = s.risk + 15; s.reasons.append("WBC high (" + str(wbc) + "): +15 risk"); s.step = 'th7'
        elif wbc < 4000: s.risk = s.risk + 15; s.reasons.append("WBC low (" + str(wbc) + "): +15 risk"); s.step = 'th7'
        else: s.step = 'th7'
        st.rerun()
elif step == 'th7':
    st.subheader("🗣️ Q8: Kya khansi bhi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th7y"): s.patient_data['cough'] = "Yes"; s.reasons.append("Cough present: viral-type pattern is possible (no risk added)"); s.step = 'th8'; st.rerun()
    if c2.button("No / Nahi", key="th7n"): s.patient_data['cough'] = "No"; s.step = 'th8'; st.rerun()
elif step == 'th8':
    st.subheader("🗣️ Q9: Kya naak behna ya chheenkein (runny nose / sneezing) hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th8y"): s.patient_data['runny_nose'] = "Yes"; s.reasons.append("Runny nose / sneezing: cold or allergy pattern is possible (no risk added)"); s.step = 'th9'; st.rerun()
    if c2.button("No / Nahi", key="th8n"): s.patient_data['runny_nose'] = "No"; s.step = 'th9'; st.rerun()
elif step == 'th9':
    st.subheader("🗣️ Q10: Kya awaaz bhari ya baith gayi hai (2 hafte se zyada)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th9y"):
        s.patient_data['hoarseness_2wk'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Hoarse voice more than 2 weeks: +15 risk"); s.step = 'th10'; st.rerun()
    if c2.button("No / Nahi", key="th9n"): s.patient_data['hoarseness_2wk'] = "No"; s.step = 'th10'; st.rerun()
elif step == 'th10':
    st.subheader("🗣️ Q11: Kya gale / gardan mein koi ganth (lump) hai jo barh rahi hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th10y"):
        s.patient_data['growing_lump'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Growing lump in throat / neck: +25 risk, doctor checkup zaroori"); s.step = 'th11'; st.rerun()
    if c2.button("No / Nahi", key="th10n"): s.patient_data['growing_lump'] = "No"; s.step = 'th11'; st.rerun()
elif step == 'th11':
    st.subheader("🗣️ Q12: Kya aap smoking, tambaku ya paan / gutka istemal karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th11y"):
        s.patient_data['tobacco_use'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Smoking / tobacco use: +10 risk"); s.step = 'th12'; st.rerun()
    if c2.button("No / Nahi", key="th11n"): s.patient_data['tobacco_use'] = "No"; s.step = 'th12'; st.rerun()
elif step == 'th12':
    st.subheader("🗣️ Q13: Kya thos khana nigalte waqt gale mein atakta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th12y"):
        s.patient_data['food_sticking'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Food sticking while swallowing: +15 risk"); s.step = 'th13'; st.rerun()
    if c2.button("No / Nahi", key="th12n"): s.patient_data['food_sticking'] = "No"; s.step = 'th13'; st.rerun()
elif step == 'th13':
    st.subheader("🗣️ Q14: Kya seene mein jalan ya khatti dakarein (acid reflux) aati hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th13y"): s.patient_data['acid_reflux'] = "Yes"; s.reasons.append("Acid reflux: throat irritation from acidity is possible (no risk added)"); s.step = 'th14'; st.rerun()
    if c2.button("No / Nahi", key="th13n"): s.patient_data['acid_reflux'] = "No"; s.step = 'th14'; st.rerun()
elif step == 'th14':
    st.subheader("🗣️ Q15: Kya aap dhool, dhuan ya pollution mein zyada rehte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="th14y"): s.patient_data['dust_exposure'] = "Yes"; s.reasons.append("Dust / smoke exposure: irritation is possible (no risk added)"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="th14n"): s.patient_data['dust_exposure'] = "No"; s.step = 'end'; st.rerun()

# ================= PATH 9: BACK PAIN (15 Qs) =================
elif step == 'bp1':
    st.subheader("🧍 [Back Pain] Q1: Kya kamar dard 6 hafte se zyada se hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp1y"):
        s.patient_data['back_pain_6wk'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Back pain more than 6 weeks: +10 risk"); s.step = 'bp2'; st.rerun()
    if c2.button("No / Nahi", key="bp1n"): s.patient_data['back_pain_6wk'] = "No"; s.step = 'bp2'; st.rerun()
elif step == 'bp2':
    st.subheader("🧍 Q2: Kya dard kamar se taang mein neeche pair tak jata hai (sciatica jaisa)?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp2y"):
        s.patient_data['pain_down_leg'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Pain radiating down the leg: +10 risk"); s.step = 'bp3'; st.rerun()
    if c2.button("No / Nahi", key="bp2n"): s.patient_data['pain_down_leg'] = "No"; s.step = 'bp3'; st.rerun()
elif step == 'bp3':
    st.subheader("🚨 Q3: Kya peshab / potty par control nahi raha ya dono taangon mein achanak kamzori aayi?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp3y"):
        s.patient_data['bladder_bowel_leg_weakness'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Loss of bladder / bowel control or sudden leg weakness (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="bp3n"): s.patient_data['bladder_bowel_leg_weakness'] = "No"; s.step = 'bp4'; st.rerun()
elif step == 'bp4':
    st.subheader("🧍 Q4: Kya kamar dard ke saath bukhar ya bagair wajah wazan kam hona hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp4y"):
        s.patient_data['fever_weight_loss'] = "Yes"; s.risk = s.risk + 25; s.reasons.append("Back pain with fever / weight loss: +25 risk"); s.step = 'bp5'; st.rerun()
    if c2.button("No / Nahi", key="bp4n"): s.patient_data['fever_weight_loss'] = "No"; s.step = 'bp5'; st.rerun()
elif step == 'bp5':
    st.subheader("🚨 Q5: Kya dard kisi bade accident ya unchaayi se girne ke baad shuru hua aur bohat shadeed hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp5y"):
        s.patient_data['major_trauma'] = "Yes"; s.risk = max(s.risk + 40, 70); s.reasons.append("Severe back pain after major accident / fall (red flag): risk raised to at least 70"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="bp5n"): s.patient_data['major_trauma'] = "No"; s.step = 'bp_xr'; st.rerun()
elif step == 'bp_xr':
    st.subheader("📋 Q6 (Report): Spine X-Ray ka result kya aaya?"); c1, c2, c3 = st.columns(3)
    if c1.button("Normal", key="bpxr_n"): s.report_data['spine_xray'] = "Normal"; s.step = 'bp_vd'; st.rerun()
    if c2.button("Abnormal", key="bpxr_a"):
        s.report_data['spine_xray'] = "Abnormal"; s.risk = s.risk + 20; s.reasons.append("Abnormal spine X-Ray report: +20 risk"); s.step = 'bp_vd'; st.rerun()
    if c3.button("X-Ray nahi hua", key="bpxr_x"):
        s.report_data['spine_xray'] = "Not done"; s.reasons.append("Spine X-Ray not done yet: imaging is advised by a doctor (no risk added)"); s.step = 'bp_vd'; st.rerun()
elif step == 'bp_vd':
    st.subheader("📋 Q7 (Report): Vitamin D level (normal 30-100 ng/mL)")
    vd = st.number_input("Apni report se Vitamin D likhein", min_value=0.0, max_value=150.0, value=40.0, step=1.0, key="vd_in")
    if st.button("Submit Report", key="vd_btn"):
        s.report_data['vitamin_d'] = vd
        if vd < 10: s.risk = s.risk + 15; s.reasons.append("Vitamin D very low (" + str(vd) + "): +15 risk"); s.step = 'bp6'
        elif vd < 30: s.risk = s.risk + 10; s.reasons.append("Vitamin D low (" + str(vd) + "): +10 risk"); s.step = 'bp6'
        else: s.step = 'bp6'
        st.rerun()
elif step == 'bp6':
    st.subheader("🧍 Q8: Kya der tak baithne ya jhukne se dard barh jata hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp6y"):
        s.patient_data['worse_sitting_bending'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Pain worse with sitting / bending (posture-related): +5 risk"); s.step = 'bp7'; st.rerun()
    if c2.button("No / Nahi", key="bp6n"): s.patient_data['worse_sitting_bending'] = "No"; s.step = 'bp7'; st.rerun()
elif step == 'bp7':
    st.subheader("🧍 Q9: Kya subah akdan 30 minute se zyada rehti hai jo harkat se behtar hoti hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp7y"):
        s.patient_data['morning_stiffness'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Morning back stiffness over 30 minutes: +10 risk"); s.step = 'bp8'; st.rerun()
    if c2.button("No / Nahi", key="bp7n"): s.patient_data['morning_stiffness'] = "No"; s.step = 'bp8'; st.rerun()
elif step == 'bp8':
    st.subheader("🧍 Q10: Kya aap bhaari wazan uthate hain ya galat posture mein kaam karte hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp8y"):
        s.patient_data['heavy_lifting_posture'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Heavy lifting / poor posture: +5 risk"); s.step = 'bp9'; st.rerun()
    if c2.button("No / Nahi", key="bp8n"): s.patient_data['heavy_lifting_posture'] = "No"; s.step = 'bp9'; st.rerun()
elif step == 'bp9':
    st.subheader("🧍 Q11: Kya taangon ya pairon mein sunn (numbness) ya jhanjhanahat hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp9y"):
        s.patient_data['leg_numbness'] = "Yes"; s.risk = s.risk + 15; s.reasons.append("Numbness / tingling in legs: +15 risk"); s.step = 'bp10'; st.rerun()
    if c2.button("No / Nahi", key="bp9n"): s.patient_data['leg_numbness'] = "No"; s.step = 'bp10'; st.rerun()
elif step == 'bp10':
    st.subheader("🧍 Q12: Kya aapko haddiyon ki kamzori (osteoporosis) ya pehle fracture ki history hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp10y"):
        s.patient_data['weak_bones_history'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Weak bones / fracture history: +10 risk"); s.step = 'bp11'; st.rerun()
    if c2.button("No / Nahi", key="bp10n"): s.patient_data['weak_bones_history'] = "No"; s.step = 'bp11'; st.rerun()
elif step == 'bp11':
    st.subheader("🧍 Q13: Kya aap dhoop mein kam jaate hain aur jism mein thakan / dard rehta hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp11y"):
        s.patient_data['low_sun_fatigue'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Low sun exposure with fatigue / body ache: +5 risk"); s.step = 'bp12'; st.rerun()
    if c2.button("No / Nahi", key="bp11n"): s.patient_data['low_sun_fatigue'] = "No"; s.step = 'bp12'; st.rerun()
elif step == 'bp12':
    st.subheader("🧍 Q14: Kya aapka wazan zyada (overweight) hai?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp12y"):
        s.patient_data['overweight'] = "Yes"; s.risk = s.risk + 5; s.reasons.append("Overweight (extra load on spine): +5 risk"); s.step = 'bp13'; st.rerun()
    if c2.button("No / Nahi", key="bp12n"): s.patient_data['overweight'] = "No"; s.step = 'bp13'; st.rerun()
elif step == 'bp13':
    st.subheader("🧍 Q15: Kya aap lambe arse se steroid dawaiyan lete hain?"); c1, c2 = st.columns(2)
    if c1.button("Yes / Haan", key="bp13y"):
        s.patient_data['long_steroid_use'] = "Yes"; s.risk = s.risk + 10; s.reasons.append("Long-term steroid use: +10 risk"); s.step = 'end'; st.rerun()
    if c2.button("No / Nahi", key="bp13n"): s.patient_data['long_steroid_use'] = "No"; s.step = 'end'; st.rerun()

# ================= FINAL RESULT =================
elif step == 'end':
    if s.risk > 100: s.risk = 100
    if s.risk >= 70: urgency = "EMERGENCY"; st.error("🚨 EMERGENCY: Go to hospital immediately!"); suggestion = "Go to the hospital immediately. Please consult a doctor right now."
    elif s.risk >= 40: urgency = "URGENT"; st.warning("⚠️ URGENT: Doctor se aaj milein"); suggestion = "Please consult a doctor today and get a medical checkup."
    elif s.risk >= 20: urgency = "ROUTINE"; st.info("📅 ROUTINE: 1-2 hafte mein checkup karwayein"); suggestion = "Get a medical checkup within 1-2 weeks. Please consult a doctor."
    else: urgency = "SELF-CARE"; st.success("🏠 SELF-CARE: Ghar pe rest karein"); suggestion = "Take rest at home. Please consult a doctor if symptoms continue."
    st.write("Risk Score: " + str(s.risk) + "/100"); st.progress(s.risk)
    st.write("**🧠 Yeh decision kyun? (Why this decision)**")
    if len(s.reasons) == 0: st.write("• No major red flags found from your answers.")
    for r in s.reasons: st.write("• " + r)
    st.info("💡 " + suggestion)
    st.write("This is NOT a diagnosis. Hamesha qualified doctor se confirm karwayein.")
    if s.saved == False:
        save_to_db(s.patient_data, s.report_data, "[" + urgency + "] Risk " + str(s.risk) + "/100 | " + suggestion + " | Reasons: " + "; ".join(s.reasons))
        s.saved = True
        st.rerun()
    st.success("💾 Consultation database mein save ho gayi.")
    if st.button("🔄 Start New Consultation", key="new"):
        s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False
        st.rerun()
else:
    st.error("Unknown step. Dobara shuru karein.")
    if st.button("Restart", key="restart"):
        s.step = 'start'; s.patient_data = {}; s.report_data = {}; s.risk = 0; s.reasons = []; s.saved = False
        st.rerun()

