# ADR-004: High-Volume Email Processing with Performance Requirements

**Status:** ✅ Accepted

**Date:** 2026-02-04

**Decision Makers:** User, Claude Code

---

## Context

During discovery, we learned:
- **Email Volume:** 50-100 emails per day (high volume)
- **Performance Requirement:** Process each email within 30 seconds of arrival
- **Monitoring Mode:** Continuous (check every 2 minutes)

This creates specific technical requirements:
- Watcher must handle burst traffic (multiple emails arriving simultaneously)
- Processing pipeline must be fast (< 30 seconds per email)
- System must not fall behind during peak hours
- Need to handle 4-5 emails per hour on average, up to 10-15 during peaks

---

## Decision

**Implement asynchronous processing with queue-based architecture for Bronze Tier to handle high volume efficiently.**

Architecture:
```
Gmail API → Watcher (detect) → Queue → Worker Pool → Skills → Vault
```

Key components:
1. **Watcher:** Lightweight, only detects and queues
2. **Queue:** In-memory queue (Python queue.Queue) for Bronze
3. **Worker Pool:** 3 concurrent workers processing emails
4. **Skills:** Optimized for speed (< 10 seconds each)

---

## Rationale

### Why Asynchronous Processing?

1. **Performance Requirements**
   - 50-100 emails/day = ~4 emails/hour average
   - Peak times could be 10-15 emails/hour
   - Sequential processing: 30 sec/email × 15 emails = 7.5 minutes backlog
   - Parallel processing: 30 sec/email ÷ 3 workers = 2.5 minutes backlog
   - Meets < 30 second requirement for most emails

2. **Watcher Responsiveness**
   - Watcher doesn't block on processing
   - Can detect new emails while others are processing
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
   - 1 worker: Sequential, too slow for peaks
   - 2 workers: Better, but still bottleneck at peaks
   - 3 workers: Handles 15 emails/hour comfortably
   - 4+ workers: Diminishing returns, more complexity

2. **Resource Constraints**
   - Each worker uses LLM API (rate limits)
   - Each worker uses memory (email content)
   - 3 workers balance speed vs resources

3. **Cost Considerations**
   - Using Qwen code (user's LLM choice)
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
            time.sleep(120)  # Check every 2 minutes

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
        # Step 1: Classify (fast, < 5 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'email-classifier', str(action_file)])

        # Step 2: Process (medium, < 10 seconds)
        subprocess.run(['ccr', 'code', '--skill', 'email-processor', str(action_file)])

        # Step 3: Dashboard update (fast, < 3 seconds)
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
| Email detection latency | < 2 minutes | Time from email arrival to detection |
| Classification time | < 5 seconds | email-classifier skill execution |
| Processing time | < 10 seconds | email-processor skill execution |
| Dashboard update | < 3 seconds | dashboard-updater skill execution |
| **Total per email** | **< 20 seconds** | Detection to completion |
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

1. **Load Test:** Send 20 emails simultaneously, verify all processed within 2 minutes
2. **Sustained Load:** Send 100 emails over 1 hour, verify no backlog
3. **Peak Load:** Send 15 emails in 5 minutes, verify < 30 second per email
4. **Stress Test:** Send 200 emails, verify graceful degradation

### Concurrency Tests

1. Test dashboard updates with concurrent workers
2. Test queue behavior with empty/full conditions
3. Test worker crash recovery
4. Test thread-safe file operations

---

## Success Criteria

1. ✅ Process 100 emails/day without backlog
2. ✅ 95% of emails processed within 30 seconds
3. ✅ No data loss or corruption
4. ✅ Workers recover from errors automatically
5. ✅ Performance metrics logged and reviewable

---

## References

- [Discovery Session](../sessions/2026-02-04-initial-discovery.md) - Q27, Q28
- Python threading documentation
- Python queue documentation

---

**Status:** ✅ Accepted
**Review Date:** After performance testing
