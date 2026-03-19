# API Reference

## Overview

The Quantum Consciousness VAE system exposes a comprehensive RESTful API for integration with external systems. All API endpoints follow standard REST conventions and return JSON-formatted responses.

## Authentication

Most API endpoints require authentication using JWT (JSON Web Tokens). Obtain a token by authenticating with valid credentials:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Include the JWT token in subsequent requests:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

## Base URL

```
https://api.tmt-os.ai/v1
```

## API Endpoints

### Model Management

#### Train Model
Starts a new training session for the quantum consciousness model.

```http
POST /api/v1/model/train
```

**Parameters:**
- `dataset_id` (string, required): Identifier for the training dataset
- `epochs` (integer, optional): Number of training epochs (default: 100)
- `batch_size` (integer, optional): Batch size for training (default: 32)

**Response:**
```json
{
  "job_id": "abc123",
  "status": "started",
  "message": "Training job initiated successfully"
}
```

#### Get Training Status
Retrieves the status of a training job.

```http
GET /api/v1/model/train/{job_id}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "running",
  "progress": 0.75,
  "metrics": {
    "epoch": 75,
    "total_epochs": 100,
    "loss": 0.234,
    "accuracy": 0.92
  }
}
```

#### Cancel Training
Cancels an ongoing training job.

```http
DELETE /api/v1/model/train/{job_id}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "cancelled",
  "message": "Training job cancelled successfully"
}
```

### Inference

#### Perform Inference
Runs inference on quantum state data using the trained model.

```http
POST /api/v1/model/inference
```

**Parameters:**
- `input_data` (array, required): Input quantum state data
- `model_version` (string, optional): Specific model version to use

**Response:**
```json
{
  "result": {
    "predicted_state": [0.8, 0.2, 0.1, 0.9],
    "confidence": 0.95,
    "quantum_metrics": {
      "fidelity": 0.92,
      "coherence": 0.88,
      "entropy": 1.2
    }
  }
}
```

### Consciousness Analysis

#### Analyze Consciousness Patterns
Analyzes EEG or other consciousness-related data.

```http
POST /api/v1/consciousness/analyze
```

**Parameters:**
- `data` (array, required): Consciousness data (EEG signals, etc.)
- `analysis_type` (string, optional): Type of analysis to perform

**Response:**
```json
{
  "consciousness_level": "transcendent",
  "metrics": {
    "complexity": 0.87,
    "coherence": 0.91,
    "integration": 0.78
  },
  "recommendations": [
    "Increase meditation practice",
    "Optimize sleep schedule"
  ]
}
```

#### Get Consciousness History
Retrieves historical consciousness data for a user.

```http
GET /api/v1/consciousness/history
Query Parameters:
- user_id (string, required): User identifier
- start_date (string, optional): Start date (ISO 8601 format)
- end_date (string, optional): End date (ISO 8601 format)
```

**Response:**
```json
{
  "user_id": "user123",
  "data_points": [
    {
      "timestamp": "2026-03-15T10:30:00Z",
      "consciousness_level": "awake",
      "metrics": {
        "alpha_waves": 0.75,
        "beta_waves": 0.82,
        "theta_waves": 0.45
      }
    }
  ]
}
```

### Quantum Metrics

#### Get Current Quantum Metrics
Retrieves current quantum system performance metrics.

```http
GET /api/v1/quantum/metrics
```

**Response:**
```json
{
  "system_health": "optimal",
  "fidelity": 0.95,
  "coherence": 0.92,
  "entropy": 1.15,
  "hardware_status": {
    "qubits_operational": 64,
    "error_rate": 0.001,
    "temperature": "15mK"
  }
}
```

#### Get Quantum Metrics History
Retrieves historical quantum metrics data.

```http
GET /api/v1/quantum/metrics/history
Query Parameters:
- hours (integer, optional): Number of hours of history (default: 24)
```

**Response:**
```json
{
  "metrics": [
    {
      "timestamp": "2026-03-15T10:30:00Z",
      "fidelity": 0.94,
      "coherence": 0.91,
      "entropy": 1.12
    }
  ]
}
```

### Node Management

#### Get Node Status
Retrieves the status of all system nodes.

```http
GET /api/v1/nodes/status
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "metatron",
      "name": "Metatron Coordinator",
      "status": "online",
      "health": "optimal",
      "last_heartbeat": "2026-03-15T10:30:45Z"
    }
  ]
}
```

#### Restart Node
Restarts a specific system node.

```http
POST /api/v1/nodes/{node_id}/restart
```

**Response:**
```json
{
  "node_id": "metatron",
  "status": "restarting",
  "message": "Node restart initiated"
}
```

### System Administration

#### Get System Health
Retrieves overall system health status.

```http
GET /api/v1/system/health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": "15d 4h 32m",
  "version": "1.2.3",
  "components": {
    "database": "online",
    "cache": "online",
    "quantum_hardware": "connected",
    "api_gateway": "operational"
  }
}
```

#### Get System Logs
Retrieves recent system logs.

```http
GET /api/v1/system/logs
Query Parameters:
- level (string, optional): Log level filter (debug, info, warn, error)
- limit (integer, optional): Number of log entries (default: 100)
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2026-03-15T10:30:45Z",
      "level": "info",
      "message": "Model training epoch 75 completed",
      "component": "quantum_vae"
    }
  ]
}
```

## Error Responses

All API endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid input parameters",
  "code": 400
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication token missing or invalid",
  "code": 401
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions for this operation",
  "code": 403
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Requested resource not found",
  "code": 404
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "code": 500
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Anonymous requests**: 60 requests per hour
- **Authenticated requests**: 1000 requests per hour
- **Premium accounts**: 10000 requests per hour

Exceeding rate limits will result in a 429 Too Many Requests response.

## WebSocket API

For real-time updates, the system also provides a WebSocket API:

```
wss://api.tmt-os.ai/ws
```

### Available Channels

- `model.training`: Real-time training progress updates
- `quantum.metrics`: Live quantum system metrics
- `consciousness.stream`: Real-time consciousness data stream
- `system.alerts`: Critical system alerts and notifications

### WebSocket Example

```javascript
const socket = new WebSocket('wss://api.tmt-os.ai/ws');

socket.onopen = function(event) {
  // Subscribe to channels
  socket.send(JSON.stringify({
    "action": "subscribe",
    "channel": "model.training"
  }));
};

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## SDKs and Libraries

Official client libraries are available for popular programming languages:

- **Python**: `pip install tmt-os-sdk`
- **JavaScript**: `npm install @tmt-os/sdk`
- **Java**: Maven dependency available
- **Go**: Go modules support

For SDK documentation, visit [SDK Documentation](../sdk/README.md).