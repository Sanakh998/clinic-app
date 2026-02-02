
def center_window(window, parent):
    """Centers a popup window relative to the parent window."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    
    # Calculate position relative to parent
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    
    x = parent_x + (parent_w // 2) - (width // 2)
    y = parent_y + (parent_h // 2) - (height // 2)
    
    # Ensure it doesn't go off screen
    if x < 0: x = 0
    if y < 0: y = 0
    
    window.geometry(f"+{x}+{y}")


# Entry Field with Placeholder
