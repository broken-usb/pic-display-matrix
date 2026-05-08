import customtkinter as ctk
import tkinter as tk
import os
import sys

class LEDMatrixGeneratorApp(ctk.CTk):
    """
    Main application class for the 8x8 LED Matrix Code Generator.
    Generates MikroBasic byte array code from a graphical grid.
    """
    def __init__(self):
        super().__init__()
        
        # --- Window Configuration ---
        self.title("LED Matrix Code Generator")
        self.geometry("650x730")
        self.minsize(550, 680)
        
        # Configuração do ícone da janela (Utiliza o PNG em ambos os sistemas)
        self._setup_window_icon()
        
        # UI Theme configuration
        ctk.set_appearance_mode("System")  
        ctk.set_default_color_theme("blue")
        
        # --- Internal State ---
        self.pixel_buffer = [[False for _ in range(8)] for _ in range(8)]
        self.button_grid = []
        
        # --- Layout Management ---
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_columnconfigure(0, weight=1)
        
        self._initialize_matrix_ui()
        self._initialize_control_panel_ui()
        self.generate_code_output()

    def _setup_window_icon(self):
        """Sets the window icon, handling paths for both script and bundled executable."""
        try:
            # Caminho dinâmico para encontrar o ícone mesmo após o empacotamento
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            
            icon_path = os.path.join(base_path, "resources", "icon.png")
            
            if os.path.exists(icon_path):
                self.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass # Silencioso se o ícone falhar em ambientes de teste

    def _initialize_matrix_ui(self):
        """Initializes the responsive 8x8 grid of toggleable buttons."""
        self.wrapper_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.wrapper_frame.grid_rowconfigure(0, weight=1)
        self.wrapper_frame.grid_columnconfigure(0, weight=1)
        
        self.grid_container = ctk.CTkFrame(self.wrapper_frame, fg_color="transparent")
        self.grid_container.grid(row=0, column=0) 
        
        for row_index in range(8):
            button_row = []
            for col_index in range(8):
                btn_pixel = ctk.CTkButton(
                    self.grid_container, 
                    text="", 
                    width=45, height=45, 
                    fg_color=("#E0E0E0", "#2b2b2b"),
                    hover_color=("#D0D0D0", "#3b3b3b"),
                    corner_radius=8,
                    command=lambda r=row_index, c=col_index: self.toggle_pixel(r, c)
                )
                btn_pixel.grid(row=row_index, column=col_index, padx=2, pady=2)
                button_row.append(btn_pixel)
            self.button_grid.append(button_row)

    def _initialize_control_panel_ui(self):
        """Initializes the lower panel containing inputs, code output, and credits."""
        self.control_panel = ctk.CTkFrame(self, corner_radius=15)
        self.control_panel.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.control_panel.grid_columnconfigure(1, weight=1) 
        
        self.lbl_constant_name = ctk.CTkLabel(self.control_panel, text="Constant Name:", font=("Roboto", 14, "bold"))
        self.lbl_constant_name.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.entry_constant_name = ctk.CTkEntry(self.control_panel, font=("Roboto", 14), corner_radius=8)
        self.entry_constant_name.insert(0, "CUSTOM")
        self.entry_constant_name.grid(row=0, column=1, padx=(0, 15), pady=(15, 5), sticky="ew")
        self.entry_constant_name.bind("<KeyRelease>", self.generate_code_output)
        
        self.btn_rotate_cw = ctk.CTkButton(
            self.control_panel, text="Rotate +90° ↻", font=("Roboto", 13, "bold"),
            fg_color=("#388E3C", "#2E7D32"), hover_color=("#4CAF50", "#1B5E20"),
            corner_radius=8, command=self.rotate_matrix_clockwise
        )
        self.btn_rotate_cw.grid(row=0, column=2, padx=(0, 15), pady=(15, 5))
        
        self.txt_code_output = ctk.CTkTextbox(self.control_panel, height=80, font=("Consolas", 14), corner_radius=8)
        self.txt_code_output.grid(row=1, column=0, columnspan=3, padx=15, pady=(10, 10), sticky="ew")

        self.lbl_credits = ctk.CTkLabel(
            self.control_panel, text="Ícone via game-icons.net (Lorc) - Licença CC BY 3.0", 
            font=("Roboto", 10), text_color="gray"
        )
        self.lbl_credits.grid(row=2, column=0, columnspan=3, pady=(0, 10))

    def toggle_pixel(self, row: int, col: int):
        self.pixel_buffer[row][col] = not self.pixel_buffer[row][col]
        self.update_grid_ui()
        self.generate_code_output()

    def rotate_matrix_clockwise(self):
        transposed_matrix = [[False for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                transposed_matrix[col][7 - row] = self.pixel_buffer[row][col]
        self.pixel_buffer = transposed_matrix
        self.update_grid_ui()
        self.generate_code_output()

    def update_grid_ui(self):
        color_active, color_inactive = ("#3584e4", "#3584e4"), ("#E0E0E0", "#2b2b2b")
        for row in range(8):
            for col in range(8):
                is_active = self.pixel_buffer[row][col]
                self.button_grid[row][col].configure(fg_color=color_active if is_active else color_inactive)

    def generate_code_output(self, event=None):
        byte_lines = [f"%{''.join('1' if self.pixel_buffer[r][c] else '0' for c in range(8))}" for r in range(8)]
        constant_name = self.entry_constant_name.get().strip() or "NEW_CHAR"
        compiled_code = f"const {constant_name} as byte[8] = ({','.join(byte_lines)})"
        self.txt_code_output.delete("0.0", "end")
        self.txt_code_output.insert("0.0", compiled_code)

if __name__ == "__main__":
    app = LEDMatrixGeneratorApp()
    app.mainloop()