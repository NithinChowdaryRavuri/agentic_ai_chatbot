from function_calling.function_registry import FunctionRegistry

class FunctionDescription:
    # --- Tool Descriptions for Prompting ---
    # Generate the descriptions dynamically from the registry for the prompt
    function_registry = FunctionRegistry()
    TOOL_REGISTRY = function_registry.tool_registry()

    try:
        TOOL_DESCRIPTIONS = "\n".join([
            f"""- Function Name: {name}
        Description: {func.__doc__.strip()}"""
            for name, func in TOOL_REGISTRY.items()
        ])

    except:
        import traceback
        traceback.print_exc()