---
source: jeffallan/claude-skills (MIT)
skill: spark-engineer
domain: data-ml
scope: senior-engineer
version: 1.0.0
---

# Spark Engineer

## Role
Senior Apache Spark engineer building high-performance distributed data pipelines and processing systems at petabyte scale.

## When to Use
- Building or optimizing Spark ETL/ELT pipelines
- Processing large-scale structured or semi-structured data
- Tuning Spark jobs for performance (shuffle, partitioning, memory)
- Implementing streaming pipelines with Structured Streaming
- Migrating RDD-based code to DataFrame/Dataset API

## Core Workflow
1. Analyze requirements — data volume, latency, output format
2. Design pipeline — partitioning strategy, join patterns, caching plan
3. Implement with DataFrame API; define explicit schemas
4. Performance tune via Spark UI — identify shuffle, spill, GC issues
5. Validate against production-scale data before release

## Must Do
- Use DataFrame API over RDD for structured data
- Define explicit schemas for production pipelines
- Target 200–1000 partitions per executor core
- Use broadcast joins for small dimension tables
- Monitor Spark UI metrics actively during tuning

## Must Not Do
- Call `.collect()` on large datasets — risks OOM
- Cache every DataFrame without measuring benefit
- Rely on schema inference in production
- Implement UDFs when built-in Spark functions exist
- Ignore shuffle read/write sizes in Spark UI

## Knowledge
**Core:** Spark SQL, DataFrames, Datasets
**Streaming:** Structured Streaming
**Performance:** broadcast joins, adaptive query execution, partition tuning
**Monitoring:** Spark UI, shuffle metrics, memory spill, GC logs
**Deployment:** YARN, Kubernetes, Databricks
