import sys
import requests
import re
import json
import time
import random
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QMainWindow, QMessageBox
)
from PyQt5.QtGui import QFont

# === API Configuration ===
API_KEY = "AIzaSyBQrgcLg3Y7RAt4xQLf_rHAutLiObt1XIw"

# Multiple endpoints to try
ENDPOINTS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
    # f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}",
    # f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEY}",
]

TEST_URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"


def markdown_to_html(text):
    """Convert markdown formatting to HTML"""
    # Convert headers
    text = re.sub(r'^### (.*?)$', r'<h3 style="color: #2c3e50; margin: 10px 0 5px 0;">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2 style="color: #2c3e50; margin: 15px 0 8px 0;">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1 style="color: #2c3e50; margin: 20px 0 10px 0;">\1</h1>', text, flags=re.MULTILINE)
    
    # Convert bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Convert italic text
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Convert code blocks
    text = re.sub(r'```(.*?)```', r'<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 4px solid #007acc; margin: 10px 0;"><code>\1</code></pre>', text, flags=re.DOTALL)
    
    # Convert inline code
    text = re.sub(r'`(.*?)`', r'<code style="background-color: #f1f2f6; padding: 2px 4px; border-radius: 3px; font-family: monospace;">\1</code>', text)
    
    # Convert bullet points
    lines = text.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result_lines.append('<ul style="margin: 10px 0; padding-left: 20px;">')
                in_list = True
            item_text = line.strip()[2:]  # Remove '- ' or '* '
            result_lines.append(f'<li style="margin: 5px 0;">{item_text}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    text = '\n'.join(result_lines)
    
    # Convert line breaks to HTML
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    
    return text


# === Enhanced Connection Test Worker ===
class ConnectionTestWorker(QThread):
    finished = pyqtSignal(bool, str, dict)

    def run(self):
        details = {}
        
        try:
            # Test 1: Basic internet
            start_time = time.time()
            response = requests.get("https://www.google.com", timeout=10)
            details['internet_latency'] = f"{(time.time() - start_time):.2f}s"
            details['internet_status'] = response.status_code
            
            if response.status_code != 200:
                self.finished.emit(False, "No internet connection", details)
                return
            
            # Test 2: Gemini API models endpoint
            start_time = time.time()
            headers = {"Content-Type": "application/json"}
            response = requests.get(TEST_URL, headers=headers, timeout=15)
            details['gemini_models_latency'] = f"{(time.time() - start_time):.2f}s"
            details['gemini_models_status'] = response.status_code
            
            if response.status_code != 200:
                if response.status_code == 401:
                    self.finished.emit(False, "Invalid API key", details)
                elif response.status_code == 403:
                    self.finished.emit(False, "API access forbidden", details)
                else:
                    self.finished.emit(False, f"API models endpoint failed: {response.status_code}", details)
                return
            
            # Test 3: Try multiple actual API calls with different strategies
            success_count = 0
            total_tests = 3
            
            for i in range(total_tests):
                try:
                    start_time = time.time()
                    
                    # Use different configurations for each test
                    if i == 0:
                        # Minimal test
                        test_data = {
                            "contents": [{"parts": [{"text": "Hi"}]}],
                            "generationConfig": {"maxOutputTokens": 5}
                        }
                        endpoint = ENDPOINTS[0]
                    elif i == 1:
                        # Different model
                        test_data = {
                            "contents": [{"parts": [{"text": "Hello"}]}],
                            "generationConfig": {"maxOutputTokens": 10, "temperature": 0.1}
                        }
                        endpoint = ENDPOINTS[1] if len(ENDPOINTS) > 1 else ENDPOINTS[0]
                    else:
                        # Ultra minimal
                        test_data = {"contents": [{"parts": [{"text": "?"}]}]}
                        endpoint = ENDPOINTS[0]
                    
                    test_response = requests.post(
                        endpoint,
                        headers=headers,
                        json=test_data,
                        timeout=25
                    )
                    
                    latency = f"{(time.time() - start_time):.2f}s"
                    details[f'api_test_{i+1}_latency'] = latency
                    details[f'api_test_{i+1}_status'] = test_response.status_code
                    
                    if test_response.status_code == 200:
                        success_count += 1
                        details[f'api_test_{i+1}_result'] = "SUCCESS"
                    elif test_response.status_code == 503:
                        details[f'api_test_{i+1}_result'] = "SERVICE_UNAVAILABLE"
                    elif test_response.status_code == 429:
                        details[f'api_test_{i+1}_result'] = "RATE_LIMITED"
                    else:
                        details[f'api_test_{i+1}_result'] = f"ERROR_{test_response.status_code}"
                    
                    # Add small delay between tests
                    time.sleep(1)
                    
                except requests.exceptions.Timeout:
                    details[f'api_test_{i+1}_result'] = "TIMEOUT"
                except Exception as e:
                    details[f'api_test_{i+1}_result'] = f"EXCEPTION: {str(e)[:50]}"
            
            details['successful_tests'] = f"{success_count}/{total_tests}"
            
            if success_count > 0:
                self.finished.emit(True, f"API working ({success_count}/{total_tests} tests passed)", details)
            else:
                self.finished.emit(False, "All API tests failed - service may be overloaded", details)
                
        except Exception as e:
            details['error'] = f"Test exception: {str(e)}"
            self.finished.emit(False, f"Connection test failed: {str(e)}", details)


# === Bulletproof Gemini Worker ===
class BulletproofGeminiWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    debug = pyqtSignal(str)

    def __init__(self, user_message):
        super().__init__()
        self.user_message = user_message
        self.should_stop = False

    def stop(self):
        self.should_stop = True

    def run(self):
        # Strategy 1: Try all endpoints with exponential backoff for 503 errors
        for attempt in range(3):  # 3 main attempts
            if self.should_stop:
                return
                
            self.progress.emit(f"Attempt {attempt + 1}/3")
            
            for endpoint_idx, endpoint in enumerate(ENDPOINTS):
                if self.should_stop:
                    return
                    
                self.debug.emit(f"🔄 Trying endpoint {endpoint_idx + 1}/{len(ENDPOINTS)}")
                
                # Try different request configurations
                configs = [
                    # Ultra minimal
                    {
                        "contents": [{"parts": [{"text": self.user_message[:200]}]}],
                        "generationConfig": {"maxOutputTokens": 50}
                    },
                    # Minimal
                    {
                        "contents": [{"parts": [{"text": self.user_message[:500]}]}],
                        "generationConfig": {"maxOutputTokens": 200, "temperature": 0.1}
                    },
                    # Standard (if message is short)
                    {
                        "contents": [{"parts": [{"text": self.user_message}]}],
                        "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7}
                    } if len(self.user_message) < 1000 else None
                ]
                
                # Remove None configs
                configs = [c for c in configs if c is not None]
                
                for config_idx, config in enumerate(configs):
                    if self.should_stop:
                        return
                        
                    try:
                        self.debug.emit(f"📡 Config {config_idx + 1}/{len(configs)}")
                        
                        headers = {
                            "Content-Type": "application/json",
                            "User-Agent": f"GeminiChat/1.0-{random.randint(1000, 9999)}"
                        }
                        
                        # Add jitter to avoid thundering herd
                        if attempt > 0:
                            jitter = random.uniform(0.5, 2.0)
                            self.debug.emit(f"⏱️ Waiting {jitter:.1f}s...")
                            time.sleep(jitter)
                        
                        start_time = time.time()
                        response = requests.post(
                            endpoint,
                            headers=headers,
                            json=config,
                            timeout=30 + (attempt * 10)  # Increase timeout with attempts
                        )
                        
                        latency = time.time() - start_time
                        self.debug.emit(f"📊 Response: {response.status_code} in {latency:.2f}s")
                        
                        if response.status_code == 200:
                            try:
                                reply = response.json()
                                if "candidates" in reply and len(reply["candidates"]) > 0:
                                    candidate = reply["candidates"][0]
                                    
                                    # Check for safety blocks
                                    if "finishReason" in candidate:
                                        if candidate["finishReason"] == "SAFETY":
                                            self.error.emit("Response blocked by safety filters. Please rephrase your message.")
                                            return
                                        elif candidate["finishReason"] == "RECITATION":
                                            self.error.emit("Response blocked due to recitation. Please try a different question.")
                                            return
                                    
                                    if "content" in candidate and "parts" in candidate["content"]:
                                        if len(candidate["content"]["parts"]) > 0:
                                            text = candidate["content"]["parts"][0]["text"]
                                            self.debug.emit("✅ Success!")
                                            self.finished.emit(text)
                                            return
                                
                                self.debug.emit("❌ Empty or invalid response structure")
                                
                            except json.JSONDecodeError:
                                self.debug.emit("❌ Invalid JSON response")
                                continue
                                
                        elif response.status_code == 503:
                            # Service unavailable - wait longer before retry
                            wait_time = (2 ** attempt) + random.uniform(1, 3)
                            self.debug.emit(f"⚠️ Service unavailable (503), waiting {wait_time:.1f}s...")
                            time.sleep(wait_time)
                            continue
                            
                        elif response.status_code == 429:
                            # Rate limited - wait even longer
                            wait_time = (3 ** attempt) + random.uniform(2, 5)
                            self.debug.emit(f"⚠️ Rate limited (429), waiting {wait_time:.1f}s...")
                            time.sleep(wait_time)
                            continue
                            
                        elif response.status_code == 400:
                            self.debug.emit(f"❌ Bad request (400): {response.text[:100]}")
                            continue
                            
                        else:
                            self.debug.emit(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                            continue
                            
                    except requests.exceptions.Timeout:
                        self.debug.emit(f"⏰ Timeout on endpoint {endpoint_idx + 1}, config {config_idx + 1}")
                        continue
                        
                    except requests.exceptions.ConnectionError:
                        self.debug.emit(f"🔌 Connection error on endpoint {endpoint_idx + 1}")
                        continue
                        
                    except Exception as e:
                        self.debug.emit(f"❌ Exception: {str(e)[:50]}")
                        continue
            
            # Wait before next main attempt
            if attempt < 2:  # Don't wait after last attempt
                wait_time = (2 ** attempt) * 3 + random.uniform(1, 3)
                self.debug.emit(f"⏳ Waiting {wait_time:.1f}s before next attempt...")
                time.sleep(wait_time)
        
        # If we get here, all attempts failed
        self.error.emit("All connection attempts failed. The Gemini API service appears to be overloaded or temporarily unavailable. Please try again in a few minutes.")


# === Enhanced Chat Dialog ===
class ChatDialog(QDialog):
    def __init__(self, existing_history=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EzChat")
        self.setWindowIcon(QIcon("UI/icons/ezz.png"))
        self.setMinimumSize(700, 800)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                background-color: white;
                font-size: 14px;
                line-height: 1.4;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QLineEdit:disabled {
                background-color: #f0f0f0;
                color: #999;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666;
            }
        """)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # Debug display
        self.debug_display = QTextEdit()
        self.debug_display.setReadOnly(True)
        self.debug_display.setMaximumHeight(120)
        self.debug_display.setStyleSheet("background-color: #f8f9fa; font-family: monospace; font-size: 11px;")
        self.debug_display.hide()
        
        # Input area
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("💬 Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        # Buttons
        self.send_button = QPushButton("📤 Send")
        self.send_button.clicked.connect(self.send_message)

        self.new_chat_button = QPushButton("🆕 New Chat")
        self.new_chat_button.clicked.connect(self.clear_chat)

        self.test_connection_button = QPushButton("🔗 Deep Test")
        self.test_connection_button.clicked.connect(self.test_connection)

        self.debug_button = QPushButton("🔍 Debug")
        self.debug_button.clicked.connect(self.toggle_debug)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("🛡️ Welcome to EzChat")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #2c3e50; 
            text-align: center; 
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        layout.addWidget(self.chat_display)
        layout.addWidget(self.debug_display)
        
        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.new_chat_button)
        btn_layout.addWidget(self.test_connection_button)
        btn_layout.addWidget(self.debug_button)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Worker setup
        self.worker = None
        self.connection_worker = None
        self.loading_timer = QTimer()
        self.loading_stage = 0
        self.loading_enabled = False
        self.is_processing = False
        self.current_typing_id = None
        self.debug_visible = False

        # Load existing history
        if existing_history:
            self.chat_display.setHtml(existing_history)
        else:
            welcome_msg = """
            
            """
            self.chat_display.setHtml(welcome_msg)

    def toggle_debug(self):
        self.debug_visible = not self.debug_visible
        if self.debug_visible:
            self.debug_display.show()
            self.debug_button.setText("🔍 Hide Debug")
        else:
            self.debug_display.hide()
            self.debug_button.setText("🔍 Debug")

    def add_debug_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.debug_display.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.debug_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def test_connection(self):
        if self.is_processing:
            return
            
        self.test_connection_button.setEnabled(False)
        self.status_label.setText("🔍 Running deep connection test...")
        self.add_debug_message("🔍 Starting deep connection test...")
        
        self.connection_worker = ConnectionTestWorker()
        self.connection_worker.finished.connect(self.handle_connection_test)
        self.connection_worker.start()

    def handle_connection_test(self, success, message, details):
        self.test_connection_button.setEnabled(True)
        
        # Log all details to debug
        for key, value in details.items():
            self.add_debug_message(f"📊 {key}: {value}")
        
        if success:
            self.status_label.setText("✅ Deep test successful!")
            detail_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
            QMessageBox.information(
                self, "Deep Connection Test - SUCCESS", 
                f"✅ Connection tests passed!\n\n{message}\n\nDetails:\n{detail_text}"
            )
        else:
            self.status_label.setText(f"❌ Deep test failed: {message}")
            detail_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
            
            # Provide specific advice based on the results
            advice = "\n\nRecommendations:\n"
            if "503" in str(details) or "SERVICE_UNAVAILABLE" in str(details):
                advice += "• API service is overloaded - try again in 5-10 minutes\n"
                advice += "• Use shorter messages to reduce server load\n"
                advice += "• Try during off-peak hours\n"
            elif "TIMEOUT" in str(details):
                advice += "• Your connection may be slow\n"
                advice += "• Try using a VPN\n"
                advice += "• Check firewall settings\n"
            elif "RATE_LIMITED" in str(details):
                advice += "• You're sending requests too quickly\n"
                advice += "• Wait a few minutes between messages\n"
            else:
                advice += "• Check internet connection\n"
                advice += "• Verify API key is valid\n"
                advice += "• Try VPN if blocked regionally\n"
            
            QMessageBox.warning(
                self, "Deep Connection Test - FAILED", 
                f"❌ {message}\n\nDetails:\n{detail_text}{advice}"
            )
        
        QTimer.singleShot(5000, lambda: self.status_label.setText(""))

    def get_history(self):
        return self.chat_display.toHtml()

    def clear_chat(self):
        if self.is_processing:
            QMessageBox.warning(self, "Processing", "Please wait for current message to complete.")
            return
            
        reply = QMessageBox.question(self, "Clear Chat", "Clear all messages?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            welcome_msg = """
            <div style="text-align: center; color: #666; font-style: italic; margin: 20px 0;">
                New chat started! 🆕<br>
                What would you like to talk about?
            </div>
            """
            self.chat_display.setHtml(welcome_msg)
            self.debug_display.clear()

    def send_message(self):
        if self.is_processing:
            self.status_label.setText("⏳ Please wait for current response...")
            return
            
        user_text = self.input_field.text().strip()
        if not user_text:
            return

        self.is_processing = True
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        self.new_chat_button.setEnabled(False)
        self.test_connection_button.setEnabled(False)
        
        self.add_debug_message(f"📤 Sending: {user_text[:50]}{'...' if len(user_text) > 50 else ''}")
        self.status_label.setText("🛡️ Sending with bulletproof retry logic...")

        # Add user message
        user_message_html = f"""
        <div style="margin: 15px 0; padding: 12px; background-color: #007acc; color: red; 
                    border-radius: 15px 15px 5px 15px; max-width: 80%; margin-left: auto; 
                    text-align: right;">
            <div style="font-size:14; font-weight: bold; margin-bottom: 5px;">👤 You</div>
            <div style="font-size:12; font-weight: bold; margin-bottom: 5px; color: red;>{user_text}</div>
        </div>
        """
        
        current_html = self.chat_display.toHtml()
        self.chat_display.setHtml(current_html + user_message_html)
        self.scroll_to_bottom()

        # Generate unique ID for typing message
        self.current_typing_id = f"typing_{int(time.time() * 1000)}"

        # Add typing indicator
        typing_message_html = f"""
        <div id="{self.current_typing_id}" style="margin: 15px 0; padding: 12px; background-color: #f1f2f6; 
                    border-radius: 15px 15px 15px 5px; max-width: 80%; margin-right: auto;">
            <div style="font-size:14; font-weight: bold; margin-bottom: 5px; color: #007acc;">🤖 Gemini</div>
            <div style="color: #666; font-style: italic;">Typing...</div>
        </div>
        """
        
        current_html = self.chat_display.toHtml()
        self.chat_display.setHtml(current_html + typing_message_html)
        self.scroll_to_bottom()

        # Start typing animation
        self.loading_stage = 0
        self.loading_enabled = True
        self.loading_timer.timeout.connect(self.update_loading)
        self.loading_timer.start(1200)

        # Start bulletproof API call
        self.worker = BulletproofGeminiWorker(user_text)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.progress.connect(self.handle_progress)
        self.worker.debug.connect(self.add_debug_message)
        self.worker.start()

    def handle_progress(self, message):
        self.status_label.setText(f"🛡️ {message}")

    def scroll_to_bottom(self):
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_loading(self):
        if not self.loading_enabled or not self.current_typing_id:
            return

        self.loading_stage = (self.loading_stage + 1) % 4
        states = [
            "trying multiple strategies",
            "trying multiple strategies.",
            "trying multiple strategies..",
            "trying multiple strategies..."
        ]
        current_state = states[self.loading_stage]
        
        current_html = self.chat_display.toHtml()
        
        if f'id="{self.current_typing_id}"' in current_html:
            lines = current_html.split('\n')
            updated_lines = []
            skip_lines = 0
            
            for i, line in enumerate(lines):
                if skip_lines > 0:
                    skip_lines -= 1
                    continue
                    
                if f'id="{self.current_typing_id}"' in line:
                    skip_lines = 3
                    updated_typing = f"""
        <div id="{self.current_typing_id}" style="margin: 15px 0; padding: 12px; background-color: #f1f2f6; 
                    border-radius: 15px 15px 15px 5px; max-width: 80%; margin-right: auto;">
            <div style="fpnt-size:14; font-weight: bold; margin-bottom: 5px; color: #007acc;">🤖 Gemini</div>
            <div style="color: #666; font-style: italic;">{current_state}</div>
        </div>
        """
                    updated_lines.append(updated_typing)
                else:
                    updated_lines.append(line)
            
            self.chat_display.setHtml('\n'.join(updated_lines))
            self.scroll_to_bottom()

    def handle_response(self, reply_text):
        self.stop_loading()
        self.add_debug_message("✅ Response received successfully!")
        
        formatted_reply = markdown_to_html(reply_text)
        
        gemini_message_html = f"""
        <div style="margin: 15px 0; padding: 12px; background-color: #f1f2f6; 
                    border-radius: 15px 15px 15px 5px; max-width: 80%; margin-right: auto;">
            <div style="fpnt-size:17; font-weight: bold; margin-bottom: 8px; color: #007acc;">🤖 Gemini</div>
            <div style="line-height: 1.5;">{formatted_reply}</div>
        </div>
        """
        
        self.replace_typing_message(gemini_message_html)
        self.reset_ui_state()
        self.status_label.setText("✅ Message sent successfully!")
        
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
        self.scroll_to_bottom()

    def handle_error(self, error_msg):
        self.stop_loading()
        self.add_debug_message(f"❌ All strategies failed: {error_msg}")
        
        error_message_html = f"""
        <div style="margin: 15px 0; padding: 12px; background-color: #ffe6e6; 
                    border-radius: 15px; border-left: 4px solid #ff4757; max-width: 80%; margin-right: auto;">
            <div style="font-weight: bold; margin-bottom: 5px; color: #ff4757;">🛡️ All Strategies Failed</div>
            <div style="color: #333; margin-bottom: 8px;">{error_msg}</div>
            <div style="color: #666; font-size: 12px;">
                💡 The API service may be overloaded. Try again in 5-10 minutes or use shorter messages.
            </div>
        </div>
        """
        
        self.replace_typing_message(error_message_html)
        self.reset_ui_state()
        self.status_label.setText("❌ Service temporarily unavailable")
        self.scroll_to_bottom()

    def replace_typing_message(self, new_content):
        current_html = self.chat_display.toHtml()
        
        if f'id="{self.current_typing_id}"' in current_html:
            lines = current_html.split('\n')
            updated_lines = []
            skip_lines = 0
            
            for i, line in enumerate(lines):
                if skip_lines > 0:
                    skip_lines -= 1
                    continue
                    
                if f'id="{self.current_typing_id}"' in line:
                    skip_lines = 3
                    updated_lines.append(new_content)
                else:
                    updated_lines.append(line)
            
            self.chat_display.setHtml('\n'.join(updated_lines))
        else:
            self.chat_display.setHtml(current_html + new_content)

    def reset_ui_state(self):
        self.is_processing = False
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.new_chat_button.setEnabled(True)
        self.test_connection_button.setEnabled(True)
        self.input_field.setFocus()

    def stop_loading(self):
        self.loading_enabled = False
        self.loading_timer.stop()
        self.current_typing_id = None

    def closeEvent(self, event):
        if self.is_processing:
            reply = QMessageBox.question(self, "Close Chat", "Message being processed. Close anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.terminate()
            self.worker.wait()
        
        if self.connection_worker and self.connection_worker.isRunning():
            self.connection_worker.terminate()
            self.connection_worker.wait()
        
        event.accept()
