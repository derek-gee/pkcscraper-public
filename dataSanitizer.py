# Function to sanitize Excel data
def sanitize_excel_input(value):
    """Prevents formula injection by prefixing potential Excel formulas with a single quote."""
    return f"'{value}" if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value
