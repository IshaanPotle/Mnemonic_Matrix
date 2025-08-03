import streamlit as st

st.title("HTML Test")

# Test simple HTML
st.markdown("<h1 style='color: red;'>This is a test</h1>", unsafe_allow_html=True)

# Test the actual HTML from visualizer
test_html = """
<div style="background-color: #1A1A1A; padding: 20px; border-radius: 10px; color: #E8E8E8;">
    <h3 style="text-align: center; color: #FF6B9D; margin-bottom: 20px;">🌟 Memory Studies Knowledge Network (6 nodes)</h3>
    <div style="margin-bottom: 20px; padding: 15px; background-color: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid #FF6B9D;">
        <h4 style="color: #FF6B9D; margin-bottom: 10px;">⏰ Time Periods</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            <span style="background-color: #FF6B9D; color: white; padding: 5px 10px; border-radius: 15px; font-size: 20px; font-weight: bold; display: inline-block; margin: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);" title="Frequency: 3 papers">T4 (3)</span>
        </div>
    </div>
</div>
"""

st.markdown("Testing the actual HTML:")
st.markdown(test_html, unsafe_allow_html=True)

st.markdown("Raw HTML:")
st.code(test_html) 