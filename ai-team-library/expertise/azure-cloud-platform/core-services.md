# Azure Core Services

Standards for deploying and operating workloads on Microsoft Azure.
This guide covers identity, networking, compute, storage, messaging, and databases.
All Azure usage must follow the Azure Well-Architected Framework. Deviations require an ADR.

---

## Defaults

| Category | Default | Alternatives |
|----------|---------|-------------|
| **Identity** | Microsoft Entra ID (Azure AD) with conditional access | Entra External ID (customer-facing), Managed Identities (service-to-service) |
| **Networking** | VNet with public + private subnets across 3 Availability Zones | Virtual WAN (multi-VNet), Private Link (service endpoints) |
| **Compute** | Azure App Service (web apps/APIs) | AKS (Kubernetes workloads), Azure Functions (event-driven, <10 min), Container Apps (serverless containers) |
| **Container Orchestration** | AKS with managed node pools | Container Apps (serverless Kubernetes), App Service (single-container) |
| **Storage** | Azure Blob Storage with soft delete enabled | Azure Files (shared filesystem), Azure Data Lake Storage Gen2 (analytics) |
| **Database** | Azure Cosmos DB (globally distributed NoSQL) | Azure SQL Database (relational), Azure Database for PostgreSQL Flexible Server |
| **Messaging** | Azure Service Bus (enterprise messaging) | Event Grid (event routing), Event Hubs (streaming ingestion), Storage Queues (simple queuing) |
| **Secrets** | Azure Key Vault with soft delete and purge protection | App Configuration (non-secret config), Managed Identity (credential-free auth) |
| **IaC** | Bicep (Azure-native) | Terraform (multi-cloud teams), Pulumi (programming-language preference), ARM templates (legacy) |

---

## Identity (Microsoft Entra ID)

### Principles

- **Least privilege.** Every role assignment grants only the permissions needed
  for the specific task. Use built-in RBAC roles before creating custom roles.
- **No long-lived credentials.** Use Managed Identities for Azure service-to-service
  authentication. Never embed client secrets or certificates in code.
- **Conditional Access.** Enforce MFA, device compliance, and location-based policies
  for all human users. Block legacy authentication protocols.

### RBAC Assignment

```json
{
  "properties": {
    "roleDefinitionId": "/subscriptions/{sub-id}/providers/Microsoft.Authorization/roleDefinitions/{role-id}",
    "principalId": "{managed-identity-object-id}",
    "principalType": "ServicePrincipal",
    "description": "Allow app to read from storage account",
    "condition": "[!(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read'})]",
    "conditionVersion": "2.0"
  }
}
```

### Guardrails

- Enable Azure Policy at the Management Group level for governance at scale.
- Deny resource deployments outside approved regions.
- Require MFA for all privileged roles (Global Admin, Subscription Owner).
- Tag every service principal and app registration with `team`, `environment`, and `purpose`.

---

## VNet & Networking

### Standard Architecture

```
VNet (10.0.0.0/16)
├── Public Subnets  (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)  — App Gateway, Bastion
├── App Subnets     (10.0.11.0/24, 10.0.12.0/24, 10.0.13.0/24) — App Service, AKS
└── Data Subnets    (10.0.21.0/24, 10.0.22.0/24, 10.0.23.0/24) — Cosmos DB, SQL, Redis
```

- **3 Availability Zones** minimum for production workloads.
- **NAT Gateway** attached to app subnets for outbound internet access.
  Use one NAT Gateway per AZ for zone-redundant outbound.
- **Network Security Groups (NSGs)** on every subnet. Default deny all inbound.
  Allow only required ports from known sources.
- **Application Security Groups (ASGs)** to group VMs/NICs by function for readable NSG rules.
- **NSG Flow Logs** enabled and shipped to Log Analytics workspace for audit.

### Connectivity

| Pattern | Solution |
|---------|----------|
| Service-to-service within VNet | NSG rules + ASGs |
| VNet-to-VNet | VNet Peering or Virtual WAN |
| VNet-to-on-premises | ExpressRoute or Site-to-Site VPN |
| VNet-to-Azure-services | Private Endpoints (all PaaS services) |

---

## Compute

### App Service (Default for Web Apps)

```json
{
  "type": "Microsoft.Web/sites",
  "apiVersion": "2023-12-01",
  "properties": {
    "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', 'my-app-plan')]",
    "siteConfig": {
      "linuxFxVersion": "PYTHON|3.12",
      "alwaysOn": true,
      "minTlsVersion": "1.2",
      "http20Enabled": true,
      "healthCheckPath": "/health",
      "appSettings": [
        {
          "name": "WEBSITE_RUN_FROM_PACKAGE",
          "value": "1"
        }
      ]
    },
    "httpsOnly": true,
    "identity": {
      "type": "SystemAssigned"
    }
  }
}
```

