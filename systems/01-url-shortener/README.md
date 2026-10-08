# System 01: URL Shortener (TinyURL / Bitly)

> **Deep-Dive Engineering Specifications**:
> - [**High-Level Design (HLD) Specification**](docs/HLD.md) - Capacity planning, global edge CDN, DB sharding, failure modes.
> - [**Low-Level Design (LLD) Specification**](docs/LLD.md) - UML domain class diagrams, sequence flows, singleflight, SQL/DynamoDB schema.
> - [**System Design RFC Document**](docs/SYSTEM_DESIGN_RFC.md) - Production RFC, SLOs/SLIs, security threat modeling, disaster recovery runbooks.

---

## 1. Requirements

### Functional Requirements
1. **Shorten URL**: Given a long URL (e.g. `https://example.com/very/long/path?param=123`), generate a unique, short alias (e.g. `http://tiny.url/7bX9qZ`).
2. **Redirection**: Accessing the short link redirects the user to the original long URL with minimum latency.
3. **Custom Aliases (Optional)**: Users can supply a custom slug (e.g. `tiny.url/my-portfolio`).
4. **Link Expiry (TTL)**: Short links can optionally expire after a defined duration (default: 2 years).
5. **Analytics**: Track click count, referrers, and access timestamps.

### Non-Functional Requirements
1. **High Availability**: 99.99% uptime (links should never fail to resolve).
2. **Low Latency**: **Internal service lookup P99 < 10ms** (server-side Redis/app resolution time, excluding client-to-edge network transit RTT).
3. **Read Heavy**: Ratio of reads (redirects) to writes (creations) is **100 : 1**.
4. **Collision Free**: Short codes must be mathematically guaranteed unique.
5. **Security**: Short URLs must be non-sequential (obfuscated) to prevent crawler enumeration.

---

## 2. Back-of-the-Envelope Capacity Estimation

### Traffic Estimation
- **New URLs created (Writes)**: 100 Million / month $\approx$ 3.3 Million / day.
- **Write QPS**: $\frac{3,300,000}{86,400} \approx 38 \text{ writes/sec}$ (Peak: ~100 writes/sec).
- **Read-to-Write Ratio**: $100 : 1$.
- **Read QPS (Redirects)**: $38 \times 100 \approx 3,800 \text{ reads/sec}$ (Peak: ~12,000 reads/sec).

### Storage Estimation (5 Years)
- **Record Size Breakdown**:
  - `short_code`: 7 bytes (VARCHAR)
  - `original_url`: 512 bytes (VARCHAR)
  - `created_at`: 8 bytes (TIMESTAMP)
  - `expires_at`: 8 bytes (TIMESTAMP)
  - `user_id`: 16 bytes (UUID)
  - Overhead & Indexes: ~150 bytes
  - **Total per record**: $\approx 700 \text{ bytes}$.
- **Total Records in 5 Years**: $100 \text{M/mo} \times 12 \times 5 = 6 \text{ Billion records}$.
- **Total Storage**: $6 \times 10^9 \times 700 \text{ bytes} \approx 4.2 \text{ TB}$ (easily managed on a sharded PostgreSQL or DynamoDB cluster).

### Memory & Cache Estimation (Active Working Set & 80/20 Rule)

The system receives $\approx 328\text{M redirects/day}$. If 80% of traffic is concentrated on the top 20% hottest URLs:
$$328\text{M} \times 80\% = 262.4\text{M redirects/day to hot URLs}$$

> **The Mathematical Nuance**: Knowing that the hot set receives $262.4\text{M}$ requests does **not** uniquely determine how many *distinct hot URLs* exist.

Depending on the domain distribution:
| Hot Unique URLs | Avg Redirects per Hot URL / Day | Logical RAM (at ~1 KB/entry) |
|---:|---:|---:|
| **100,000** | 2,624 | ~100 MB |
| **500,000** | 525 | ~500 MB |
| **660,000** (Baseline 20% of 3.3M daily writes) | 398 | **~660 MB** |
| **1,000,000** | 262 | ~1.0 GB |
| **10,000,000** (Multi-week campaign pool) | 26 | ~10.0 GB |

#### Concrete Production Sizing Recommendation:
> **"Cache approximately 660K hot URLs initially, based on the assumption that 20% of the 3.3M daily active URLs generate 80% of traffic. At ~1 KB per Redis entry (including key, value, and Redis memory overhead), this requires ~660 MB of logical cache capacity. With replication, jemalloc fragmentation, and operational headroom, provision approximately 2–3 GB. In production, the hot-set size should be determined from actual access-frequency data rather than assuming all newly created URLs are active."**

---

