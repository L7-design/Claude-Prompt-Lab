import streamlit as st
import anthropic

# 1. Page Configuration
st.set_page_config(
    page_title="Claude System Prompt Precision Lab",
    page_icon="⚡",
    layout="wide"
)

# 2. Sidebar Setup & API Key Input
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "Anthropic API Key", 
    type="password", 
    help="Enter your Anthropic API key to run live evaluations."
)
model_name = st.sidebar.text_input("Claude Model", value="claude-3-5-sonnet-20240620")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

# 3. Main Header & Banner
st.title("⚡ Claude Prompt Precision & System Evaluation Lab")
st.caption("A system-level testbed evaluating baseline vs. XML-structured system prompts using Claude 3.5 Sonnet.")

# Guide visitors if no API key is provided
if not api_key:
    st.info("💡 **Getting Started:** Please enter your **Anthropic API Key** in the sidebar on the left to run live evaluations.")

# 4. Inputs Section
st.subheader("Baseline System Prompt")
baseline_prompt = st.text_area(
    "Unstructured Baseline", 
    value="You are an educational assistant. Provide a lesson activity for high school biology. Make sure it is clear and helpful for inclusion classrooms and ESL students.",
    height=100
)

st.subheader("XML-Optimized System Prompt")
xml_prompt = st.text_area(
    "Anthropic XML Tag Structured", 
    value="""<role> You are an expert Instructional Designer and Educational AI Specialist. </role>

<task> Create a targeted, multi-tiered learning activity based on the user's topic and classroom constraints. </task>

<instructions>
1. Break down complex biology terminology into plain language with an included visual glossary.
2. Structure the activity using universal design for learning (UDL) principles.
3. Provide explicit step-by-step instructions for the teacher.
</instructions>

<output_format>
Return the response in markdown with the following section headers:
- ## Activity Overview
- ## Visual & Vocabulary Scaffolds (ESL Focus)
- ## Multi-Tiered Step-by-Step Instructions
- ## Formative Assessment Criteria
</output_format>

<constraints>
- Do not use dense jargon without immediate context or definitions.
- Keep total output concise and actionable.
</constraints>""",
    height=250
)

test_query = st.text_input(
    "Test Input Query", 
    value="Design a high school biology activity about cellular respiration for an inclusion classroom with ESL students."
)

# 5. Execution Guardrails & LLM Calls
if st.button("Run Evaluation"):
    if not api_key:
        st.error("🔑 Please enter your Anthropic API Key in the sidebar before running the evaluation.")
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            with st.spinner("Generating responses and running LLM-as-a-Judge evaluation..."):
                # Call Baseline
                baseline_res = client.messages.create(
                    model=model_name,
                    max_tokens=1000,
                    temperature=temperature,
                    system=baseline_prompt,
                    messages=[{"role": "user", "content": test_query}]
                )
                
                # Call XML Optimized
                xml_res = client.messages.create(
                    model=model_name,
                    max_tokens=1000,
                    temperature=temperature,
                    system=xml_prompt,
                    messages=[{"role": "user", "content": test_query}]
                )
                
                # Display Results Side-by-Side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Unstructured Baseline Output")
                    st.markdown(baseline_res.content[0].text)
                    
                with col2:
                    st.subheader("XML-Optimized Output")
                    st.markdown(xml_res.content[0].text)
                    
        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")