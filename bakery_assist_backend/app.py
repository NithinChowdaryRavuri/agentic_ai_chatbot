from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import re
from helpers.customer_helper import CustomerHelper
from helpers.customer_verification import CustomerVerificationHelper
from templates.prompt import SYSTEM_PROMPT_TEMPLATE, TOOL_DESCRIPTIONS_TEXT, RESPONSE_PROMPT_TEMPLATE
from helpers.ollama_helper import call_ollama, parse_function_call
from function_calling.function_registry import FunctionRegistry


# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)
function_registry = FunctionRegistry()
TOOL_REGISTRY = function_registry.tool_registry()


# --- Routes ---

@app.route('/')
def home():
    """Serves the default home page."""
    return "Welcome to Bake Assist chatbot"

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Fetches and returns a list of key customer details."""
    customer_helper = CustomerHelper()
    customers = customer_helper.get_all_customers()

    if customers is None:
        return jsonify({"error": "Failed to retrieve customer data"}), 500
    elif not customers:
        return jsonify([]), 200
    else:
        return jsonify(customers), 200
    
@app.route('/api/chat', methods=['POST'])
def chat_handler():
    """Handles incoming chat messages for a specific customer."""
    try:
        # 1. Get data from request
        customer_number = request.args.get('customer_number') # Get from query param
        
        # Check if customer_number is provided
        if not customer_number:
            return jsonify({"error": "Missing 'customer_number' query parameter"}), 400
        
        #1. Check if customer_number is valid
        customer_verification_helper = CustomerVerificationHelper()
        if not customer_verification_helper.is_valid_customer(customer_number):
            return jsonify({"error": "Invalid 'customer_number'"}), 400
        

        # Get message from JSON body
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in JSON body"}), 400
        user_message = data['message']

        # 2. First LLM Call (Check for Tool Use)
        # Provide BOTH placeholders expected by the template string
        initial_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            TOOL_DESCRIPTIONS=TOOL_DESCRIPTIONS_TEXT,
            customer_number=customer_number
        ) + f"\n\nUser Query: {user_message}"

        llm_response_content = call_ollama(initial_prompt)
        if llm_response_content is None:
            return jsonify({"error": "Failed to get response from language model"}), 500
        
        # 3. Parse for Function Call
        function_call_data = parse_function_call(llm_response_content)

        print("----function call data------")
        print(function_call_data)
        print("----end function call data------")

        if function_call_data:
            # 4. Execute Function if requested
            tool_name = function_call_data.get("name")
            tool_args = function_call_data.get("arguments", {})

            if tool_name in TOOL_REGISTRY:
                tool_function = TOOL_REGISTRY[tool_name]
                try:
                    # IMPORTANT: Ensure arguments match the function signature.
                    # For simplicity here, we pass the dict. More robust parsing/validation needed for production.
                    # Ensure customer_number from context is used if not provided by LLM or override if needed.
                    #if 'customer_number' not in tool_args:
                    tool_args['customer_number'] = customer_number # Inject if missing
                    
                    # Call the actual Python function associated with the tool name
                    function_result_str = tool_function(**tool_args)
                    print("----function response------")
                    print(function_result_str)
                    print("----end function response------")
                    
                except TypeError as e:
                     print(f"Argument mismatch calling tool {tool_name}: {e}")
                     function_result_str = json.dumps({"error": f"Internal error: Incorrect arguments provided for tool {tool_name}."})
                except Exception as e:
                     print(f"Error executing tool {tool_name}: {e}")
                     function_result_str = json.dumps({"error": f"Error executing tool {tool_name}."})

                # 5. Second LLM Call (Generate Final Response using Tool Result)

                # Step 5a: Format the response-specific part using the template
                response_task_prompt = RESPONSE_PROMPT_TEMPLATE.format(
                    function_result=function_result_str, # Pass the actual result string
                    user_message=user_message           # Pass the original user message
                )

                # Step 5c: Combine system context and the response task
                final_prompt = "" + "\n\n" + response_task_prompt
                # --- END CORRECTION ---


                # Step 5d: Call Ollama with the combined final prompt
                final_llm_response = call_ollama(final_prompt)
                if final_llm_response is None:
                    return jsonify({"error": "Failed to get final response from language model after tool use"}), 500

            else:
                # LLM tried to call a function that doesn't exist
                print(f"Error: LLM requested unknown tool '{tool_name}'")
                bot_reply = f"Sorry, I encountered an issue trying to use an internal tool ('{tool_name}'). Please try rephrasing your request."

        else:
            # 6. No Function Call Needed - Use initial response directly
            bot_reply = "bot ain't working"

        # 7. Clean the final response (remove think block and trim whitespace)
        bot_reply = final_llm_response # Start with the potentially unclean response
        if isinstance(bot_reply, str): # Ensure it's a string before cleaning
            think_pattern = r"<think>.*?</think>"
            # Use re.sub to replace the pattern with an empty string
            # Flags: re.DOTALL to match across newlines, re.IGNORECASE for case-insensitivity
            cleaned_reply = re.sub(think_pattern, "", bot_reply, flags=re.DOTALL | re.IGNORECASE)
            # Strip leading/trailing whitespace that might remain after removal
            bot_reply = cleaned_reply.strip()
        else:
            # Handle cases where the response wasn't a string (e.g., None)
             bot_reply = "Sorry, I encountered an unexpected issue generating a response."
        
        # 7. Return Final Reply
        return jsonify({"reply": bot_reply}), 200
        

    except Exception as e:
        import traceback
        traceback.print_exc()
        # Catch other potential errors like JSON decoding errors, etc.
        print(f"An unexpected error occurred in chat handler: {e}")
        return jsonify({"error": "An unexpected server error occurred"}), 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