## 3. End-to-End System Architecture

```mermaid
flowchart TD
    User([User / Browser])
    Cloudflare[Cloudflare Edge / Anycast DNS]
    EdgeCache[(Cloudflare Edge Cache)]
    LB[Load Balancer / Nginx]
    
    subgraph Compute Tier: Redirect Service
        API[Redirect Service Instances - Go / Python]
    end
    
    subgraph In-Memory Cache Tier
        Redis[(Redis Cluster - LRU Cache)]
        Bloom[Distributed Bloom Filter]
    end
    
    subgraph Data Tier
        DB[(Primary DB - PostgreSQL / DynamoDB)]
        IDGen[Snowflake ID Generator + Bit Permutation]
    end
    
    subgraph Asynchronous Decoupled Analytics
        Kafka[Kafka: click-events topic]
        Worker[Analytics Ingestion Consumer]
        ClickDB[(ClickHouse OLAP)]
    end

    User --> Cloudflare
    Cloudflare --> EdgeCache
    EdgeCache -- "HIT (Edge 302)" --> User
    EdgeCache -- "MISS" --> LB --> API

    %% Critical Path
    API <--> Bloom
    API <--> Redis
    API <--> DB
    API <--> IDGen
    API -->|302 Redirect Location| User

    %% Fully Decoupled Async Path (Zero latency impact on redirect)
    API -. "Async Fire-and-Forget Event" .-> Kafka
    Kafka --> Worker --> ClickDB
```

---

## 4. Key Design Decisions & Trade-offs

### A. Namespace Capacity (7 Characters)
- Character set: `[0-9, a-z, A-Z]` = $10 + 26 + 26 = 62$ characters (**Base62**).
- Total Combinations:
  $$62^7 = 3,521,614,606,208 \approx 3.52 \text{ Trillion}$$
- At 100 Million new URLs created per month:
  $$\frac{3.52 \times 10^{12}}{100 \times 10^6} = 35,216 \text{ months} \approx 2,935 \text{ years}$$

### B. Slug Generation: Snowflake + Bit Permutation vs KGS
1. **Naive Random Generation / Random KGS**:
   - Requires collision detection on every write, or a massive pre-generated inventory database of unused keys.
2. **Auto-Incrementing Integer**:
   - Single DB bottleneck and exposes business volume (sequential IDs can be scraped).
3. **Production Standard (Recommended): Distributed Unique ID + Permutation + Base62**:
   $$\text{Twitter Snowflake (64-bit ID)} \longrightarrow \text{Bit Permutation / Feistel Obfuscation} \longrightarrow \text{Base62}$$
   - **Guaranteed Uniqueness**: Snowflake IDs are inherently collision-free across distributed nodes.
   - **Zero Collision Checks**: No database lookups needed during slug generation.
   - **Non-Sequential & Secure**: Feistel cipher / pseudo-random bit permutation scatters sequential IDs into non-contiguous numbers, preventing enumeration attacks.
   - **No Inventory Overhead**: Zero pre-generated key storage required.

### C. Redirection Status Code: 302/307 vs 301
- **HTTP 301 (Moved Permanently)**:
  - The *initial* redirect request hits our service and can be logged.
  - However, browsers and intermediate CDNs cache the redirect aggressively. **Subsequent clicks from that user bypass our infrastructure completely**, leading to severely undercounted analytics.
- **HTTP 302 Found / 307 Temporary**:
  - Browser executes the request through our edge on every click.
  - Retains full control to record every click, inspect user-agent/referrer, and revoke compromised or malicious links instantly.
  - *Internal Lookup Latency*: Kept $< 5\text{ms}$ via Edge / Redis cache.

### D. Critical Path vs Asynchronous Analytics Decoupling
- **Critical Path**: Client $\rightarrow$ Edge Cache $\rightarrow$ Redis $\rightarrow$ DB (Resolve `short_code` $\rightarrow$ `original_url` and return 302).
- **Asynchronous Path**: Background non-blocking push to Kafka/Buffer for analytics processing in ClickHouse.
- **Guarantee**: Even if Kafka, ClickHouse, or analytics workers crash completely, **redirections continue functioning with zero degradation**.

---

## 5. Implementation Directory Structure

```
01-url-shortener/
├── backend-python/       # Asynchronous FastAPI service (Base62, Redis, Analytics)
├── backend-go/           # High-throughput Go net/http service (Goroutine safe)
├── frontend/             # Modern dashboard (Dark glassmorphism, QR code, live charts)
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── k8s/
└── docs/
    ├── HLD.md
    ├── LLD.md
    └── SYSTEM_DESIGN_RFC.md
```
