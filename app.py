
import streamlit as st
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="طرح‌های جاباما", layout="wide")

DATA_FILE = "all_requests.csv"
LOGO_PATH = "jabama_logo.png"
VIDEO_URL = "https://www.youtube.com/embed/Bey4XXJAqS8"

# اگر فایل CSV موجود نیست، بساز
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["host_code", "place_name", "plan", "timestamp"]).to_csv(DATA_FILE, index=False)
df = pd.read_csv(DATA_FILE)

# اتصال به گوگل شیت از طریق st.secrets معمولی
def get_google_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(credentials)

def write_to_google_sheet(host_code, place_name, plan, timestamp):
    try:
        client = get_google_client()
        sheet = client.open("JabamaRegistrations").sheet1
        sheet.append_row([host_code, place_name, plan, str(timestamp)])
    except Exception as e:
        st.error(f"❌ خطا در اتصال به Google Sheet: {e}")

# لوگو
col1, col2 = st.columns([3, 1])
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)

# عنوان و ویدیو
st.markdown("<h1 style='text-align: center;'>با طرح‌های ویژه جاباما بیشتر دیده شوید!</h1>", unsafe_allow_html=True)
st.markdown("### معرفی کوتاه:")
st.video(VIDEO_URL)
st.markdown("---")
st.markdown("## طرح‌های ما", unsafe_allow_html=True)

# تعریف طرح‌ها
plans = {
    "طرح ۱": {"ویژگی‌ها": ["پشتیبانی تلفنی", "افزایش نمایش"], "شرایط": ["فعال بودن اقامتگاه", "نداشتن بدهی"]},
    "طرح ۲": {"ویژگی‌ها": ["تبلیغات ویژه", "پشتیبانی اختصاصی"], "شرایط": ["امتیاز بالای ۴", "تأیید هویت"]},
    "طرح ۳": {"ویژگی‌ها": ["مشاوره بازاریابی", "اولویت در جستجو"], "شرایط": ["ارائه تعهدنامه", "بیش از ۶ ماه فعالیت"]}
}

# فرم‌ها برای هر طرح
for plan_name, content in plans.items():
    with st.container():
        st.subheader(plan_name)
        st.write("**ویژگی‌ها:**")
        st.markdown("<ul>" + "".join([f"<li>{item}</li>" for item in content["ویژگی‌ها"]]) + "</ul>", unsafe_allow_html=True)
        st.write("**شرایط:**")
        st.markdown("<ul>" + "".join([f"<li>{item}</li>" for item in content["شرایط"]]) + "</ul>", unsafe_allow_html=True)

        with st.form(f"form_{plan_name}"):
            host_code = st.text_input("کد میزبانی", key=f"host_{plan_name}")
            place_name = st.text_input("نام اقامتگاه", key=f"place_{plan_name}")
            submitted = st.form_submit_button(f"درخواست برای {plan_name}")

            if submitted:
                if not host_code or not place_name:
                    st.warning("لطفاً تمام فیلدها را پر کنید.")
                else:
                    existing = df[
                        (df["host_code"] == host_code) &
                        (df["place_name"] == place_name) &
                        (df["plan"] == plan_name)
                    ]
                    if not existing.empty:
                        st.info("درخواست شما قبلاً ثبت شده. به‌زودی با شما تماس خواهیم گرفت.")
                    else:
                        timestamp = pd.Timestamp.now()
                        new_entry = pd.DataFrame([{
                            "host_code": host_code,
                            "place_name": place_name,
                            "plan": plan_name,
                            "timestamp": timestamp
                        }])
                        df = pd.concat([df, new_entry], ignore_index=True)
                        df.to_csv(DATA_FILE, index=False)
                        write_to_google_sheet(host_code, place_name, plan_name, timestamp)
                        st.success("درخواست شما با موفقیت ثبت شد ✅")
        st.markdown("---")
