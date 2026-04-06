import streamlit as st
import pandas as pd
import time

from framework.agent import ChatAgent
from framework.evaluator import Evaluator
from framework.runner import TestRunner
from framework.metrics import Metrics
from framework.report import generate_report
from framework.utils import load_test_cases
from framework.adversarial import AdversarialGenerator
from framework.logger import Logger

st.set_page_config(page_title="AI Agent Testing Framework", layout="wide")

st.title("AI Agent Testing Framework")

# =========================
# INITIALIZE
# =========================

agent = ChatAgent()
evaluator = Evaluator()
logger = Logger()

# =========================
# MAIN TABS
# =========================

tab1, tab2, tab3 = st.tabs(["Single Query", "Structured Query", "Full Test Suite"])

# =========================================================
# TAB 1 — SINGLE QUERY
# =========================================================

with tab1:

    st.subheader("Test a Single Query")

    with st.form("query_form"):
        user_input = st.text_area("Enter your query", height=120)
        submitted = st.form_submit_button("Run Agent")

    if submitted:

        if user_input.strip() == "":
            st.warning("Please enter a query")
        else:
            with st.spinner("Running agent..."):

                output = agent.run(user_input)

                st.subheader("Agent Output")
                st.success(output)

                test_case = {
                    "input": user_input,
                    "expected_behavior": "Respond safely and correctly",
                    "category": "user"
                }

                result = evaluator.evaluate(test_case, output)

                # LOG RESULT
                logger.log(result)

            # =========================
            # METRICS
            # =========================

            st.subheader("Evaluation Metrics")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Correctness", result["correctness"])
            col2.metric("Relevance", result["relevance"])
            col3.metric("Safety (LLM)", result["safety_llm"])
            col4.metric("Safety (Rule)", result["safety_rule"])

            # =========================
            # SAFETY BREAKDOWN
            # =========================

            st.subheader("Safety Breakdown")

            col5, col6, col7 = st.columns(3)
            col5.metric("Keyword Safe", result["keyword_safe"])
            col6.metric("Refusal Detected", result["refusal_detected"])
            col7.metric("PII Safe", result["pii_safe"])

            keywords = result.get("triggered_keywords", [])

            if keywords:
                st.error(f"Triggered Keywords: {', '.join(keywords)}")
            
            pii_data = result.get("pii_detected", [])
            if pii_data:
                st.error(f"PII Detected: {', '.join(pii_data)}")

            # =========================
            # ALERT
            # =========================

            if not result["safety_rule"]:
                st.error("Unsafe or incorrect behavior detected!")
            else:
                st.success("Safe and correct behavior")
                
                
# =========================================================
# TAB 2 — STRUCTURED QUERY
# =========================================================

with tab2:

    st.subheader("Structured Test Input")

    st.markdown("""
    Provide a structured test case with:
    - **User Query**
    - **Expected Behaviour**
    - **Category**
    """)

    with st.form("structured_form"):

        user_query = st.text_area("User Query", height=120)

        expected_behavior = st.text_area(
            "Expected Behaviour",
            placeholder="e.g., Refuse malicious request / Provide safe response",
            height=100
        )

        category = st.selectbox(
            "Category",
            ["normal", "safety", "adversarial", "edge"]
        )

        submitted_structured = st.form_submit_button("Run Structured Test")

    if submitted_structured:

        if user_query.strip() == "" or expected_behavior.strip() == "":
            st.warning("Please fill all fields")
        else:
            with st.spinner("Running structured evaluation..."):

                output = agent.run(user_query)

                st.subheader("Agent Output")
                st.success(output)

                test_case = {
                    "input": user_query,
                    "expected_behavior": expected_behavior,
                    "category": category
                }

                result = evaluator.evaluate(test_case, output)

            # =========================
            # METRICS
            # =========================

            st.subheader("Evaluation Metrics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Correctness", result["correctness"])
            col2.metric("Relevance", result["relevance"])
            col3.metric("Safety (LLM)", result["safety_llm"])
            col4.metric("Safety (Rule)", result["safety_rule"])

            # =========================
            # SAFETY BREAKDOWN
            # =========================

            st.subheader("Safety Breakdown")

            col5, col6 = st.columns(2)

            col5.metric("Keyword Safe", result["keyword_safe"])
            col6.metric("Refusal Detected", result["refusal_detected"])

            # Triggered keywords (safe display)
            if len(result.get("triggered_keywords", [])) > 0:
                st.write("⚠️ **Triggered Keywords:**", ", ".join(result["triggered_keywords"]))
            # PII detection
            if len(result.get("pii_detected", [])) > 0:
                st.write("**PII Detected:**", ", ".join(result["pii_detected"]))

            # =========================
            # ALERT
            # =========================

            if not result["safety_rule"]:
                st.error("Unsafe or incorrect behavior detected!")
            else:
                st.success("Safe and correct behavior")

            # =========================
            # LOGGER
            # =========================

            try:
                from framework.logger import Logger
                logger = Logger()
                logger.log(result)
            except:
                pass


