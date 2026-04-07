import streamlit as st
import pandas as pd
import time
import plotly.express as px

from framework.agent import ChatAgent
from framework.evaluator import Evaluator
from framework.runner import TestRunner
from framework.metrics import Metrics
from framework.report import generate_report
from framework.utils import load_test_cases
from framework.adversarial import AdversarialGenerator
from framework.logger import Logger
from framework.google_logger import GoogleLogger
from schemas import TestCase, EvaluationResult


st.set_page_config(page_title="Agent Testing Framework", layout="wide")

st.title("Agent Testing Framework")

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
            try:
                with st.spinner("Running agent..."):

                    validated_test = TestCase(
                        input=user_input,
                        expected_behavior="Respond safely and correctly",
                        category="normal"
                    )

                    output = agent.run(validated_test.input)

                    st.subheader("Agent Output")
                    st.success(output)

                    result = evaluator.evaluate(validated_test.model_dump(), output)

                    validated_result = EvaluationResult(**result)
                    result = validated_result.model_dump()

                    try:
                        logger.log(result)
                        glogger = GoogleLogger()
                        glogger.log(result)
                        st.success("Logged successfully")
                    except Exception as e:
                        st.error(f"Logging failed: {e}")

            except Exception as e:
                st.error(f"Validation/Error: {e}")
                st.stop()
                
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
            # LIVE FACT CHECK
            # =========================

            #st.subheader("Live Fact Check")

            #col7, col8 = st.columns(2)

            #col7.metric("Hallucination (Web)", not result["web_hallucination"])
            #col8.metric("Confidence", result["web_confidence"])

            #if result["web_hallucination"]:
                #st.error(f"⚠️ Possible Hallucination → {result['web_evidence']}")
            #else:
                #st.success(f"Supported → {result['web_evidence']}")

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

                try:
                    validated_test = TestCase(
                        input=user_query,
                        expected_behavior=expected_behavior,
                        category=category
                    )

                    output = agent.run(validated_test.input)

                    st.subheader("Agent Output")
                    st.success(output)

                    result = evaluator.evaluate(validated_test.model_dump(), output)

                    validated_result = EvaluationResult(**result)
                    result = validated_result.model_dump()

                    try:
                        logger.log(result)
                        glogger = GoogleLogger()
                        glogger.log(result)
                        st.success("Logged successfully")
                    except Exception as e:
                        st.error(f"Logging failed: {e}")

                except Exception as e:
                    st.error(f"Validation/Error: {e}")
                    st.stop()

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
# TAB 3 — FULL EVALUATION
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

            test_cases = []

            for case in load_test_cases():
                try:
                    validated = TestCase(**case)
                    test_cases.append(validated.model_dump())
                except Exception:
                    continue

            for a in AdversarialGenerator().generate():
                try:
                    validated = TestCase(
                        input=a,
                        expected_behavior="Refuse malicious request",
                        category="adversarial"
                    )
                    test_cases.append(validated.model_dump())
                except:
                    continue

            runner = TestRunner(agent, evaluator)

            results = []
            timings = []

            total = len(test_cases)

            for i, test in enumerate(test_cases):
                status.text(f"Running test {i+1}/{total}")

                start = time.time()

                try:
                    output = agent.run(test["input"])
                    result = evaluator.evaluate(test, output)
                except Exception as e:
                    result = {
                        "input": test["input"],
                        "output": str(e),
                        "category": test["category"],
                        "correctness": 0,
                        "relevance": 0,
                        "safety_llm": 0,
                        "safety_rule": False,
                        "keyword_safe": False,
                        "triggered_keywords": [],
                        "pii_safe": False,
                        "pii_detected": [],
                        "refusal_detected": False
                    }

                end = time.time()

                results.append(result)
                timings.append(end - start)
                
                try:
                    logger.log(result)
                    glogger = GoogleLogger()
                    glogger.log(result)
                    st.success("Logged successfully")
                except Exception as e:
                    st.error(f"Logging failed: {e}")

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

    # =========================================================
    # INTERACTIVE DASHBOARD
    # =========================================================

    with subtab2:

        import plotly.express as px

        st.subheader("Interactive Dashboard")

        # =========================
        # CATEGORY FILTER
        # =========================

        st.markdown("### Filter by Category")

        categories = ["All"] + sorted(results_df["category"].unique().tolist())
        selected_category = st.selectbox("Select Category", categories)

        if selected_category == "All":
            filtered_df = results_df.copy()
        else:
            filtered_df = results_df[results_df["category"] == selected_category]

        # =========================
        # KPI CARDS
        # =========================

        st.markdown("### Key Metrics")

        #col1, col2, col3, col4, col5 = st.columns(5)
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Correctness", round(filtered_df["correctness"].mean(), 2))
        col2.metric("Relevance", round(filtered_df["relevance"].mean(), 2))
        col3.metric("Safety (LLM)", round(filtered_df["safety_llm"].mean(), 2))
        col4.metric("Safety (Rule)", round(filtered_df["safety_rule"].mean(), 2))
        #col5.metric("Web Safe", round((~filtered_df["web_hallucination"]).mean(), 2))

        # =========================
        # METRIC COMPARISON BAR
        # =========================

        st.markdown("### Metric Comparison")

        comparison_df = pd.DataFrame({
            #"Metric": ["Correctness", "Relevance", "Safety_LLM", "Safety_Rule", "Web_Safe"],
            "Metric": ["Correctness", "Relevance", "Safety_LLM", "Safety_Rule"],
            "Score": [
                filtered_df["correctness"].mean(),
                filtered_df["relevance"].mean(),
                filtered_df["safety_llm"].mean(),
                filtered_df["safety_rule"].mean(),
                #(~filtered_df["web_hallucination"]).mean()
            ]
        })

        st.bar_chart(comparison_df.set_index("Metric"))

        # =========================
        # SAFETY COMPARISON
        # =========================

        st.markdown("### Safety Comparison (LLM vs Rule)")

        safety_compare = pd.DataFrame({
            "LLM Safe": filtered_df["safety_llm"].value_counts(),
            "Rule Safe": filtered_df["safety_rule"].value_counts()
        }).fillna(0)

        st.bar_chart(safety_compare)

        # =========================
        # HALLUCINATION ANALYSIS
        # =========================

        #st.markdown("### Hallucination Analysis")

        #hallucination_compare = pd.DataFrame({
        #    "Relevance (LLM)": filtered_df["relevance"].value_counts(),
        #    "Hallucination check": filtered_df["web_hallucination"].value_counts()
        #}).fillna(0)

        #st.bar_chart(hallucination_compare)

        # =========================
        # CORRECT VS INCORRECT
        # =========================

        st.markdown("### Correct vs Incorrect")

        correct = filtered_df["correctness"].sum()
        incorrect = len(filtered_df) - correct

        pie_df = pd.DataFrame({
            "Result": ["Correct", "Incorrect"],
            "Count": [correct, incorrect]
        })

        st.pyplot(
            pie_df.set_index("Result").plot.pie(
                y="Count",
                autopct="%1.1f%%",
                legend=False
            ).get_figure()
        )

        # =========================
        # SAFETY DISAGREEMENT
        # =========================

        st.markdown("### Safety Disagreement (LLM vs Rule)")

        disagreement_df = filtered_df[
            filtered_df["safety_llm"] != filtered_df["safety_rule"]
        ]

        if len(disagreement_df) == 0:
            st.success("No disagreement between LLM and Rule-based safety")
        else:
            st.warning(f"{len(disagreement_df)} disagreement cases found")
            st.dataframe(disagreement_df, use_container_width=True)


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
                    
                    #st.write("**Web Hallucination:**", f["web_hallucination"])
                    #st.write("**Confidence:**", f["web_confidence"])
                    #st.write("**Evidence:**", f["web_evidence"])
                    
                    keywords = f.get("triggered_keywords", [])
                    if keywords:
                        st.error(f"Triggered Keywords: {', '.join(keywords)}")
                        
                    if len(f.get("pii_detected", [])) > 0:
                        st.error(f"PII Detected: {', '.join(f['pii_detected'])}")
