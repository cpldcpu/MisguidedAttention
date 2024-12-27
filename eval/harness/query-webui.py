import streamlit as st
import json
from datetime import datetime
import os
from jsonschema import validate, ValidationError

# Set the page config to use the entire width
st.set_page_config(page_title="Query Response Collector", layout="wide")

# Schema for validation
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["prompt_id", "prompt", "llm", "output", "timestamp"],
                "properties": {
                    "prompt_id": {"type": "string"},
                    "prompt": {"type": "string"},
                    "llm": {"type": "string"},
                    "output": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "timestamp": {"type": "string"}
                }
            }
        }
    }
}

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"results": []}

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_default_dataset():
    try:
        with open("misguided_attention.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Default dataset file 'misguided_attention.json' not found!")
        return {"prompts": []}

def main():
    st.title("Query Response Collector")

    # Initialize session state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {"results": []}
    if 'dataset' not in st.session_state:
        st.session_state.dataset = load_default_dataset()
    if 'selected_attempts' not in st.session_state:
        # Default to 3 attempts when no file is loaded
        st.session_state.selected_attempts = 3

    # File operations with validation
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Load responses JSON", type=['json'])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                validate(instance=data, schema=RESPONSE_SCHEMA)
                st.session_state.responses = data
                st.success("Responses loaded and validated successfully!")
                # Reset to first question (remove st.experimental_rerun call)
                st.session_state.current_question = 0
                # ...removed st.experimental_rerun()...
            except ValidationError as e:
                st.error(f"Invalid response format: {str(e)}")
            except json.JSONDecodeError:
                st.error("Invalid JSON file")

    with col2:
        if st.button("Save responses"):
            try:
                validate(instance=st.session_state.responses, schema=RESPONSE_SCHEMA)
                save_json(st.session_state.responses, "output_queries.json")
                st.success("Responses validated and saved successfully!")
            except ValidationError as e:
                st.error(f"Invalid response format: {str(e)}")
            except Exception as e:
                st.error(f"Error saving responses: {str(e)}")

    # Attempt selection
    st.subheader("Response Configuration")
    st.session_state.selected_attempts = st.number_input(
        "Number of attempts", 
        min_value=1, 
        max_value=5, 
        value=st.session_state.selected_attempts
    )

    # Question navigation
    st.subheader("Question Navigation")
    total_prompts = len(st.session_state.dataset['prompts'])


    col1, col3 = st.columns(2)
    with col1:
        if st.button("Previous") and st.session_state.current_question > 0:
            st.session_state.current_question -= 1
    with col3:
        if st.button("Next") and st.session_state.current_question < total_prompts - 1:
            st.session_state.current_question += 1

    # Display current question
    current_prompt = st.session_state.dataset['prompts'][st.session_state.current_question]
    st.text(f"ID: {current_prompt['prompt_id']} ({st.session_state.current_question + 1} of {total_prompts})")
    
    # Prompt display with copy button and black text
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.text_area(
            "Prompt",
            current_prompt['prompt'],
            height=100,
            disabled=True,
            key="prompt_text",
            help="Click copy button to copy text",
            # Using custom CSS to make text black
            label_visibility="visible"
        )
    with col2:
        if st.button("📋", help="Copy prompt to clipboard"):
            st.write(f'<script>navigator.clipboard.writeText("{current_prompt["prompt"]}");</script>', unsafe_allow_html=True)
            st.success("Copied!")

    # Find or create result entry with correct number of attempts
    result_entry = None
    for result in st.session_state.responses["results"]:
        if result["prompt_id"] == current_prompt["prompt_id"]:
            result_entry = result
            break
    
    if result_entry is None:
        result_entry = {
            "prompt_id": current_prompt["prompt_id"],
            "prompt": current_prompt["prompt"],
            "llm": "manual",
            "output": ["" for _ in range(st.session_state.selected_attempts)],
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.responses["results"].append(result_entry)
    
    # Ensure output array matches selected attempts
    while len(result_entry["output"]) < st.session_state.selected_attempts:
        result_entry["output"].append("")
    while len(result_entry["output"]) > st.session_state.selected_attempts:
        result_entry["output"].pop()

    # Display and edit responses
    st.subheader("Responses")
    for i, response in enumerate(result_entry["output"]):
        widget_key = f"resp_{current_prompt['prompt_id']}_{i}"
        new_response = st.text_area(
            f"Attempt {i+1}",
            value=response,
            height=150,
            key=widget_key,
            label_visibility="visible"
        )
        if new_response != result_entry["output"][i]:
            result_entry["output"][i] = new_response
            result_entry["timestamp"] = datetime.now().isoformat()

if __name__ == "__main__":
    main()
