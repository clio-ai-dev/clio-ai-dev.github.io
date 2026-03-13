# Chapter 24: Agents and .NET Aspire

*.NET Aspire changes how you build cloud-native applications. It also changes how agents build them for you. This chapter covers both: using Aspire as a developer experience layer for agent-built services, and teaching agents to work within Aspire projects effectively.*

## What .NET Aspire Actually Is

.NET Aspire is an opinionated stack for building cloud-native, distributed applications in .NET. If that sounds like marketing, here's what it means in practice: Aspire gives you a single project (the AppHost) that wires together all your services, databases, caches, and message brokers. You run one project and everything starts. You get a dashboard that shows logs, traces, and metrics across all services. You get service discovery so services find each other by name instead of hardcoded URLs.

For solo developers and small teams, Aspire eliminates the "how do I run all this locally" problem. For agent-assisted development, it eliminates something even more important: the gap between "the agent built a service" and "I can actually see if it works."

### Why Aspire Matters for Agentic Development

When an agent creates a new service or modifies an existing one, you need to verify the work. Without Aspire, that means:

1. Figuring out which services to start
2. Making sure dependencies (databases, caches) are running
3. Checking logs across multiple terminal windows
4. Manually testing HTTP endpoints
5. Hoping the service discovery configuration is correct

With Aspire, you run `dotnet run --project src/AppHost` and everything comes up. The dashboard shows you every service, every log line, every HTTP trace. You can see immediately if the agent's code works, throws errors, or has performance issues.

This is the real value proposition: Aspire compresses the feedback loop between agent output and developer verification.

## The Aspire Project Structure

An Aspire solution has a predictable structure that agents need to understand:


```
src/
  AppHost/                    # The orchestrator (you run this)
    Program.cs                # Wires everything together
    appsettings.json
  ServiceDefaults/            # Shared configuration for all services
    Extensions.cs             # OpenTelemetry, health checks, resilience
  Api/                        # Your API service
    Program.cs
  Worker/                     # Background worker service
    Program.cs
  Web/                        # Blazor frontend
    Program.cs
```

The AppHost is the entry point. It doesn't serve traffic. It orchestrates: it starts your services, provisions containers for dependencies, and configures service discovery. The ServiceDefaults project provides shared setup that every service references (telemetry, health checks, resilience policies).

### The AppHost: Your Orchestration File

Here's what a typical AppHost Program.cs looks like:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var postgres = builder.AddPostgres("postgres")
    .WithPgAdmin();

var ordersDb = postgres.AddDatabase("ordersdb");

var redis = builder.AddRedis("cache")
    .WithRedisInsight();

var messaging = builder.AddRabbitMQ("messaging")
    .WithManagementPlugin();

var api = builder.AddProject<Projects.Api>("api")
    .WithReference(ordersDb)
    .WithReference(redis)
    .WithReference(messaging);

builder.AddProject<Projects.Worker>("worker")
    .WithReference(ordersDb)
    .WithReference(messaging);

builder.AddProject<Projects.Web>("web")
    .WithReference(api);

builder.Build().Run();
```

This is the file agents need to modify when adding new services or dependencies. It's also the file agents most commonly get wrong.

## The Aspire + Agent Workflow


Here's the workflow I recommend for building services with Aspire and coding agents:

### Step 1: Scaffold with Aspire CLI

Never let agents create Aspire projects from scratch. Use the CLI:

```bash
dotnet new aspire-starter -n MyApp
```

Or for a blank slate:

```bash
dotnet new aspire -n MyApp
```

This gives you the correct project structure with AppHost, ServiceDefaults, and proper project references. Agents can add to this, but they shouldn't create it.

### Step 2: Define the Service in AppHost First

Before asking an agent to build a service, define it in the AppHost. This is your spec:

```csharp
var catalogDb = postgres.AddDatabase("catalogdb");

var catalogApi = builder.AddProject<Projects.CatalogApi>("catalog-api")
    .WithReference(catalogDb)
    .WithReference(redis);
