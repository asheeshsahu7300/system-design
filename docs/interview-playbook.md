# 🎯 The Senior / Staff System Design Interview Playbook

How to structure your 45-minute System Design interview to consistently receive "Strong Hire" ratings at top tech companies.

---

## ⏱️ 1. Pacing & Time Management (45-Minute Breakdown)

| Minutes | Phase | Primary Objective | Key Traps to Avoid |
|---|---|---|---|
| **00 - 05** | **Scoping & Requirements** | Clarify core functional & non-functional requirements. Define API contracts. | Diving into databases or code before understanding scale. |
| **05 - 10** | **Capacity Estimation** | Compute Read/Write QPS, 5-year storage, RAM cache size, bandwidth. | Getting stuck on hyper-precise decimals; use rounded numbers ($10^6, 10^9$). |
| **10 - 25** | **High-Level Design (HLD)** | Draw end-to-end data flow: Client -> CDN -> LB -> App -> Cache -> DB. | Overcomplicating too early with 15 microservices; start simple. |
| **25 - 40** | **Deep Dive & Bottlenecks** | Drill into the hardest challenge (e.g. race conditions, partition tolerance, caching). | Hand-waving ("We will just add Kafka"). Explain *why* and partition keys! |
| **40 - 45** | **Wrap-Up & Failure Modes** | Discuss SPOFs, monitoring (P99 latency), disaster recovery. | Not leaving time for interviewer questions. |

---

## 🗣️ 2. The Golden Communication Framework: RESHADED

- **R**equirements (Functional & Non-Functional)
- **E**stimation (Traffic, Storage, Memory, Bandwidth)
- **S**ervices & API Interface (REST / gRPC signatures)
- **H**igh-Level Diagram (Boxes and arrows)
- **A**rchitecture Deep Dive (The core algorithm: Base62, H3, ABR, Paxos)
- **D**atabase & Data Model (Schema, Primary key, Indexes, Sharding key)
- **E**dge Cases & Failure Modes (Network partitions, Thundering herd, Split-brain)
- **D**iscuss Trade-offs (CAP theorem, Consistency vs Latency)

---

## 🚨 3. Top 5 Pitfalls That Disqualify Candidates

1. **Jumping straight to tools without justification**:
   - Saying: *"We'll use Cassandra and Kafka"* without justifying why Postgres or RabbitMQ is insufficient.
2. **Ignoring the Read/Write Ratio**:
   - A 100:1 read-heavy system (URL Shortener) demands aggressive caching and read replicas.
   - A write-heavy system (Uber GPS stream) demands append-only logs (Kafka/Cassandra) or in-memory write buffers.
3. **Forgetting Distributed Race Conditions**:
   - When 2 users book the last ticket or park in the last spot simultaneously, how do you prevent double allocation? (Redis distributed locks with Redlock, conditional updates `WHERE version = x`, DB row-level locks).
4. **Vague Scaling Answers**:
   - Saying *"We scale horizontally"* without explaining how state is shared or partitioned (Consistent Hashing with virtual nodes).
5. **Treating Cache as Indestructible**:
   - What happens when Redis restarts or the cache expires? (Cache stampede, Cache breakdown, Cache penetration). Always mention Bloom Filters and Mutex locks for cache misses.
