#include "WiFi.h"
#include "esp_camera.h"
#include <WebServer.h>

// WiFi Credentials
const char* ssid = "WIFI_NAME"; // Replace with your WiFi
const char* password = "WIFI PASSWORD"; // Replace with your password

// Set up WebServer on port 80
WebServer server(80);

// Forward declaration
void startCameraServer();

// ---- Stream Handler ----
void handleJPGStream() {
  WiFiClient client = server.client();
  camera_fb_t * fb = NULL;
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent(response);

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    response = "--frame\r\n";
    response += "Content-Type: image/jpeg\r\n\r\n";
    server.sendContent(response);
    server.sendContent((const char*)fb->buf, fb->len);
    server.sendContent("\r\n");
    esp_camera_fb_return(fb);

    if (!client.connected()) break;
  }
}

// ---- Start Camera Server ----
void startCameraServer() {
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", "<img src=\"/stream\">");
  });
  server.on("/stream", HTTP_GET, handleJPGStream);
  server.begin();
}

unsigned long last_time = 0;
int frame_count = 0;

// Call this in your stream loop:
// printFPS();
// ---- Setup ----
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Booting...");

  // Camera Config (AI Thinker ESP32-CAM)
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5; config.pin_d1 = 18;
  config.pin_d2 = 19; config.pin_d3 = 21;
  config.pin_d4 = 36; config.pin_d5 = 39;
  config.pin_d6 = 34; config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 24000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA; // 640x480
  config.jpeg_quality = 12;           // Lower = better quality (10-63)
  config.fb_count = 2;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("Camera Ready! View at: http://");
  Serial.println(WiFi.localIP());

  // Start the server
  startCameraServer();
}

// ---- Loop ----
void loop() {
  server.handleClient();  // Handle web requests
}