- Use **Premium v3** or **Premium v2** plans for production (zone-redundant, VNet integration).
- Enable **deployment slots** for blue-green deployments with auto-swap.
- Configure **auto-scaling** based on CPU, memory, or HTTP queue length.
- Use **Managed Identity** for authentication to Key Vault, Storage, and databases.

### AKS (Kubernetes Workloads)

```yaml
# AKS cluster essentials
apiVersion: containerservice.azure.com/v1
kind: ManagedCluster
properties:
  kubernetesVersion: "1.30"
  dnsPrefix: my-cluster
  agentPoolProfiles:
    - name: system
      count: 3
      vmSize: Standard_D4s_v5
      mode: System
      availabilityZones: ["1", "2", "3"]
    - name: workload
      count: 3
      vmSize: Standard_D8s_v5
      mode: User
      availabilityZones: ["1", "2", "3"]
      enableAutoScaling: true
      minCount: 3
      maxCount: 10
  networkProfile:
    networkPlugin: azure
    networkPolicy: calico
    serviceCidr: 10.1.0.0/16
    dnsServiceIP: 10.1.0.10
  addonProfiles:
    azureKeyvaultSecretsProvider:
      enabled: true
    omsAgent:
      enabled: true
```

- Use **system and user node pools** — system pool for cluster services, user pools for workloads.
- Enable **Azure CNI** for VNet-native pod networking (pod IP from subnet CIDR).
- Configure **cluster autoscaler** on user node pools.
- Use **Workload Identity** (not pod identity) for Azure resource access from pods.
- Store images in **Azure Container Registry (ACR)** with vulnerability scanning enabled.

### Azure Functions (Event-Driven)

- Use for event-driven workloads: HTTP triggers, Service Bus triggers, Timer triggers,
  Blob Storage triggers.
- **Consumption plan** for variable/bursty workloads. **Premium plan** for VNet integration
  and pre-warmed instances.
- **Timeout:** Consumption plan max 10 minutes, Premium plan max 60 minutes.
- **Cold starts:** Use Premium plan with minimum instance count for latency-sensitive endpoints.

---

## Storage (Azure Blob Storage)

### Storage Account Configuration

- **Redundancy:** ZRS (zone-redundant) for production, LRS (locally redundant) for dev/test.
  GRS (geo-redundant) for disaster recovery of critical data.
- **Encryption:** Azure-managed keys (default) or customer-managed keys in Key Vault (regulatory).
- **Public access:** Disabled at the storage account level. Use Private Endpoints for access.
- **Soft delete:** Enabled with 14-day retention for blobs and containers.
- **Lifecycle management:** Transition to Cool tier after 90 days, Archive after 365 days.
  Delete old snapshots and versions after retention period.

```json
{
  "rules": [
    {
      "name": "archiveOldBlobs",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": { "daysAfterModificationGreaterThan": 90 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 365 }
          },
          "snapshot": {
            "delete": { "daysAfterCreationGreaterThan": 180 }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"]
        }
      }
    }
  ]
}
```

---

## Database (Azure Cosmos DB)

### Cosmos DB Standards

- **Consistency level:** Session consistency (default). Strong consistency only when required
  by business logic (increases latency and cost).
- **Partition key:** Choose a high-cardinality key that evenly distributes reads and writes.
  Avoid hot partitions. Design the partition key before writing any data.
- **Throughput:** Use autoscale throughput for variable workloads. Manual throughput for
  predictable, steady-state workloads. Start with autoscale max 4000 RU/s and tune.
- **Availability:** Multi-region writes for globally distributed applications. Zone redundancy
  enabled in each region.
- **Backup:** Continuous backup with point-in-time restore (PITR) enabled. 30-day retention.

```json
{
  "type": "Microsoft.DocumentDB/databaseAccounts",
  "properties": {
    "databaseAccountOfferType": "Standard",
    "consistencyPolicy": {
      "defaultConsistencyLevel": "Session"
    },
    "locations": [
      { "locationName": "East US", "failoverPriority": 0, "isZoneRedundant": true },
      { "locationName": "West US", "failoverPriority": 1, "isZoneRedundant": true }
    ],
    "backupPolicy": {
      "type": "Continuous",
      "continuousModeProperties": { "tier": "Continuous30Days" }
    },
    "publicNetworkAccess": "Disabled"
  }
}
```

### Connection Management

- Use **Managed Identity** with Cosmos DB RBAC for data-plane access (no connection strings).
- Use the **Cosmos DB SDK** with singleton client instance per application. Never create
  a new client per request.
- Enable **integrated cache** for read-heavy workloads to reduce RU consumption.

---

## Messaging (Azure Service Bus)

### Service Bus Standards

