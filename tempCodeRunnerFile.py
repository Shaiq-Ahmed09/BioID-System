import cv2
import os
import sys
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

# Set dark/modern cyberpunk style theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FaceScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MATRIX QUANTUM TERMINAL")
        self.geometry("950x650")
        self.resizable(False, False)

        # 1. Initialize Face Recognition Architecture
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        self.known_faces_dir = "known_faces"
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)

        self.faces_data = []
        self.labels_data = []
        self.names_map = {}
        self.has_images = False
        
        self.load_and_train_database()

        # 2. Setup Video & Scanner State Engines
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            print("[CRITICAL] Could not access webcam hardware.")
            sys.exit(1)

        self.process_this_frame = True
        self.face_locations = []
        self.face_names = []
        
        # Scanner Flow Variables
        self.scan_locked = False
        self.locked_name = ""
        
        # Typewriter Queue variables
        self.terminal_queue = []
        self.bottom_hud_queue = []
        self.current_hud_display_text = ""

        # 3. Design Modern UI Layout
        # Left Side: Hacker Terminal Panel
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#040a12")
        self.sidebar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self.sidebar, text="MATRIX OS V4.0", font=ctk.CTkFont(family="Courier", size=20, weight="bold"), text_color="#00ff66")
        self.title_label.pack(padx=20, pady=(30, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.sidebar, text="--- BIOMETRIC LINK ---", font=ctk.CTkFont(family="Courier", size=11), text_color="#00aa44")
        self.subtitle_label.pack(padx=20, pady=(0, 20))

        # Main Hacker Log Terminal
        self.log_box = ctk.CTkTextbox(self.sidebar, width=240, height=360, fg_color="#01050c", text_color="#00ff66", font=ctk.CTkFont(family="Courier", size=11))
        self.log_box.pack(padx=20, pady=10)
        
        # Reset / Shutdown Buttons
        self.reset_btn = ctk.CTkButton(self.sidebar, text="RESET SCAN", font=ctk.CTkFont(family="Courier", weight="bold"), fg_color="#1e293b", hover_color="#334155", text_color="#00ff66", border_width=1, border_color="#00ff66", command=self.reset_scanner)
        self.reset_btn.pack(padx=20, pady=(15, 5), fill="x")

        self.quit_btn = ctk.CTkButton(self.sidebar, text="DISCONNECT", font=ctk.CTkFont(family="Courier", weight="bold"), fg_color="#7f1d1d", hover_color="#991b1b", text_color="#fca5a5", command=self.close_app)
        self.quit_btn.pack(padx=20, pady=(5, 20), fill="x")

        # Right Side: Cinematic Video Screen
        self.main_content = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Upper Cinema Architectural Strip
        self.top_bar = ctk.CTkFrame(self.main_content, height=50, fg_color="#020617", corner_radius=0)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)
        
        self.app_title = ctk.CTkLabel(self.top_bar, text="QUANTUM FACE SCANNER // ACTIVE_STREAM", font=ctk.CTkFont(family="Courier", size=13, weight="bold"), text_color="#38bdf8")
        self.app_title.pack(padx=20, expand=True, side="left")

        # Bottom Cinema Architectural Strip
        self.bottom_bar = ctk.CTkFrame(self.main_content, height=60, fg_color="#020617", corner_radius=0, border_width=1, border_color="#1e293b")
        self.bottom_bar.pack(side="bottom", fill="x")
        self.bottom_bar.pack_propagate(False)

        self.hud_status_label = ctk.CTkLabel(self.bottom_bar, text="STATUS: INITIALIZING...", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color="#00ff66")
        self.hud_status_label.pack(padx=20, expand=True, side="left")

        # Embedded Raw Video Stream Container
        self.video_label = ctk.CTkLabel(self.main_content, text="")
        self.video_label.pack(expand=True, fill="both")

        # Bootstrap Logs
        self.queue_terminal_text("initializing core systems...\nmapping biometric profiles...\n")
        if self.has_images:
            user_list = ", ".join(list(self.names_map.values()))
            self.queue_terminal_text(f"database active.\ncompiled keys: [{user_list}]\nawaiting target acquisition...\n")
        else:
            self.queue_terminal_text("[!] warning: database profile vector empty.\n")
        
        self.queue_hud_text("ANALYZING ENVIRONMENT...")

        # Fire Loops
        self.process_typewriter_loops()
        self.update_video_frame()

    def queue_terminal_text(self, text):
        for char in text:
            self.terminal_queue.append(char)

    def queue_hud_text(self, text):
        self.bottom_hud_queue = list(text)
        self.current_hud_display_text = ""

    def process_typewriter_loops(self):
        # Handle Left Sidebar Terminal Logger
        if self.terminal_queue:
            char = self.terminal_queue.pop(0)
            self.log_box.configure(state="normal")
            self.log_box.insert("end", char)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        
        # Handle Bottom Architectural HUD Typewriter
        if self.bottom_hud_queue:
            char = self.bottom_hud_queue.pop(0)
            self.current_hud_display_text += char
            self.hud_status_label.configure(text=self.current_hud_display_text)

        self.after(20, self.process_typewriter_loops)

    def load_and_train_database(self):
        label_id = 0
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                img_path = os.path.join(self.known_faces_dir, filename)
                img = cv2.imread(img_path)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        face_roi = cv2.resize(face_roi, (200, 200))
                        self.faces_data.append(face_roi)
                        self.labels_data.append(label_id)
                        name = os.path.splitext(filename)[0].replace("_", " ").title()
                        self.names_map[label_id] = name
                        self.has_images = True
                        break
                label_id += 1
        if self.has_images:
            self.recognizer.train(self.faces_data, np.array(self.labels_data))

    def reset_scanner(self):
        self.scan_locked = False
        self.locked_name = ""
        self.hud_status_label.configure(text_color="#00ff66")
        self.queue_hud_text("ANALYZING...")
        self.queue_terminal_text("\n[system reset] scanning re-initialized...\n")

    def update_video_frame(self):
        try:
            ret, frame = self.video_capture.read()
            if not ret:
                self.after(30, self.update_video_frame)
                return

            frame = cv2.flip(frame, 1)

            # Only scan if target match hasn't locked out calculations yet
            if self.process_this_frame and not self.scan_locked:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

                self.face_locations = []
                self.face_names = []

                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200, 200))
                    name = "Unknown"

                    if self.has_images:
                        label, confidence = self.recognizer.predict(face_roi)
                        if confidence < 95:
                            name = self.names_map.get(label, "Unknown")
                    
                    self.face_locations.append((x*2, y*2, w*2, h*2))
                    self.face_names.append(name)
                    
                    # Lock Scan State instantly upon successful match identification
                    if name != "Unknown":
                        self.scan_locked = True
                        self.locked_name = name
                        self.hud_status_label.configure(text_color="#00ff66")
                        self.queue_hud_text(f"SUCCEEDED: WELCOME \"{name.upper()}\"")
                        self.queue_terminal_text(f"\n>> SUCCESS: matched identity profile [{name.upper()}]\n>> link secure.\n")
                        break
            
            # If scan locked, maintain dynamic bounding tracking around face positions
            elif self.scan_locked:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
                
                self.face_locations = []
                self.face_names = []
                
                # Continuously track the bounding coordinates without re-triggering calculation logs
                for (x, y, w, h) in faces:
                    self.face_locations.append((x*2, y*2, w*2, h*2))
                    self.face_names.append(self.locked_name)

            self.process_this_frame = not self.process_this_frame

            # Render Modern HUD Elements over live frames
            for (x, y, w, h), name in zip(self.face_locations, self.face_names):
                color = (102, 255, 0) if name != "Unknown" else (68, 68, 239)
                length = int(w * 0.2)
                thickness = 3
                
                # Draw Tech corner brackets
                cv2.line(frame, (x, y), (x + length, y), color, thickness)
                cv2.line(frame, (x, y), (x, y + length), color, thickness)
                cv2.line(frame, (x + w, y), (x + w - length, y), color, thickness)
                cv2.line(frame, (x + w, y), (x + w, y + length), color, thickness)
                cv2.line(frame, (x, y + h), (x + length, y + h), color, thickness)
                cv2.line(frame, (x, y + h), (x, y + h - length), color, thickness)
                cv2.line(frame, (x + w, y + h), (x + w - length, y + h), color, thickness)
                cv2.line(frame, (x + w, y + h), (x + w, y + h - length), color, thickness)

                # Render name tracking tag overlaying the frame area
                label_text = name.upper()
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                font_thickness = 2
                (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
                cv2.rectangle(frame, (x, y - text_h - 14), (x + text_w + 16, y), color, cv2.FILLED)
                cv2.putText(frame, label_text, (x + 8, y - 8), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

            # --- RENDER WITH ORIGINAL ASPECT RATIO AND CINEMA BARS ---
            # --- FULLSCREEN ASPECT-FILL ZOOM ENGINE ---
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            
            # Core width and height dimensions of your UI video container
            available_w = 670
            available_h = 500
            
            # 1. Use 'max' instead of 'min' to ensure the image covers the entire box
            scale_factor = max(available_w / img.width, available_h / img.height)
            new_w = int(img.width * scale_factor)
            new_h = int(img.height * scale_factor)
            
            # 2. Resize the image to cover the area
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # 3. Calculate perfect center-crop coordinates to slice off the overflow
            left = (new_w - available_w) // 2
            top = (new_h - available_h) // 2
            right = left + available_w
            bottom = top + available_h
            
           # 4. Crop the image and apply it to the UI
            final_canvas = img_resized.crop((left, top, right, bottom))
            
            # --- HIGH-DPI SCALING FIX ---
            # Use CustomTkinter's native image class instead of PIL's PhotoImage
            ctk_img = ctk.CTkImage(light_image=final_canvas, dark_image=final_canvas, size=(available_w, available_h))
            
            # Apply the native image to the label (no .imgtk reference needed)
            self.video_label.configure(image=ctk_img)

            self.after(15, self.update_video_frame)
            
            # Determine maximum scale parameter matching the original structural aspect ratio
            scale_factor = min(available_w / img.width, available_h / img.height)
            new_w = int(img.width * scale_factor)
            new_h = int(img.height * scale_factor)
            
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Overlay centered onto a solid layout background canvas matching the container boundaries
            final_canvas = Image.new("RGB", (available_w, available_h), (0, 0, 0))
            paste_x = (available_w - new_w) // 2
            paste_y = (available_h - new_h) // 2
            final_canvas.paste(img_resized, (paste_x, paste_y))
            
            imgtk = ImageTk.PhotoImage(image=final_canvas)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            self.after(15, self.update_video_frame)

        except Exception as e:
            print(f"[CRITICAL FRAME LOOP ERROR] {e}")
            self.after(30, self.update_video_frame)

    def close_app(self):
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.destroy()

if __name__ == "__main__":
    app = FaceScannerApp()
    app.mainloop()