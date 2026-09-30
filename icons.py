"""
icons.py — VMS 3000 full-color toolbar icon painter

Requires:
    Pillow
    tkinter

Font:
    MaterialIcons-Regular.ttf

Place the font in either:
    ./MaterialIcons-Regular.ttf
or:
    ./icons/MaterialIcons-Regular.ttf

Design:
    Every toolbar icon has its own color.

    New          -> Violet
    Open         -> Amber
    Save         -> Green
    Print        -> Slate
    Settings     -> Blue
    Cut          -> Orange
    Copy         -> Indigo
    Paste        -> Teal
    Upload       -> Cyan
    Download     -> Blue
    Refresh      -> Sky
    Security     -> Purple
    Help         -> Blue
    Connection   -> Emerald
    Network      -> Cyan
    Disconnect   -> Red

Supports:
    normal
    hover
    active
    disabled

And connection/status states:
    connected
    connecting
    warning
    error
"""


import os
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageTk


# ============================================================================
# MATERIAL ICON CODEPOINTS
# ============================================================================

_CODEPOINTS: dict[str, str] = {

    # ------------------------------------------------------------------------
    # Files / documents
    # ------------------------------------------------------------------------

    "add":            "\ue145",
    "note_add":       "\ue89c",
    "description":    "\ue873",
    "folder_open":    "\ue2c7",
    "save":           "\ue161",
    "print":          "\ue8ad",

    # ------------------------------------------------------------------------
    # Editing
    # ------------------------------------------------------------------------

    "content_cut":    "\ue14e",
    "content_copy":   "\ue14d",
    "content_paste":  "\ue14f",

    # ------------------------------------------------------------------------
    # Transfer
    # ------------------------------------------------------------------------

    "upload":         "\ue2c6",
    "download":       "\ue2c4",

    # ------------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------------

    "refresh":        "\ue5d5",
    "settings":       "\ue8b8",
    "help":           "\ue887",

    # ------------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------------

    "vpn_key":        "\ue0da",

    # ------------------------------------------------------------------------
    # Network / connection
    # ------------------------------------------------------------------------

    "router":         "\ue328",
    "device_hub":     "\ue335",
    "wifi":           "\ue1e9",
    "link":           "\ue157",
    "link_off":       "\ue157",

    # ------------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------------

    "check":          "\ue5ca",
    "close":          "\ue5cd",
    "warning":        "\ue002",
    "error":          "\ue000",
    "info":           "\ue88e",
}


# ============================================================================
# TOOLBAR ICON MAP
# ============================================================================

_ICON_MAP: dict[str, str] = {

    "new":          "note_add",
    "open":         "folder_open",
    "save":         "save",
    "print":        "print",

    "settings":     "settings",
    "help":         "help",

    "cut":          "content_cut",
    "copy":         "content_copy",
    "paste":        "content_paste",

    "upload":       "upload",
    "download":     "download",

    "refresh":      "refresh",

    "key":          "vpn_key",

    "connection":   "router",
    "network":      "wifi",
    "disconnect":   "link_off",

    "connected":    "check",
    "connecting":   "refresh",
    "warning":      "warning",
    "error":        "error",
    "info":         "info",
}


# ============================================================================
# VMS 3000 UI COLORS
# ============================================================================

# Toolbar background
_DEFAULT_BG = "#F4F6F9"


# ---------------------------------------------------------------------------
# Individual icon colors
# ---------------------------------------------------------------------------

_ICON_COLORS: dict[str, str] = {

    # File / document
    "new":          "#7C3AED",     # Violet
    "open":         "#D97706",     # Amber
    "save":         "#16A34A",     # Green
    "print":        "#475569",     # Slate

    # System
    "settings":     "#2563EB",     # Blue
    "help":         "#0284C7",     # Sky blue
    "refresh":      "#0EA5E9",     # Cyan / sky

    # Editing
    "cut":          "#EA580C",     # Orange
    "copy":         "#4F46E5",     # Indigo
    "paste":        "#0D9488",     # Teal

    # Transfer
    "upload":       "#0891B2",     # Cyan
    "download":     "#2563EB",     # Blue

    # Security
    "key":          "#9333EA",     # Purple

    # Network
    "connection":   "#059669",     # Emerald
    "network":      "#0284C7",     # Sky
    "disconnect":   "#DC2626",     # Red

    # Status
    "connected":    "#16A34A",     # Green
    "connecting":   "#F59E0B",     # Amber
    "warning":      "#F59E0B",     # Amber
    "error":        "#DC2626",     # Red
    "info":         "#2563EB",     # Blue
}


