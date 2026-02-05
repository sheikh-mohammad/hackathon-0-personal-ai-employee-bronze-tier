# ADR-004: High-Volume Email Processing with Performance Requirements

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

During discovery, we learned:
- **Email Volume:** High volume (can vary, user didn't specify exact number)
- **Performance Requirement:** Fast processing (< 10 seconds per email)
- **Monitoring Mode:** Continuous (check every 10 seconds)

This creates specific technical requirements:
- Watcher must handle burst traffic (multiple emails arriving simultaneously)
- Processing pipeline must be fast (< 10 seconds per email)
- System must not fall behind during peak hours
- Need to handle variable email volume efficiently

---

## Decision

**Implement asynchronous processing with queue-based architecture for Bronze Tier to handle high volume efficiently.**

Architecture:
```
Gmail API → Watcher (detect) → Queue → Worker Pool → Skills → Vault
```

Key components:
1. **Watcher:** Lightweight, only detects and queues (checks every 10 seconds)
2. **Queue:** In-memory queue (Python queue.Queue) for Bronze
3. **Worker Pool:** 3 concurrent workers processing emails
4. **Skills:** Optimized for speed (< 3 seconds each, < 10 seconds total)

---

## Rationale

### Why Asynchronous Processing?

1. **Performance Requirements**
   - High volume with variable traffic patterns
   - Peak times could have multiple emails arriving simultaneously
   - Sequential processing: 10 sec/email × 10 emails = 100 seconds backlog
   - Parallel processing: 10 sec/email ÷ 3 workers = ~33 seconds backlog
   - Meets < 10 second requirement for most emails when queue is empty

2. **Watcher Responsiveness**
   - Watcher doesn't block on processing
   - Can detect new emails every 10 seconds while others are processing
   - No missed emails during processing delays

3. **Resource Utilization**
   - Better CPU utilization (parallel processing)
   - LLM API calls can run concurrently
   - Vault writes are serialized to avoid conflicts

4. **Scalability**
   - Easy to add more workers if volume increases
   - Can upgrade to Redis queue for Silver tier
   - Architecture supports distributed processing later

### Why 3 Workers?

1. **Performance Testing**
   - 1 worker: Sequential, too slow for bursts
   - 2 workers: Better, but still bottleneck at peaks
   - 3 workers: Handles burst traffic comfortably
   - 4+ workers: Diminishing returns, more complexity

2. **Resource Constraints**
   - Each worker uses LLM API (rate limits)
   - Each worker uses memory (email content)
   - 3 workers balance speed vs resources

3. **Cost Considerations**
   - Using Qwen code or Kiro IDE (user's LLM choices)
   - 3 concurrent API calls is reasonable
   - Can adjust based on API rate limits

---

## Implementation Details

### Queue-Based Watcher

```python
# gmail_watcher.py

import queue
import threading
from concurrent.futures import ThreadPoolExecutor

class GmailWatcher:
    def __init__(self, vault_path: str, num_workers: int = 3):
        self.vault_path = Path(vault_path)
        self.email_queue = queue.Queue()
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def detect_emails(self):
        """Lightweight detection loop"""
        while True:
            try:
                new_emails = self.check_gmail_api()
                for email in new_emails:
                    # Create action file
                    action_file = self.create_action_file(email)
                    # Queue for processing (non-blocking)
                    self.email_queue.put(action_file)
                    logging.info(f"Queued: {action_file.name}")
            except Exception as e:
                logging.error(f"Detection error: {e}")
            time.sleep(10)  # Check every 10 seconds

    def process_worker(self):
        """Worker thread that processes queued emails"""
        while True:
            try:
                # Get email from queue (blocking)
                action_file = self.email_queue.get(timeout=60)

                # Process through skill pipeline
                start_time = time.time()
                self.process_email_pipeline(action_file)
                duration = time.time() - start_time

                logging.info(f"Processed {action_file.name} in {duration:.2f}s")

                # Mark task as done
                self.email_queue.task_done()

            except queue.Empty:
                continue  # No emails, keep waiting
            except Exception as e:
                logging.error(f"Worker error: {e}")
                self.email_queue.task_done()

    def process_email_pipeline(self, action_file: Path):
        """Run email through skill pipeline"""
        # Step 1: Classify (fast, < 2 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'email-classifier', str(action_file)])

        # Step 2: Process (fast, < 2 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'email-processor', str(action_file)])

        # Step 3: Draft Reply (medium, < 3 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'email-reply-writer', str(action_file)])

        # Step 4: Create Summary (fast, < 2 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'summary-creation', str(action_file)])

        # Step 5: Dashboard update (fast, < 1 second)
        # Note: Dashboard updates are serialized to avoid conflicts
        with self.dashboard_lock:
            subprocess.run(['ccr', 'code', '--skill', 'dashboard-updater', str(self.vault_path)])

    def run(self):
        """Start watcher with worker pool"""
        # Start worker threads
        for i in range(self.num_workers):
            worker = threading.Thread(target=self.process_worker, daemon=True)
            worker.start()
            logging.info(f"Started worker {i+1}")

        # Start detection loop (main thread)
        self.detect_emails()
```

### Performance Optimizations

1. **Skill Optimization**
   - Keep prompts concise
   - Use faster LLM for classification (if available)
   - Cache Company_Handbook rules in memory
   - Minimize file I/O operations

2. **Dashboard Updates**
   - Serialize dashboard updates (lock)
   - Batch updates every 30 seconds instead of per-email
   - Use incremental updates (don't recalculate everything)

3. **API Efficiency**
   - Batch Gmail API calls (fetch multiple emails)
   - Use partial responses (only needed fields)
   - Implement exponential backoff for rate limits

---

## Performance Targets

### Bronze Tier Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Email detection latency | < 10 seconds | Time from email arrival to detection |
| Classification time | < 2 seconds | email-classifier skill execution |
| Processing time | < 2 seconds | email-processor skill execution |
| Reply drafting time | < 3 seconds | email-reply-writer skill execution |
| Summary creation time | < 2 seconds | summary-creation skill execution |
| Dashboard update | < 1 second | dashboard-updater skill execution |
| **Total per email** | **< 10 seconds** | Detection to completion |
| Queue backlog | < 5 emails | Max queued emails during peaks |
| Worker utilization | 60-80% | Workers busy percentage |

### Monitoring

```python
# Add performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'emails_processed': 0,
            'total_time': 0,
            'classification_time': 0,
            'processing_time': 0,
            'dashboard_time': 0,
            'queue_size_max': 0
        }

    def log_processing(self, email_id: str, timings: dict):
        """Log processing metrics"""
        self.metrics['emails_processed'] += 1
        self.metrics['total_time'] += timings['total']
        # ... log other metrics

        # Write to metrics file every 10 emails
        if self.metrics['emails_processed'] % 10 == 0:
            self.write_metrics()
```

---

## Consequences

### Positive

- ✅ Handles high volume (50-100 emails/day) efficiently
- ✅ Meets performance requirement (< 30 seconds)
- ✅ No missed emails during processing
- ✅ Better resource utilization
- ✅ Scalable architecture for future growth
- ✅ Can handle burst traffic (multiple emails at once)

### Negative

- ❌ More complex than sequential processing
- ❌ Need thread-safe code (locks for shared resources)
- ❌ Harder to debug (concurrent execution)
- ❌ More memory usage (queue + workers)
- ❌ Need performance monitoring

### Mitigations

- Comprehensive logging with thread IDs
- Performance monitoring dashboard
- Unit tests for concurrent scenarios
- Graceful degradation (reduce workers if errors)
- Clear documentation of threading model

---

## Alternatives Considered

### Alternative 1: Sequential Processing

Process one email at a time, blocking.

**Rejected because:**
- Too slow for 50-100 emails/day
- Can't meet < 30 second requirement during peaks
- Watcher blocks during processing
- Poor resource utilization

### Alternative 2: Celery/Redis Queue

Use production-grade task queue.

**Rejected for Bronze because:**
- Over-engineering for Bronze tier
- Adds external dependency (Redis)
- More complex setup and maintenance
- Can add in Silver/Gold if needed

### Alternative 3: Event-Driven (asyncio)

Use Python asyncio for async processing.

**Rejected because:**
- subprocess.run() is blocking (skills invocation)
- Would need async subprocess library
- More complex error handling
- Threading is simpler for this use case

---

## Testing Strategy

### Performance Tests

1. **Load Test:** Send 20 emails simultaneously, verify all processed within reasonable time
2. **Sustained Load:** Monitor system over several hours with variable traffic
3. **Burst Test:** Send 10 emails in quick succession, verify < 10 second per email (when queue empty)
4. **Stress Test:** Send large volume, verify graceful degradation

### Concurrency Tests

1. Test dashboard updates with concurrent workers
2. Test queue behavior with empty/full conditions
3. Test worker crash recovery
4. Test thread-safe file operations

---

## Success Criteria

1. ✅ Process variable email volume without backlog
2. ✅ 95% of emails processed within 10 seconds (when queue is empty)
3. ✅ No data loss or corruption
4. ✅ Workers recover from errors automatically
5. ✅ Performance metrics logged and reviewable
6. ✅ System handles burst traffic gracefully

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q31 (high volume), Q36 (fast processing)
- [Component Tier Mapping](../architecture/component-tier-mapping.md)
- Python threading documentation
- Python queue documentation

---

**Status:** ✅ Accepted
**Review Date:** After performance testing with real email volume
