# Data Model: Prompt Management System

**Feature ID:** 001  
**Based on:** `spec.md` version 2025-11-06  
**Created:** 2025-11-06

---

## Entity Definitions

### Prompt

The main entity representing a prompt template with metadata.

```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_prompts_title_gin ON prompts USING gin(to_tsvector('english', title));
CREATE INDEX idx_prompts_description_gin ON prompts USING gin(to_tsvector('english', description));
CREATE INDEX idx_prompts_tags ON prompts USING gin(tags);
CREATE INDEX idx_prompts_created_at ON prompts(created_at DESC);
```

### PromptVersion

Represents a specific version of a prompt's content.

```sql
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(prompt_id, version_number)
);
```

**Indexes:**
```sql
CREATE INDEX idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX idx_prompt_versions_content_gin ON prompt_versions USING gin(to_tsvector('english', content));
CREATE INDEX idx_prompt_versions_created_at ON prompt_versions(created_at DESC);
```

### LLMConfig

Configuration for LLM providers.

```sql
CREATE TABLE llm_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'google', 'local'
    api_key_encrypted TEXT NOT NULL,
    base_url VARCHAR(500),
    model VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}', -- temperature, max_tokens, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_llm_configs_provider ON llm_configs(provider);
CREATE INDEX idx_llm_configs_is_active ON llm_configs(is_active);
```

### Comparison

Stores comparison results between prompts or across LLMs.

```sql
CREATE TABLE comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('version_comparison', 'cross_llm')),
    input_text TEXT NOT NULL,
    results JSONB NOT NULL, -- Structured comparison results
    metadata JSONB DEFAULT '{}', -- Execution times, token counts, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_comparisons_type ON comparisons(type);
CREATE INDEX idx_comparisons_created_at ON comparisons(created_at DESC);
CREATE INDEX idx_comparisons_results_gin ON comparisons USING gin(results);
```

### ComparisonPromptVersion

Junction table for comparisons involving multiple prompt versions.

```sql
CREATE TABLE comparison_prompt_versions (
    comparison_id UUID NOT NULL REFERENCES comparisons(id) ON DELETE CASCADE,
    prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
    llm_config_id UUID REFERENCES llm_configs(id), -- NULL for version_comparison
    result JSONB NOT NULL, -- Individual execution result
    PRIMARY KEY (comparison_id, prompt_version_id, llm_config_id)
);
```

**Indexes:**
```sql
CREATE INDEX idx_comparison_pv_comparison_id ON comparison_prompt_versions(comparison_id);
CREATE INDEX idx_comparison_pv_prompt_version_id ON comparison_prompt_versions(prompt_version_id);
```

---

## JSON Schema Definitions

### Comparison Results Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "executions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "prompt_version_id": {"type": "string"},
          "llm_config_id": {"type": "string"},
          "output": {"type": "string"},
          "execution_time_ms": {"type": "integer"},
          "tokens_used": {"type": "integer"},
          "error": {"type": "string"},
          "status": {"type": "string", "enum": ["success", "error", "timeout"]}
        },
        "required": ["prompt_version_id", "status"]
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_executions": {"type": "integer"},
        "successful_executions": {"type": "integer"},
        "average_execution_time_ms": {"type": "number"},
        "total_tokens_used": {"type": "integer"}
      }
    }
  },
  "required": ["executions", "summary"]
}
```

### LLM Parameters Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "temperature": {"type": "number", "minimum": 0, "maximum": 2},
    "max_tokens": {"type": "integer", "minimum": 1},
    "top_p": {"type": "number", "minimum": 0, "maximum": 1},
    "frequency_penalty": {"type": "number", "minimum": -2, "maximum": 2},
    "presence_penalty": {"type": "number", "minimum": -2, "maximum": 2},
    "stop_sequences": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

---

## Data Validation Rules

### Prompt Validation

- **Title:** Required, max 255 characters, unique within user scope
- **Description:** Optional, max 1000 characters
- **Tags:** Array of strings, each max 50 characters, max 20 tags
- **Content:** Required for versions, max 50,000 characters

### Version Validation

- **Version Number:** Sequential integers starting from 1
- **Content:** Required, non-empty
- **Change Notes:** Optional, max 1000 characters

### LLM Config Validation

- **Name:** Required, unique, max 100 characters
- **Provider:** Required, must be supported provider
- **API Key:** Required, encrypted at rest
- **Model:** Required, valid model for provider
- **Parameters:** Valid JSON, conform to provider's API

---

## Relationship Diagram

```
Prompts (1) -----> (N) PromptVersions
    |
    |
    v
Comparisons (N) <-----> (N) PromptVersions
    |                        |
    |                        |
    v                        v
LLMConfigs (1) <---------- (N) ComparisonPromptVersions
```

**Explanation:**
- Each Prompt can have multiple PromptVersions
- Each Comparison can involve multiple PromptVersions
- For cross-LLM comparisons, each execution uses an LLMConfig
- For version comparisons, LLMConfig is shared across all versions

---

## Migration Strategy

### Initial Migration

```sql
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create tables in dependency order
-- 1. prompts
-- 2. prompt_versions
-- 3. llm_configs
-- 4. comparisons
-- 5. comparison_prompt_versions
```

### Version Control

All migrations will be versioned using Alembic with forward and rollback scripts.

---

## Performance Considerations

### Indexing Strategy

- Full-text search indexes on prompt content and metadata
- Composite indexes for common query patterns
- GIN indexes for JSONB fields to enable efficient querying

### Query Optimization

- Use pagination for large result sets
- Implement search result caching
- Optimize comparison queries with proper joins

### Data Archival

- Old comparison results can be archived after 90 days
- Prompt versions older than 1 year can be compressed
- Implement soft deletes for recovery options

---

## Security Considerations

### Data Encryption

- LLM API keys encrypted using AES-256
- Database connections use SSL
- Sensitive data in JSONB fields encrypted

### Access Control

- Row-level security for multi-tenant scenarios
- API rate limiting to prevent abuse
- Audit logging for sensitive operations

---

## Backup and Recovery

### Backup Strategy

- Daily full database backups
- Point-in-time recovery capability
- Separate backup of comparison results

### Recovery Procedures

- Database restoration from backup
- Data consistency checks
- Service restart procedures
