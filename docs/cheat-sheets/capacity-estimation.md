# Capacity Estimation & Back-of-the-Envelope Math

In any System Design interview, being able to quickly compute QPS, storage, and memory bandwidth sets senior engineers apart from juniors.

---

## 1. Numbers Every Software Engineer Should Know

| Metric / Operation | Approximate Latency |
|--------------------|---------------------|
| L1 Cache reference | 0.5 ns |
| L2 Cache reference | 7 ns |
| Main memory (RAM) reference | 100 ns |
| Read 1 MB sequentially from memory | 3,000 ns (3 µs) |
| Read 1 MB sequentially from NVMe SSD | 50,000 ns (50 µs) |
| Read 1 MB sequentially from HDD | 20,000,000 ns (20 ms) |
| Round trip within same datacenter | 500,000 ns (0.5 ms) |
| Round trip cross-country (US / Europe) | 150 ms |

> **Key Rule of Thumb**: Memory is ~1,000x faster than SSD, and SSD is ~1,000x faster than traditional spinning disk.

---

## 2. Powers of Two & Storage Prefixes

| Power of 2 | Value | Exact Bytes | Approx | Common Symbol |
|------------|-------|-------------|--------|---------------|
| $2^{10}$ | 1,024 | 1 KB | Thousand | Kilo (KB) |
| $2^{20}$ | 1,048,576 | 1 MB | Million | Mega (MB) |
| $2^{30}$ | 1,073,741,824 | 1 GB | Billion | Giga (GB) |
| $2^{40}$ | 1,099,511,627,776 | 1 TB | Trillion | Tera (TB) |
| $2^{50}$ | 1,125,899,906,842,624 | 1 PB | Quadrillion | Peta (PB) |

---

## 3. Essential Formulas & Shortcuts

### Seconds in a Day
$$\text{Seconds in a Day} = 24 \times 60 \times 60 = 86,400 \approx 100,000 \text{ (for fast mental estimation)}$$
Or use $86,400 \approx 8.64 \times 10^4$.

### Daily Traffic to QPS (Queries Per Second)
$$\text{Average QPS} = \frac{\text{Total Requests per Day}}{86,400}$$
$$\text{Peak QPS} = \text{Average QPS} \times 2 \text{ to } 5$$

*Example*: If an app receives 100 Million daily requests:
$$\text{Average QPS} = \frac{100,000,000}{86,400} \approx 1,157 \text{ QPS}$$
$$\text{Peak QPS} \approx 1,157 \times 3 \approx 3,500 \text{ QPS}$$

---

### Storage Calculation Formula
$$\text{Daily Storage} = \text{Writes per Day} \times \text{Size of 1 Record}$$
$$\text{Storage for } N \text{ Years} = \text{Daily Storage} \times 365 \times N$$

*Example*: URL Shortener with 100 Million new URLs created per month (~3.3M/day), average record size 500 bytes:
$$\text{Daily Storage} = 3.3 \times 10^6 \times 500 \text{ bytes} \approx 1.65 \text{ GB / day}$$
$$\text{5-Year Storage} = 1.65 \text{ GB} \times 365 \times 5 \approx 3 \text{ TB}$$

---

### Cache Memory Estimation (80 / 20 Rule & Working Sets)
> **Critical Conceptual Distinction**: The 80/20 rule states that **20% of unique items/URLs** generate **80% of read traffic**. It does **not** mean you cache "20% of reads".
- **Step 1**: Establish the **active working set of unique items** ($U_{\text{active}}$).
  - *Baseline*: If daily created items ($3.3\text{M}$) approximate the active set:
    $$\text{Hot Unique Items} = 3.3\text{M} \times 0.20 = 660,000 \text{ items}$$
- **Step 2**: Calculate logical memory:
  $$\text{Logical RAM} = \text{Hot Unique Items} \times \text{Size per Entry (incl. Redis overhead)}$$
  $$660,000 \times 1\text{ KB} \approx 660 \text{ MB}$$
- **Step 3**: Apply operational headroom factor (Replication + Fragmentation + Spike buffer $\approx 3\times$):
  $$\text{Provisioned RAM} \approx 2 \text{ to } 3 \text{ GB}$$
- **Senior Rule**: Never claim you can derive the count of hot unique items from read traffic alone; access-frequency distribution determines the working set size.
