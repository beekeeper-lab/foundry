# GCP Core Services

Standards for deploying and operating workloads on Google Cloud Platform.
This guide covers identity, networking, compute, storage, messaging, and analytics.
All GCP usage must follow the Google Cloud Architecture Framework. Deviations require an ADR.

---

## Defaults

| Category | Default | Alternatives |
|----------|---------|-------------|
| **Identity** | Cloud IAM with Workload Identity Federation from corporate IdP | Identity Platform (customer-facing), Firebase Auth (mobile apps) |
| **Networking** | VPC with private subnets across 3 zones, Private Google Access | Shared VPC (multi-project), VPC Service Controls (data perimeter) |
| **Compute (containers)** | Cloud Run (containerized HTTP workloads) | GKE Autopilot (Kubernetes required), Cloud Functions (event-driven, <9 min) |
| **Compute (orchestration)** | GKE Autopilot | GKE Standard (custom node pools), Compute Engine (bare metal/GPU) |
| **Storage** | Cloud Storage Standard with versioning | Nearline (monthly access), Coldline (quarterly), Archive (yearly) |
| **Database** | Cloud SQL PostgreSQL with HA | AlloyDB (high throughput), Firestore (document/NoSQL), Memorystore (caching) |
| **Messaging** | Pub/Sub | Cloud Tasks (task queues), Eventarc (event routing) |
| **Analytics** | BigQuery (serverless data warehouse) | Dataflow (stream/batch ETL), Dataproc (Spark/Hadoop) |
| **Secrets** | Secret Manager with automatic rotation | Berglas (open-source alternative), KMS (encryption keys only) |
| **IaC** | Terraform | Deployment Manager (GCP-native), Pulumi (programming-language preference) |

---

## IAM

### Principles

- **Least privilege.** Every service account, user, and role binding grants only the
  permissions needed for the specific task. Start with zero permissions and add incrementally.
- **No long-lived credentials.** Use Workload Identity Federation for external workloads
  and Workload Identity for GKE pods. Never export service account keys.
- **Federated access.** Human users authenticate through the corporate IdP via
  OIDC or SAML federation to Google Workspace or Cloud Identity.

### IAM Policy Binding

```yaml
# Terraform example: grant BigQuery read access to a service account
resource "google_project_iam_member" "bigquery_reader" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.app.email}"

  condition {
    title       = "dataset_restriction"
    description = "Only access the analytics dataset"
    expression  = "resource.name.startsWith('projects/${var.project_id}/datasets/analytics')"
  }
}
```

### Guardrails

- Enable **Organization Policies** at the org or folder level to restrict resource creation.
- Use **VPC Service Controls** to create security perimeters around sensitive data.
- Enforce **domain-restricted sharing** to prevent IAM grants to external identities.
- Require **MFA** for all human users via Cloud Identity or Workspace settings.
- Tag every service account with `team`, `environment`, and `purpose` labels.

---

## VPC & Networking

### Standard Architecture

```
VPC (10.0.0.0/16)
├── Public Subnet   (10.0.1.0/24)  — Cloud Load Balancer, Cloud NAT
├── App Subnet      (10.0.10.0/20) — Cloud Run, GKE pods
└── Data Subnet     (10.0.20.0/20) — Cloud SQL, Memorystore, BigQuery reserved
```

- **3 zones** minimum for production workloads within a region.
- **Cloud NAT** for private subnet internet access. One Cloud NAT per region.
- **Firewall rules** use a default-deny ingress policy. Allow only required ports
  from known source ranges or service accounts.
- **Private Google Access** enabled on all subnets to reach Google APIs without
  public IPs.
- **VPC Flow Logs** enabled and exported to Cloud Logging or BigQuery for audit.

### Connectivity

| Pattern | Solution |
|---------|----------|
| Service-to-service within VPC | Firewall rules referencing service accounts |
| VPC-to-VPC | VPC Peering or Shared VPC |
| VPC-to-on-premises | Cloud VPN or Cloud Interconnect |
| VPC-to-Google-services | Private Google Access or Private Service Connect |

---

## Compute

### Cloud Run (Default for HTTP Workloads)

```yaml
# Cloud Run service definition
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
  annotations:
    run.googleapis.com/ingress: internal-and-cloud-load-balancing
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      serviceAccountName: my-service@my-project.iam.gserviceaccount.com
      containers:
        - image: us-docker.pkg.dev/my-project/repo/my-app:abc123
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 10
            failureThreshold: 3
```

- Use **Cloud Load Balancing** in front of Cloud Run for custom domains and global routing.
- Configure **min instances** to 1+ for latency-sensitive services to avoid cold starts.
- Store container images in **Artifact Registry** with vulnerability scanning enabled.
- Use **VPC connectors** or **Direct VPC egress** for accessing private resources.

