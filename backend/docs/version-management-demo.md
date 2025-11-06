# Prompt Version Management Demo

This document demonstrates the enhanced version management features implemented in Feature 2.

## 🎯 Features Implemented

### Core Version Management

- ✅ **Version Creation** - Create new versions with change notes
- ✅ **Version History** - Get detailed version history with optional content
- ✅ **Version Comparison** - Compare versions with diff analysis
- ✅ **Version Revert** - Revert to previous versions
- ✅ **Duplicate Prevention** - Prevent creating identical versions

### Enhanced Features

- ✅ **Latest Version API** - Quick access to the latest version
- ✅ **Detailed Comparison** - HTML diff, unified diff, and statistics
- ✅ **Content Preview** - Preview content without full payload
- ✅ **Smart Version Numbering** - Automatic version numbering

## 📚 API Endpoints

### Basic Version Management

```http
GET    /api/v1/prompts/{prompt_id}/versions              # List versions
POST   /api/v1/prompts/{prompt_id}/versions              # Create version
GET    /api/v1/prompts/{prompt_id}/versions/{version_id} # Get specific version
PUT    /api/v1/prompts/{prompt_id}/versions/{version_id} # Update version
DELETE /api/v1/prompts/{prompt_id}/versions/{version_id} # Delete version
```

### Enhanced Version Management

```http
GET  /api/v1/prompts/{prompt_id}/versions/history           # Version history
GET  /api/v1/prompts/{prompt_id}/versions/latest            # Latest version
GET  /api/v1/prompts/{prompt_id}/versions/compare           # Simple comparison
GET  /api/v1/prompts/{prompt_id}/versions/compare/detailed  # Detailed comparison
POST /api/v1/prompts/{prompt_id}/versions/revert            # Revert to version
POST /api/v1/prompts/{prompt_id}/versions/from-content      # Create from content
```

## 🚀 Usage Examples

### 1. Create a Prompt and Versions

```bash
# Create a prompt
curl -X POST "http://localhost:8000/api/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer Support Response",
    "description": "Template for customer support responses",
    "content": "Hello! Thank you for contacting us. How can I help you today?",
    "tags": ["support", "template"]
  }'

# Create version 1
curl -X POST "http://localhost:8000/api/v1/prompts/{prompt_id}/versions" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! Thank you for contacting our support team. How may I assist you today?",
    "change_notes": "Made more professional and specific to support team"
  }'

# Create version 2
curl -X POST "http://localhost:8000/api/v1/prompts/{prompt_id}/versions" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! Thank you for reaching out to our premium support team. I'\''m here to help resolve your issue. What can I assist you with today?",
    "change_notes": "Added premium branding and more helpful tone"
  }'
```

### 2. Get Version History

```bash
# Get basic history
curl "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/history"

# Get history with full content
curl "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/history?include_content=true"
```

### 3. Compare Versions

```bash
# Simple comparison
curl "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/compare?version_a=1&version_b=2"

# Detailed comparison with HTML diff
curl "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/compare/detailed?version_a=1&version_b=2&include_diff=true"
```

### 4. Revert to Previous Version

```bash
# Revert to version 1 with custom notes
curl -X POST "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/revert?version_number=1&change_notes=Reverted due to customer feedback"
```

### 5. Get Latest Version

```bash
# Quick access to latest version
curl "http://localhost:8000/api/v1/prompts/{prompt_id}/versions/latest"
```

## 📊 Response Examples

### Version History Response

```json
{
  "prompt_id": "123e4567-e89b-12d3-a456-426614174000",
  "history": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "version_number": 3,
      "change_notes": "Reverted due to customer feedback",
      "created_at": "2025-11-06T10:30:00Z",
      "updated_at": "2025-11-06T10:30:00Z"
    },
    {
      "id": "789e0123-e89b-12d3-a456-426614174002",
      "version_number": 2,
      "change_notes": "Added premium branding and more helpful tone",
      "created_at": "2025-11-06T10:25:00Z",
      "updated_at": "2025-11-06T10:25:00Z"
    }
  ],
  "total_versions": 3
}
```

### Detailed Comparison Response

```json
{
  "version_a": {
    "version_number": 1,
    "content": "Hello! Thank you for contacting our support team. How may I assist you today?",
    "change_notes": "Made more professional and specific to support team",
    "created_at": "2025-11-06T10:20:00Z"
  },
  "version_b": {
    "version_number": 2,
    "content": "Hello! Thank you for reaching out to our premium support team. I'm here to help resolve your issue. What can I assist you with today?",
    "change_notes": "Added premium branding and more helpful tone",
    "created_at": "2025-11-06T10:25:00Z"
  },
  "is_identical": false,
  "unified_diff": "@@ -1 +1 @@\n-Hello! Thank you for contacting our support team. How may I assist you today?\n+Hello! Thank you for reaching out to our premium support team. I'm here to help resolve your issue. What can I assist you with today?\n",
  "html_diff": "<table>...</table>",
  "stats": {
    "additions": 3,
    "deletions": 2,
    "modifications": 1,
    "total_changes": 6
  }
}
```

## 🛡️ Business Logic Features

### Duplicate Prevention

The system prevents creating identical versions:

```bash
# This will return 400 Bad Request
curl -X POST "http://localhost:8000/api/v1/prompts/{prompt_id}/versions" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! Thank you for reaching out to our premium support team. I'\''m here to help resolve your issue. What can I assist you with today?",
    "change_notes": "Duplicate version"
  }'

# Response: {"detail": "Content is identical to latest version"}
```

### Smart Version Numbering

Versions are automatically numbered sequentially (1, 2, 3, ...)

### Content Preview

Each version includes a content preview (first 100 characters) for quick display without loading full content.

## 🧪 Testing

All version management features are tested with:

- Contract tests for API compliance
- Business logic tests for duplicate prevention
- Integration tests for version comparison
- Edge case tests for empty prompts and invalid versions

Run tests:

```bash
uv run python -m pytest tests/contract/test_versions.py -v
```

## 🎉 Summary

Feature 2 provides a comprehensive version management system with:

- **Full CRUD operations** for prompt versions
- **Advanced comparison** with diff visualization and statistics
- **Smart revert functionality** with change tracking
- **Duplicate prevention** to maintain clean version history
- **Rich metadata** including change notes and timestamps
- **Business logic services** for complex operations

This forms the foundation for advanced prompt management and comparison features in subsequent phases.
