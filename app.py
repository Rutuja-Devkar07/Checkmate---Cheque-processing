import streamlit as st
from PIL import Image
import pdf2image
import json
import re
import os
import matplotlib.pyplot as plt
import google.generativeai as genai
from db_connection import insert_cheque_details, fetch_cheque_details


def load_css(file_name):
    """Load custom CSS for styling."""
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file '{file_name}' not found!")


def render_sidebar():
    """Render the sidebar navigation using Material Symbols icons."""
    st.sidebar.title("⚙️ Navigation")  

    # Using Material Symbols icons
    page = st.sidebar.radio(
        "Go to",
        [
            ":material/home: Home",
            ":material/receipt_long: Extract",
            ":material/monitoring: Dashboard",
            ":material/insights: Analytics",
        ],
    )

    return page
def render_home():
    st.markdown(
        '<h1 class="custom-title">Welcome to ChequeMate - Automated Cheque Processing</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="white-text">ChequeMate helps you process, analyze, and track cheques efficiently.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class="white-text">
        Automated cheque processing uses AI technology to quickly extract and verify cheque details,
        eliminating manual errors. It enhances security with fraud detection and signature verification,
        ensuring fast, accurate, and efficient transactions. Ideal for banks, businesses, and individuals,
        this system speeds up cheque clearance, reduces costs, and improves financial workflows.
        </p> """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h2 class="why-choose-title">🚀 Why Choose ChequeMate?</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div class="centered-list">
        <ul>
            <li>⚡ <strong>Fast Data Extraction</strong></li>
            <li>🔒 <strong>Secure & Reliable</strong></li>
            <li>📤 <strong>Easy to Export</strong></li>
            <li>📊 <strong>Real-Time Insights</strong></li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )
  
def render_dashboard(data):
    """Render the dashboard with cheque records."""
    st.markdown('<h1 class="white-text">📊 Dashboard</h1>', unsafe_allow_html=True)

    if data is None or data.empty:
        st.markdown(
            '<p class="white-text">⚠️ No cheque data available.</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<h2 class="white-text"> Extracted Records from Database</h2>',
            unsafe_allow_html=True,
        )

        selected_columns = ["date", "cheque_number", "payee", "amount", "bank"]

        missing_cols = [col for col in selected_columns if col not in data.columns]
        if missing_cols:
            st.markdown(
                f'<p class="white-text">⚠️ Missing columns in database: {missing_cols}</p>',
                unsafe_allow_html=True,
            )
        else:
            # Filter data to show selected columns
            filtered_data = data[selected_columns]

            # Add a Serial Number column starting from 1
            filtered_data.insert(0, "Serial Number", range(1, len(filtered_data) + 1))

            # Search bar for filtering
            search_query = st.text_input("🔍 Search records", "")

            if search_query:
                filtered_data = filtered_data[
                    filtered_data.astype(str).apply(
                        lambda row: search_query.lower() in row.to_string().lower(),
                        axis=1,
                    )
                ]
            with st.container():
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.data_editor(
                    filtered_data, use_container_width=True, height=400, hide_index=True
                )
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<h3 class="white-text">📥 Download Cheque Records</h3>',
            unsafe_allow_html=True,
        )

        csv_data = filtered_data.to_csv(index=False).encode("utf-8")
        json_data = filtered_data.to_json(orient="records", indent=4).encode("utf-8")

        st.download_button(
            label="⬇️ CSV Format",
            data=csv_data,
            file_name="cheque_records.csv",
            mime="text/csv",
        )

        st.download_button(
            label="📄 JSON Format",
            data=json_data,
            file_name="cheque_records.json",
            mime="application/json",
        )


def render_extract():
    st.markdown(
        '<h1 class="white-text">📝 Automated Cheque Processing</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="white-text">Upload a cheque image or PDF</p>', unsafe_allow_html=True
    )

    def convert_pdf_to_image(pdf_file):
        images = pdf2image.convert_from_bytes(pdf_file.read())
        return images[0] if images else None

    def process_uploaded_image(uploaded_file):
        if uploaded_file is not None:
            st.markdown(
                f'<p class="uploaded-image-text">✅ Uploaded: {uploaded_file.name}</p>',
                unsafe_allow_html=True,
            )
            return {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}
        else:
            st.error("No file uploaded!")
            return None

    def get_api_response(image_content):
        """Send request to Gemini AI and return structured JSON response."""
        try:
            prompt = """
            Extract cheque details like payee, amount, bank, MICR code, branch, IFSC code, 
            account number, cheque number, date, and signature verification.
            Return JSON format.
            """

            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(
                [image_content, prompt]
            )

            if not response or not response.text:
                st.error("Empty response received from AI model.")
                return None

            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if match:
                json_text = match.group(0)
            else:
                st.error("AI response did not return valid JSON.")
                st.subheader("Raw Response for Debugging:")
                st.write(response.text)
                return None

            return json.loads(json_text.strip())

        except Exception as e:
            st.error(f"API Error: {e}")
            return None

    uploaded_file = st.file_uploader(
        "Upload Cheque Image or PDF", type=["jpg", "png", "jpeg", "pdf"]
    )
    if uploaded_file:
        image = (
            convert_pdf_to_image(uploaded_file)
            if uploaded_file.type == "application/pdf"
            else Image.open(uploaded_file)
        )
        if image:
            st.image(image, use_container_width=True)
            image_content = process_uploaded_image(uploaded_file)
            if image_content:
                if st.button("Process"):
                    with st.spinner("Processing cheque... Please wait ⏳"):
                        response = get_api_response(image_content)
                        if response:
                            st.markdown(
                                '<p class="white-text">Extracted cheque details</p>',
                                unsafe_allow_html=True,
                            )
                            st.json(response)

                            if insert_cheque_details(response):
                                st.success(
                                    "✅ Cheque details saved to database successfully!"
                                )
                            else:
                                st.error("❌ Failed to save cheque details.")
                        else:
                            st.error("⚠️ Failed to get AI response.")

def render_analytics():
    st.markdown(
        '<h1 class="white-text">📊 Cheque Processing Analytics</h1>',
        unsafe_allow_html=True,
    )

    # Fetch cheque data from the database
    data = fetch_cheque_details()

    if data is None or data.empty:
        st.markdown(
            '<p class="white-text">⚠️ No cheque data available.</p>',
            unsafe_allow_html=True,
        )
        return

    # Ensure 'status' column exists
    if "status" not in data.columns:
        data["status"] = "Processed"  # Temporary fix

    # Calculate key metrics
    total_cheques = len(data)
    processed_cheques = data[data["status"] == "Processed"].shape[0]
    failed_cheques = data[data["status"] == "Failed"].shape[0]

    # Display key metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<h3 class="white-text">📤 Total Cheques Uploaded</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="metric-text">{total_cheques}</p>', unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<h3 class="white-text">❌ Failed Cheques</h3>', unsafe_allow_html=True
        )
        st.markdown(
            f'<p class="metric-text">{failed_cheques}</p>', unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<h3 class="white-text">✅ Processed Cheques</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="metric-text">{processed_cheques}</p>', unsafe_allow_html=True
        )

    # Bar Chart: Status
    st.markdown("<h3 class='purple-text'>📊 STATISTICS</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        ["Processed", "Failed"],
        [processed_cheques, failed_cheques],
        color="#00AEEF",
        edgecolor="#00FFFF",
        linewidth=2,
        alpha=0.8,
    )

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 2,
            f"{int(height)}",
            ha="center",
            fontsize=14,
            fontweight="bold",
            color="white",
        )
    fig.patch.set_facecolor("#000000")
    ax.set_facecolor("#000000")
    ax.spines["bottom"].set_color("#00AEEF")
    ax.spines["left"].set_color("#00AEEF")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.label.set_color("#00AEEF")
    ax.yaxis.label.set_color("#00AEEF")
    ax.tick_params(axis="x", colors="white", labelsize=12)
    ax.tick_params(axis="y", colors="white", labelsize=12)
    ax.set_xlabel("Cheque Status", fontsize=14, color="#00AEEF")
    ax.set_ylabel("Number of Cheques", fontsize=14, color="#00AEEF")
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(False)
    st.pyplot(fig)

    st.markdown(
        '<p class="purple-text">📈 <strong>Insights:</strong> Analyze cheque processing trends, identify errors, and improve accuracy.</p>',
        unsafe_allow_html=True,
    )

    # Gap before pie chart
    st.markdown("<br>", unsafe_allow_html=True)

    # Pie Chart: Cheques by Bank
    if "bank" in data.columns:

        bank_counts = data["bank"].dropna().value_counts()

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax2.pie(
            bank_counts,
            labels=bank_counts.index,
            autopct="%1.1f%%",
            textprops={"color": "white", "fontsize": 12},
            startangle=140,
            # colors=plt.cm.coolwarm(range(len(bank_counts)))
            colors=["#2973B2"] * len(bank_counts),
        )

        fig2.patch.set_facecolor("#000000")
        ax2.set_facecolor("#000000")
        for text in texts:
            text.set_color("white")
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax2.set_title("Bank-wise Cheque Distribution", color="#C68EFD", fontsize=16)
        st.pyplot(fig2)

        st.markdown(
            '<p class="purple-text">📌 <strong>Insights:</strong> Understand which banks contribute the most to cheque volume.</p>',
            unsafe_allow_html=True,
        )
