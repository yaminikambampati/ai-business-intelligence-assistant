"""Streamlit frontend for AI Business Intelligence Assistant."""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
import plotly.express as px

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI Business Intelligence Assistant",
    page_icon="📊",
    layout="wide"
)


def check_backend_health() -> bool:
    """Check if the backend is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_metadata() -> Dict[str, Any]:
    """Get dataset metadata."""
    try:
        response = requests.get(f"{API_BASE_URL}/metadata", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def ask_question(question: str) -> Dict[str, Any]:
    """Send a question to the backend."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "answer": f"Error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "answer": f"Connection error: {str(e)}"}


def main():
    """Main Streamlit application."""

    # Header
    st.title("📊 AI Business Intelligence Assistant")
    st.markdown("Ask questions about your sales data and receive answers supported by database queries.")

    # Check backend health
    with st.spinner("Connecting to backend..."):
        backend_healthy = check_backend_health()

    if not backend_healthy:
        st.error("⚠️ Backend is not available. Please start the FastAPI backend first.")
        st.info("Run: `uvicorn backend.main:app --reload`")
        st.stop()

    # Get metadata
    metadata = get_metadata()
    if metadata:
        st.success(f"✅ Backend connected. {metadata['record_count']} transactions loaded.")
        if metadata.get('date_range'):
            st.info(f"📅 Data range: {metadata['date_range']['start']} to {metadata['date_range']['end']}")
    else:
        st.warning("Could not retrieve metadata.")

    # Example questions
    st.markdown("### Example Questions")
    example_questions = [
        "What is the total revenue?",
        "Which product generated the highest revenue?",
        "What is the monthly revenue trend?",
        "Which region generated the highest sales?",
        "How did revenue change between January 2026 and February 2026?"
    ]

    cols = st.columns(5)
    for i, question in enumerate(example_questions):
        if cols[i].button(question, key=f"example_{i}"):
            st.session_state.user_question = question

    # Question input
    st.markdown("### Ask a Question")
    user_question = st.text_input(
        "Enter your question about sales data:",
        value=st.session_state.get("user_question", ""),
        key="question_input"
    )

    col_ask, col_clear = st.columns([1, 1])
    if col_ask.button("Ask", type="primary"):
        if user_question:
            with st.spinner("Processing your question..."):
                response = ask_question(user_question)
                st.session_state.last_response = response
                st.session_state.last_question = user_question
        else:
            st.warning("Please enter a question.")

    if col_clear.button("Clear"):
        st.session_state.user_question = ""
        st.session_state.last_response = None
        st.session_state.last_question = None
        st.rerun()

    # Display response
    if "last_response" in st.session_state and st.session_state.last_response:
        response = st.session_state.last_response
        question = st.session_state.last_question

        st.markdown("---")
        st.markdown("### Answer")

        if response.get("success"):
            st.success(response.get("answer", ""))

            # Display data
            if response.get("data"):
                data = response["data"]

                # Monthly revenue chart
                if "monthly_data" in data and data["monthly_data"]:
                    st.markdown("#### Monthly Revenue Trend")
                    monthly_df = pd.DataFrame(data["monthly_data"])
                    fig = px.line(
                        monthly_df,
                        x="month",
                        y="total_revenue",
                        title="Monthly Revenue",
                        markers=True
                    )
                    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue")
                    st.plotly_chart(fig, use_container_width=True)

                    # Display table
                    st.markdown("#### Monthly Revenue Table")
                    st.dataframe(monthly_df, use_container_width=True)

                # Top product
                elif "all_products" in data and data["all_products"]:
                    st.markdown("#### Product Revenue Breakdown")
                    product_df = pd.DataFrame(data["all_products"])
                    st.dataframe(product_df, use_container_width=True)

                    # Chart
                    fig = px.bar(
                        product_df,
                        x="product",
                        y="total_revenue",
                        title="Revenue by Product"
                    )
                    fig.update_layout(xaxis_title="Product", yaxis_title="Revenue")
                    st.plotly_chart(fig, use_container_width=True)

                # Top region
                elif "all_regions" in data and data["all_regions"]:
                    st.markdown("#### Region Revenue Breakdown")
                    region_df = pd.DataFrame(data["all_regions"])
                    st.dataframe(region_df, use_container_width=True)

                    # Chart
                    fig = px.bar(
                        region_df,
                        x="region",
                        y="total_revenue",
                        title="Revenue by Region"
                    )
                    fig.update_layout(xaxis_title="Region", yaxis_title="Revenue")
                    st.plotly_chart(fig, use_container_width=True)

                # Revenue comparison
                elif "month1_revenue" in data:
                    st.markdown("#### Revenue Comparison")
                    comparison_df = pd.DataFrame([
                        {"Metric": "Month 1 Revenue", "Value": data["month1_revenue"]},
                        {"Metric": "Month 2 Revenue", "Value": data["month2_revenue"]},
                        {"Metric": "Absolute Change", "Value": data["absolute_change"]},
                        {"Metric": "Percentage Change", "Value": data.get("percentage_change", "N/A")}
                    ])
                    st.dataframe(comparison_df, use_container_width=True)

                # Total revenue
                elif "total_revenue" in data:
                    st.markdown("#### Revenue Details")
                    st.metric("Total Revenue", f"{data['total_revenue']:.2f}")
                    st.metric("Transaction Count", data.get("transaction_count", 0))

            # Display explanation
            if response.get("explanation"):
                st.info(f"💡 {response['explanation']}")

            # Display limitations
            if response.get("limitations"):
                st.markdown("#### Limitations")
                for limitation in response["limitations"]:
                    st.warning(f"⚠️ {limitation}")

        else:
            st.error(response.get("answer", "Failed to process question"))

            if response.get("explanation"):
                st.info(f"ℹ️ {response['explanation']}")

    # Dataset metadata section
    if metadata:
        st.markdown("---")
        st.markdown("### Dataset Metadata")

        col1, col2 = st.columns(2)
        col1.metric("Total Transactions", metadata["record_count"])
        col2.metric("Import Status", metadata["import_status"])

        if metadata.get("products"):
            st.markdown("#### Available Products")
            st.write(", ".join(metadata["products"]))

        if metadata.get("regions"):
            st.markdown("#### Available Regions")
            st.write(", ".join(metadata["regions"]))

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p><strong>Data Source:</strong> SQLite database loaded from CSV</p>
    <p><strong>AI Status:</strong> Deterministic parsing (LLM integration optional)</p>
    <p>Answers are calculated from actual database records, not fabricated.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
