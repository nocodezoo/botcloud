#!/usr/bin/env python3
"""
TikTok-style Video Text & Voice Editor (Lightweight Version)
- Uses ffmpeg directly (no moviepy dependency hell)
- Text overlay + TTS voiceover
- Web server for viewing exports
"""

import os
import sys
import subprocess
import threading
import socket
import http.server
import socketserver
import shutil

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Directories
BASE_DIR = "/home/openryanclaw"
VIDEOS_DIR = os.path.join(BASE_DIR, "Videos/mp4")
OUTPUT_DIR = os.path.join(VIDEOS_DIR, "exports")
PUBLIC_DIR = os.path.join(VIDEOS_DIR, "public")
STATIC_DIR = os.path.join(PUBLIC_DIR, "static")

for d in [OUTPUT_DIR, PUBLIC_DIR, STATIC_DIR]:
    os.makedirs(d, exist_ok=True)

# Check ffmpeg
FFMPEG_OK = shutil.which("ffmpeg") is not None

class TikTokEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🦞 TikTok Editor")
        self.root.geometry("1100x750")
        
        self.current_video = None
        self.preview_photo = None
        
        # Text settings
        self.text_content = "Your text here"
        self.font_family = "Arial"
        self.font_size = 48
        self.text_color = "#FFFFFF"
        self.bg_color = "#000000"
        self.bg_alpha = 0.85
        self.bg_shape = "round"
        self.text_position = 50
        
        # TTS settings  
        self.tts_speed = 100
        self.tts_engine = None
        
        self.setup_ui()
        self.refresh_video_list()
        
        if not FFMPEG_OK:
            messagebox.showwarning("ffmpeg", "ffmpeg not found! Install with: sudo apt install ffmpeg")
        
        self.init_tts()
    
    def init_tts(self):
        """Try to init TTS engine"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.tts_speed)
            voices = self.tts_engine.getProperty('voices')
            self.voices = voices if voices else []
        except:
            try:
                from gtts import gTTS
                self.tts_engine = "gtts"
                self.voices = ["Google TTS"]
            except:
                self.tts_engine = None
                self.voices = []
    
    def setup_ui(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Videos + TTS
        left_frame = ttk.LabelFrame(paned, text="Videos", padding=10)
        paned.add(left_frame, weight=1)
        
        self.video_listbox = tk.Listbox(left_frame, width=28, height=8)
        self.video_listbox.pack(fill=tk.X, pady=(0, 5))
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        ttk.Button(left_frame, text="↻ Refresh", command=self.refresh_video_list).pack(fill=tk.X, pady=(0, 10))
        
        # TTS
        tts_frame = ttk.LabelFrame(left_frame, text="🎤 Text-to-Speech", padding=10)
        tts_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(tts_frame, text="Voiceover Text:").pack(anchor=tk.W)
        self.tts_text_area = scrolledtext.ScrolledText(tts_frame, height=4, width=30)
        self.tts_text_area.pack(fill=tk.X, pady=(0, 5))
        
        speed_frame = ttk.Frame(tts_frame)
        speed_frame.pack(fill=tk.X, pady=2)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.tts_speed_var = tk.IntVar(value=100)
        ttk.Spinbox(speed_frame, from_=50, to=300, textvariable=self.tts_speed_var, width=8).pack(side=tk.LEFT, padx=5)
        
        tts_btn = ttk.Button(tts_frame, text="🔊 Test", command=self.test_tts)
        tts_btn.pack(fill=tk.X, pady=(5, 0))
        
        self.tts_status = ttk.Label(tts_frame, text="", foreground="gray")
        self.tts_status.pack(anchor=tk.W)
        
        if self.tts_engine:
            self.tts_status.config(text="✅ TTS Ready", foreground="green")
        else:
            self.tts_status.config(text="❌ No TTS (install pyttsx3)", foreground="red")
        
        # Center: Preview
        center_frame = ttk.LabelFrame(paned, text="Preview", padding=10)
        paned.add(center_frame, weight=3)
        
        self.preview_label = tk.Label(center_frame, bg="black", text="Select a video", fg="gray", font=("Arial", 14))
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize to update preview
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Right: Text Controls
        right_frame = ttk.LabelFrame(paned, text="Text Overlay", padding=10)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Text:").pack(anchor=tk.W, pady=(0, 3))
        self.text_entry = tk.Entry(right_frame, width=32)
        self.text_entry.insert(0, self.text_content)
        self.text_entry.pack(fill=tk.X, pady=(0, 8))
        self.text_entry.bind('KeyRelease', self.update_preview)
        
        ttk.Label(right_frame, text="Font:").pack(anchor=tk.W, pady=(0, 3))
        self.font_var = tk.StringVar(value="Arial")
        fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Impact", "Georgia"]
        ttk.Combobox(right_frame, textvariable=self.font_var, values=fonts, state="readonly").pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(right_frame, text="Font Size:").pack(anchor=tk.W, pady=(0, 3))
        self.size_var = tk.IntVar(value=48)
        ttk.Spinbox(right_frame, from_=12, to=120, textvariable=self.size_var).pack(anchor=tk.W, pady=(0, 8))
        
        # Colors
        color_frame = ttk.Frame(right_frame)
        color_frame.pack(fill=tk.X, pady=(0, 8))
        self.text_color_btn = tk.Button(color_frame, text="Text", bg="white", width=8, command=self.choose_text_color)
        self.text_color_btn.pack(side=tk.LEFT)
        self.bg_color_btn = tk.Button(color_frame, text="Bg", bg="black", fg="white", width=8, command=self.choose_bg_color)
        self.bg_color_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.bg_shape_var = tk.StringVar(value="round")
        shape_frame = ttk.Frame(right_frame)
        shape_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Radiobutton(shape_frame, text="Round", variable=self.bg_shape_var, value="round", command=self.update_preview).pack(side=tk.LEFT)
        ttk.Radiobutton(shape_frame, text="Square", variable=self.bg_shape_var, value="square", command=self.update_preview).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(right_frame, text="Background Opacity:").pack(anchor=tk.W, pady=(0, 3))
        self.alpha_var = tk.DoubleVar(value=0.85)
        ttk.Scale(right_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, variable=self.alpha_var).pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(right_frame, text="Vertical Position:").pack(anchor=tk.W, pady=(0, 3))
        self.pos_var = tk.IntVar(value=50)
        ttk.Scale(right_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.pos_var, command=lambda _: self.update_preview()).pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        self.export_btn = ttk.Button(right_frame, text="🎬 Export Video", command=self.export_video)
        self.export_btn.pack(fill=tk.X, pady=(0, 3))
        
        self.serve_btn = ttk.Button(right_frame, text="🌐 Start Web Server", command=self.toggle_server)
        self.serve_btn.pack(fill=tk.X)
        
        self.status_label = ttk.Label(right_frame, text="Ready", foreground="green")
        self.status_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.server_status = ttk.Label(right_frame, text="Server: Stopped", foreground="gray")
        self.server_status.pack(anchor=tk.W)
        
        self.server = None
    
    def on_window_resize(self, event):
        """Update preview when window is resized"""
        if event.widget == self.root and self.current_video:
            # Debounce - only update if size changed significantly
            if hasattr(self, '_last_size'):
                w, h = self._last_size
                if abs(event.width - w) < 50 and abs(event.height - h) < 50:
                    return
            self._last_size = (event.width, event.height)
            # Regenerate preview with new size
            self.generate_preview()
    
    def refresh_video_list(self):
        self.video_listbox.delete(0, tk.END)
        if os.path.exists(VIDEOS_DIR):
            for f in sorted(os.listdir(VIDEOS_DIR)):
                if f.lower().endswith('.mp4'):
                    self.video_listbox.insert(tk.END, f)
    
    def on_video_select(self, event):
        sel = self.video_listbox.curselection()
        if sel:
            self.current_video = os.path.join(VIDEOS_DIR, self.video_listbox.get(sel[0]))
            self.status_label.config(text=f"Loaded: {os.path.basename(self.current_video)}")
            self.generate_preview()
    
    def generate_preview(self):
        if not self.current_video:
            return
        
        self.status_label.config(text="Generating preview...")
        self.root.update()
        
        # Get preview window size
        preview_w = self.preview_label.winfo_width() or 500
        preview_h = self.preview_label.winfo_height() or 400
        
        # Extract frame scaled to preview size
        frame_file = os.path.join(OUTPUT_DIR, "preview_frame.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2", "-i", self.current_video,
            "-vframes", "1", "-vf", f"scale={preview_w}:{preview_h}:force_original_aspect_ratio=decrease",
            frame_file
        ], capture_output=True)
        
        if os.path.exists(frame_file):
            # Render text on frame
            self.render_text_preview(frame_file)
    
    def render_text_preview(self, frame_path):
        """Render text overlay using PIL for preview"""
        img = Image.open(frame_path)
        draw = ImageDraw.Draw(img)
        
        text = self.text_entry.get() or "Your text"
        font_size = max(16, int(img.height * 0.08 * (self.size_var.get() / 48)))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        x = (img.width - tw) // 2
        y = int(img.height * (self.pos_var.get() / 100)) - th // 2
        
        # Background
        pad = 15
        bg_box = [x - pad, y - pad, x + tw + pad, y + th + pad]
        
        alpha = int(255 * self.alpha_var.get())
        bg_rgb = self.hex_to_rgb(self.bg_color)
        
        if self.bg_shape_var.get() == "round":
            draw.rounded_rectangle(bg_box, radius=12, fill=(*bg_rgb, alpha))
        else:
            draw.rectangle(bg_box, fill=(*bg_rgb, alpha))
        
        # Text
        text_rgb = self.hex_to_rgb(self.text_color)
        draw.text((x, y), text, fill=text_rgb, font=font)
        
        self.preview_photo = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_photo, text="")
        self.status_label.config(text="Preview ready")
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def update_preview(self, event=None):
        if self.current_video:
            self.generate_preview()
    
    def choose_text_color(self):
        c = colorchooser.askcolor(self.text_color)[1]
        if c:
            self.text_color = c
            self.text_color_btn.config(bg=c)
            self.update_preview()
    
    def choose_bg_color(self):
        c = colorchooser.askcolor(self.bg_color)[1]
        if c:
            self.bg_color = c
            self.bg_color_btn.config(bg=c)
            self.update_preview()
    
    def test_tts(self):
        text = self.tts_text_area.get("1.0", tk.END).strip() or "This is a test."
        self.tts_status.config(text="🔊 Playing...", foreground="blue")
        self.root.update()
        
        if self.tts_engine == "gtts":
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en')
                tts.save("/tmp/test_tts.mp3")
                subprocess.run(["mpg123", "-q", "/tmp/test_tts.mp3"], check=False)
            except:
                pass
        elif hasattr(self.tts_engine, 'say'):
            try:
                self.tts_engine.setProperty('rate', self.tts_speed_var.get())
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass
        
        self.tts_status.config(text="✅ Ready" if self.tts_engine else "❌ No TTS", 
                               foreground="green" if self.tts_engine else "red")
    
    def generate_tts(self, output_path):
        """Generate TTS audio file"""
        text = self.tts_text_area.get("1.0", tk.END).strip()
        if not text:
            return None
        
        try:
            if self.tts_engine == "gtts":
                from gtts import gTTS
                gTTS(text=text, lang='en').save(output_path)
                return output_path
            elif hasattr(self.tts_engine, 'save_to_file'):
                self.tts_engine.setProperty('rate', self.tts_speed_var.get())
                self.tts_engine.save_to_file(text, output_path)
                self.tts_engine.runAndWait()
                return output_path
        except Exception as e:
            print(f"TTS error: {e}")
        return None
    
    def export_video(self):
        if not self.current_video:
            self.status_label.config(text="No video selected!", foreground="red")
            return
        
        self.status_label.config(text="Exporting...", foreground="orange")
        self.export_btn.config(state=tk.DISABLED)
        self.root.update()
        
        thread = threading.Thread(target=self.do_export)
        thread.start()
    
    def do_export(self):
        base_name = os.path.splitext(os.path.basename(self.current_video))[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base_name}_tiktok.mp4")
        
        text = self.text_entry.get() or ""
        
        # Create text overlay image for ffmpeg
        text_overlay_file = None
        video_w, video_h = 1280, 720  # defaults
        
        # Get video dimensions
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0", self.current_video
            ], capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                video_w, video_h = map(int, result.stdout.strip().split('x'))
        except:
            pass
        
        if text:
            # Generate a sample frame with text to get font metrics
            sample_frame = os.path.join(OUTPUT_DIR, "sample_frame.jpg")
            subprocess.run([
                "ffmpeg", "-y", "-ss", "1", "-i", self.current_video,
                "-vframes", "1", sample_frame
            ], capture_output=True)
            
            if os.path.exists(sample_frame):
                # Create text image
                img = Image.open(sample_frame)
                text_overlay_file = os.path.join(OUTPUT_DIR, "text_overlay.png")
                self.create_text_overlay(img.width, img.height, text_overlay_file)
        
        # Generate TTS if text provided
        tts_audio = None
        tts_text = self.tts_text_area.get("1.0", tk.END).strip()
        if tts_text:
            tts_audio = os.path.join(OUTPUT_DIR, f"{base_name}_tts.mp3")
            self.generate_tts(tts_audio)
        
        # Simple approach: 2-pass export
        # Pass 1: Add text overlay
        temp_video = output_file.replace(".mp4", "_temp.mp4")
        
        if text_overlay_file and os.path.exists(text_overlay_file):
            # Add text overlay
            y_pos = int(video_h * (self.pos_var.get() / 100))
            cmd = [
                "ffmpeg", "-y", "-i", self.current_video, "-i", text_overlay_file,
                "-filter_complex", f"[0:v][1:v]overlay=x=(W-w)/2:y={y_pos}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "copy", "-shortest", "-pix_fmt", "yuv420p", temp_video
            ]
            subprocess.run(cmd, capture_output=True)
        else:
            shutil.copy(self.current_video, temp_video)
        
        # Pass 2: Add/replace audio
        if tts_audio and os.path.exists(tts_audio):
            # Replace original audio with TTS
            cmd = [
                "ffmpeg", "-y", "-i", temp_video, "-i", tts_audio,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-map", "0:v", "-map", "1:a", "-shortest", "-pix_fmt", "yuv420p", output_file
            ]
            subprocess.run(cmd, capture_output=True)
            os.remove(tts_audio)
        else:
            # Just remux with compatible settings
            cmd = [
                "ffmpeg", "-y", "-i", temp_video,
                "-c:v", "copy", "-c:a", "copy", "-pix_fmt", "yuv420p", output_file
            ]
            subprocess.run(cmd, capture_output=True)
            os.remove(temp_video)
        
        # Also remove temp text overlay
        if text_overlay_file and os.path.exists(text_overlay_file):
            os.remove(text_overlay_file)
        
        # Copy to public
        public_file = os.path.join(STATIC_DIR, os.path.basename(output_file))
        if os.path.exists(output_file):
            shutil.copy(output_file, public_file)
        
        self.root.after(0, self.export_done, output_file, public_file if os.path.exists(output_file) else None)
    
    def create_text_overlay(self, width, height, output_path):
        """Create PNG with transparent background for text overlay"""
        # Scale font relative to video size
        font_size = max(24, int(height * 0.08 * (self.size_var.get() / 48)))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = self.text_entry.get() or ""
        
        # Create image large enough for text
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        x = (width - tw) // 2
        y = int(height * (self.pos_var.get() / 100)) - th // 2
        
        # Background
        pad = 20
        bg_box = [x - pad, y - pad, x + tw + pad, y + th + pad]
        
        bg_rgb = self.hex_to_rgb(self.bg_color)
        alpha = int(255 * self.alpha_var.get())
        
        if self.bg_shape_var.get() == "round":
            draw.rounded_rectangle(bg_box, radius=15, fill=(*bg_rgb, alpha))
        else:
            draw.rectangle(bg_box, fill=(*bg_rgb, alpha))
        
        # Text
        text_rgb = self.hex_to_rgb(self.text_color)
        draw.text((x, y), text, fill=text_rgb, font=font)
        
        img.save(output_path, 'PNG')
    
    def export_done(self, output_file, public_file):
        self.export_btn.config(state=tk.NORMAL)
        if output_file and os.path.exists(output_file):
            self.status_label.config(text=f"✅ Saved: {os.path.basename(output_file)}", foreground="green")
        else:
            self.status_label.config(text="❌ Export failed", foreground="red")
    
    def toggle_server(self):
        if self.server:
            self.server.shutdown()
            self.server = None
            self.serve_btn.config(text="🌐 Start Web Server")
            self.server_status.config(text="Server: Stopped", foreground="gray")
        else:
            for port in range(8080, 8090):
                try:
                    os.chdir(STATIC_DIR)
                    self.server = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
                    break
                except:
                    continue
            
            thread = threading.Thread(target=self.server.serve_forever)
            thread.daemon = True
            thread.start()
            
            self.serve_btn.config(text="⏹ Stop Server")
            self.server_status.config(text=f"Server: localhost:{port}", foreground="green")
            
            import webbrowser
            webbrowser.open(f"http://localhost:{port}/")

def main():
    root = tk.Tk()
    app = TikTokEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
