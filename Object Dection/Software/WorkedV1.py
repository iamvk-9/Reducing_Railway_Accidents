from flask import Flask, Response, jsonify, request
import cv2
import numpy as np
import requests

app = Flask(__name__)

# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()

# Get unconnected output layers
unconnected_out_layers = net.getUnconnectedOutLayers()

# If the output is a single scalar, convert it to a list
if isinstance(unconnected_out_layers, np.ndarray):
    unconnected_out_layers = unconnected_out_layers.flatten()

output_layers = [layer_names[i - 1] for i in unconnected_out_layers]

# Load class names
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# ESP32-CAM URL and IP
ESP32_CAM_URL = 'http://192.168.0.9/cam-hi.jpg'  # Replace with your ESP32-CAM's IP address
ESP32_CAM_IP = '192.168.0.9'  # Replace with your ESP32-CAM's IP address

# Global variables to store the latest detections and distance
latest_detections = []
latest_distance = "N/A"

# Define living and non-living classes
living_classes = ['person', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
non_living_classes = ['bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat']

def update_esp32_detection(detections):
    living_detected = any(detection['label'].lower() in living_classes for detection in detections)
    non_living_detected = any(detection['label'].lower() in non_living_classes for detection in detections)
    
    try:
        response = requests.post(f'http://{ESP32_CAM_IP}/update_detection', 
                               json={'living_detected': living_detected, 'non_living_detected': non_living_detected},
                               timeout=1)
        if response.status_code == 200:
            print("Successfully updated ESP32-CAM")
        else:
            print(f"Failed to update ESP32-CAM: {response.status_code}")
    except Exception as e:
        print(f"Error updating ESP32-CAM: {e}")

def generate_frames():
    global latest_detections, latest_distance
    while True:
        try:
            # Get the video stream from the ESP32-CAM
            response = requests.get(ESP32_CAM_URL, stream=True)
            if response.status_code == 200:
                # Get the distance from the header
                latest_distance = response.headers.get('X-Distance', 'N/A')
                
                bytes_data = b''
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]
                        frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)

                        # YOLO Object Detection
                        height, width, channels = frame.shape
                        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                        net.setInput(blob)
                        outputs = net.forward(output_layers)

                        # Process detections
                        boxes = []
                        confidences = []
                        class_ids = []
                        for output in outputs:
                            for detection in output:
                                scores = detection[5:]
                                class_id = np.argmax(scores)
                                confidence = scores[class_id]
                                if confidence > 0.5:  # Confidence threshold
                                    center_x = int(detection[0] * width)
                                    center_y = int(detection[1] * height)
                                    w = int(detection[2] * width)
                                    h = int(detection[3] * height)

                                    # Rectangle coordinates
                                    x = int(center_x - w / 2)
                                    y = int(center_y - h / 2)

                                    boxes.append([x, y, w, h])
                                    confidences.append(float(confidence))
                                    class_ids.append(class_id)

                        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                        
                        # Update latest_detections
                        current_detections = []
                        for i in range(len(boxes)):
                            if i in indexes:
                                x, y, w, h = boxes[i]
                                label = str(classes[class_ids[i]])
                                confidence = confidences[i]
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                cv2.putText(frame, f'{label} {confidence:.2f}', (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                                current_detections.append({
                                    'label': label,
                                    'confidence': confidence
                                })
                        latest_detections = current_detections

                        # Update ESP32-CAM with detection results
                        update_esp32_detection(current_detections)

                        # Add distance to the frame
                        cv2.putText(frame, f'Distance: {latest_distance} cm', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                        _, buffer = cv2.imencode('.jpg', frame)
                        frame = buffer.tobytes()

                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                print("Failed to get a valid response from ESP32-CAM.")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'Error frame' + b'\r\n')
        except Exception as e:
            print(f"Error: {e}")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'Error frame' + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_detections')
def get_detections():
    return jsonify({
        'detections': latest_detections,
        'distance': latest_distance
    })

@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>ESP32-CAM Stream with YOLO Detection</title>
                <style>
                    .container {
                        display: flex;
                        padding: 20px;
                    }
                    .video-container {
                        flex: 2;
                    }
                    .info-container {
                        flex: 1;
                        margin-left: 20px;
                        padding: 20px;
                        background-color: #f0f0f0;
                        border-radius: 5px;
                    }
                    #detections-list, #distance {
                        list-style-type: none;
                        padding: 0;
                    }
                    .detection-item, #distance {
                        margin: 5px 0;
                        padding: 10px;
                        background-color: white;
                        border-radius: 3px;
                    } </style>
            </head>
            <body>
                <div class="container">
                    <div class="video-container">
                        <img src="/video_feed" style="width: 100%;"/>
                    </div>
                    <div class="info-container">
                        <h2>Detections:</h2>
                        <ul id="detections-list"></ul>
                        <h2>Distance:</h2>
                        <p id="distance"></p>
                    </div>
                </div>
                <script>
                    const detectionsList = document.getElementById('detections-list');
                    const distanceElement = document.getElementById('distance');
                    const updateInterval = 1000; // Update interval in milliseconds

                    function updateDetections() {
                        fetch('/get_detections')
                            .then(response => response.json())
                            .then(data => {
                                const detectionsHtml = data.detections.map(detection => `
                                    <li class="detection-item">
                                        <span>${detection.label}</span>
                                        <span>(${detection.confidence.toFixed(2)})</span>
                                    </li>
                                `).join('');
                                detectionsList.innerHTML = detectionsHtml;
                                distanceElement.textContent = `Distance: ${data.distance} cm`;
                            });
                    }

                    setInterval(updateDetections, updateInterval);
                </script>
            </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)