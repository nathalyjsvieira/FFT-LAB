import customtkinter as ctk

class GeneratorView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1, minsize=340)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.wave_counter = 1

        # ==========================================
        # COLUNA ESQUERDA: MIXER (Adicionar Ondas)
        # ==========================================
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        self.mixer_panel = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.mixer_panel.pack(fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.mixer_panel, text="Sintetizador de Sinais", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(anchor="w", pady=(0, 5))
        
        self.math_label = ctk.CTkLabel(self.mixer_panel, text="y(t) = A * sin(2πft + φ)", text_color=("#555555", "#AAAAAA"))
        self.math_label.pack(anchor="w", pady=(0, 20))

        self.btn_add_wave = ctk.CTkButton(
            self.mixer_panel,
            text="➕ Adicionar Nova Onda",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#06b6d4",
            text_color="white",
            hover_color="#0891b2",
            command=self.add_wave_card
        )
        self.btn_add_wave.pack(fill="x", pady=(0, 20), ipady=8)

        self.waves_container = ctk.CTkFrame(self.mixer_panel, fg_color="transparent")
        self.waves_container.pack(fill="both", expand=True)

        self.add_wave_card()

        # ==========================================
        # COLUNA DIREITA: OSCILOSCÓPIO E EXPORTAÇÃO
        # ==========================================
        self.right_panel = ctk.CTkFrame(self, corner_radius=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # --- TOOLBAR SUPERIOR ---
        self.toolbar_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.toolbar_frame.grid_columnconfigure(1, weight=1)

        # 1. Switch de Inspeção (Substituindo o Checkbox)
        self.switch_inspect = ctk.CTkSwitch(
            self.toolbar_frame,
            text="Inspecionar Ondas",
            progress_color="#06b6d4",
            text_color=("black", "white")
        )
        self.switch_inspect.grid(row=0, column=0, sticky="w")

        # 2. Agrupamento dos Controles de Zoom (Régua/Pílula)
        self.zoom_ctrl = ctk.CTkFrame(self.toolbar_frame, fg_color=("gray85", "gray20"), corner_radius=6)
        self.zoom_ctrl.grid(row=0, column=2, sticky="e")
        
        # Botões com fundo transparente para herdar a cor da pílula, mas com hover_color ativo
        btn_opts = {"width": 30, "height": 30, "fg_color": "transparent", "text_color": ("black", "white"), "hover_color": ("gray75", "gray30")}
        ctk.CTkButton(self.zoom_ctrl, text="◀", **btn_opts).pack(side="left", padx=1, pady=1)
        ctk.CTkButton(self.zoom_ctrl, text="▶", **btn_opts).pack(side="left", padx=1, pady=1)
        ctk.CTkButton(self.zoom_ctrl, text="➕", **btn_opts).pack(side="left", padx=1, pady=1)
        ctk.CTkButton(self.zoom_ctrl, text="➖", **btn_opts).pack(side="left", padx=1, pady=1)

        # --- ÁREA DO GRÁFICO ---
        self.graph_placeholder = ctk.CTkFrame(self.right_panel, corner_radius=5, fg_color=("gray85", "gray10"))
        self.graph_placeholder.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # 3. Contraste do Placeholder (Cinza escuro no Modo Claro, Cinza claro no Modo Escuro)
        ctk.CTkLabel(
            self.graph_placeholder, 
            text="[ Display do Osciloscópio ]\nA soma matemática das ondas ativas será desenhada aqui em tempo real.",
            text_color=("#555555", "#CCCCCC") # <-- Correção de contraste aqui
        ).place(relx=0.5, rely=0.5, anchor="center")

        # --- MÓDULO DE ÁUDIO ---
        self.audio_panel = ctk.CTkFrame(self.right_panel, fg_color=("gray90", "gray15"), corner_radius=10)
        self.audio_panel.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20), ipadx=10, ipady=10)
        self.audio_panel.grid_columnconfigure(1, weight=1)

        self.player_frame = ctk.CTkFrame(self.audio_panel, fg_color="transparent")
        self.player_frame.grid(row=0, column=0, sticky="w", padx=10)

        self.btn_play = ctk.CTkButton(self.player_frame, text="▶ PLAY", width=100, fg_color="#10b981", hover_color="#059669", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.btn_play.pack(side="left", padx=(0, 10))

        self.btn_stop = ctk.CTkButton(self.player_frame, text="■ STOP", width=100, fg_color="#ef4444", hover_color="#dc2626", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.btn_stop.pack(side="left")

        self.export_frame = ctk.CTkFrame(self.audio_panel, fg_color="transparent")
        self.export_frame.grid(row=0, column=2, sticky="e", padx=10)

        self.btn_wav = ctk.CTkButton(self.export_frame, text="💾 Salvar WAV", width=110, fg_color="transparent", border_width=1, text_color=("black", "white"))
        self.btn_wav.pack(side="left", padx=(0, 10))

        self.btn_mp3 = ctk.CTkButton(self.export_frame, text="💾 Salvar MP3", width=110, fg_color="transparent", border_width=1, text_color=("black", "white"))
        self.btn_mp3.pack(side="left")

    # ==========================================
    # LÓGICA DE CRIAÇÃO DINÂMICA DOS CARDS
    # ==========================================
    def add_wave_card(self):
        if len(self.waves_container.winfo_children()) >= 4:
            return

        colors = ["#c026d3", "#eab308", "#ec4899", "#8b5cf6"]
        color = colors[(self.wave_counter - 1) % len(colors)]

        card = ctk.CTkFrame(self.waves_container, corner_radius=8)
        card.pack(fill="x", pady=(0, 15), ipadx=5, ipady=10)

        border = ctk.CTkFrame(card, width=5, fg_color=color, corner_radius=0)
        border.place(relx=0, rely=0, relheight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=(15, 10), pady=(0, 10))

        ctk.CTkLabel(header, text=f"Onda {self.wave_counter}", font=ctk.CTkFont(weight="bold")).pack(side="left")

        # 4. Botão de Excluir Onda ("X" -> Ícone Lixeira + Hitbox + Hover Vermelho)
        btn_close = ctk.CTkButton(
            header,
            text="🗑️",
            width=30,
            height=30,
            fg_color="transparent",
            text_color=("#4B5563", "#9CA3AF"),
            hover_color="#ef4444" # Fundo vermelho destrutivo ao passar o mouse
        )
        # Quando o mouse passar por cima, o texto fica branco para contrastar com o vermelho
        btn_close.bind("<Enter>", lambda e: btn_close.configure(text_color="white"))
        btn_close.bind("<Leave>", lambda e: btn_close.configure(text_color=("#4B5563", "#9CA3AF")))
        btn_close.configure(command=card.destroy)
        btn_close.pack(side="right")

        self.wave_counter += 1

        ctk.CTkLabel(card, text="Forma de Onda:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15)
        formas_onda = ["Senoidal (sin)", "Quadrada (square)", "Dente de Serra (saw)", "Triangular (tri)"]
        ctk.CTkOptionMenu(card, values=formas_onda, fg_color=("gray85", "gray25"), text_color=("black", "white")).pack(fill="x", padx=15, pady=(0, 15))

        self.create_slider_row(card, "Frequência", 20, 20000, 440, "Hz", color)
        self.create_slider_row(card, "Amplitude", 0, 100, 50, "%", color)
        self.create_slider_row(card, "Fase", 0, 360, 0, "°", color)

    def create_slider_row(self, parent, name, min_val, max_val, default_val, unit, hex_color):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=15, pady=(0, 10))

        labels_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        labels_frame.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(labels_frame, text=name, font=ctk.CTkFont(size=12)).pack(side="left")

        val_label = ctk.CTkLabel(labels_frame, text=f"{default_val} {unit}", font=ctk.CTkFont(size=12, weight="bold"), text_color=hex_color)
        val_label.pack(side="right")

        slider = ctk.CTkSlider(row_frame, from_=min_val, to=max_val, progress_color=hex_color)
        slider.set(default_val)
        slider.pack(fill="x")

        def update_label(value):
            val_label.configure(text=f"{int(value)} {unit}")

        slider.configure(command=update_label)