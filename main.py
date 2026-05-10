import customtkinter as ctk
import tkinter as tk
import os
import sys

# Deve ser chamado antes de qualquer widget CTk ser instanciado
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

MATRIX_SIZE: int = 8

COLOR_ACTIVE: tuple[str, str] = ("#3584e4", "#3584e4")
COLOR_INACTIVE: tuple[str, str] = ("#E0E0E0", "#2b2b2b")
COLOR_HOVER_INACTIVE: tuple[str, str] = ("#D0D0D0", "#3b3b3b")


class LEDMatrixGeneratorApp(ctk.CTk):
    """
    Main application class for the LED Matrix Code Generator.
    Generates MikroBasic byte array code from a graphical grid.
    Supports click-and-drag painting, rotation, invert, clear and copy.
    """

    def __init__(self) -> None:
        super().__init__()

        # --- Window Configuration ---
        self.title("LED Matrix Code Generator")
        self.geometry("650x780")
        self.minsize(550, 720)

        self._setup_window_icon()

        # --- Internal State ---
        self.pixel_buffer: list[list[bool]] = [
            [False] * MATRIX_SIZE for _ in range(MATRIX_SIZE)
        ]
        self.button_grid: list[list[ctk.CTkButton]] = []
        # Controla o modo de pintura durante o arraste (True = ativar, False = desativar)
        self._drag_paint_mode: bool = True

        # --- Layout Management ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._initialize_matrix_ui()
        self._initialize_control_panel_ui()
        self.generate_code_output()

    # ------------------------------------------------------------------ #
    #  Setup                                                               #
    # ------------------------------------------------------------------ #

    def _setup_window_icon(self) -> None:
        """Sets the window icon, handling paths for both script and bundled executable."""
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")

            icon_path = os.path.join(base_path, "resources", "icon.png")

            if os.path.exists(icon_path):
                # Armazena referência para evitar garbage collection
                self._icon_image = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, self._icon_image)
        except Exception:
            pass  # Silencioso se o ícone falhar em ambientes de teste

    # ------------------------------------------------------------------ #
    #  UI Initialization                                                   #
    # ------------------------------------------------------------------ #

    def _initialize_matrix_ui(self) -> None:
        """Initializes the responsive NxN grid of toggleable buttons."""
        self.wrapper_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.wrapper_frame.grid_rowconfigure(0, weight=1)
        self.wrapper_frame.grid_columnconfigure(0, weight=1)

        self.grid_container = ctk.CTkFrame(self.wrapper_frame, fg_color="transparent")
        self.grid_container.grid(row=0, column=0)

        for row_index in range(MATRIX_SIZE):
            button_row: list[ctk.CTkButton] = []
            for col_index in range(MATRIX_SIZE):
                btn = ctk.CTkButton(
                    self.grid_container,
                    text="",
                    width=45, height=45,
                    fg_color=COLOR_INACTIVE,
                    hover_color=COLOR_HOVER_INACTIVE,
                    corner_radius=8,
                    command=lambda r=row_index, c=col_index: self.toggle_pixel(r, c)
                )
                btn.grid(row=row_index, column=col_index, padx=2, pady=2)

                # Suporte a click-and-drag para pintura contínua
                btn.bind("<ButtonPress-1>",
                         lambda e, r=row_index, c=col_index: self._on_drag_start(r, c))
                btn.bind("<B1-Motion>",
                         lambda e: self._on_drag_motion(e))

                button_row.append(btn)
            self.button_grid.append(button_row)

    def _initialize_control_panel_ui(self) -> None:
        """Initializes the lower panel with inputs, action buttons and code output."""
        self.control_panel = ctk.CTkFrame(self, corner_radius=15)
        self.control_panel.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.control_panel.grid_columnconfigure(1, weight=1)

        # --- Row 0: Constant name + Rotate buttons ---
        self.lbl_constant_name = ctk.CTkLabel(
            self.control_panel, text="Constant Name:", font=("Roboto", 14, "bold")
        )
        self.lbl_constant_name.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.entry_constant_name = ctk.CTkEntry(
            self.control_panel, font=("Roboto", 14), corner_radius=8
        )
        self.entry_constant_name.insert(0, "CUSTOM")
        self.entry_constant_name.grid(row=0, column=1, padx=(0, 10), pady=(15, 5), sticky="ew")
        self.entry_constant_name.bind("<KeyRelease>", self.generate_code_output)

        btn_frame_rotate = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        btn_frame_rotate.grid(row=0, column=2, padx=(0, 15), pady=(15, 5))

        self.btn_rotate_ccw = ctk.CTkButton(
            btn_frame_rotate, text="↺ -90°", font=("Roboto", 13, "bold"),
            fg_color=("#1565C0", "#0D47A1"), hover_color=("#1976D2", "#1565C0"),
            corner_radius=8, width=75,
            command=self.rotate_matrix_counter_clockwise
        )
        self.btn_rotate_ccw.grid(row=0, column=0, padx=(0, 5))

        self.btn_rotate_cw = ctk.CTkButton(
            btn_frame_rotate, text="+90° ↻", font=("Roboto", 13, "bold"),
            fg_color=("#388E3C", "#2E7D32"), hover_color=("#4CAF50", "#1B5E20"),
            corner_radius=8, width=75,
            command=self.rotate_matrix_clockwise
        )
        self.btn_rotate_cw.grid(row=0, column=1)

        # --- Row 1: Action buttons (Invert, Clear, Copy) ---
        btn_frame_actions = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        btn_frame_actions.grid(row=1, column=0, columnspan=3, padx=15, pady=(5, 5), sticky="ew")
        btn_frame_actions.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_invert = ctk.CTkButton(
            btn_frame_actions, text="⬛ Invert", font=("Roboto", 13, "bold"),
            fg_color=("#7B1FA2", "#6A1B9A"), hover_color=("#9C27B0", "#7B1FA2"),
            corner_radius=8,
            command=self.invert_matrix
        )
        self.btn_invert.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_clear = ctk.CTkButton(
            btn_frame_actions, text="🗑 Clear", font=("Roboto", 13, "bold"),
            fg_color=("#C62828", "#B71C1C"), hover_color=("#E53935", "#C62828"),
            corner_radius=8,
            command=self.clear_matrix
        )
        self.btn_clear.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_copy = ctk.CTkButton(
            btn_frame_actions, text="📋 Copy", font=("Roboto", 13, "bold"),
            fg_color=("#F57C00", "#E65100"), hover_color=("#FB8C00", "#F57C00"),
            corner_radius=8,
            command=self.copy_code_to_clipboard
        )
        self.btn_copy.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # --- Row 2: Code output ---
        self.txt_code_output = ctk.CTkTextbox(
            self.control_panel, height=80, font=("Consolas", 14), corner_radius=8
        )
        self.txt_code_output.grid(
            row=2, column=0, columnspan=3, padx=15, pady=(5, 10), sticky="ew"
        )

        # --- Row 3: Credits ---
        self.lbl_credits = ctk.CTkLabel(
            self.control_panel,
            text="Ícone via game-icons.net (Lorc) - Licença CC BY 3.0",
            font=("Roboto", 10), text_color="gray"
        )
        self.lbl_credits.grid(row=3, column=0, columnspan=3, pady=(0, 10))

    # ------------------------------------------------------------------ #
    #  Drag-to-paint                                                       #
    # ------------------------------------------------------------------ #

    def _on_drag_start(self, row: int, col: int) -> None:
        """Define o modo de pintura com base no estado atual do pixel clicado."""
        # Se o pixel está inativo, o arraste vai ativar; se ativo, vai desativar.
        self._drag_paint_mode = not self.pixel_buffer[row][col]

    def _on_drag_motion(self, event: tk.Event) -> None:
        """Pinta o pixel sob o cursor durante o arraste."""
        widget = event.widget.winfo_containing(
            event.widget.winfo_rootx() + event.x,
            event.widget.winfo_rooty() + event.y,
        )
        for row in range(MATRIX_SIZE):
            for col in range(MATRIX_SIZE):
                if self.button_grid[row][col] == widget:
                    if self.pixel_buffer[row][col] != self._drag_paint_mode:
                        self.pixel_buffer[row][col] = self._drag_paint_mode
                        self._update_pixel_ui(row, col)
                        self.generate_code_output()
                    return

    # ------------------------------------------------------------------ #
    #  Matrix Operations                                                   #
    # ------------------------------------------------------------------ #

    def toggle_pixel(self, row: int, col: int) -> None:
        """Alterna o estado de um único pixel e atualiza apenas ele na UI."""
        self.pixel_buffer[row][col] = not self.pixel_buffer[row][col]
        self._update_pixel_ui(row, col)
        self.generate_code_output()

    def rotate_matrix_clockwise(self) -> None:
        """Rotaciona a matriz 90° no sentido horário."""
        self.pixel_buffer = [list(row) for row in zip(*self.pixel_buffer[::-1])]
        self._update_all_pixels_ui()
        self.generate_code_output()

    def rotate_matrix_counter_clockwise(self) -> None:
        """Rotaciona a matriz 90° no sentido anti-horário."""
        self.pixel_buffer = [list(row) for row in zip(*self.pixel_buffer)][::-1]
        self._update_all_pixels_ui()
        self.generate_code_output()

    def invert_matrix(self) -> None:
        """Inverte o estado de todos os pixels da matriz."""
        self.pixel_buffer = [
            [not pixel for pixel in row] for row in self.pixel_buffer
        ]
        self._update_all_pixels_ui()
        self.generate_code_output()

    def clear_matrix(self) -> None:
        """Apaga todos os pixels da matriz."""
        self.pixel_buffer = [[False] * MATRIX_SIZE for _ in range(MATRIX_SIZE)]
        self._update_all_pixels_ui()
        self.generate_code_output()

    def copy_code_to_clipboard(self) -> None:
        """Copia o código gerado para a área de transferência com feedback visual."""
        code = self.txt_code_output.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(code)

        # Feedback visual temporário no botão
        self.btn_copy.configure(text="✅ Copiado!", fg_color=("#2E7D32", "#1B5E20"))
        self.after(1500, self._reset_copy_button)

    def _reset_copy_button(self) -> None:
        self.btn_copy.configure(text="📋 Copy", fg_color=("#F57C00", "#E65100"))

    # ------------------------------------------------------------------ #
    #  UI Update                                                           #
    # ------------------------------------------------------------------ #

    def _update_pixel_ui(self, row: int, col: int) -> None:
        """Atualiza visualmente apenas um pixel específico — O(1) ao invés de O(n²)."""
        is_active = self.pixel_buffer[row][col]
        self.button_grid[row][col].configure(
            fg_color=COLOR_ACTIVE if is_active else COLOR_INACTIVE
        )

    def _update_all_pixels_ui(self) -> None:
        """Atualiza todos os pixels da grade (usado após operações em massa)."""
        for row in range(MATRIX_SIZE):
            for col in range(MATRIX_SIZE):
                self._update_pixel_ui(row, col)

    # ------------------------------------------------------------------ #
    #  Code Generation                                                     #
    # ------------------------------------------------------------------ #

    def generate_code_output(self, event: tk.Event | None = None) -> None:
        """Gera e exibe o código MikroBasic correspondente ao estado atual da grade."""
        byte_lines = [
            f"%{''.join('1' if self.pixel_buffer[r][c] else '0' for c in range(MATRIX_SIZE))}"
            for r in range(MATRIX_SIZE)
        ]
        constant_name = self.entry_constant_name.get().strip() or "NEW_CHAR"
        compiled_code = f"const {constant_name} as byte[{MATRIX_SIZE}] = ({','.join(byte_lines)})"

        self.txt_code_output.delete("1.0", "end")
        self.txt_code_output.insert("1.0", compiled_code)


if __name__ == "__main__":
    app = LEDMatrixGeneratorApp()
    app.mainloop()