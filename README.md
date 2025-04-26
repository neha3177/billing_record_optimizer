# billing_record_optimizer
This solution uses:
Azure Cosmos DB (hot data, < 3 months)
Azure Blob Storage (cold data, > 3 months)
Azure Data Factory or Azure Functions for data archival
Middleware function for unified reads

1. Data Archival Script (Durable Azure Function – Pseudocode)
This script runs daily/weekly and exports data older than 3 months from Cosmos DB to Blob Storage.

# Setup
cutoff_date = datetime.utcnow() - timedelta(days=90)
query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date.isoformat()}'"

# Cosmos DB Setup
cosmos_client = CosmosClient(endpoint, key)
container = cosmos_client.get_database_client("billing-db").get_container_client("records")

# Blob Storage Setup
blob_container = blob_service_client.get_container_client("billing-archive")

# Query with pagination
items = container.query_items(query, enable_cross_partition_query=True)
for page in items.by_page():
    records = list(page)
    blob_name = f"billing_{cutoff_date.strftime('%Y-%m-%d')}_{uuid4()}.json"
    blob_container.upload_blob(name=blob_name, data=json.dumps(records))

# (Optional) Delete records from Cosmos DB
for record in records:
    container.delete_item(record["id"], partition_key=record["partitionKey"])

 2. Automated Data Archival Process
Use Azure Data Factory (ADF) or Durable Azure Functions to automate data movement.

Steps:
Query Cosmos DB for records older than 3 months.
Export data to Blob Storage (JSON or Parquet).
Verify export succeeded.
Delete archived records from Cosmos DB.
Set a trigger to run daily or weekly.
Add a Delete Activity after copy to remove records from Cosmos DB if export succeeds.

 3. Unified Access Layer (Seamless Read API Support)
Introduce a middleware (e.g., Azure API Management policy, Azure Function, or custom service) to:
Intercept read requests.
Check if the requested data is within the last 3 months:
If yes → read from Cosmos DB.
If no → read from Blob Storage.
For write requests → continue writing to Cosmos DB.

4. Blob Storage Optimization
Use Cool Tier for infrequently accessed files.
Use Archive Tier if data is accessed rarely.
Apply lifecycle rules to move blobs between tiers automatically.

 5. Monitoring & Governance
Add Application Insights for observability.
Track archival status and alert on failures.
Use RBAC & managed identities for secure access between services.
