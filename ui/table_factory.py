from tkinter import ttk
from utils.scrollable_frame import ScrollableFrame
from config.config import COLOR_BG, COLOR_SURFACE

def create_table(parent, columns, column_config, scrollbar=True):
    if scrollbar:
        wrapper = ScrollableFrame(parent)
        params_parent = wrapper.scrollable_frame
    else:
        wrapper = ttk.Frame(parent)
        params_parent = wrapper
        
    wrapper.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        params_parent,
        columns=columns,
        show="headings",
        style="App.Treeview"
    )

    stretch_assigned = False

    for col in columns:
        cfg = column_config.get(col, {})

        stretch = cfg.get("stretch", False)

        # 👇 ensure at least ONE column stretches
        if stretch and not stretch_assigned:
            stretch_assigned = True
        else:
            stretch = False

        tree.heading(col, text=col)
        tree.column(
            col,
            width=cfg.get("width", 120),
            anchor=cfg.get("anchor", "w"),
            stretch=stretch
        )

    # fallback: last column stretches
    if not stretch_assigned and columns:
        tree.column(columns[-1], stretch=True)

    tree.pack(fill="both", expand=True)

    tree.tag_configure("odd", background=COLOR_BG)
    tree.tag_configure("even", background=COLOR_SURFACE)

    return tree
