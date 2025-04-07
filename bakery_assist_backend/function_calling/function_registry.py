from function_calling.function_declaration import FunctionDeclaration

class FunctionRegistry:
    def __init__(self):
        self.function_declaration = FunctionDeclaration()

    # --- Tool Registry ---
    # Maps tool names (as the LLM should use them) to the actual Python functions
    def tool_registry(self):
        TOOL_REGISTRY = {
            "get_customer_invoices": FunctionDeclaration.get_customer_invoices_from_db,
        }

        return TOOL_REGISTRY