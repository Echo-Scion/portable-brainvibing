# Systems Load Testing Tactics (K6 / Artillery)

## 📊 Load Profile Definition
- **Baseline**: Normal traffic metrics (e.g., 100 VU constant).
- **Stress Test**: Gradual ramp up to breaking point (e.g., 0 to 5000 VU over 30 mins).
- **Spike Test**: Immediate jump to 10x traffic (e.g., 50 to 2000 VU in 1 min).

## 👨‍💻 Virtual User (VU) Scripting
- **Think-Time**: Use `sleep(random(1, 3))` between requests.
- **Realistic Paths**: Do not just hit one endpoint; simulate Login -> Dashboard -> Search -> Log out.

## 🛡️ Load Testing Validations
- **NEVER** run massive tests against live prod. Use Staging clones.
- **NEVER** report mean response times; always report **P95** and **P99** latency.
- **Distribute load**: Use multiple generator IPs if testing rate limits.

---
*Derived from Antigravity Skills Archive*
