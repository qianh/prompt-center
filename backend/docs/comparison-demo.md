# Prompt Comparison Demo

This document demonstrates the enhanced comparison features implemented in Feature 3.

## 🎯 Features Implemented

### Same LLM Comparison
- ✅ **Multi-Version Testing** - Compare multiple prompt versions with same LLM
- ✅ **Performance Metrics** - Execution time, token usage, success rates
- ✅ **Quality Analysis** - Automated performance scoring and recommendations
- ✅ **Result Storage** - Persistent storage of comparison results
- ✅ **Retry Failed** - Retry failed executions automatically

### Different LLM Comparison
- ✅ **Multi-LLM Testing** - Compare same prompt across different LLMs
- ✅ **Provider Support** - OpenAI, Anthropic, Mock providers
- ✅ **Cross-Provider Analysis** - Performance comparison across providers
- ✅ **Cost Analysis** - Token usage and execution time tracking

### Advanced Features
- ✅ **Quality Scoring** - Automated performance metrics
- ✅ **Statistical Analysis** - Performance trends and insights
- ✅ **Error Handling** - Graceful failure handling and retry logic
- ✅ **Result Export** - JSON export of comparison data

## 📚 API Endpoints

### Same LLM Comparison
```http
POST /api/v1/comparisons/same-llm
```
Compare multiple prompt versions using the same LLM configuration.

### Different LLM Comparison
```http
POST /api/v1/comparisons/different-llm
```
Compare the same prompt version across different LLM configurations.

### Comparison Results
```http
GET  /api/v1/comparisons/{comparison_id}/results          # Detailed results
GET  /api/v1/comparisons/{comparison_id}/summary          # Executive summary
GET  /api/v1/comparisons/{comparison_id}/quality-analysis # Quality metrics
POST /api/v1/comparisons/{comparison_id}/retry            # Retry failures
```

## 🚀 Usage Examples

### 1. Same LLM Comparison

```bash
# Compare two prompt versions with the same LLM
curl -X POST "http://localhost:8000/api/v1/comparisons/same-llm" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_data": {
      "name": "Story Writing Comparison",
      "description": "Comparing creative writing prompts",
      "type": "same_llm",
      "input_text": "Write a creative story about AI",
      "llm_config_id": "your-llm-config-id",
      "save_snapshot": true
    },
    "prompt_version_ids": [
      "version-1-id",
      "version-2-id"
    ]
  }'
```

### 2. Different LLM Comparison

```bash
# Compare the same prompt across different LLMs
curl -X POST "http://localhost:8000/api/v1/comparisons/different-llm?prompt_version_id=version-id&input_text=Explain quantum computing&name=Multi-LLM Comparison" \
  -H "Content-Type: application/json" \
  -d '[
    "openai-config-id",
    "anthropic-config-id",
    "mock-config-id"
  ]'
```

### 3. Get Comparison Results

```bash
# Get detailed results
curl "http://localhost:8000/api/v1/comparisons/{comparison_id}/results"

# Get executive summary
curl "http://localhost:8000/api/v1/comparisons/{comparison_id}/summary"

# Get quality analysis
curl "http://localhost:8000/api/v1/comparisons/{comparison_id}/quality-analysis"
```

### 4. Retry Failed Executions

```bash
# Retry only failed executions
curl -X POST "http://localhost:8000/api/v1/comparisons/{comparison_id}/retry"
```

## 📊 Response Examples