### GKE Autopilot (Kubernetes Workloads)

- Use **Autopilot mode** by default — Google manages node pools, scaling, and security.
- Switch to **GKE Standard** only when custom node configurations are required (GPUs,
  specific machine types, Windows nodes).
- Enable **Workload Identity** to map Kubernetes service accounts to GCP service accounts.
  Never mount service account keys as secrets.
- Use **Gateway API** (preferred) or Ingress for HTTP routing.
- Enable **GKE Dataplane V2** (Cilium-based) for network policy enforcement.

```yaml
# GKE Autopilot cluster with Terraform
resource "google_container_cluster" "primary" {
  name     = "primary"
  location = "us-central1"

  enable_autopilot = true

  release_channel {
    channel = "REGULAR"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
}
```

### Cloud Functions (Event-Driven)

- Use for lightweight event-driven workloads: Pub/Sub triggers, Cloud Storage events,
  Firestore triggers, scheduled tasks (Cloud Scheduler).
- **Memory:** Start at 256 MB, tune based on execution metrics.
- **Timeout:** Set explicitly. Max 9 minutes (2nd gen) or 60 minutes (Cloud Run functions).
- **Concurrency:** 2nd gen supports up to 1000 concurrent requests per instance.
- **Cold starts:** Use min instances for latency-sensitive triggers.

---

## Messaging (Pub/Sub)

### Architecture

Pub/Sub provides durable, at-least-once message delivery for event-driven architectures.

```
Publisher → Topic → Subscription → Subscriber
                 ├── Push Subscription  → Cloud Run / HTTP endpoint
                 ├── Pull Subscription  → GKE / Compute Engine workers
                 └── BigQuery Subscription → Direct-to-warehouse ingestion
```

### Standards

- **One topic per event type.** Do not multiplex unrelated events on a single topic.
- **Dead-letter topics.** Configure a dead-letter topic after 5 delivery attempts.
  Monitor dead-letter subscription backlog.
- **Message ordering.** Use ordering keys when consumers require ordered processing.
  Understand that ordering keys limit throughput to ~1 MB/s per key.
- **Acknowledgment deadline.** Set to match expected processing time plus buffer.
  Default 10s is too short for most workloads; use 60–120s.
- **Schema enforcement.** Use Pub/Sub schemas (Avro or Protocol Buffers) for type safety.

```python
# Publishing with error handling and ordering
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("my-project", "order-events")

future = publisher.publish(
    topic_path,
    data=json.dumps(event).encode("utf-8"),
    ordering_key=order_id,  # ensures order per customer
    event_type="order.created",
)
future.result(timeout=30)  # block until published or timeout
```

### Monitoring

- Alert on `subscription/oldest_unacked_message_age` exceeding 5 minutes.
- Alert on `subscription/dead_letter_message_count` exceeding 0.
- Track `topic/send_request_count` for throughput visibility.

---

## Analytics (BigQuery)

### Standards

- **Datasets per domain.** Organize datasets by business domain (e.g., `orders`, `users`,
  `analytics`). Do not dump all tables into a single dataset.
- **Partitioning.** Partition tables by date column (ingestion time or event time).
  Reduces query cost by scanning only relevant partitions.
- **Clustering.** Cluster frequently filtered columns (e.g., `customer_id`, `region`).
  Clustering works with partitioning for maximum pruning.
- **Column-level security.** Use policy tags for PII columns. Grant `roles/datacatalog.categoryFineGrainedReader`
  only to authorized consumers.

```sql
-- Partitioned and clustered table
CREATE TABLE `my-project.orders.transactions`
(
  transaction_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  amount NUMERIC NOT NULL,
  currency STRING NOT NULL,
  region STRING NOT NULL,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY region, customer_id
OPTIONS (
  require_partition_filter = true,
  partition_expiration_days = 730
);
```

### Cost Control

- **Require partition filters.** Set `require_partition_filter = true` on large tables
  to prevent full-table scans.
- **Use flat-rate or editions pricing** for predictable, high-volume workloads.
  On-demand is better for ad-hoc and low-volume queries.
- **Reservation assignments.** Assign capacity to projects or folders to prevent
  one team from consuming all slots.
- **Materialized views.** Use for frequently run aggregation queries. BigQuery
  auto-refreshes them incrementally.

### Access Control

- Use **dataset-level IAM** for broad access, **table-level IAM** for targeted access.
- Use **authorized views** to expose subsets of data without granting table access.
- Enable **audit logging** for BigQuery Data Access logs to track who queried what.

