# billing_record_optimizer Overview

**This solution uses:**
1. Azure Cosmos DB (hot data, < 3 months)
2. Azure Blob Storage (cold data, > 3 months)
3. Azure Data Factory or Azure Functions for data archival
4. Middleware function for unified reads

## 1. Data Tiering Strategy

| Tier      | Storage             | Access Frequency | Cost              |
|-----------|---------------------|------------------|-------------------|
| **Hot**   | Cosmos DB           | Frequent         | $$$ (expensive)   |
| **Cold**  | Azure Blob (Cool/Archive) | Rare (≥ 3 months) | $ (very cheap)     |

## 2. Automated Data Archival Process
Use Azure Data Factory (ADF) or Durable Azure Functions to automate data movement.

Steps:
1. Query Cosmos DB for records older than 3 months.
2. Export data to Blob Storage (JSON or Parquet).
3. Verify export succeeded.
4. Delete archived records from Cosmos DB.
5. Set a trigger to run daily or weekly.
6. Add a Delete Activity after copy to remove records from Cosmos DB if export succeeds.

## 3. Unified Access Layer (Seamless Read API Support)
Introduce a middleware (e.g., Azure API Management policy, Azure Function, or custom service) to:
1. Intercept read requests.
2. Check if the requested data is within the last 3 months:
    * If yes → read from Cosmos DB.
    * If no → read from Blob Storage.
3. For write requests → continue writing to Cosmos DB.

## 4. Blob Storage Optimization
1. Use Cool Tier for infrequently accessed files.
2. Use Archive Tier if data is accessed rarely.
3. Apply lifecycle rules to move blobs between tiers automatically.

## 5. Monitoring & Governance
1. Add Application Insights for observability.
2. Track archival status and alert on failures.
3. Use RBAC & managed identities for secure access between services.

# Move old blobs to Cool or Archive Tier
* Move to cool tier
az storage blob set-tier \
  --container-name billing-archive \
  --name billing_2024-12-01.json \
  --tier Cool \
  --account-name <your-storage-account>

* Move to archive tier (even cheaper)
az storage blob set-tier \
  --container-name billing-archive \
  --name billing_2023-01-01.json \
  --tier Archive \
  --account-name <your-storage-account>

