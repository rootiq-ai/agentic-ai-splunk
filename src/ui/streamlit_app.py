"""Streamlit UI for Splunk Agentic AI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Configure page
st.set_page_config(
    page_title="Agentic AI Splunk",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import application modules
try:
    from config.config import config
    from src.core.query_processor import QueryProcessor
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    
    # Initialize query processor
    @st.cache_resource
    def get_query_processor():
        """Get cached query processor instance."""
        return QueryProcessor()
    
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

def main():
    """Main Streamlit application."""
    
    # App header
    st.title("🔍 Splunk Agentic AI")
    st.markdown("Ask questions in natural language and get SPL queries with results!")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Display connection status
        st.subheader("Connection Status")
        status_container = st.container()
        
        # Settings
        st.subheader("Query Settings")
        max_results = st.slider("Max Results", 10, 1000, 100, 10)
        show_spl = st.checkbox("Show Generated SPL", value=True)
        show_stats = st.checkbox("Show Statistics", value=True)
        auto_refresh = st.checkbox("Auto-refresh Health", value=True)
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            query_timeout = st.slider("Query Timeout (seconds)", 10, 300, 60)
            confidence_threshold = st.selectbox("Confidence Threshold", ["low", "medium", "high"], index=1)
        
        # Check health status
        try:
            processor = get_query_processor()
            health = processor.get_health_status()
            
            with status_container:
                if health["overall_status"] == "healthy":
                    st.success("🟢 All systems healthy")
                elif health["overall_status"] == "degraded":
                    st.warning("🟡 Some issues detected")
                else:
                    st.error("🔴 System issues")
                
                # Show component status
                if st.checkbox("Show Details", key="health_details"):
                    for service, status in health.items():
                        if service not in ["overall_status", "timestamp"]:
                            if isinstance(status, dict):
                                st.write(f"**{service}**: {status.get('status', 'unknown')}")
        
        except Exception as e:
            with status_container:
                st.error(f"🔴 Connection failed: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input section
        st.subheader("💬 Ask Your Question")
        
        # Example questions
        example_questions = [
            "Show me error logs from the last hour",
            "What are the top source IPs by traffic volume?",
            "Find failed login attempts in the last 24 hours",
            "Show me the most common HTTP status codes",
            "Which users have logged in today?"
        ]
        
        selected_example = st.selectbox(
            "Or choose an example:",
            [""] + example_questions,
            key="example_selector"
        )
        
        # Main query input
        if selected_example:
            default_question = selected_example
        else:
            default_question = ""
        
        question = st.text_area(
            "Enter your question:",
            value=default_question,
            height=100,
            placeholder="e.g., Show me failed login attempts from the last 24 hours"
        )
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            query_button = st.button("🔍 Execute Query", type="primary", use_container_width=True)
        
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        with col_btn3:
            save_button = st.button("💾 Save Query", use_container_width=True, disabled=not question)
        
        # Direct SPL input (collapsible)
        with st.expander("🔧 Direct SPL Input"):
            spl_query = st.text_area(
                "Enter SPL query directly:",
                height=80,
                placeholder="search index=_internal | head 10"
            )
            spl_button = st.button("Execute SPL", key="spl_execute")
    
    with col2:
        # Query suggestions
        st.subheader("💡 Suggestions")
        if question:
            try:
                processor = get_query_processor()
                suggestions = processor.get_query_suggestions(question)
                
                for i, suggestion in enumerate(suggestions[:3]):
                    if st.button(f"💭 {suggestion[:50]}...", key=f"suggestion_{i}"):
                        st.session_state.example_selector = suggestion
                        st.rerun()
            except Exception as e:
                st.error(f"Failed to get suggestions: {e}")
    
    # Handle button clicks
    if clear_button:
        st.session_state.current_results = None
        st.rerun()
    
    if save_button and question:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.query_history.append({
            "timestamp": timestamp,
            "question": question,
            "type": "natural_language"
        })
        st.success("Query saved to history!")
    
    # Execute natural language query
    if query_button and question:
        execute_natural_language_query(question, max_results, show_spl, show_stats)
    
    # Execute SPL query
    if spl_button and spl_query:
        execute_spl_query(spl_query, max_results, show_stats)
    
    # Display results
    if st.session_state.current_results:
        display_results(st.session_state.current_results, show_spl, show_stats)
    
    # Query history section
    display_query_history()

def execute_natural_language_query(question: str, max_results: int, show_spl: bool, show_stats: bool):
    """Execute natural language query."""
    try:
        processor = get_query_processor()
        
        with st.spinner("🤖 Converting question to SPL and executing..."):
            start_time = time.time()
            result = processor.process_natural_language_query(question, max_results)
            
        if result["success"]:
            st.session_state.current_results = result
            
            # Add to history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.query_history.append({
                "timestamp": timestamp,
                "question": question,
                "spl_query": result.get("spl_query", ""),
                "result_count": result.get("result_count", 0),
                "type": "natural_language",
                "success": True
            })
            
            st.success(f"✅ Query executed successfully! Found {result['result_count']} results in {result['processing_time']:.2f}s")
            
        else:
            st.error(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            
            # Add failed query to history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.query_history.append({
                "timestamp": timestamp,
                "question": question,
                "error": result.get('error', 'Unknown error'),
                "type": "natural_language",
                "success": False
            })
    
    except Exception as e:
        st.error(f"❌ Execution failed: {str(e)}")

def execute_spl_query(spl_query: str, max_results: int, show_stats: bool):
    """Execute direct SPL query."""
    try:
        processor = get_query_processor()
        
        with st.spinner("⚡ Executing SPL query..."):
            result = processor.execute_spl_query(spl_query, max_results)
        
        if result["success"]:
            # Convert to match natural language result format
            result["question"] = "Direct SPL Query"
            result["explanation"] = "Direct SPL execution"
            result["confidence"] = "high"
            
            st.session_state.current_results = result
            
            # Add to history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.query_history.append({
                "timestamp": timestamp,
                "question": "Direct SPL",
                "spl_query": spl_query,
                "result_count": result.get("result_count", 0),
                "type": "spl_direct",
                "success": True
            })
            
            st.success(f"✅ SPL executed successfully! Found {result['result_count']} results in {result['processing_time']:.2f}s")
            
        else:
            st.error(f"❌ SPL execution failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"❌ SPL execution failed: {str(e)}")

def display_results(result: Dict[str, Any], show_spl: bool, show_stats: bool):
    """Display query results."""
    st.divider()
    st.subheader("📊 Results")
    
    # Show SPL query if requested
    if show_spl and result.get("spl_query"):
        st.subheader("🔧 Generated SPL Query")
        st.code(result["spl_query"], language="sql")
        
        # Show explanation and confidence
        if result.get("explanation"):
            st.info(f"**Explanation**: {result['explanation']}")
        
        confidence = result.get("confidence", "medium")
        confidence_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        st.write(f"**Confidence**: {confidence_color.get(confidence, '⚪')} {confidence.title()}")
    
    # Show statistics if requested
    if show_stats and result.get("statistics"):
        stats = result["statistics"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Results", stats.get("result_count", 0))
        with col2:
            st.metric("Scanned", stats.get("scan_count", 0))
        with col3:
            st.metric("Duration", f"{stats.get('run_duration', 0):.2f}s")
        with col4:
            st.metric("Processing", f"{result.get('processing_time', 0):.2f}s")
    
    # Display results
    results_data = result.get("results", [])
    
    if not results_data:
        st.info("No results found.")
        return
    
    # Results display options
    display_mode = st.radio(
        "Display Mode:",
        ["Table", "JSON", "Chart"],
        horizontal=True,
        key="display_mode"
    )
    
    if display_mode == "Table":
        display_table_results(results_data)
    elif display_mode == "JSON":
        display_json_results(results_data)
    elif display_mode == "Chart":
        display_chart_results(results_data)

def display_table_results(results_data: List[Dict[str, Any]]):
    """Display results as a table."""
    if not results_data:
        return
    
    try:
        df = pd.DataFrame(results_data)
        
        # Show column info
        st.write(f"**Columns**: {', '.join(df.columns)}")
        
        # Display dataframe with pagination
        if len(df) > 100:
            st.info(f"Showing first 100 of {len(df)} results")
            df = df.head(100)
        
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"splunk_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Failed to display table: {e}")
        st.json(results_data[:5])  # Fallback to JSON

def display_json_results(results_data: List[Dict[str, Any]]):
    """Display results as JSON."""
    # Limit display for performance
    display_data = results_data[:10] if len(results_data) > 10 else results_data
    
    if len(results_data) > 10:
        st.info(f"Showing first 10 of {len(results_data)} results")
    
    st.json(display_data)

def display_chart_results(results_data: List[Dict[str, Any]]):
    """Display results as charts."""
    if not results_data:
        st.info("No data to chart")
        return
    
    try:
        df = pd.DataFrame(results_data)
        
        # Auto-detect chartable columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if not numeric_cols and not categorical_cols:
            st.info("No suitable columns found for charting")
            return
        
        chart_type = st.selectbox("Chart Type:", ["Bar", "Line", "Pie", "Histogram"])
        
        if chart_type == "Bar" and categorical_cols:
            # Count occurrences
            col = st.selectbox("Column:", categorical_cols)
            value_counts = df[col].value_counts().head(10)
            
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Top 10 {col} Values"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Pie" and categorical_cols:
            col = st.selectbox("Column:", categorical_cols)
            value_counts = df[col].value_counts().head(10)
            
            fig = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f"{col} Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Histogram" and numeric_cols:
            col = st.selectbox("Column:", numeric_cols)
            
            fig = px.histogram(df, x=col, title=f"{col} Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info(f"Chart type '{chart_type}' not available for this data")
            
    except Exception as e:
        st.error(f"Failed to create chart: {e}")

def display_query_history():
    """Display query history."""
    if not st.session_state.query_history:
        return
    
    st.divider()
    st.subheader("📜 Query History")
    
    # History controls
    col1, col2 = st.columns([3, 1])
    with col1:
        show_count = st.slider("Show recent queries:", 5, 50, 10)
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Display history
    history = st.session_state.query_history[-show_count:]
    history.reverse()  # Most recent first
    
    for i, entry in enumerate(history):
        with st.expander(f"{entry['timestamp']} - {entry.get('question', 'Unknown')[:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type**: {entry.get('type', 'unknown').replace('_', ' ').title()}")
                st.write(f"**Question**: {entry.get('question', 'N/A')}")
                if entry.get('spl_query'):
                    st.code(entry['spl_query'], language="sql")
            
            with col2:
                if entry.get('success'):
                    st.success(f"✅ Success - {entry.get('result_count', 0)} results")
                else:
                    st.error(f"❌ Failed: {entry.get('error', 'Unknown error')}")
                
                # Rerun button
                if st.button(f"🔄 Re-run", key=f"rerun_{i}"):
                    if entry['type'] == 'natural_language':
                        # Re-execute natural language query
                        execute_natural_language_query(entry['question'], 100, True, True)
                    elif entry['type'] == 'spl_direct' and entry.get('spl_query'):
                        # Re-execute SPL query
                        execute_spl_query(entry['spl_query'], 100, True)

if __name__ == "__main__":
    try:
        # Validate configuration
        config.validate()
        main()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.info("Please check your .env file and ensure all required variables are set.")
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please check the logs for more details.")