```

Now the agent knows: build a project called CatalogApi that uses a PostgreSQL database called catalogdb and a Redis cache.

### Step 3: Agent Builds the Service

Give the agent a prompt like:

> "Create the CatalogApi project. It's registered in the AppHost with a PostgreSQL database (catalogdb) and Redis cache. Build CRUD endpoints for a Product entity with fields: Name (string, required, max 200), Price (decimal), Category (string). Follow the conventions in AGENTS.md."

The agent creates the project, adds endpoints, sets up EF Core, and configures caching.

### Step 4: Verify with the Dashboard

Run the AppHost:


```bash
dotnet run --project src/AppHost
```

Open the Aspire dashboard (usually at https://localhost:17027). You'll see:

- All services and their status (running, stopped, error)
- Logs from every service in one place
- Distributed traces showing HTTP calls between services
- Metrics for request rates, error rates, response times
- Health check status

If the agent's code has issues, you'll see them immediately. Red status indicators, error logs, failed health checks. No hunting through terminal windows.

### Step 5: Iterate

If something's wrong, give the agent the error from the dashboard. Aspire's structured logging and distributed tracing give you precise error context that makes agent debugging dramatically faster.

## Service Discovery: What Agents Need to Know

Aspire uses named references for service discovery. When you write `.WithReference(api)` in the AppHost, the consuming service can access the API using the name "api" instead of a hardcoded URL.

In the consuming service:

```csharp
builder.Services.AddHttpClient<CatalogApiClient>(client =>
{
    client.BaseAddress = new Uri("https+http://catalog-api");
});
```

The `https+http://` scheme tells the service discovery system to resolve the address at runtime. Agents frequently get this wrong in two ways:

1. They hardcode `localhost:5001` instead of using the service name
2. They forget the `https+http://` scheme prefix

Your context file should call this out explicitly.

## Configuration and Connection Strings

Aspire manages connection strings through the AppHost. When you write `.WithReference(ordersDb)`, Aspire injects a connection string into the consuming service's configuration. The service accesses it by name:

```csharp
builder.AddNpgsqlDbContext<AppDbContext>("ordersdb");
```

Or for Redis:

```csharp
builder.AddRedisDistributedCache("cache");
```

The name in `AddNpgsqlDbContext("ordersdb")` must match the name in `postgres.AddDatabase("ordersdb")`. Agents sometimes invent their own names. Your context file should list all resource names and their expected consumers.

## Health Checks and Resilience

The ServiceDefaults project configures health checks and resilience policies for all services. Agents need to know this exists so they don't duplicate the configuration:

```csharp
// In ServiceDefaults/Extensions.cs (already configured)
public static IHostApplicationBuilder AddServiceDefaults(this IHostApplicationBuilder builder)
{
    builder.ConfigureOpenTelemetry();
    builder.AddDefaultHealthChecks();
    builder.Services.AddServiceDiscovery();
    builder.Services.ConfigureHttpClientDefaults(http =>
    {
        http.AddStandardResilienceHandler();
        http.AddServiceDiscovery();
    });
    return builder;
}
```

Every new service should call `builder.AddServiceDefaults()` at the top of its `Program.cs`. Agents need to know this is required, not optional.

## Context File Additions for Aspire Projects

Add these sections to your AGENTS.md for Aspire projects:

```markdown
## .NET Aspire

### Project Structure
- AppHost: src/AppHost/ (orchestrator, run this to start everything)
- ServiceDefaults: src/ServiceDefaults/ (shared config, DO NOT MODIFY without asking)
- Services: src/{ServiceName}/ (individual services)

### Creating New Services
1. Create the project: dotnet new webapi -n {ServiceName} -o src/{ServiceName}
2. Add reference to ServiceDefaults: dotnet add src/{ServiceName} reference src/ServiceDefaults
3. Register in AppHost Program.cs with appropriate resource references
4. Call builder.AddServiceDefaults() at the top of the service's Program.cs
5. launchSettings.json is required for every service project

### Resource Names (must match exactly)
- "ordersdb" - PostgreSQL database for orders
- "cache" - Redis cache
- "messaging" - RabbitMQ message broker

### Service Discovery
- Use named references, never hardcoded URLs
- HTTP clients: new Uri("https+http://{service-name}")
- Connection strings: resolved by resource name

### What NOT to Do
- Do NOT modify ServiceDefaults without asking
- Do NOT hardcode connection strings (Aspire manages them)
- Do NOT hardcode service URLs (use service discovery)
- Do NOT remove launchSettings.json from any project
- Do NOT create Aspire projects by hand (use dotnet new aspire or aspire new)
```

## Using the Dashboard for Agent Verification

The Aspire dashboard is your primary verification tool for agent-built services. Here's how to use it effectively.

### Structured Logs

Click on any service to see its logs. When an agent adds a new endpoint and you test it, the logs show you exactly what happened: request received, database query executed, response sent. If the agent forgot to add error handling, you'll see unhandled exceptions in red.

### Distributed Traces

When a request flows through multiple services (Web calls API, API queries database), the trace view shows the entire chain. This is invaluable for verifying that the agent wired up service communication correctly.

Click a trace to see each span: HTTP request, database query, cache lookup. You can see timing, status codes, and any errors. If the agent's code makes an N+1 query, you'll see it as dozens of database spans where there should be one.

