# Quickstart Validation Scenarios: Prompt Management System

**Feature ID:** 001  
**Based on:** `spec.md` version 2025-11-06  
**Created:** 2025-11-06

---

## Scenario 1: Basic Prompt Management

### User Story: Prompt Repository Management

**Given:** A new user with an empty prompt library  
**When:** The user creates, searches, and manages prompts  
**Then:** All CRUD operations work correctly with proper validation

### Test Steps

1. **Create First Prompt**
   ```bash
   # Via API
   curl -X POST http://localhost:8000/api/prompts \
     -H "Content-Type: application/json" \
     -d '{
       "title": "System Prompt",
       "description": "A helpful assistant prompt",
       "content": "You are a helpful AI assistant...",
       "tags": ["system", "assistant"]
     }'
   
   # Expected: 201 Created with prompt ID
   ```

2. **Search for Prompt**
   ```bash
   curl "http://localhost:8000/api/prompts?search=system&tags=assistant"
   
   # Expected: 200 OK with prompt in results
   ```

3. **Update Prompt Metadata**
   ```bash
   curl -X PUT http://localhost:8000/api/prompts/{id} \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Updated System Prompt",
       "description": "An improved assistant prompt",
       "tags": ["system", "assistant", "v2"]
     }'
   
   # Expected: 200 OK with updated prompt
   ```

4. **Delete Prompt**
   ```bash
   curl -X DELETE http://localhost:8000/api/prompts/{id}
   
   # Expected: 204 No Content
   ```

### Validation Criteria

- [ ] Prompt creation validates required fields
- [ ] Search returns relevant results within 500ms
- [ ] Updates persist correctly with new timestamps
- [ ] Delete removes prompt and all versions
- [ ] Pagination works for large prompt sets

---

## Scenario 2: Version Control Workflow

### User Story: Version Control Management

**Given:** An existing prompt with multiple versions  
**When:** The user creates new versions and compares them  
**Then:** Version history is maintained with proper relationships

### Test Steps

1. **Create Initial Version**
   ```bash
   curl -X POST http://localhost:8000/api/prompts/{id}/versions \
     -H "Content-Type: application/json" \
     -d '{
       "content": "You are a helpful AI assistant. Be concise.",
       "change_notes": "Initial version with conciseness requirement"
     }'
   
   # Expected: 201 Created, version_number = 1
   ```

2. **Create New Version Based on Previous**
   ```bash
   curl -X POST http://localhost:8000/api/prompts/{id}/versions \
     -H "Content-Type: application/json" \
     -d '{
       "content": "You are a helpful AI assistant. Be concise and friendly.",
       "change_notes": "Added friendliness requirement",
       "based_on_version_id": "{version_1_id}"
     }'
   
   # Expected: 201 Created, version_number = 2
   ```

3. **List All Versions**
   ```bash
   curl "http://localhost:8000/api/prompts/{id}/versions"
   
   # Expected: Array with 2 versions in chronological order
   ```

4. **Compare Two Versions**
   ```bash
   curl "http://localhost:8000/api/prompts/{id}/versions/compare?version_a=1&version_b=2"
   
   # Expected: Side-by-side comparison with highlighted differences
   ```

### Validation Criteria

- [ ] Version numbers increment automatically
- [ ] Based-on relationships are tracked correctly
- [ ] Change notes are preserved with timestamps
- [ ] Version comparison shows meaningful diffs
- [ ] Cannot delete a prompt if it has versions (cascade)

---

## Scenario 3: LLM Provider Configuration

### User Story: LLM Configuration Management

**Given:** A user wants to test prompts across multiple LLM providers  
**When:** The user configures providers and tests connections  
**Then:** All providers are accessible with proper authentication

### Test Steps

1. **Add OpenAI Configuration**
   ```bash
   curl -X POST http://localhost:8000/api/llm-configs \
     -H "Content-Type: application/json" \
     -d '{
       "name": "OpenAI GPT-4",
       "provider": "openai",
       "api_key": "sk-test-key",
       "model": "gpt-4",
       "parameters": {
         "temperature": 0.7,
         "max_tokens": 1000
       }
     }'
   
   # Expected: 201 Created with encrypted API key
   ```

2. **Add Anthropic Configuration**
   ```bash
   curl -X POST http://localhost:8000/api/llm-configs \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Anthropic Claude",
       "provider": "anthropic",
       "api_key": "sk-ant-test-key",
       "model": "claude-3-sonnet-20240229"
     }'
   
   # Expected: 201 Created
   ```

