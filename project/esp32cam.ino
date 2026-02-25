#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "281G26";
const char* WIFI_PASS = "hotspot1";

WebServer server(80);

// Set resolution (Lower = Higher FPS)
// Choices: QVGA(320x240), VGA(640x480), SVGA(800x600)
static auto hiRes = esp32cam::Resolution::find(800, 600);

void handleStream() {
  auto client = server.client();
  auto frame = esp32cam::capture();
  
  if (frame) {
    // Basic MJPEG Header
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
    client.println();

    while (client.connected()) {
      frame = esp32cam::capture();
      if (!frame) break;

      client.printf("--frame\r\n");
      client.printf("Content-Type: image/jpeg\r\n");
      client.printf("Content-Length: %u\r\n\r\n", frame->size());
      frame->writeTo(client);
      client.printf("\r\n");
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Camera configuration
  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker); // Most common model
  cfg.setResolution(hiRes);
  cfg.setBufferCount(2);
  cfg.setXclk(20);
  cfg.setJpeg(80); // Quality 10-63 (lower is better quality)

  if (!Camera.begin(cfg)) {
    Serial.println("Camera Init Failed");
  }

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
  
  Serial.print("Stream Link: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");

  server.on("/stream", handleStream);
  server.begin();
}

void loop() {
  server.handleClient();
}
