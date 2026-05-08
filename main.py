import customtkinter as ctk

class LEDMatrixGeneratorApp(ctk.CTk):
    """
    Main application class for the 8x8 LED Matrix Code Generator.
    Generates MikroBasic byte array code from a graphical grid.
    """
    def __init__(self):
        super().__init__()
        
        # --- Window Configuration ---
        self.title("LED Matrix Code Generator")
        self.geometry("650x700")
        self.minsize(550, 650)
        
        # UI Theme configuration
        ctk.set_appearance_mode("System")  
        ctk.set_default_color_theme("blue")
        
        # --- Internal State ---
        # pixel_buffer stores the boolean state of the 8x8 grid
        self.pixel_buffer = [[False for _ in range(8)] for _ in range(8)]
        self.button_grid = []
        
        # --- Main Layout Management ---
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_columnconfigure(0, weight=1)
        
        self._initialize_matrix_ui()
        self._initialize_control_panel_ui()
        
        # Trigger initial code generation
        self.generate_code_output()

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
        """Initializes the lower panel containing inputs and code output."""
        self.control_panel = ctk.CTkFrame(self, corner_radius=15)
        self.control_panel.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.control_panel.grid_columnconfigure(1, weight=1) 
        self.control_panel.grid_columnconfigure(2, weight=0) 
        
        # Constant Name Input
        self.lbl_constant_name = ctk.CTkLabel(
            self.control_panel, 
            text="Constant Name:", 
            font=("Roboto", 14, "bold")
        )
        self.lbl_constant_name.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.entry_constant_name = ctk.CTkEntry(
            self.control_panel, 
            font=("Roboto", 14), 
            corner_radius=8
        )
        self.entry_constant_name.insert(0, "CUSTOM")
        self.entry_constant_name.grid(row=0, column=1, padx=(0, 15), pady=(15, 5), sticky="ew")
        self.entry_constant_name.bind("<KeyRelease>", self.generate_code_output)
        
        # Rotate Button
        self.btn_rotate_cw = ctk.CTkButton(
            self.control_panel, 
            text="Rotate +90° ↻", 
            font=("Roboto", 13, "bold"),
            fg_color=("#388E3C", "#2E7D32"), 
            hover_color=("#4CAF50", "#1B5E20"),
            corner_radius=8,
            command=self.rotate_matrix_clockwise
        )
        self.btn_rotate_cw.grid(row=0, column=2, padx=(0, 15), pady=(15, 5))
        
        # Generated Code Output
        self.txt_code_output = ctk.CTkTextbox(
            self.control_panel, 
            height=80, 
            font=("Consolas", 14), 
            corner_radius=8
        )
        self.txt_code_output.grid(row=1, column=0, columnspan=3, padx=15, pady=(10, 15), sticky="ew")

    def toggle_pixel(self, row: int, col: int):
        """Inverts the boolean state of a specific pixel and updates the UI."""
        self.pixel_buffer[row][col] = not self.pixel_buffer[row][col]
        self.update_grid_ui()
        self.generate_code_output()

    def rotate_matrix_clockwise(self):
        """Rotates the 8x8 pixel buffer 90 degrees clockwise."""
        transposed_matrix = [[False for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                transposed_matrix[col][7 - row] = self.pixel_buffer[row][col]
                
        self.pixel_buffer = transposed_matrix
        self.update_grid_ui()
        self.generate_code_output()

    def update_grid_ui(self):
        """Synchronizes the visual grid colors with the internal pixel_buffer state."""
        color_active = ("#3584e4", "#3584e4")
        color_inactive = ("#E0E0E0", "#2b2b2b")
        hover_active = ("#1c71d8", "#1c71d8")
        hover_inactive = ("#D0D0D0", "#3b3b3b")
        
        for row in range(8):
            for col in range(8):
                is_active = self.pixel_buffer[row][col]
                self.button_grid[row][col].configure(
                    fg_color=color_active if is_active else color_inactive,
                    hover_color=hover_active if is_active else hover_inactive
                )

    def generate_code_output(self, event=None):
        """Generates the MikroBasic byte array code based on the current state."""
        byte_lines = []
        for row in range(8):
            bit_string = "".join("1" if self.pixel_buffer[row][col] else "0" for col in range(8))
            byte_lines.append(f"%{bit_string}")

        constant_name = self.entry_constant_name.get().strip()
        if not constant_name:
            constant_name = "NEW_CHAR"

        compiled_code = f"const {constant_name} as byte[8] = ({','.join(byte_lines)})"
        
        self.txt_code_output.delete("0.0", "end")
        self.txt_code_output.insert("0.0", compiled_code)

if __name__ == "__main__":
    app = LEDMatrixGeneratorApp()
    app.mainloop()