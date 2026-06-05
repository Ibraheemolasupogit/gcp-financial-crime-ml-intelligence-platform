# Distributed Systems Design

## Purpose

This document describes distributed systems considerations for a future productionised version of the financial crime ML platform. It is a design blueprint only and is not production deployment.

## Batch vs Streaming Ingestion

Batch ingestion is appropriate for daily model training, historical feature backfills, governance evidence generation, and periodic monitoring. Cloud Storage and BigQuery provide a simple foundation for batch landing, validation, and analytics.

Streaming ingestion is appropriate when low-latency transaction risk signals are required. Pub/Sub can accept transaction events, Dataflow can enrich and validate records, and BigQuery can store streaming risk features or alert events.

## Pub/Sub Event Ingestion Design

Future transaction, account, beneficiary, device, and alert events can be published to dedicated Pub/Sub topics. Topic schemas should be versioned, documented, and validated before downstream processing. Failed messages should be sent to dead-letter topics with enough metadata for replay and investigation.

## Dataflow Batch and Stream Processing

Dataflow can support both batch enrichment and streaming transformations. Batch jobs can generate feature tables, while streaming jobs can compute near-real-time velocity indicators. Dataflow should write operational logs to Cloud Logging and pipeline outputs to BigQuery.

## BigQuery Partitioning and Clustering

Financial crime tables should be partitioned by event date, processing date, or alert date. Clustering should use fields commonly used for joins and investigation, such as `account_id`, `customer_id`, `transaction_id`, `beneficiary_id`, `device_id`, and risk band fields. Partition expiration should follow retention policy and audit obligations.

## Idempotency

Pipelines should support idempotent writes using deterministic transaction IDs, run IDs, and partition overwrite strategies. Batch scoring outputs should include scoring date, model version, config version, and source data version.

## Retries and Dead-Letter Queues

Transient failures should use bounded retries. Validation failures, schema failures, and malformed events should be routed to dead-letter storage or Pub/Sub topics for review. Dead-letter records should be monitored and included in operational reporting.

## Schema Evolution

Schemas should support additive changes through versioned contracts. Breaking changes should require validation, migration planning, lineage updates, and downstream consumer review. BigQuery table changes should be documented and tested before promotion.

## Late-Arriving Data

Late-arriving transactions and alerts should be processed through controlled backfill windows. Feature tables should capture processing timestamps so model training and monitoring can distinguish event time from processing time.

## Backfills

Backfills should use explicit run IDs, bounded date ranges, and audited configuration. Outputs should be written to isolated partitions or staging tables before replacement of production partitions.

## Replayability

Cloud Storage landing buckets, Pub/Sub retention, BigQuery snapshots, and versioned configuration support replayability. Model and scoring outputs should reference source artifact versions so investigators and validators can reproduce historical decisions.

## Audit Logging and Data Lineage

Cloud Logging and BigQuery audit tables should capture pipeline execution, validation results, model versions, scoring runs, monitoring outcomes, and evidence generation. Dataplex-style metadata can support lineage and discovery.

## Performance and Cost Considerations

BigQuery query design should minimise full-table scans through partition pruning and clustering. Dataflow autoscaling should be monitored for cost. Vertex AI Training should use appropriately sized compute. Batch jobs should be scheduled with clear service-level expectations and cost controls.

## Synthetic Data and Human Review Caveat

This repository uses synthetic data only. Any future production implementation would require privacy review, security review, model validation, human-in-the-loop controls, and financial crime governance before use.