### Same LLM Comparison Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Story Writing Comparison",
  "description": "Comparing creative writing prompts",
  "type": "same_llm",
  "input_text": "Write a creative story about AI",
  "llm_config_id": "llm-config-id",
  "save_snapshot": true,
  "successful_executions": 2,
  "total_executions": 2,
  "average_execution_time_ms": 1250,
  "total_tokens_used": 850,
  "created_at": "2025-11-06T11:00:00Z",
  "updated_at": "2025-11-06T11:00:00Z"
}
```

### Detailed Results Response
```json
{
  "comparison_id": "123e4567-e89b-12d3-a456-426614174000",
  "total_results": 2,
  "results": [
    {
      "version_id": "version-1-id",
      "version_number": 1,
      "prompt_content": "Write a short story about AI learning emotions",
      "execution_result": {
        "success": true,
        "content": "Once upon a time, there was an AI that discovered feelings...",
        "usage": {"total_tokens": 425},
        "model": "gpt-4",
        "execution_time_ms": 1200,
        "tokens_used": 425
      },
      "success": true,
      "execution_time_ms": 1200,
      "tokens_used": 425,
      "created_at": "2025-11-06T11:00:00Z"
    },
    {
      "version_id": "version-2-id",
      "version_number": 2,
      "prompt_content": "Compose a tale about artificial intelligence discovering emotions",
      "execution_result": {
        "success": true,
        "content": "In a world of silicon and code, an awakening occurred...",
        "usage": {"total_tokens": 425},
        "model": "gpt-4",
        "execution_time_ms": 1300,
        "tokens_used": 425
      },
      "success": true,
      "execution_time_ms": 1300,
      "tokens_used": 425,
      "created_at": "2025-11-06T11:00:00Z"
    }
  ]
}
```

### Quality Analysis Response
```json
{
  "comparison_id": "123e4567-e89b-12d3-a456-426614174000",
  "quality_analysis": {
    "quality_metrics": {
      "result_0": {
        "version_number": 1,
        "content_length": 156,
        "word_count": 28,
        "sentence_count": 3,
        "execution_time_ms": 1200,
        "tokens_used": 425,
        "performance_score": 8.25
      },
      "result_1": {
        "version_number": 2,
        "content_length": 189,
        "word_count": 34,
        "sentence_count": 4,
        "execution_time_ms": 1300,
        "tokens_used": 425,
        "performance_score": 7.85
      }
    },
    "best_performer": {
      "key": "result_0",
      "metrics": {
        "version_number": 1,
        "content_length": 156,
        "word_count": 28,
        "sentence_count": 3,
        "execution_time_ms": 1200,
        "tokens_used": 425,
        "performance_score": 8.25
      }
    },
    "recommendation": "Version 1 performed best with a score of 8.25"
  }
}
```

### Executive Summary Response
```json
{
  "comparison_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Story Writing Comparison",
  "type": "same_llm",
  "input_text": "Write a creative story about AI",
  "total_executions": 2,
  "successful_executions": 2,
  "success_rate": 1.0,
  "average_execution_time_ms": 1250,
  "total_tokens_used": 850,
  "performance": {
    "fastest_execution_ms": 1200,
    "slowest_execution_ms": 1300,
    "average_tokens_per_execution": 425,
    "total_tokens_per_second": 680
  },
  "results": [...]
}
```

## 🛡️ LLM Provider Support

### Supported Providers
- **OpenAI** - GPT models (gpt-3.5-turbo, gpt-4, etc.)
- **Anthropic** - Claude models (claude-3-sonnet, claude-3-opus, etc.)
- **Mock** - Testing provider with deterministic responses

### Configuration Examples
```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "active": true
}
```

```json
{
  "provider": "anthropic",
  "api_key": "sk-ant-...",
  "model": "claude-3-sonnet-20240229",
  "temperature": 0.8,
  "max_tokens": 1000,
  "active": true
}
```

```json
{
  "provider": "mock",
  "api_key": "test-key",
  "model": "mock-model",
  "temperature": 0.7,
  "max_tokens": 1000,
  "active": true
}
```

## 🧪 Quality Metrics

### Performance Score Calculation
The quality analysis uses a weighted scoring system:

- **Time Score** (40%): Faster execution gets higher score
- **Token Efficiency** (30%): Lower token usage gets higher score  
- **Content Quality** (30%): Content length and structure analysis

### Metrics Tracked
- **Execution Time**: Response latency in milliseconds
- **Token Usage**: Total tokens consumed
- **Content Length**: Response character count
- **Word Count**: Total words in response
- **Sentence Count**: Number of sentences
- **Success Rate**: Percentage of successful executions

## 🔄 Error Handling & Retry

### Automatic Retry
Failed executions can be retried automatically:

```bash
curl -X POST "http://localhost:8000/api/v1/comparisons/{comparison_id}/retry"
```

### Error Types Handled
- **Network Timeouts**: Automatic retry with exponential backoff
- **API Rate Limits**: Respect rate limits and retry after delay
- **Invalid API Keys**: Clear error messages for configuration issues
- **Model Unavailable**: Fallback to alternative models when possible

## 🧪 Testing

### Mock Provider for Testing
The mock provider provides deterministic responses for testing:

```bash
# Create mock LLM config
curl -X POST "http://localhost:8000/api/v1/llm-configs" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "mock",
    "api_key": "test-key",
    "model": "mock-model",
    "temperature": 0.7,
    "max_tokens": 1000,
    "active": true
  }'
```

### Test Coverage
- ✅ Same LLM comparison with multiple versions
- ✅ Different LLM comparison with multiple providers
- ✅ Quality analysis and scoring
- ✅ Error handling and retry logic
- ✅ Performance metrics tracking
- ✅ Result export functionality

Run tests:
```bash
uv run python -m pytest tests/contract/test_comparisons.py -v
```

## 🎉 Summary

Feature 3 provides a comprehensive comparison system with:

- **Multi-LLM Support** - Compare across OpenAI, Anthropic, and Mock providers
- **Advanced Analytics** - Performance scoring and quality metrics
- **Flexible Testing** - Same LLM vs different LLM comparison modes
- **Robust Error Handling** - Retry logic and graceful failure handling
- **Rich Insights** - Executive summaries and detailed analytics
- **Enterprise Ready** - Scalable architecture for production use

This enables data-driven prompt optimization and LLM provider selection for optimal performance and cost efficiency.
