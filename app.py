import os
import json
import streamlit as st
import anthropic

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Claude System Prompt Precision Lab",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Claude Prompt Precision & System Evaluation Lab")
st.caption("A system-level testbed evaluating baseline vs. XML-structured system prompts using Claude 3.5 Sonnet.")

# Sidebar for API Key and Settings
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", help="Enter your Anthropic API Key")
    selected_model = st.selectbox(
        "Claude Model",
        ["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"],
        index=0
    )
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# Initialize Anthropic Client
if api_key:
    client = anthropic.Anthropic(api_key=api_key)
else:
    client = None
    st.warning("Please enter your Anthropic API Key in the sidebar to run live evaluations.")

# ------------------------------------------------------------------------------
# 2. PROMPT TEMPLATES (Baseline vs. Anthropic XML Optimized)
# ------------------------------------------------------------------------------
DEFAULT_USER_INPUT = "Design a high school biology activity about cellular respiration for an inclusion classroom with ESL students."

BASELINE_SYSTEM_PROMPT = """You are an educational assistant. Provide a lesson activity for high school biology. Make sure it is clear and helpful for inclusion classrooms and ESL students."""

XML_OPTIMIZED_SYSTEM_PROMPT = """<role>
You are an expert Instructional Designer and Educational AI Specialist.
</role>

<task>
Create a targeted, multi-tiered learning activity based on the user's topic and classroom constraints.
</task>

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
</constraints>"""

# ------------------------------------------------------------------------------
# 3. INTERFACE LAYOUT
# ------------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Baseline System Prompt")
    prompt_a = st.text_area("Unstructured Baseline", BASELINE_SYSTEM_PROMPT, height=220)

with col2:
    st.subheader("XML-Optimized System Prompt")
    prompt_b = st.text_area("Anthropic XML Tag Structured", XML_OPTIMIZED_SYSTEM_PROMPT, height=220)

user_query = st.text_area("Test Input Query", DEFAULT_USER_INPUT, height=80)

# ------------------------------------------------------------------------------
# 4. EXECUTION & EVALUATION PIPELINE
# ------------------------------------------------------------------------------
if st.button("Run Evaluation", type="primary"):
    if not client:
        st.error("API Key missing.")
    else:
        with st.spinner("Executing Claude responses and running evaluation judge..."):
            
            # Function to call Claude API
            def get_claude_response(sys_prompt, user_text):
                res = client.messages.create(
                    model=selected_model,
                    max_tokens=1024,
                    temperature=temperature,
                    system=sys_prompt,
                    messages=[{"role": "user", "content": f"<user_query>{user_text}</user_query>"}]
                )
                return res.content[0].text

            # Run parallel completion requests
            out_a = get_claude_response(prompt_a, user_query)
            out_b = get_claude_response(prompt_b, user_query)

            # Display Outputs Side-by-Side
            out_col1, out_col2 = st.columns(2)
            with out_col1:
                st.markdown("### Output A (Baseline)")
                st.info(out_a)

            with out_col2:
                st.markdown("### Output B (XML Optimized)")
                st.success(out_b)

            # ------------------------------------------------------------------
            # LLM-as-a-Judge Scoring Call
            # ------------------------------------------------------------------
            st.divider()
            st.subheader("📊 Automated Evaluation (LLM-as-a-Judge)")

            eval_judge_prompt = """<role>
You are an AI System Evaluator benchmarking LLM output quality.
</role>

<task>
Compare Output A and Output B against the user input. Score each on a scale of 1-5 across three metrics:
1. Structural Adherence (Did it follow required headers and schema?)
2. Pedagogical Differentiation (Did it provide actual ESL/Inclusion support?)
3. Actionability (Is it clear and ready to use?)
</task>

<output_format>
Return strictly a JSON object matching this schema:
{
  "output_a_scores": {"structure": 0, "differentiation": 0, "actionability": 0},
  "output_b_scores": {"structure": 0, "differentiation": 0, "actionability": 0},
  "winner": "Output A" | "Output B",
  "rationale": "Brief explanation"
}
</output_format>"""

            judge_input = f"""<user_query>{user_query}</user_query>
<output_a>{out_a}</output_a>
<output_b>{out_b}</output_b>"""

            eval_res = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=512,
                temperature=0.0,
                system=eval_judge_prompt,
                messages=[{"role": "user", "content": judge_input}]
            )

            try:
                scores = json.loads(eval_res.content[0].text)
                
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Baseline Avg Score", f"{sum(scores['output_a_scores'].values())/3:.1f} / 5.0")
                with m_col2:
                    st.metric("XML Optimized Avg Score", f"{sum(scores['output_b_scores'].values())/3:.1f} / 5.0")
                with m_col3:
                    st.metric("Top Performer", scores["winner"])

                st.json(scores)
            except Exception as e:
                st.write("Raw Judge Evaluation Output:")
                st.write(eval_res.content[0].text)