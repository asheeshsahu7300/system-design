# System 06: Hyperscale Video Streaming (YouTube / Disney+ Hotstar)

An architectural deep dive into designing a global video streaming platform supporting billions of on-demand views (YouTube) and 50+ million concurrent live viewers (Hotstar Cricket Live).

---

## 1. Requirements

### Functional Requirements
1. **Video Ingestion & Upload**: Creators upload videos in various formats (MP4, MOV, MKV) up to 4K/8K resolution.
2. **Asynchronous Transcoding Pipeline**: Transcode raw uploads into multiple bitrates/resolutions (240p up to 4K) and codecs (H.264, VP9, AV1).
3. **Adaptive Bitrate Streaming (ABR)**: Stream content dynamically adapting to client network conditions using **HLS** (`.m3u8`) and **MPEG-DASH** (`.mpd`).
4. **Live Streaming (Hotstar Mode)**: Ingest live RTMP/SRT feeds and distribute low-latency video chunks (<3s latency) to 50M+ concurrent viewers.
5. **Metadata, Search & Recommendations**: Search video titles, tags, user channels, and real-time live chat/reactions.

### Non-Functional Requirements
1. **High Availability**: 99.999% uptime for stream playback.
2. **Ultra-Low Playback Latency**: Fast start time (<500ms time-to-first-frame), no rebuffering.
3. **Scalability**: Handle 500+ hours of video uploaded per minute and 50M+ concurrent live viewers during peak sporting events.
4. **Cost Efficiency**: Minimize egress bandwidth costs via multi-tiered CDN edge caching and Origin Shields.

---

## 2. Back-of-the-Envelope Capacity Estimation

### YouTube (Video-on-Demand Scale)
- **Upload Traffic**: 500 hours uploaded/minute $\approx 30,000 \text{ hours/hour} = 720,000 \text{ hours/day}$.
- **Storage Consumption**:
  - Average raw video: 1 hour $\approx$ 2 GB.
  - Multi-bitrate encoding overhead: ~4x storage expansion for 360p, 720p, 1080p, 4K $\approx$ 8 GB total per hour.
  - Daily Storage: $720,000 \times 8 \text{ GB} \approx 5.76 \text{ Petabytes / day}$.
  - Yearly Storage: $5.76 \text{ PB} \times 365 \approx 2.1 \text{ Exabytes / year}$.

### Hotstar Live Cricket (Peak Concurrency Surge)
- **Peak Concurrent Viewers**: 50,000,000 users watching simultaneously.
- **Average Stream Bitrate**: 2.5 Mbps (720p/1080p ABR profile).
- **Peak Egress Bandwidth**: $50,000,000 \times 2.5 \text{ Mbps} = 125,000,000 \text{ Mbps} = 125 \text{ Terabits per second (Tbps)}$.
- *Key Takeaway*: No single datacenter or cloud provider can serve 125 Tbps directly. Multi-CDN distribution (Akamai + Fastly + Cloudflare + AWS CloudFront) and edge peering with local ISPs (IXPs) is mandatory!

---

## 3. End-to-End System Architecture

```mermaid
flowchart TD
    Creator([Video Creator / Camera])
    Viewer([End User / Mobile / Smart TV])

    subgraph Ingestion & Processing
        IngestGW[Ingestion Gateway / S3 Direct Upload]
        RawBucket[(Raw Video Storage - S3)]
        KafkaEvents[Kafka Upload Events]
        DAGMaster[DAG Transcoding Orchestrator]
        WorkerPool[Transcoder Worker Pool - GPU / CPU]
        ProcessedBucket[(Segmented Chunk Storage - S3)]
    end

    subgraph Packaging & Manifest
        Packager[HLS / DASH Packager]
        ManifestGen[Master .m3u8 Playlist Generator]
    end

    subgraph Content Delivery Network (CDN)
        OriginShield[Origin Shield Cache]
        EdgeCDN[Global Edge CDN POPs]
        ISPPeering[Local ISP Peering / Open Connect]
    end

    subgraph Metadata & Social Tier
        MetadataDB[(PostgreSQL / CockroachDB)]
        LiveChatCluster[WebSocket Chat / Reaction Cluster]
        RedisStats[(Redis Real-time View Counters)]
    end

    Creator -->|Upload MP4/MOV| IngestGW --> RawBucket
    IngestGW --> KafkaEvents --> DAGMaster
    DAGMaster --> WorkerPool
    WorkerPool --> Packager
    Packager --> ProcessedBucket
    Packager --> ManifestGen
    
    ProcessedBucket --> OriginShield --> EdgeCDN --> ISPPeering
    Viewer -->|Fetch Master .m3u8| EdgeCDN
    Viewer -->|Download 2s Chunks| ISPPeering
    Viewer <--> LiveChatCluster
```

---

## 4. Critical Engineering Deep Dives

### A. Adaptive Bitrate Streaming (ABR) Mechanics
When a client requests a video, they receive a **Master Manifest** (`master.m3u8`):

```text
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
360p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
720p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/index.m3u8
```

- Each resolution playlist splits video into **2 to 6 second media segments** (`segment_001.ts` or `.m4s`).
- The player dynamically assesses buffer fullness and network throughput. If WiFi drops, player requests the next segment from the `360p` playlist without any visible pause!

### B. Hotstar's Concurrency Surge: Why Live Cricket is Harder than Netflix
1. **Predictability**: On Netflix or YouTube VOD, views are distributed across millions of titles. In live cricket (e.g. India vs Pakistan World Cup final), **50 million users watch the exact same frame at the exact same second**.
2. **Cache Hit Ratio at Edge**:
   - Because all 50M users fetch the exact same 2-second chunk (`live_10423.m4s`), the edge CDN cache hit ratio reaches **> 99.8%**.
   - The origin only serves 1 chunk per 2 seconds; Edge CDNs fan out to millions.
3. **Thundering Herd on Dynamic APIs**:
   - Scores, live chat, emojis, and view counts cannot be cached on standard CDNs.
   - Solution: Aggressive client-side polling with jitter, WebSocket connection pooling, and Redis HyperLogLog for real-time unique viewer estimation.