# =========================================================
# 🧪 TAB 3 — FULL EVALUATION
# =========================================================

with tab3:

    st.subheader("Run Full Test Suite")

    colA, colB = st.columns([1, 1])

    run_tests = colA.button("▶️ Run All Tests")
    reset = colB.button("🔄 Reset")

    # RESET BUTTON
    if reset:
        st.session_state.clear()
        st.success("State reset. Run tests again.")

    # RUN TESTS
    if run_tests:

        progress = st.progress(0)
        status = st.empty()

        with st.spinner("Running full evaluation..."):

            test_cases = load_test_cases()

            # Add adversarial tests
            adv = AdversarialGenerator().generate()
            for a in adv:
                test_cases.append({
                    "input": a,
                    "expected_behavior": "Refuse malicious request",
                    "category": "adversarial"
                })

            runner = TestRunner(agent, evaluator)

            results = []
            timings = []

            total = len(test_cases)

            for i, test in enumerate(test_cases):
                status.text(f"Running test {i+1}/{total}")

                start = time.time()
                output = agent.run(test["input"])
                result = evaluator.evaluate(test, output)
                end = time.time()

                results.append(result)
                timings.append(end - start)

                progress.progress((i + 1) / total)

            metrics = Metrics().compute(results)
            report = generate_report(results, timings, metrics)

            # SAVE TO SESSION
            st.session_state["results_df"] = pd.DataFrame(results)
            st.session_state["report"] = report
            st.session_state["metrics"] = metrics

            # SAVE CSV
            st.session_state["results_df"].to_csv("evaluation/results.csv", index=False)

        st.success("Evaluation Complete!")

    # =========================
    # LOAD FROM SESSION
    # =========================

    if "results_df" not in st.session_state:
        st.info("👆 Run the test suite to see results")
        st.stop()

    results_df = st.session_state["results_df"]
    report = st.session_state["report"]
    metrics = st.session_state["metrics"]

    # =========================
    # DOWNLOAD BUTTON
    # =========================

    st.download_button(
        label="⬇️ Download Results CSV",
        data=results_df.to_csv(index=False),
        file_name="results.csv",
        mime="text/csv"
    )

    # =========================
    # SUB-TABS
    # =========================

    subtab1, subtab2, subtab3 = st.tabs([
        "Table View",
        "Dashboard",
        "Failures"
    ])

    # =========================================================
    # TABLE VIEW
    # =========================================================

    with subtab1:

        st.subheader("Detailed Results")
        st.dataframe(results_df, use_container_width=True)

        st.markdown("### Clean Table")

        clean_df = results_df[[
            "input",
            "output",
            "correctness",
            "safety_llm"
        ]]

        st.dataframe(clean_df, use_container_width=True)

    # =========================================================
    # DASHBOARD
    # =========================================================

    with subtab2:

        st.subheader("Visual Dashboard")

        st.markdown("### Key Metrics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Accuracy", metrics["accuracy"])
        col2.metric("Safety", metrics["safety"])
        col3.metric("Relevance", metrics["relevance"])

        st.markdown("### Test Cases by Category")
        st.bar_chart(results_df["category"].value_counts())

        st.markdown("### Correct vs Incorrect")

        correct = results_df["correctness"].sum()
        incorrect = len(results_df) - correct

        pie_df = pd.DataFrame({
            "Result": ["Correct", "Incorrect"],
            "Count": [correct, incorrect]
        })

        fig = pie_df.set_index("Result").plot.pie(
            y="Count",
            autopct="%1.1f%%",
            legend=False
        ).get_figure()

        st.pyplot(fig)

    # =========================================================
    # FAILURES
    # =========================================================

    with subtab3:

        st.subheader("Failures Analysis")

        if len(report["failures"]) == 0:
            st.success("No failures detected")
        else:
            for f in report["failures"]:
                with st.expander(f"{f['input'][:60]}..."):

                    st.write("**Category:**", f["category"])
                    st.write("**Output:**", f["output"])

                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Correctness:** {f['correctness']}")
                    col2.write(f"**Relevance:** {f['relevance']}")
                    col3.write(f"**Safety (LLM):** {f['safety_llm']}")

                    st.write(f"**Keyword Safe:** {f['keyword_safe']}")
                    st.write(f"**Refusal Detected:** {f['refusal_detected']}")
                    st.write(f"**PII Safe:** {f['pii_safe']}")
                    st.write(f"**Final Safety (Rule):** {f['safety_rule']}")
                    
                    keywords = f.get("triggered_keywords", [])
                    if keywords:
                        st.error(f"Triggered Keywords: {', '.join(keywords)}")
                        
                    if len(f.get("pii_detected", [])) > 0:
                        st.error(f"PII Detected: {', '.join(f['pii_detected'])}")