3. **Test Provider Connection**
   ```bash
   curl -X POST http://localhost:8000/api/llm-configs/{id}/test
   
   # Expected: 200 OK with test response
   ```

4. **List All Configurations**
   ```bash
   curl "http://localhost:8000/api/llm-configs"
   
   # Expected: Array of configs without exposing API keys
   ```

### Validation Criteria

- [ ] API keys are encrypted in database
- [ ] Connection tests validate credentials
- [ ] Invalid configurations are rejected
- [ ] Provider-specific parameters are validated
- [ ] List endpoint never exposes sensitive data

---

## Scenario 4: Version Comparison Testing

### User Story: Prompt Comparison Testing

**Given:** Multiple prompt versions and a configured LLM provider  
**When:** The user runs a version comparison with test input  
**Then:** All versions execute and results are comparable

### Test Steps

1. **Setup Test Data**
   ```bash
   # Create prompt with 2 versions (from Scenario 2)
   # Configure LLM provider (from Scenario 3)
   ```

2. **Run Version Comparison**
   ```bash
   curl -X POST http://localhost:8000/api/comparisons/compare \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Conciseness Test",
       "type": "version_comparison",
       "input_text": "Explain quantum computing in simple terms",
       "prompt_version_ids": ["{version_1_id}", "{version_2_id}"],
       "llm_config_id": "{openai_config_id}",
       "save_snapshot": true
     }'
   
   # Expected: 200 OK with comparison results
   ```

3. **Verify Results Structure**
   ```json
   {
     "id": "comparison-uuid",
     "results": {
       "executions": [
         {
           "prompt_version_id": "version-1-uuid",
           "output": "Quantum computing is...",
           "execution_time_ms": 1250,
           "tokens_used": 150,
           "status": "success"
         },
         {
           "prompt_version_id": "version-2-uuid", 
           "output": "Let me explain quantum computing...",
           "execution_time_ms": 1380,
           "tokens_used": 165,
           "status": "success"
         }
       ],
       "summary": {
         "total_executions": 2,
         "successful_executions": 2,
         "average_execution_time_ms": 1315,
         "total_tokens_used": 315
       }
     }
   }
   ```

4. **Retrieve Saved Snapshot**
   ```bash
   curl "http://localhost:8000/api/comparisons/{comparison_id}"
   
   # Expected: Full comparison results with metadata
   ```

### Validation Criteria

- [ ] All prompt versions execute in parallel
- [ ] Execution times and token usage are tracked
- [ ] Failed executions don't block successful ones
- [ ] Results are saved as snapshots when requested
- [ ] Comparison completes within 30 seconds

---

## Scenario 5: Cross-LLM Comparison

### User Story: Cross-LLM Comparison

**Given:** A single prompt and multiple LLM configurations  
**When:** The user runs a cross-LLM comparison  
**Then:** All providers execute and results are compared

### Test Steps

1. **Run Cross-LLM Comparison**
   ```bash
   curl -X POST http://localhost:8000/api/comparisons/compare \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Provider Comparison",
       "type": "cross_llm",
       "input_text": "Write a haiku about programming",
       "prompt_version_ids": ["{prompt_version_id}"],
       "llm_config_ids": ["{openai_id}", "{anthropic_id}"],
       "save_snapshot": true
     }'
   
   # Expected: 200 OK with provider-specific results
   ```

2. **Analyze Provider Differences**
   ```json
   {
     "results": {
       "executions": [
         {
           "prompt_version_id": "version-uuid",
           "llm_config_id": "openai-config",
           "output": "Code flows like water\nBugs hide in the logic deep\nDebug brings the light",
           "provider": "openai",
           "model": "gpt-4",
           "execution_time_ms": 890,
           "tokens_used": 45
         },
         {
           "prompt_version_id": "version-uuid",
           "llm_config_id": "anthropic-config", 
           "output": "Logic dances bright\nThrough silicon valleys deep\nAlgorithms bloom",
           "provider": "anthropic",
           "model": "claude-3-sonnet",
           "execution_time_ms": 1120,
           "tokens_used": 42
         }
       ]
     }
   }
   ```

### Validation Criteria

- [ ] All LLM providers execute simultaneously
- [ ] Provider-specific metadata is captured
- [ ] Different response formats are normalized
- [ ] Rate limiting is respected per provider
- [ ] Cost estimation is accurate

