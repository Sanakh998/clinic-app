from config.config import (
    FONT_BODY, FONT_BODY_BOLD, FONT_HEADER, FONT_SMALL_ITALIC,
    COLOR_BG, COLOR_PRIMARY, COLOR_ACCENT, COLOR_SURFACE,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER,
    PAD_SMALL, PAD_MEDIUM, PAD_LARGE,
    FONT_TITLE_MAIN, FONT_TITLE_SUB
)

def setup_styles(style):
    """Global ttk styles for Clinic Manager App"""

    # -----------------------------
    # Base / Global
    # -----------------------------
    style.configure(
        ".",
        font=FONT_BODY,
        background=COLOR_BG,
        foreground=COLOR_TEXT_MAIN
    )

    style.configure(
        "TLabel",
        background=COLOR_BG,
        foreground=COLOR_TEXT_MAIN
    )

    # -----------------------------
    # Headings
    # -----------------------------
    style.configure(
        "Title.TLabel",
        font=FONT_TITLE_MAIN,
        foreground=COLOR_PRIMARY,
        background=COLOR_BG
    )

    style.configure(
        "SubTitle.TLabel",
        font=FONT_TITLE_SUB,
        foreground=COLOR_TEXT_MAIN,
        background=COLOR_BG
    )

    style.configure(
        "Muted.TLabel",
        font=FONT_SMALL_ITALIC,
        foreground=COLOR_TEXT_MUTED,
        background=COLOR_BG
    )

    # -----------------------------
    # Sidebar Buttons
    # -----------------------------
    # Sidebar Frame
    style.configure(
        "Sidebar.TFrame",
        background=COLOR_SURFACE
    )

    # Sidebar Button
    style.configure(
        "Sidebar.TButton",
        font=FONT_BODY,
        anchor="w",
        padding=(15, 10),
        background=COLOR_SURFACE,
        foreground=COLOR_TEXT_MAIN,
        borderwidth=0
    )

    style.map(
        "Sidebar.TButton",
        background=[("active", COLOR_ACCENT)]
    )

    # Active Sidebar Button
    style.configure(
        "SidebarActive.TButton",
        font=FONT_BODY_BOLD,
        anchor="w",
        padding=(15, 10),
        background=COLOR_ACCENT,
        foreground=COLOR_PRIMARY,
        borderwidth=0
    )

    # Sidebar Hover
    style.configure(
        "SidebarHover.TButton",
        font=FONT_BODY,
        anchor="w",
        padding=(15, 10),
        background=COLOR_ACCENT,
        foreground=COLOR_TEXT_MAIN,
        borderwidth=0
    )



    # -----------------------------
    # Buttons
    # -----------------------------
    style.configure(
        "TButton",
        font=FONT_BODY,
        padding=(PAD_MEDIUM, PAD_SMALL)
    )

    style.configure(
        "Accent.TButton",
        font=FONT_BODY_BOLD
    )

    style.configure(
        "Danger.TButton",
        foreground=COLOR_DANGER
    )

    style.configure(
        "Quick.TButton",
        font=FONT_BODY_BOLD
    )

    # -----------------------------
    # Frames
    # -----------------------------
    style.configure(
        "TFrame",
        background=COLOR_BG
    )

    style.configure(
        "Card.TFrame",
        background=COLOR_SURFACE,
        relief="solid",
        borderwidth=1
    )

    style.configure(
        "Outer.TFrame",
        background=COLOR_ACCENT,
        relief="flat",
        borderwidth=0
    )

    # -----------------------------
    # Label Frames
    # -----------------------------
    style.configure(
        "TLabelframe",
        background=COLOR_BG,
        padding=PAD_MEDIUM
    )

    style.configure(
        "TLabelframe.Label",
        font=FONT_HEADER,
        foreground=COLOR_PRIMARY,
        background=COLOR_BG
    )

    # -----------------------------
    # Treeview (Tables)
    # -----------------------------
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
