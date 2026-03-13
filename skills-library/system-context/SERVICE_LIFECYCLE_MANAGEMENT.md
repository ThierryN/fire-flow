---
name: service-lifecycle-management
category: system-context
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [services, docker, qdrant, ollama, neo4j, lifecycle, startup]
difficulty: easy
---

# Service Lifecycle Management

## Problem

Projects depend on background services (Qdrant, Ollama, Neo4j, MySQL). Agents waste time when services are down, get cryptic connection errors, and don't know how to start/stop/check each service.

## Solution Pattern

Standard check → start → verify flow for each service.

## Service Quick Reference

### Qdrant (Native — Primary)

```bash
# Check
curl -s http://localhost:6335/healthz

# Start (background)
"C:/path/to/tools/qdrant/qdrant.exe" --config-path "C:/path/to/tools/qdrant/config.yaml" &

# Collection stats
curl -s http://localhost:6335/collections/power_flow_memory | jq '.result.points_count'
```

### Qdrant (Docker — Backup)

```bash
# Check
docker ps | grep qdrant

# Start
docker start qdrant  # if container exists
# OR create new:
docker run -d --name qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Verify
curl -s http://localhost:6333/healthz
```

### Ollama

```bash
# Check
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# Start (if not running)
ollama serve &

# Verify embedding model
curl -s http://localhost:11434/api/tags | jq '.models[] | select(.name | contains("nomic"))'
```

### Neo4j (Docker — CodeGraphContext)

```bash
# Check
docker ps | grep neo4j-cgc

# Start
docker start neo4j-cgc

# Verify
curl -s http://localhost:7474 -u neo4j:codegraph123
```

### XAMPP MySQL

```bash
# Check
"C:/xampp/mysql/bin/mysqladmin" -u root status

# Start via XAMPP control panel or:
"C:/xampp/xampp_start.exe"

# Connect
"C:/xampp/mysql/bin/mysql" -u root -p
```

## Graceful Degradation Pattern

When a service is unavailable, don't crash — degrade:

```javascript
// Pattern: try service, fall back gracefully
async function searchMemory(query) {
  try {
    const results = await qdrantSearch(query)
    return results
  } catch (err) {
    if (err.code === 'ECONNREFUSED') {
      console.log('Qdrant unavailable — searching flat files instead')
      return flatFileSearch(query)
    }
    throw err
  }
}
```

## When to Use

- Starting a work session that depends on background services
- Debugging connection refused / timeout errors
- Setting up services on a fresh machine

## When NOT to Use

- Cloud-hosted services (they have their own health checks)
- CI/CD (use Docker Compose for all services)
