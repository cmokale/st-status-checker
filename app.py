import streamlit as st
import pandas as pd
from curl_cffi import requests as cureq
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import json
import base64
import os

# Helper function to encode image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Default headers (same as original script)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Function to check the HTTP status of a given URL
def check_url_status(url, headers, delay=0, timeout=10):
    time.sleep(delay)
    redirect_chain = []
    try:
        response = cureq.get(url, headers=headers, timeout=timeout, allow_redirects=True, impersonate="chrome")
        for resp in response.history:
            redirect_chain.append((resp.status_code, resp.url))
        redirect_chain.append((response.status_code, response.url))
        return response.status_code, redirect_chain
    except cureq.exceptions.RequestException as e:
        if "timeout" in str(e).lower():
            return 'Timeout', [(None, url)]
        else:
            return 'Error', [(None, url)]
    except Exception as e:
        return 'Error', [(None, url)]

# Function to get status color
def get_status_color(status):
    if isinstance(status, int):
        if 200 <= status < 300:
            return "🟢"
        elif 300 <= status < 400:
            return "🟡"
        elif 400 <= status < 500:
            return "🟠"
        elif status >= 500:
            return "🔴"
    return "⚪"

# Streamlit app configuration
st.set_page_config(
    page_title="URL Status Checker",
    page_icon="🔍",
    layout="wide"
)

