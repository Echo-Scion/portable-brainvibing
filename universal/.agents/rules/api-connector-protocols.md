---
description: Standardized rules for interacting with external APIs, ensuring safety and data integrity.
---

# API Connector Protocols

## Safety First
1. Always validate incoming data against expected schemas before processing.
2. Use strong typing for API responses.
3. Gracefully handle network timeouts and errors.

## Standard Formats
1. Prefer JSON for REST payloads.
2. Ensure consistent date formatting (ISO 8601).
3. Always implement pagination for list endpoints.

## Authentication
1. Never log bearer tokens or API keys.
2. Ensure tokens are stored securely based on the platform's best practices.