# ---------------------------------------------------------------------------
# State colors
# ---------------------------------------------------------------------------

_HOVER_LIGHTEN = {
    "#7C3AED": "#8B5CF6",
    "#D97706": "#F59E0B",
    "#16A34A": "#22C55E",
    "#475569": "#64748B",
    "#2563EB": "#3B82F6",
    "#0284C7": "#0EA5E9",
    "#0EA5E9": "#38BDF8",
    "#EA580C": "#F97316",
    "#4F46E5": "#6366F1",
    "#0D9488": "#14B8A6",
    "#0891B2": "#06B6D4",
    "#9333EA": "#A855F7",
    "#059669": "#10B981",
    "#DC2626": "#EF4444",
    "#F59E0B": "#FBBF24",
}


_DISABLED_COLOR = "#CBD5E1"

_ACTIVE_COLOR = "#1E40AF"


# ============================================================================
# FONT SEARCH
# ============================================================================

def _find_font(
    size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Search common locations for MaterialIcons-Regular.ttf.
    """

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    candidates = [

        # Same directory
        os.path.join(
            base_dir,
            "MaterialIcons-Regular.ttf",
        ),

        # icons sub-folder
        os.path.join(
            base_dir,
            "icons",
            "MaterialIcons-Regular.ttf",
        ),

        # Current working directory
        "MaterialIcons-Regular.ttf",

        # Windows
        r"C:\Windows\Fonts\MaterialIcons-Regular.ttf",

        # Linux
        "/usr/share/fonts/truetype/material-design-icons/"
        "MaterialIcons-Regular.ttf",

        "/usr/share/fonts/MaterialIcons-Regular.ttf",

        # macOS
        "/Library/Fonts/MaterialIcons-Regular.ttf",

        os.path.expanduser(
            "~/Library/Fonts/MaterialIcons-Regular.ttf"
        ),
    ]

    for path in candidates:

        if not os.path.exists(path):
            continue

        try:

            font = ImageFont.truetype(
                path,
                size,
            )

            print(
                f"[OK] Material Icons font loaded: {path}"
            )

            return font

        except Exception as exc:

            print(
                f"[WARN] Could not load font "
                f"'{path}': {exc}"
            )

    print(
        "[WARN] MaterialIcons-Regular.ttf not found."
    )

    print(
        "       Put MaterialIcons-Regular.ttf "
        "beside icons.py."
    )

    return ImageFont.load_default()


# ============================================================================
# ICON PAINTER
# ============================================================================

class IconPainter:
    """
    Full-color Material Icon renderer for VMS 3000.

    Example:

        icons = IconPainter()

        image = icons.get("save")

        button = tk.Button(
            root,
            image=image,
        )
    """

    # Rendered glyph size
    SZ = 26

    # Transparent-looking padding
    PAD = 3

    def __init__(
        self,
        bg_hex: str = _DEFAULT_BG,
    ):
        self.bg_hex = bg_hex

        self._cache: dict[
            tuple[str, str],
            ImageTk.PhotoImage,
        ] = {}

        self._font = _find_font(
            self.SZ
        )

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def get(
        self,
        name: str,
        state: str = "normal",
    ) -> ImageTk.PhotoImage:
        """
        Return an icon.

        Supported states:

            normal
            hover
            active
            disabled
            connected
            connecting
            warning
            error
            info
        """

        key = (
            name,
            state,
        )

        if key not in self._cache:

            self._cache[key] = self._render(
                name,
                state,
            )

        return self._cache[key]

    # ========================================================================
    # SHORTCUTS
    # ========================================================================

    def normal(
        self,
        name: str,
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "normal",
        )

    def hover(
        self,
        name: str,
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "hover",
        )

    def active(
        self,
        name: str,
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "active",
        )

    def disabled(
        self,
        name: str,
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "disabled",
        )

    def connected(
        self,
        name: str = "connection",
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "connected",
        )

    def connecting(
        self,
        name: str = "connection",
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "connecting",
        )

    def warning(
        self,
        name: str = "connection",
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "warning",
        )

    def error(
        self,
        name: str = "connection",
    ) -> ImageTk.PhotoImage:

        return self.get(
            name,
            "error",
        )

    # ========================================================================
    # RENDER
    # ========================================================================

    def _render(
        self,
        name: str,
        state: str,
    ) -> ImageTk.PhotoImage:

        # --------------------------------------------------------------------
        # Find codepoint
        # --------------------------------------------------------------------

        cp_key = _ICON_MAP.get(
            name
        )

        if cp_key is None:

            print(
                f"[WARN] Unknown icon: {name}"
            )

            cp_key = "error"

        char = _CODEPOINTS.get(
            cp_key,
            _CODEPOINTS["error"],
        )

        # --------------------------------------------------------------------
        # Canvas
        # --------------------------------------------------------------------

        total = (
            self.SZ
            + self.PAD * 2
        )

        img = Image.new(
            "RGB",
            (
                total,
                total,
            ),
            self.bg_hex,
        )

        draw = ImageDraw.Draw(
            img
        )

        # --------------------------------------------------------------------
        # Color
        # --------------------------------------------------------------------

        colour = self._get_colour(
            name,
            state,
        )

        # --------------------------------------------------------------------
        # Draw
        # --------------------------------------------------------------------

        try:

            draw.text(
                (
                    total // 2,
                    total // 2,
                ),
                char,
                font=self._font,
                fill=colour,
                anchor="mm",
            )

            print(
                f"[OK] icon "
                f"[{name}] "
                f"[{state}] "
                f"-> {colour}"
            )

        except Exception as exc:

            print(
                f"[WARN] Failed to render "
                f"[{name}]: {exc}"
            )

            self._draw_fallback(
                draw,
                total,
                colour,
            )

        return ImageTk.PhotoImage(
            img
        )

    # ========================================================================
    # COLOR SELECTION
    # ========================================================================

    def _get_colour(
        self,
        name: str,
        state: str,
    ) -> str:

        state = state.lower().strip()

        # --------------------------------------------------------------------
        # Disabled
        # --------------------------------------------------------------------

        if state == "disabled":
            return _DISABLED_COLOR

        # --------------------------------------------------------------------
        # Connection states
        # --------------------------------------------------------------------

        if state == "connected":
            return "#16A34A"

        if state == "connecting":
            return "#F59E0B"

        if state == "warning":
            return "#F59E0B"

        if state == "error":
            return "#DC2626"

        if state == "info":
            return "#2563EB"

        # --------------------------------------------------------------------
        # Active
        # --------------------------------------------------------------------

        if state == "active":
            return _ACTIVE_COLOR

        # --------------------------------------------------------------------
        # Base icon color
        # --------------------------------------------------------------------

        base_colour = _ICON_COLORS.get(
            name,
            "#475569",
        )

        # --------------------------------------------------------------------
        # Hover
        # --------------------------------------------------------------------

        if state == "hover":

            return _HOVER_LIGHTEN.get(
                base_colour,
                base_colour,
            )

        # --------------------------------------------------------------------
        # Normal
        # --------------------------------------------------------------------

        return base_colour

    # ========================================================================
    # FALLBACK
    # ========================================================================

    def _draw_fallback(
        self,
        draw: ImageDraw.ImageDraw,
        size: int,
        colour: str,
    ) -> None:

        margin = max(
            4,
            size // 4,
        )

        try:

            draw.rounded_rectangle(
                [
                    margin,
                    margin,
                    size - margin,
                    size - margin,
                ],
                radius=5,
                fill=colour,
            )

        except Exception:

            draw.rectangle(
                [
                    margin,
                    margin,
                    size - margin,
                    size - margin,
                ],
                fill=colour,
            )

    # ========================================================================
    # TKINTER FALLBACK
    # ========================================================================

    def _fallback(
        self,
    ) -> tk.PhotoImage:

        size = (
            self.SZ
            + self.PAD * 2
        )

        image = tk.PhotoImage(
            width=size,
            height=size,
        )

        image.put(
            self.bg_hex,
            to=(
                0,
                0,
                size,
                size,
            ),
        )

        margin = size // 4

        for y in range(
            margin,
            size - margin,
        ):

            for x in range(
                margin,
                size - margin,
            ):

                image.put(
                    "#475569",
                    to=(
                        x,
                        y,
                        x + 1,
                        y + 1,
                    ),
                )

        return image


# ============================================================================
# VMS 3000 TOOLBAR ICON COLLECTION
# ============================================================================

class ToolbarIcons:
    """
    Preloads the complete VMS 3000 colorful toolbar.

    Example:

        icons = ToolbarIcons()

        button = tk.Button(
            toolbar,
            image=icons.save,
        )
    """

    def __init__(
        self,
        bg_hex: str = _DEFAULT_BG,
    ):

        self.painter = IconPainter(
            bg_hex=bg_hex,
        )

        # --------------------------------------------------------------------
        # FILE
        # --------------------------------------------------------------------

        self.new = self.painter.get(
            "new"
        )

        self.open = self.painter.get(
            "open"
        )

        self.save = self.painter.get(
            "save"
        )

        self.print = self.painter.get(
            "print"
        )

        # --------------------------------------------------------------------
        # SYSTEM
        # --------------------------------------------------------------------

        self.settings = self.painter.get(
            "settings"
        )

        self.help = self.painter.get(
            "help"
        )

        self.refresh = self.painter.get(
            "refresh"
        )

        # --------------------------------------------------------------------
        # EDITING
        # --------------------------------------------------------------------

        self.cut = self.painter.get(
            "cut"
        )

        self.copy = self.painter.get(
            "copy"
        )

        self.paste = self.painter.get(
            "paste"
        )

        # --------------------------------------------------------------------
        # TRANSFER
        # --------------------------------------------------------------------

        self.upload = self.painter.get(
            "upload"
        )

        self.download = self.painter.get(
            "download"
        )

        # --------------------------------------------------------------------
        # SECURITY
        # --------------------------------------------------------------------

        self.key = self.painter.get(
            "key"
        )

        # --------------------------------------------------------------------
        # NETWORK
        # --------------------------------------------------------------------

        self.connection = self.painter.get(
            "connection"
        )

        self.network = self.painter.get(
            "network"
        )

        self.disconnect = self.painter.get(
            "disconnect"
        )

        # --------------------------------------------------------------------
        # STATUS
        # --------------------------------------------------------------------

        self.connected = self.painter.get(
            "connection",
            "connected",
        )

        self.connecting = self.painter.get(
            "connection",
            "connecting",
        )

        self.warning = self.painter.get(
            "connection",
            "warning",
        )

        self.error = self.painter.get(
            "connection",
            "error",
        )

        self.info = self.painter.get(
            "connection",
            "info",
        )


# ============================================================================
# OPTIONAL COLOR LOOKUP
# ============================================================================

def get_icon_colour(
    name: str,
) -> str:
    """
    Return the normal color assigned to an icon.

    Useful if your toolbar also needs matching
    text/indicator colors.
    """

    return _ICON_COLORS.get(
        name,
        "#475569",
    )


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "VMS 3000 - Icon Preview"
    )

    root.configure(
        bg=_DEFAULT_BG
    )

    icons = IconPainter()

    toolbar = tk.Frame(
        root,
        bg=_DEFAULT_BG,
        padx=12,
        pady=12,
    )

    toolbar.pack(
        fill="x"
    )

    # ------------------------------------------------------------------------
    # Preview icons
    # ------------------------------------------------------------------------

    icon_names = [
        "new",
        "open",
        "save",
        "print",
        "settings",
        "cut",
        "copy",
        "paste",
        "upload",
        "download",
        "refresh",
        "key",
        "connection",
        "network",
        "disconnect",
        "help",
    ]

    for name in icon_names:

        button = tk.Button(
            toolbar,
            image=icons.get(name),
            bg=_DEFAULT_BG,
            activebackground="#E2E8F0",
            relief="flat",
            borderwidth=0,
            padx=5,
            pady=5,
            cursor="hand2",
        )

        button.pack(
            side="left",
            padx=3,
        )

    # ------------------------------------------------------------------------
    # Status preview
    # ------------------------------------------------------------------------

    status_frame = tk.Frame(
        root,
        bg=_DEFAULT_BG,
        padx=12,
        pady=10,
    )

    status_frame.pack(
        fill="x"
    )

    statuses = [
        ("Normal", "connection", "normal"),
        ("Connected", "connection", "connected"),
        ("Connecting", "connection", "connecting"),
        ("Warning", "connection", "warning"),
        ("Error", "connection", "error"),
    ]

    for label, name, state in statuses:

        frame = tk.Frame(
            status_frame,
            bg=_DEFAULT_BG,
        )

        frame.pack(
            side="left",
            padx=8,
        )

        image = icons.get(
            name,
            state,
        )

        icon_label = tk.Label(
            frame,
            image=image,
            bg=_DEFAULT_BG,
        )

        icon_label.pack()

        text_label = tk.Label(
            frame,
            text=label,
            bg=_DEFAULT_BG,
            fg="#475569",
            font=(
                "Segoe UI",
                9,
            ),
        )

        text_label.pack()

    # ------------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------------

    root.mainloop()
