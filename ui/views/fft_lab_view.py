import customtkinter as ctk
import tkinter as tk
import math

# --- UTILITÁRIO DE TOOLTIP ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 30
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # O Tooltip também precisa de cores que contrastem
        label = tk.Label(tw, text=self.text, justify='left', background="#1A1A1B", foreground="white", relief='solid', borderwidth=1, font=("Arial", 10, "normal"), padx=10, pady=5)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# --- TELA PRINCIPAL FFT LAB ---
class FFTLabView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1, minsize=320)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # COLUNA ESQUERDA: PAINEL DE CONTROLES
        # ==========================================
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        self.controls_panel = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.controls_panel.pack(fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.controls_panel, text="FFT Lab: Análise", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(anchor="w", pady=(0, 15))

        # --- CARD 1: ÁUDIO ORIGINAL ---
        self.card_original = ctk.CTkFrame(self.controls_panel, corner_radius=10)
        self.card_original.pack(fill="x", pady=(0, 20), ipadx=10, ipady=15)

        lbl_orig = ctk.CTkLabel(self.card_original, text="1. Sinal Original", font=ctk.CTkFont(weight="bold"))
        lbl_orig.pack(anchor="w", padx=15, pady=(5, 10)) # Aumentamos o padding aqui
        ToolTip(lbl_orig, "Onda de áudio no Domínio do Tempo.\nMostra a amplitude (volume) variando ao longo dos milissegundos.")

        # Mini Gráfico Original
        self.draw_mini_graph(self.card_original, "wave", "#06b6d4")

        self.btn_load = ctk.CTkButton(self.card_original, text="Carregar Arquivo", fg_color="#06b6d4", hover_color="#0891b2", text_color="white")
        self.btn_load.pack(fill="x", padx=15, pady=(15, 10)) # Aumentamos o padding aqui

        # Botão Gravar com o Círculo Vermelho e fundo adaptativo (Claro/Escuro)
        self.btn_record = ctk.CTkButton(self.card_original, text="🔴 Gravar Áudio", fg_color=("gray85", "gray25"), text_color=("black", "white"), hover_color=("gray75", "gray35"))
        self.btn_record.pack(fill="x", padx=15, pady=(0, 5))

        # --- CARD 2: FFT ---
        self.card_fft = ctk.CTkFrame(self.controls_panel, corner_radius=10)
        self.card_fft.pack(fill="x", pady=(0, 20), ipadx=10, ipady=15)

        lbl_fft = ctk.CTkLabel(self.card_fft, text="2. Criptografia (FFT)", font=ctk.CTkFont(weight="bold"))
        lbl_fft.pack(anchor="w", padx=15, pady=(5, 10))
        ToolTip(lbl_fft, "Transformada Rápida de Fourier.\nConverte o tempo em Frequência (Espectro).")

        self.draw_mini_graph(self.card_fft, "bars", "#c026d3")

        self.btn_apply_fft = ctk.CTkButton(self.card_fft, text="Aplicar FFT", fg_color="#c026d3", hover_color="#a21caf", text_color="white")
        self.btn_apply_fft.pack(fill="x", padx=15, pady=(15, 5))

        # --- CARD 3: IFFT ---
        self.card_ifft = ctk.CTkFrame(self.controls_panel, corner_radius=10)
        self.card_ifft.pack(fill="x", pady=(0, 20), ipadx=10, ipady=15)

        lbl_ifft = ctk.CTkLabel(self.card_ifft, text="3. Restauração (IFFT)", font=ctk.CTkFont(weight="bold"))
        lbl_ifft.pack(anchor="w", padx=15, pady=(5, 10))
        ToolTip(lbl_ifft, "Transformada Inversa.\nReconstrói as frequências de volta para o domínio do tempo.")

        self.draw_mini_graph(self.card_ifft, "noisy_wave", "#eab308")

        self.btn_apply_ifft = ctk.CTkButton(self.card_ifft, text="Aplicar IFFT", fg_color="#eab308", text_color="black", hover_color="#ca8a04")
        self.btn_apply_ifft.pack(fill="x", padx=15, pady=(15, 5))

        # --- BARRA DE STATUS ---
        self.status_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=(10, 0))

        self.lbl_status = ctk.CTkLabel(self.status_frame, text="Status: Aguardando áudio...", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray50")
        self.lbl_status.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, progress_color="#06b6d4", height=8)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.set(0)


        # ==========================================
        # COLUNA DIREITA: ÁREA DE VISUALIZAÇÃO
        # ==========================================
        self.view_panel = ctk.CTkFrame(self, corner_radius=10)
        self.view_panel.grid(row=0, column=1, sticky="nsew")
        self.view_panel.grid_rowconfigure(1, weight=1)
        self.view_panel.grid_columnconfigure(0, weight=1)

        # --- Filtros e Controles de Zoom usando GRID para alinhamento perfeito ---
        self.filters_frame = ctk.CTkFrame(self.view_panel, fg_color="transparent")
        self.filters_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.filters_frame.grid_columnconfigure(4, weight=1) # Empurra o zoom para a direita

        # Label perfeitamente alinhada com os Checkboxes (usando sticky="e" e sem padding vertical irregular)
        lbl_view = ctk.CTkLabel(self.filters_frame, text="Visualização Ativa:", font=ctk.CTkFont(weight="bold"))
        lbl_view.grid(row=0, column=0, padx=(0, 15), sticky="e")
        
        # Checkboxes permitem ativar os 3 gráficos ao mesmo tempo
        self.chk_orig = ctk.CTkCheckBox(self.filters_frame, text="Original", fg_color="#06b6d4", text_color=("black", "white"))
        self.chk_orig.grid(row=0, column=1, padx=10)
        self.chk_orig.select() # Vem selecionado por padrão

        self.chk_fft = ctk.CTkCheckBox(self.filters_frame, text="FFT", fg_color="#c026d3", text_color=("black", "white"))
        self.chk_fft.grid(row=0, column=2, padx=10)

        self.chk_ifft = ctk.CTkCheckBox(self.filters_frame, text="IFFT", fg_color="#eab308", text_color=("black", "white"))
        self.chk_ifft.grid(row=0, column=3, padx=10)

        # Barra de Ferramentas de Zoom / Navegação
        self.toolbar_frame = ctk.CTkFrame(self.filters_frame, fg_color="transparent")
        self.toolbar_frame.grid(row=0, column=4, sticky="e")

        # Botões da Toolbar
        btn_args = {"width": 30, "fg_color": ("gray80", "gray20"), "text_color": ("black", "white"), "hover_color": ("gray70", "gray30")}
        ctk.CTkButton(self.toolbar_frame, text="◀", **btn_args).pack(side="left", padx=2)
        ctk.CTkButton(self.toolbar_frame, text="▶", **btn_args).pack(side="left", padx=2)
        ctk.CTkButton(self.toolbar_frame, text="➖", **btn_args).pack(side="left", padx=2)
        ctk.CTkButton(self.toolbar_frame, text="➕", **btn_args).pack(side="left", padx=2)

        # --- Espaço do Gráfico ---
        self.graph_placeholder = ctk.CTkFrame(self.view_panel, corner_radius=5, fg_color=("gray85", "gray10"))
        self.graph_placeholder.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.graph_placeholder, text="[ Renderização Interativa do Matplotlib ]\n\nNesta área as 3 ondas poderão ser sobrepostas.", text_color="gray50").place(relx=0.5, rely=0.5, anchor="center")

    # ==========================================
    # FUNÇÃO: DESENHAR MINI GRÁFICOS
    # ==========================================
    def draw_mini_graph(self, parent, graph_type, color_hex):
        # A Mágica do Modo Claro/Escuro para o Canvas do Tkinter:
        # Pega a cor correspondente ["Cor Modo Claro", "Cor Modo Escuro"]
        bg_color = self._apply_appearance_mode(["#EAEAEA", "#2D2D2E"])

        wrapper = ctk.CTkFrame(parent, fg_color=bg_color, height=60, corner_radius=5)
        wrapper.pack(fill="x", padx=15, pady=5)
        wrapper.pack_propagate(False)

        canvas = tk.Canvas(wrapper, bg=bg_color, highlightthickness=0, height=60)
        canvas.pack(fill="both", expand=True, padx=5, pady=5)

        width = 250

        if graph_type == "wave":
            points = []
            for x in range(width):
                y = 25 + math.sin(x * 0.08) * 15
                points.extend([x, y])
            canvas.create_line(points, fill=color_hex, width=2, smooth=True)

        elif graph_type == "bars":
            for i in range(10, width - 10, 8):
                height = 5 if i % 40 == 0 else (25 if i % 25 == 0 else 12)
                canvas.create_rectangle(i, 50 - height, i + 4, 50, fill=color_hex, outline="")

        elif graph_type == "noisy_wave":
            points = []
            for x in range(width):
                y = 25 + math.sin(x * 0.08) * 15 + (math.sin(x * 0.9) * 3)
                points.extend([x, y])
            canvas.create_line(points, fill=color_hex, width=2, dash=(2, 2))