# System Design Learning Roadmap

A structured learning path from Object-Oriented Low-Level Design (LLD) to distributed hyperscale architectures.

---

## Phase 1: Object-Oriented & Low-Level Design (LLD)
Objective: Master design patterns, clean code principles, thread safety, and concurrency controls.

- [x] **01. Parking Lot System** (`systems/02-parking-lot`)
  - Patterns: Strategy (pricing), Factory (vehicle/spot), State.
  - Concurrency: Goroutine safety (`sync.RWMutex`), Python thread locks.
  - Branch: [`parking-lot`](https://github.com/asheeshsahu7300/system-design/tree/parking-lot)
- [ ] **02. Elevator System (Multi-Car Controller)**
  - Patterns: State Pattern, Dispatcher Algorithm (LOOK / SCAN).
  - Branch: [`elevator-system`](https://github.com/asheeshsahu7300/system-design/tree/elevator-system)
- [ ] **03. In-Memory Key-Value Store with TTL & LRU/LFU Eviction**
  - Patterns: Doubly Linked List + Hash Map, Read-Write locks.
  - Branch: [`lru-cache`](https://github.com/asheeshsahu7300/system-design/tree/lru-cache)
- [ ] **04. Movie Ticket Booking System (BookMyShow / Fandango)**
  - Patterns: Distributed Locks (Redis Redlock), Optimistic Concurrency Control.
  - Branch: [`ticket-booking`](https://github.com/asheeshsahu7300/system-design/tree/ticket-booking)

---

## Phase 2: Foundational Microservices & Tier-1 Systems
Objective: Master API design, caching, hashing, data storage selection, and failure handling.

- [x] **01. URL Shortener (TinyURL / Bitly)** (`systems/01-url-shortener`)
  - Concepts: Base62 encoding, Snowflake ID + Feistel Permutation, 302 vs 301, Redis Cache Aside, Bloom Filter.
  - Branch: [`url-shortner`](https://github.com/asheeshsahu7300/system-design/tree/url-shortner)
- [ ] **02. Distributed Rate Limiter** (`systems/03-rate-limiter`)
  - Concepts: Token Bucket, Leaky Bucket, Sliding Window Log, Redis Lua Scripts.
  - Branch: [`rate-limiter`](https://github.com/asheeshsahu7300/system-design/tree/rate-limiter)
- [ ] **03. Distributed Unique ID Generator**
  - Concepts: Twitter Snowflake (Timestamp + Datacenter + Worker ID + Sequence), Ticket Server, UUIDv7.
  - Branch: [`snowflake-id`](https://github.com/asheeshsahu7300/system-design/tree/snowflake-id)
- [ ] **04. Notification Engine (Multi-Channel)** (`systems/04-notification-system`)
  - Concepts: Fanout exchange, Idempotency keys, Priority Queues (Kafka/RabbitMQ), Dead Letter Queue (DLQ).
  - Branch: [`notification-system`](https://github.com/asheeshsahu7300/system-design/tree/notification-system)

---

## Phase 3: Real-Time & High-Concurrency Systems
Objective: Master WebSockets, stateful servers, message brokers, and event streaming.

- [ ] **01. Real-Time Chat System (WhatsApp / Slack / Discord)** (`systems/05-whatsapp-chat`)
  - Concepts: Long Polling vs WebSockets, Presence Server, Message ordering, Cassandra/ScyllaDB wide-column storage.
  - Branch: [`chat-system`](https://github.com/asheeshsahu7300/system-design/tree/chat-system)
- [ ] **02. Collaborative Document Editor (Google Docs / Figma)**
  - Concepts: Operational Transformation (OT), Conflict-free Replicated Data Types (CRDTs), WebRTC.
  - Branch: [`collaborative-editor`](https://github.com/asheeshsahu7300/system-design/tree/collaborative-editor)
- [ ] **03. Web Crawler & Search Autocomplete**
  - Concepts: Distributed Crawling, Robots.txt, Dedup with Bloom Filters, Trie structure for Typeahead suggestions.
  - Branch: [`search-autocomplete`](https://github.com/asheeshsahu7300/system-design/tree/search-autocomplete)

---

## Phase 4: Hyperscale & Domain-Specific Heavyweights
Objective: Master geospatial indexing, video transcoding pipelines, CDN architecture, and surge algorithms.

- [ ] **01. Video Streaming Platform (YouTube / Netflix / Disney+ Hotstar)** (`systems/06-youtube-hotstar-streaming`)
  - Concepts: Ingestion pipelines, Adaptive Bitrate Streaming (HLS/DASH), Video chunking, Transcoding DAG, CDN Edge caching, Live cricket surge handling.
  - Branch: [`video-streaming`](https://github.com/asheeshsahu7300/system-design/tree/video-streaming)
- [ ] **02. Ride Hailing & Dispatch Platform (Uber / Rapido / Lyft)** (`systems/07-uber-rapido-ride-matching`)
  - Concepts: Geospatial indexing (Uber H3 Hexagons), Real-time driver GPS tracking, Ride matching algorithm, Dynamic Surge Pricing, WebSocket location stream.
  - Branch: [`ride-hailing`](https://github.com/asheeshsahu7300/system-design/tree/ride-hailing)
- [ ] **03. Flash Sale / E-Commerce Inventory (Amazon / Flipkart)**
  - Concepts: Distributed transactions, Two-Phase Commit vs Saga Pattern, Redis inventory reservation with Lua, Outbox Pattern.
  - Branch: [`flash-sale`](https://github.com/asheeshsahu7300/system-design/tree/flash-sale)
- [ ] **04. Payment Processing Gateway (Stripe / Razorpay)**
  - Concepts: Strict Idempotency, Double-entry ledger, Reconciliation workers, Webhook retry with exponential backoff.
  - Branch: [`payment-gateway`](https://github.com/asheeshsahu7300/system-design/tree/payment-gateway)

---

## Weekly Roadmap Schedule

| Timeline | Milestone Focus | Hands-On Deliverable | Dedicated Branch |
|---|---|---|---|
| **Week 1** | URL Shortener + Capacity Math | Deploy Go & Python APIs + Web UI | [`url-shortner`](https://github.com/asheeshsahu7300/system-design/tree/url-shortner) |
| **Week 2** | Parking Lot & LLD Patterns | Implement concurrency-safe OOP in Python & Go | [`parking-lot`](https://github.com/asheeshsahu7300/system-design/tree/parking-lot) |
| **Week 3** | Rate Limiter & ID Generator | Implement Token Bucket & Snowflake algorithms | [`rate-limiter`](https://github.com/asheeshsahu7300/system-design/tree/rate-limiter) |
| **Week 4** | Notification & Chat Architecture | WebSockets + Redis PubSub + Message queues | [`chat-system`](https://github.com/asheeshsahu7300/system-design/tree/chat-system) |
| **Week 5** | Video Streaming (YouTube/Hotstar) | HLS streaming server + Transcoder DAG design | [`video-streaming`](https://github.com/asheeshsahu7300/system-design/tree/video-streaming) |
| **Week 6** | Ride Hailing (Uber/Rapido) | H3 Spatial indexing & Dispatcher simulation | [`ride-hailing`](https://github.com/asheeshsahu7300/system-design/tree/ride-hailing) |