# Header with profile section
st.markdown("""
<style>
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0;
    margin-bottom: 20px;
    border-bottom: 2px solid #e0e0e0;
}
.profile-card {
    text-align: right;
    padding: 0px;
    background: transparent;
    border-radius: 0px;
    min-width: 250px;
    display: flex;
    justify-content: flex-end;
}
.profile-img-container {
    margin-bottom: 15px;
    margin-right: 25px;
}
.profile-img {
    border-radius: 50%;
    width: 100px;
    height: 100px;
    object-fit: cover;
    border: 3px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
.profile-name {
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin: 10px 0 5px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: flex-end;
}
.profile-name a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}
.profile-name a:hover {
    color: #4da6ff;
    text-decoration: underline;
}
.linkedin-icon {
    width: 18px;
    height: 18px;
    opacity: 0.9;
    transition: opacity 0.3s;
}
.linkedin-icon:hover {
    opacity: 1;
}
.profile-link {
    font-size: 14px;
    margin: 8px 0;
}
.profile-link a {
    color: #4da6ff;
    text-decoration: none;
    transition: color 0.3s;
}
.profile-link a:hover {
    color: #80bfff;
    text-decoration: underline;
}
.profile-footer {
    font-size: 13px;
    color: #b0b0b0;
    margin-top: 12px;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

header_col1, header_col2 = st.columns([2, 2])

with header_col1:
    st.title("🔍 Robust Status Checker")
    st.markdown("""
    <div style="max-width: 700px;">
    A robust status code checker built in Python with libraries and mechanisms designed to bypass Cloudflare, Shopify and other bot prevention systems. If anything breaks, please let me know with a breakdown so I can try pin point the issue.
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Profile section - Responsive: left on mobile, right on desktop
    st.markdown("""
    <style>
    .profile-wrapper {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin: 0;
        padding: 0;
    }
    .profile-content {
        text-align: right;
    }
    .profile-img-wrapper {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 15px;
    }
    .profile-name-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        justify-content: flex-end;
    }
    @media (max-width: 768px) {
        .profile-wrapper {
            justify-content: flex-start;
        }
        .profile-content {
            text-align: left;
        }
        .profile-img-wrapper {
            justify-content: flex-start;
        }
        .profile-name-wrapper {
            justify-content: flex-start;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    profile_image_path = os.path.join(os.path.dirname(__file__), "assets", "profile.png")

    if os.path.exists(profile_image_path):
        img_data = get_base64_image(profile_image_path)
        st.markdown(f"""
        <div class="profile-wrapper">
            <div class="profile-content">
                <div class="profile-img-wrapper">
                    <img src="data:image/png;base64,{img_data}"
                         style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #fff; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);"
                         alt="JP Garbaccio">
                </div>
                <div class="profile-name-wrapper" style="font-size: 20px; font-weight: bold; color: white; margin: 10px 0 5px 0;">
                    <a href="https://www.linkedin.com/in/garbacciojp/" target="_blank" style="color: white; text-decoration: none;">JP Garbaccio</a>
                    <a href="https://www.linkedin.com/in/garbacciojp/" target="_blank" style="display: inline-block;">
                        <svg style="width: 18px; height: 18px; opacity: 0.9;" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                    </a>
                </div>
                <div style="font-size: 13px; color: #b0b0b0; margin: 5px 0 10px 0; font-style: italic;">
                    Building tools and systems for marketers.
                </div>
                <div style="font-size: 14px; margin: 8px 0;">
                    Made with ❤️ @ <a href="https://jpgarbaccio.com/" target="_blank" style="color: #4da6ff; text-decoration: none;">jpgarbaccio.com</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="profile-wrapper">
            <div class="profile-content">
                <div class="profile-img-wrapper">
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 3px solid #fff;
                                background: #333; display: flex; align-items: center; justify-content: center;
                                font-size: 40px;">👤</div>
                </div>
                <div class="profile-name-wrapper" style="font-size: 20px; font-weight: bold; color: white; margin: 10px 0 5px 0;">JP Garbaccio</div>
                <div style="font-size: 13px; color: #b0b0b0; margin: 5px 0 10px 0; font-style: italic;">
                    Building tools and systems for marketers.
                </div>
                <div style="font-size: 14px; margin: 8px 0;">
                    Made with ❤️ @ <a href="https://jpgarbaccio.com/" target="_blank" style="color: #4da6ff; text-decoration: none;">jpgarbaccio.com</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Add spacing between header and settings
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# Initialize session state
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Settings section in main area
with st.expander("⚙️ Settings", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_workers = st.slider("Max Parallel Workers", min_value=1, max_value=20, value=10)
    
    with col2:
        delay = st.slider("Delay Between Requests (seconds)", min_value=0.0, max_value=2.0, value=0.1, step=0.1)
    
    with col3:
        timeout = st.slider("Request Timeout (seconds)", min_value=5, max_value=60, value=10)
    
    st.divider()
    
    st.subheader("🔧 Custom Headers")
    use_custom_headers = st.checkbox("Use Custom Headers")
    
    if use_custom_headers:
        st.markdown("Paste your custom headers in JSON format:")
        custom_headers_text = st.text_area(
            "Headers (JSON)",
            value=json.dumps(DEFAULT_HEADERS, indent=2),
            height=200,
            help="Enter valid JSON format headers",
            label_visibility="collapsed"
        )
        try:
            headers = json.loads(custom_headers_text)
            st.success("✅ Valid JSON headers")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format")
            headers = DEFAULT_HEADERS
    else:
        headers = DEFAULT_HEADERS
        with st.expander("View Default Headers"):
            st.json(DEFAULT_HEADERS)

# Main content area - URL entry
st.subheader("Enter URLs")
st.markdown("Enter one URL per line")

url_text = st.text_area("URLs", height=200, placeholder="https://example.com\nhttps://google.com", label_visibility="collapsed")

if st.button("🚀 Check URLs", type="primary", disabled=st.session_state.processing):
    urls = [url.strip() for url in url_text.split('\n') if url.strip()]

    if not urls:
        st.warning("⚠️ Please enter at least one URL")
    else:
        st.session_state.processing = True

        # Create dataframe
        df = pd.DataFrame({'URLs To Check': urls})
        df['Status Code'] = None
        df['Final URL'] = None
        for i in range(5):
            df[f'URL {i+1}'] = None

        total_urls = len(urls)

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        processed_count = 0

        # Process URLs
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for index, url in enumerate(urls):
                future = executor.submit(check_url_status, url, headers, delay, timeout)
                future_to_index[future] = index

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                current_url = urls[index]

                try:
                    status, redirect_chain = future.result()
                    df.at[index, 'Status Code'] = status

                    if redirect_chain:
                        final_url = redirect_chain[-1][1]
                        df.at[index, 'Final URL'] = final_url
                        for i in range(5):
                            if i < len(redirect_chain):
                                df.at[index, f'URL {i+1}'] = redirect_chain[i][1]
                            else:
                                df.at[index, f'URL {i+1}'] = None
                    else:
                        df.at[index, 'Final URL'] = None
                        for i in range(5):
                            df.at[index, f'URL {i+1}'] = None

                except Exception as e:
                    df.at[index, 'Status Code'] = 'Error'
                    df.at[index, 'Final URL'] = None
                    for i in range(5):
                        df.at[index, f'URL {i+1}'] = None

                processed_count += 1
                progress = processed_count / total_urls
                progress_bar.progress(progress)
                status_text.text(f"Processing: {processed_count}/{total_urls} URLs ({progress*100:.1f}%)")

        st.session_state.results_df = df
        st.session_state.processing = False
        progress_bar.progress(1.0)
        status_text.text(f"✅ Complete! Processed {total_urls} URLs")
        st.rerun()

# Display results
if st.session_state.results_df is not None:
    st.divider()
    st.header("📊 Results")

    df = st.session_state.results_df

    # Download button at the top
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="url_status_results.csv",
        mime="text/csv",
        type="primary",
        width="content"
    )
    st.markdown("---")

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total URLs", len(df))

    with col2:
        success_count = len(df[df['Status Code'].apply(lambda x: isinstance(x, int) and 200 <= x < 300)])
        st.metric("Success (2xx)", success_count)

    with col3:
        redirect_count = len(df[df['Status Code'].apply(lambda x: isinstance(x, int) and 300 <= x < 400)])
        st.metric("Redirects (3xx)", redirect_count)

    with col4:
        error_count = len(df[df['Status Code'].apply(lambda x: isinstance(x, int) and x >= 400)])
        st.metric("Errors (4xx/5xx)", error_count)

    # Status code breakdown
    st.subheader("Status Code Distribution")
    status_counts = df['Status Code'].value_counts().reset_index()
    status_counts.columns = ['Status Code', 'Count']
    status_counts['Icon'] = status_counts['Status Code'].apply(get_status_color)
    status_counts = status_counts[['Icon', 'Status Code', 'Count']]
    st.dataframe(status_counts, width="stretch", hide_index=True)

    # Results table with filtering
    st.subheader("Detailed Results")

    # Filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        # Convert all status codes to strings for sorting (handles mixed int/str types)
        status_options = [str(code) for code in df['Status Code'].unique()]
        status_filter = st.multiselect(
            "Filter by Status Code",
            options=sorted(status_options),
            default=None
        )

    # Apply filters
    filtered_df = df.copy()
    if status_filter:
        # Convert status codes to strings for comparison
        filtered_df = filtered_df[filtered_df['Status Code'].astype(str).isin(status_filter)]

    # Add status color column for display
    display_df = filtered_df.copy()
    display_df.insert(1, '📊', display_df['Status Code'].apply(get_status_color))

    st.dataframe(display_df, width="stretch", hide_index=True)

    # Download filtered results button
    if status_filter:
        csv_filtered = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results as CSV",
            data=csv_filtered,
            file_name="url_status_results_filtered.csv",
            mime="text/csv",
            type="secondary"
        )

    # Clear results button
    if st.button("🗑️ Clear Results"):
        st.session_state.results_df = None
        st.rerun()
