from config.config import (
    FONT_BODY, FONT_BODY_BOLD, FONT_HEADER, FONT_SMALL_ITALIC,
    COLOR_BG, COLOR_PRIMARY, COLOR_ACCENT, COLOR_SURFACE, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    COLOR_DANGER, PAD_SMALL, PAD_MEDIUM, PAD_LARGE, FONT_TITLE_MAIN, FONT_TITLE_SUB
)

def setup_styles(style):
    """Configures all custom styles based on config.py"""

    # General Labels
    style.configure(".", font=FONT_BODY, background=COLOR_BG, foreground=COLOR_TEXT_MAIN)
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MAIN)

    # Headings
    style.configure("Title.TLabel", font=FONT_TITLE_MAIN, foreground=COLOR_PRIMARY)
    style.configure("SubTitle.TLabel", font=FONT_TITLE_SUB, foreground=COLOR_TEXT_MAIN)
    style.configure("Muted.TLabel", font=FONT_SMALL_ITALIC, foreground=COLOR_TEXT_MUTED)

    # Siderbar
    style.configure(
        "Sidebar.TButton",
        font=FONT_BODY,
        anchor="w",
        padding=(PAD_MEDIUM, PAD_SMALL),
        background=COLOR_SURFACE,
        foreground=COLOR_TEXT_MAIN
        )


    style.configure(
        "SidebarActive.TButton",
        font=FONT_BODY_BOLD,
        anchor="w",
        padding=(PAD_MEDIUM, PAD_SMALL),
        background=COLOR_ACCENT,
        foreground=COLOR_PRIMARY
        )

    # Buttons
    style.configure("TButton", font=FONT_BODY, padding=(PAD_MEDIUM, PAD_SMALL))
    style.configure("Accent.TButton", font=FONT_BODY_BOLD) # sv_ttk handles blue color usually
    style.configure("Danger.TButton", foreground=COLOR_DANGER)
    # Quick Action Buttons
    style.configure("Quick.TButton", font=FONT_BODY_BOLD)

    # Frames
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_SURFACE, relief="solid", borderwidth=1)
    style.configure("Outer.TFrame", background=COLOR_ACCENT, relief="flat", borderwidth=1)

    # Label Frames
    style.configure("TLabelframe", background=COLOR_BG, padding=PAD_MEDIUM)
    style.configure("TLabelframe.Label", font=FONT_HEADER, foreground=COLOR_PRIMARY, background=COLOR_BG)
    
    # Treeview 
    # style.configure("Dashboard.Treeview", rowheight=36, font=FONT_BODY)

    style.configure(
        "App.Treeview",
        font=FONT_BODY,
        rowheight=40,
        background=COLOR_SURFACE,
        fieldbackground=COLOR_SURFACE,
        borderwidth=0
    )

    style.configure(
        "App.Treeview.Heading",
        font=FONT_HEADER,
        background=COLOR_BG,
        foreground=COLOR_TEXT_MAIN,
        padding=(PAD_SMALL, PAD_MEDIUM)
    )

    style.map(
        "App.Treeview",
        background=[("selected", COLOR_ACCENT)],
        foreground=[("selected", COLOR_PRIMARY)]
    )


    # style.configure("Treeview", 
    #                     font=FONT_BODY, 
    #                     rowheight=40, # More space for touch/ease
    #                     background=COLOR_SURFACE,
    #                     fieldbackground=COLOR_SURFACE,
    #                     borderwidth=0)

    # style.configure("Treeview.Heading", 
    #                     font=FONT_HEADER, 
    #                     background=COLOR_BG, 
    #                     foreground=COLOR_TEXT_MAIN,
    #                     padding=(PAD_SMALL, PAD_MEDIUM))

    # style.map("Treeview", 
    #             background=[("selected", COLOR_ACCENT)], 
    #             foreground=[("selected", COLOR_PRIMARY)])