### Metrics

The metrics tab shows request rates, error rates, and response time percentiles. After an agent builds a new endpoint, hit it with a few requests and check: Are response times reasonable? Any errors? Is the database connection pool behaving?

### Health Checks

The dashboard shows health check status for every service. Green means healthy, red means something's wrong. If the agent's code has a misconfigured database connection or a broken dependency, the health check catches it before you manually test.

## Real Example: Building a Notification Service with Aspire + Agents

Let's walk through a complete example. You have an existing Aspire solution with an Orders API. You need a Notification service that sends emails when orders are placed.

### Define in AppHost First

```csharp
var smtp = builder.AddMailDev("smtp");

var notifications = builder.AddProject<Projects.NotificationService>("notifications")
    .WithReference(messaging)
    .WithReference(smtp);
```

You've declared: the Notification service needs RabbitMQ (for receiving order events) and an SMTP server (for sending emails). MailDev gives you a local SMTP server with a web UI for testing.

### Prompt the Agent

> "Create the NotificationService project. It consumes OrderPlaced messages from RabbitMQ (via MassTransit) and sends email notifications via SMTP. Use the resource references already defined in AppHost: 'messaging' for RabbitMQ, 'smtp' for mail. Follow AGENTS.md conventions."

### What the Agent Builds

A well-configured agent produces:

```csharp
// src/NotificationService/Program.cs
var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();

builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<OrderPlacedConsumer>();
    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host(builder.Configuration.GetConnectionString("messaging"));
        cfg.ConfigureEndpoints(context);
    });
});

builder.Services.AddFluentEmail("noreply@myapp.com")
    .AddSmtpSender(builder.Configuration.GetConnectionString("smtp"));

var app = builder.Build();
app.MapDefaultEndpoints();
app.Run();
```

```csharp
// src/NotificationService/Consumers/OrderPlacedConsumer.cs
namespace NotificationService.Consumers;

public class OrderPlacedConsumer(IFluentEmail email, ILogger<OrderPlacedConsumer> logger)
    : IConsumer<OrderPlaced>
{
    public async Task Consume(ConsumeContext<OrderPlaced> context)
    {
        var order = context.Message;
        logger.LogInformation("Sending notification for order {OrderId}", order.Id);

        await email
            .To(order.CustomerEmail)
            .Subject($"Order {order.Id} Confirmed")
            .Body($"Your order for {order.ItemCount} items has been confirmed.")
            .SendAsync();
    }
}
```

### Verify in Dashboard

Run the AppHost. The dashboard shows five services now: API, Worker, Web, NotificationService, and MailDev. All green. Place an order through the API. The distributed trace shows:

1. POST /api/v1/orders hits the API
2. API publishes OrderPlaced to RabbitMQ
3. NotificationService consumes the message
4. SMTP call to MailDev

Open MailDev's web UI (linked from the dashboard) and confirm the email arrived. The entire verification took 30 seconds without writing a single test.

## Common Agent Mistakes with Aspire

After months of building Aspire projects with agents, these are the recurring issues:

**Missing ServiceDefaults reference.** The agent creates a new project but forgets to add the ServiceDefaults project reference. Result: no telemetry, no health checks, no service discovery. Your context file must state this is required.

**Hardcoded connection strings.** The agent puts `"Host=localhost;Port=5432;Database=mydb"` in appsettings.json instead of using the Aspire-injected connection string. Everything works when you run standalone, breaks when you run through AppHost.

**Missing launchSettings.json.** Aspire AppHost needs launchSettings.json in each service project to set environment variables. Agents sometimes delete or skip this file, causing dashboard environment variable crashes.

**Wrong Aspire NuGet packages.** Aspire has specific client packages (like `Aspire.Npgsql.EntityFrameworkCore` instead of plain `Npgsql.EntityFrameworkCore.PostgreSQL`). The Aspire packages integrate with the dashboard, provide health checks, and work with service discovery. Agents use the non-Aspire versions unless told otherwise.

**Not calling MapDefaultEndpoints().** The ServiceDefaults extension adds health check and alive endpoints. If the service doesn't call `app.MapDefaultEndpoints()`, the dashboard can't monitor its health.

Add all of these to your "What NOT to Do" section. Every one of them will save you debugging time.

## The Aspire Advantage

.NET Aspire isn't just a development convenience. It's an observability layer that makes agent-assisted development dramatically more productive. Without it, you're reviewing code in a vacuum, hoping the agent got things right. With it, you're verifying behavior in real time across your entire distributed system.

Every .NET developer using agents to build cloud-native applications should be using Aspire. It's not optional. It's the difference between trusting agent output and verifying it.