- **Premium tier** for production workloads (dedicated resources, VNet integration, message
  size up to 100 MB).
- **Standard tier** acceptable for dev/test environments.
- Use **topics and subscriptions** for publish-subscribe patterns.
- Use **queues** for point-to-point messaging with guaranteed FIFO ordering (sessions).
- Enable **dead-letter queues** and monitor dead-letter count with alerts.

```csharp
// Service Bus sender with Managed Identity
var client = new ServiceBusClient(
    "my-namespace.servicebus.windows.net",
    new DefaultAzureCredential());

var sender = client.CreateSender("order-events");

var message = new ServiceBusMessage(BinaryData.FromObjectAsJson(orderEvent))
{
    ContentType = "application/json",
    Subject = "OrderCreated",
    SessionId = orderEvent.CustomerId,
    MessageId = Guid.NewGuid().ToString()
};

await sender.SendMessageAsync(message);
```

### Messaging Patterns

| Pattern | Implementation |
|---------|---------------|
| Competing consumers | Multiple receivers on a single queue |
| Publish-subscribe | Topics with filtered subscriptions |
| Request-reply | Reply-to queue with correlation ID |
| Ordered processing | Sessions with session ID per entity |
| Deferred processing | Scheduled messages with enqueue time |

---

## Do / Don't

- **Do** use Management Groups and multiple subscriptions (dev, staging, production).
- **Do** tag every resource with `Environment`, `Team`, `CostCenter`, and `ManagedBy`.
- **Do** use Private Endpoints to keep traffic off the public internet.
- **Do** enable Microsoft Defender for Cloud across all subscriptions.
- **Do** encrypt all data at rest and in transit.
- **Do** use infrastructure as code for all resource provisioning.
- **Don't** use classic deployment model resources. Use Azure Resource Manager (ARM) only.
- **Don't** hardcode subscription IDs, tenant IDs, or resource IDs. Use Bicep/Terraform references.
- **Don't** create service principals with client secrets for applications. Use Managed Identities.
- **Don't** deploy production resources in a single Availability Zone.
- **Don't** use default networking. Create purpose-built VNets with NSGs on every subnet.
- **Don't** leave storage accounts with public network access enabled.

---

## Common Pitfalls

1. **Over-permissive RBAC assignments.** Assigning Owner or Contributor at the subscription level
   when a resource-group-scoped role suffices. Solution: assign roles at the narrowest scope
   possible and use Azure Policy to audit overprivileged assignments.
2. **Single-zone deployments.** A single zone outage takes down the entire application.
   Solution: deploy across 3 Availability Zones with zone-redundant services (App Service,
   AKS, Cosmos DB, Storage ZRS).
3. **NSGs without deny rules.** Default NSG rules allow intra-VNet traffic. Unintended
   lateral movement is possible. Solution: explicitly deny traffic between tiers and allow
   only required ports.
4. **Unmonitored costs.** Forgotten premium-tier services or idle resources run up the bill.
   Solution: set up Azure Cost Management budgets with alerts at 50%, 80%, and 100%.
5. **No disaster recovery plan.** Backups exist but have never been tested.
   Solution: schedule quarterly DR drills. Restore from backup and verify data integrity.
6. **Cosmos DB hot partitions.** A poorly chosen partition key causes throttling on a
   subset of physical partitions while others are idle. Solution: analyze partition key
   distribution before production launch using Cosmos DB metrics.
7. **Service Bus message loss.** Using ReceiveAndDelete mode causes message loss on
   consumer failure. Solution: use PeekLock mode with explicit message completion
   after successful processing.

---

## Checklist

- [ ] Subscriptions structured with Management Groups (dev/staging/prod separation)
- [ ] Azure Policy enforces region restrictions and naming conventions
- [ ] RBAC uses least-privilege built-in roles at narrowest scope; no wildcard permissions
- [ ] Managed Identities used for all service-to-service authentication; no client secrets
- [ ] MFA enforced for all human users via Conditional Access policies
- [ ] VNet spans 3+ Availability Zones with public, app, and data subnets
- [ ] NSGs default-deny inbound; only required ports open from known sources
- [ ] NSG Flow Logs enabled and retained in Log Analytics for audit
- [ ] Microsoft Defender for Cloud enabled across all subscriptions
- [ ] All storage accounts have encryption, soft delete, and public access disabled
- [ ] Cosmos DB uses appropriate partition key with autoscale throughput and continuous backup
- [ ] App Service / AKS configured with zone redundancy and auto-scaling
- [ ] Service Bus uses Premium tier with dead-letter monitoring for production
- [ ] All resources tagged with Environment, Team, CostCenter, ManagedBy
- [ ] Infrastructure provisioned via IaC (Bicep/Terraform)
- [ ] Azure Cost Management budgets configured with cost alerts
