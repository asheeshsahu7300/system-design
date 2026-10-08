# 🗺️ Master System Design Learning Roadmap

A structured, battle-tested learning path taking you from foundational Object-Oriented Low-Level Design (LLD) to million-QPS distributed architectures.

---

## 🟢 Phase 1: Object-Oriented & Low-Level Design (LLD)
*Goal: Master Design Patterns, Clean Code, Solid Principles, Thread Safety, and Concurrency.*

- [x] **01. Parking Lot System** (`systems/02-parking-lot`)
  - *Patterns*: Strategy (pricing), Factory (vehicle/spot), Observer/State.
  - *Concurrency*: Goroutine safety (`sync.RWMutex`), Python thread locks.
- [ ] **02. Elevator System (Multi-Car Controller)**
  - *Patterns*: State Pattern, Dispatcher Algorithm (LOOK / SCAN).
- [ ] **03. In-Memory Key-Value Store with TTL & LRU/LFU Eviction**
  - *Patterns*: Doubly Linked List + Hash Map, Read-Write locks.
- [ ] **04. Tic-Tac-Toe / Chess Game Engine**
  - *Patterns*: Command Pattern (Undo/Redo), Minimax heuristic stub.
- [ ] **05. Movie Ticket Booking System (BookMyShow / Fandango)**
  - *Patterns*: Distributed Locks (Redis Redlock), Optimistic Concurrency Control.

---

## 🟡 Phase 2: Foundational Microservices & Tier-1 Systems
*Goal: Master API design, caching, hashing, data storage selection, and failure handling.*

- [x] **01. URL Shortener (TinyURL / Bitly)** (`systems/01-url-shortener`)
  - *Concepts*: Base62 encoding, MD5/SHA256 collisions, Key Generation Service (KGS), 301 vs 302, Redis Cache Aside, Bloom Filter.
- [ ] **02. Distributed Rate Limiter** (`systems/03-rate-limiter`)
  - *Concepts*: Token Bucket, Leaky Bucket, Sliding Window Log, Redis Lua Scripts, Distributed synchronizations.
- [ ] **03. Distributed Unique ID Generator**
  - *Concepts*: Twitter Snowflake (Timestamp + Datacenter + Worker ID + Sequence), Ticket Server, UUIDv4 vs UUIDv7.
- [ ] **04. Notification Engine (Multi-Channel)** (`systems/04-notification-system`)
  - *Concepts*: Fanout exchange, Idempotency keys, Priority Queues (Kafka/RabbitMQ), Dead Letter Queue (DLQ).

---

## 🟠 Phase 3: Real-Time & High-Concurrency Systems
*Goal: Master WebSockets, stateful servers, message brokers, and event streaming.*

- [ ] **01. Real-Time Chat System (WhatsApp / Slack / Discord)** (`systems/05-whatsapp-chat`)
  - *Concepts*: Long Polling vs WebSockets, Presence Server, Message ordering, Cassandra/ScyllaDB wide-column storage, Group message fanout.
- [ ] **02. Collaborative Document Editor (Google Docs / Figma)**
  - *Concepts*: Operational Transformation (OT), Conflict-free Replicated Data Types (CRDTs), WebRTC/WebSockets.
- [ ] **03. Web Crawler & Search Autocomplete**
  - *Concepts*: Distributed Crawling, Robots.txt, Dedup with Bloom Filters, Trie structure for Typeahead suggestions, Top-K queries.

---

## 🔴 Phase 4: Hyperscale & Domain-Specific Heavyweights
*Goal: Master geospatial indexing, video transcoding pipelines, CDN architecture, and surge algorithms.*

- [ ] **01. Video Streaming Platform (YouTube / Netflix / Disney+ Hotstar)** (`systems/06-youtube-hotstar-streaming`)
  - *Concepts*: Ingestion pipelines, Adaptive Bitrate Streaming (HLS/DASH), Video chunking, Transcoding DAG, CDN Edge caching, Live cricket surge handling.
- [ ] **02. Ride Hailing & Dispatch Platform (Uber / Rapido / Lyft)** (`systems/07-uber-rapido-ride-matching`)
  - *Concepts*: Geospatial indexing (Geohash vs Google S2 vs Uber H3 Hexagons), Real-time driver GPS tracking, Ride matching algorithm, Dynamic Surge Pricing, WebSocket location stream.
- [ ] **03. Flash Sale / E-Commerce Inventory (Amazon / Flipkart Big Billion Days)**
  - *Concepts*: Distributed transactions, Two-Phase Commit vs Saga Pattern, Redis inventory reservation with Lua, Outbox Pattern, Eventual Consistency.
- [ ] **04. Payment Processing Gateway (Stripe / Razorpay)**
  - *Concepts*: Strict Idempotency, Double-entry ledger, Reconciliation workers, Webhook retry with exponential backoff.

---

## 📈 Suggested Weekly Learning Schedule
| Week | Focus | Hands-On Deliverable |
|------|-------|----------------------|
| **Week 1** | URL Shortener + Capacity Math | Deploy Go & Python APIs + Web UI |
| **Week 2** | Parking Lot & LLD Patterns | Implement concurrency-safe OOP in Python & Go |
| **Week 3** | Rate Limiter & ID Generator | Implement Token Bucket & Snowflake algorithms |
| **Week 4** | Notification & Chat Architecture | WebSockets + Redis PubSub + Message queues |
| **Week 5** | Video Streaming (YouTube/Hotstar) | HLS streaming server + Transcoder DAG design |
| **Week 6** | Ride Hailing (Uber/Rapido) | H3 Spatial indexing & Dispatcher simulation |