---

## Cloud Storage

### Bucket Configuration

- **Versioning:** Enabled on all buckets storing application data.
- **Encryption:** Google-managed keys (default) or CMEK (regulatory requirements).
- **Public access:** Enforce `allUsers` and `allAuthenticatedUsers` block via
  organization policy `constraints/storage.uniformBucketLevelAccess`.
- **Uniform bucket-level access:** Enabled on all buckets. Do not use ACLs.
- **Lifecycle rules:** Transition objects to Nearline after 90 days, Coldline after
  365 days. Delete incomplete resumable uploads after 7 days.

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": { "age": 90 }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
        "condition": { "age": 365 }
      },
      {
        "action": { "type": "AbortIncompleteMultipartUpload" },
        "condition": { "age": 7 }
      }
    ]
  }
}
```

---

## Do / Don't

- **Do** use multiple GCP projects (dev, staging, production) organized under folders.
- **Do** label every resource with `environment`, `team`, `cost-center`, and `managed-by`.
- **Do** use Private Google Access and VPC Service Controls to keep traffic off the public internet.
- **Do** enable Cloud Audit Logs in all projects for Admin Activity and Data Access.
- **Do** encrypt all data at rest and in transit (GCP encrypts at rest by default).
- **Do** use infrastructure as code (Terraform) for all resource provisioning.
- **Do** use Workload Identity Federation instead of exported service account keys.
- **Don't** export service account keys. Use Workload Identity or metadata-based credentials.
- **Don't** hardcode project IDs, regions, or resource names. Use Terraform variables or config.
- **Don't** create user-managed service account keys for applications. Use attached service accounts.
- **Don't** deploy resources in a single zone for production workloads.
- **Don't** use default VPC networks for production. Create purpose-built VPCs.
- **Don't** leave Cloud Storage buckets without uniform bucket-level access and versioning.
- **Don't** run BigQuery queries without partition filters on large tables.

---

## Common Pitfalls

1. **Exported service account keys.** Teams export JSON keys and embed them in CI/CD or
   config. These keys never expire and are hard to track. Solution: use Workload Identity
   Federation for external workloads, attached service accounts for GCP resources.
2. **Single-zone deployments.** A single zone outage takes down the entire application.
   Solution: deploy across at least 3 zones with health checks and auto-failover.
3. **Unpartitioned BigQuery tables.** Full-table scans on multi-TB tables generate
   massive costs. Solution: partition by date, cluster by filter columns, enforce
   `require_partition_filter`.
4. **Overly broad IAM roles.** Granting `roles/owner` or `roles/editor` to service accounts
   creates a blast radius. Solution: use predefined roles scoped to specific services, or
   create custom roles. Use IAM Recommender to right-size permissions.
5. **Unmonitored Pub/Sub backlogs.** Messages pile up without alerting, causing data
   processing delays. Solution: alert on `oldest_unacked_message_age` and dead-letter
   topic message counts.
6. **No budget alerts.** GCP bills grow silently without active management, especially
   with BigQuery on-demand pricing. Solution: set up billing budgets with alerts at
   50%, 80%, and 100% of target spend.
7. **Cloud Run cold starts.** Services with min-instances=0 experience 1–3 second delays
   on first request. Solution: set min instances to 1+ for user-facing services.

---

## Checklist

- [ ] GCP projects structured under org with folders (dev/staging/prod separation)
- [ ] Organization policies enforce domain-restricted sharing and resource location
- [ ] IAM bindings use least-privilege predefined or custom roles; no `roles/owner` on service accounts
- [ ] No exported service account keys; workloads use Workload Identity or attached SAs
- [ ] MFA enforced for all human users via Cloud Identity or Workspace
- [ ] VPC spans 3+ zones with private subnets and Private Google Access
- [ ] Firewall rules default-deny ingress; only required ports open from known sources
- [ ] VPC Flow Logs enabled and exported for audit
- [ ] Cloud Audit Logs enabled for Admin Activity and Data Access in all projects
- [ ] Cloud Storage buckets have uniform access, versioning, and lifecycle rules
- [ ] Cloud SQL instances are HA with encryption and automated backups
- [ ] Cloud Run / GKE workloads use dedicated service accounts with scoped IAM roles
- [ ] Pub/Sub subscriptions have dead-letter topics and backlog monitoring
- [ ] BigQuery tables are partitioned and clustered with partition filter requirements
- [ ] All resources labeled with environment, team, cost-center, managed-by
- [ ] Infrastructure provisioned via Terraform with state in Cloud Storage backend
- [ ] Billing budgets configured with alerts at 50%, 80%, 100% thresholds