---

## Scenario 6: Snapshot Management

### User Story: Comparison Snapshot Management

**Given:** Multiple saved comparison snapshots  
**When:** The user searches, filters, and manages snapshots  
**Then:** Snapshots are organized and accessible

### Test Steps

1. **Create Multiple Snapshots**
   ```bash
   # Run 3-4 different comparisons with save_snapshot=true
   ```

2. **List All Snapshots**
   ```bash
   curl "http://localhost:8000/api/comparisons?type=version_comparison"
   
   # Expected: Filtered list of snapshots
   ```

3. **Search Snapshots**
   ```bash
   curl "http://localhost:8000/api/comparisons?search=consciseness"
   
   # Expected: Snapshots matching search term
   ```

4. **Export Snapshot**
   ```bash
   curl "http://localhost:8000/api/comparisons/{id}/export?format=json" \
     -o comparison_snapshot.json
   
   # Expected: Downloadable file with full data
   ```

5. **Delete Old Snapshot**
   ```bash
   curl -X DELETE http://localhost:8000/api/comparisons/{id}
   
   # Expected: 204 No Content
   ```

### Validation Criteria

- [ ] Snapshots are searchable by name and description
- [ ] Filtering works by type, date, and prompt
- [ ] Export formats include all necessary data
- [ ] Delete cascades properly to related data
- [ ] Storage usage is tracked and manageable

---

## Performance Validation

### Load Testing Scenarios

1. **Concurrent Comparisons**
   - Run 10 comparisons simultaneously
   - Verify all complete without errors
   - Monitor database connection pool usage

2. **Large Prompt Search**
   - Create 1000+ prompts with varied content
   - Search performance should remain < 500ms
   - Pagination should handle large datasets efficiently

3. **Memory Usage**
   - Monitor memory during comparison execution
   - Verify no memory leaks in long-running processes
   - Check garbage collection for large result sets

### Acceptance Criteria

- [ ] Prompt retrieval < 500ms for 10,000 prompts
- [ ] Comparison execution < 30s for 5 providers
- [ ] System handles 50 concurrent comparisons
- [ ] Database queries use proper indexes
- [ ] Memory usage remains stable under load

---

## Error Handling Validation

### Failure Scenarios

1. **LLM Provider Failure**
   - Simulate API rate limit exceeded
   - Verify graceful error handling
   - Check retry logic implementation

2. **Database Connection Loss**
   - Temporarily disconnect database
   - Verify application recovers gracefully
   - Check data integrity after reconnection

3. **Invalid Input Handling**
   - Test with malformed JSON
   - Verify validation error messages
   - Check SQL injection protection

### Validation Criteria

- [ ] All error scenarios return appropriate HTTP status codes
- [ ] Error messages are user-friendly and actionable
- [ ] No sensitive information leaks in error responses
- [ ] System recovers automatically from transient failures
- [ ] Audit logging captures all error conditions

---

## Security Validation

### Security Test Cases

1. **API Key Protection**
   - Verify API keys are encrypted at rest
   - Check that keys never appear in logs
   - Test that list endpoints don't expose keys

2. **Input Validation**
   - Test SQL injection attempts
   - Verify XSS protection in prompt content
   - Check file upload restrictions

3. **Authentication Bypass**
   - Test API endpoints without proper auth
   - Verify rate limiting prevents abuse
   - Check CORS configuration

### Validation Criteria

- [ ] All sensitive data is encrypted
- [ ] Input validation prevents injection attacks
- [ ] Error messages don't reveal system information
- [ ] Rate limiting prevents API abuse
- [ ] Security headers are properly configured

---

## Success Metrics

### Quantitative Measures

- **Prompt Creation Time:** < 2 seconds from form submit to confirmation
- **Search Response Time:** < 500ms for full-text search across 10,000 prompts
- **Comparison Execution:** < 30 seconds for 5-provider comparison
- **UI Responsiveness:** < 100ms for all interactive elements
- **Error Rate:** < 1% for all API operations under normal load

### Qualitative Measures

- **Usability Score:** 8/10 or higher in user testing
- **Feature Completeness:** 100% of acceptance criteria met
- **Code Quality:** 90%+ test coverage, no critical security issues
- **Documentation:** All APIs documented with examples
- **Performance:** No memory leaks or performance regressions

These scenarios provide comprehensive validation of all major features and edge cases for the prompt management system.
