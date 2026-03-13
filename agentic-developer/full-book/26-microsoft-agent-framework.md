# Chapter 26: Building Multi-Agent Apps with Microsoft Agent Framework

*There are two sides to agents and .NET. The first, covered in the rest of this book, is using agents to build .NET applications. The second is building agent-powered applications with .NET. This chapter covers the second: the Microsoft Agent Framework, the unified AI abstractions, and how to build multi-agent systems in C#.*

## The Microsoft Agent Framework

For over a year, the .NET ecosystem had a confusing split: Semantic Kernel for enterprise AI orchestration, AutoGen for multi-agent research. They had different APIs, different philosophies, and overlapping capabilities. Developers had to pick one and hope it was the right bet.

In late 2025, Microsoft unified them into the Microsoft Agent Framework. One set of APIs. One programming model. One NuGet metapackage. Semantic Kernel's production-grade kernel and plugin system, combined with AutoGen's multi-agent orchestration patterns. If you were using either one, you have a migration path. If you're starting fresh, you only need to learn one thing.

The core abstraction is the `Agent`. An agent has a name, instructions, tools it can call, and a model it uses for reasoning. You compose agents into workflows: sequential (one after another), concurrent (all at once), or orchestrated (a coordinator decides who runs when).

```csharp
var writer = new ChatCompletionAgent
{
    Name = "Writer",
    Instructions = "You write clear, concise technical documentation.",
    Kernel = kernel
};

var reviewer = new ChatCompletionAgent
{
    Name = "Reviewer",
    Instructions = "You review documentation for accuracy and clarity. Be critical.",
    Kernel = kernel
};
```

That's it. Two agents. Each with a role, instructions, and access to the same kernel (which provides the AI model and any tools). Now you can orchestrate them.

## Microsoft.Extensions.AI: The Foundation

Before diving into multi-agent patterns, you need to understand the abstraction layer underneath: `Microsoft.Extensions.AI`. This is the unified interface for AI services in .NET, following the same patterns as `Microsoft.Extensions.Http` and `Microsoft.Extensions.Caching`.


The key interfaces:

```csharp
// Chat completion (conversational AI)
IChatClient chatClient = new OpenAIChatClient("gpt-4o", apiKey);

// Embeddings (vector representations)
IEmbeddingGenerator<string, Embedding<float>> embeddings = ...;
```

`IChatClient` is the interface that every AI provider implements. OpenAI, Azure OpenAI, Anthropic, Ollama, local models. You program against the interface, swap providers via DI configuration. No code changes.

```csharp
// Registration in Program.cs
builder.Services.AddChatClient(new OpenAIChatClient("gpt-4o", apiKey));

// Or switch to Anthropic without changing any consuming code
builder.Services.AddChatClient(new AnthropicChatClient("claude-sonnet-4-20250514", apiKey));

// Or use a local model via Ollama
builder.Services.AddChatClient(new OllamaChatClient(new Uri("http://localhost:11434"), "llama3"));
```

The middleware pipeline pattern works here too. You can add logging, caching, rate limiting, and telemetry as delegating handlers:

```csharp
builder.Services.AddChatClient(pipeline => pipeline
    .UseOpenTelemetry()
    .UseDistributedCache()
    .UseRateLimiting()
    .Use(new OpenAIChatClient("gpt-4o", apiKey)));
```

This is the .NET way. If you've used `HttpClient` middleware, this feels identical. And it means your multi-agent apps get observability for free when running under Aspire.

## Agent Patterns


The Microsoft Agent Framework provides three core orchestration patterns. Each solves a different problem.

### Sequential Agents (AgentGroupChat with TerminationStrategy)

Agents take turns in a defined order. Agent A produces output, Agent B refines it, Agent C validates it.

```csharp
var chat = new AgentGroupChat(writer, reviewer)
{
    ExecutionSettings = new()
    {
        TerminationStrategy = new MaximumIterationTerminationStrategy(4)
        {
            Agents = [reviewer] // Reviewer decides when to stop
        }
    }
};

await foreach (var message in chat.InvokeAsync())
{
    Console.WriteLine($"{message.AuthorName}: {message.Content}");
}
```

Use sequential agents when the task has a natural pipeline: draft, review, revise. The writer drafts, the reviewer critiques, the writer revises based on feedback, and the loop continues until the reviewer is satisfied (or you hit the iteration limit).

### Concurrent Agents

Multiple agents work on the same input simultaneously. You collect all their outputs and merge the results.

```csharp
var agents = new[] { securityReviewer, performanceReviewer, accessibilityReviewer };

var tasks = agents.Select(agent => agent.InvokeAsync(
    new ChatHistory([new ChatMessageContent(AuthorRole.User, codeToReview)])
));

var results = await Task.WhenAll(tasks);

foreach (var result in results)
{
    Console.WriteLine($"{result.AuthorName}: {result.Content}");
}
```

Use concurrent agents when you need multiple perspectives on the same input and the agents don't depend on each other's output. Code review is the classic example: security, performance, and accessibility are independent concerns.

### Orchestrated Agents (Handoff Pattern)

A coordinator agent decides which specialist to invoke based on the current state of the conversation. This is the most flexible and most complex pattern.

```csharp
var triage = new ChatCompletionAgent
{
    Name = "Triage",
    Instructions = """
        You are a customer support triage agent. 
        Route to BillingAgent for payment issues.
        Route to TechAgent for technical problems.
        Route to GeneralAgent for everything else.
        """,
    Kernel = kernel
};

// Configure handoff behavior
var orchestrator = new HandoffOrchestrator([triage, billingAgent, techAgent, generalAgent]);
```

The orchestrator pattern works well for customer support, IT help desks, and any scenario where the right specialist depends on the user's request.

## MCP C# SDK: Connecting to External Tools

The Model Context Protocol (MCP) is Anthropic's open standard for connecting AI models to external tools and data sources. The MCP C# SDK lets you build MCP servers (expose your .NET APIs as tools) and MCP clients (consume external MCP servers) in C#.

### Building an MCP Server

An MCP server exposes tools that any MCP-compatible agent can call. Here's a server that provides access to your product catalog:

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddMcpServer()
    .WithTools<ProductTools>();

var app = builder.Build();
app.MapMcp();
app.Run();

public class ProductTools(AppDbContext db)
{
    [McpTool("search_products", "Search products by name or category")]
    public async Task<List<ProductDto>> SearchProducts(
        [Description("Search query")] string query,
        [Description("Maximum results")] int limit = 10)
    {
        return await db.Products
            .Where(p => p.Name.Contains(query) || p.Category.Contains(query))
            .Take(limit)
            .Select(p => new ProductDto(p.Id, p.Name, p.Price, p.Category))
            .ToListAsync();
    }

    [McpTool("get_product", "Get product details by ID")]
    public async Task<ProductDto?> GetProduct(
        [Description("Product ID")] int id)
    {
        var product = await db.Products.FindAsync(id);
        return product is null ? null : new ProductDto(product.Id, product.Name, product.Price, product.Category);
    }
}
```

The `[McpTool]` attribute exposes methods as tools. The `[Description]` attributes on parameters help the AI model understand what each parameter does. That's the entire server. Any MCP client (Claude Desktop, VS Code agents, other .NET apps) can connect and use these tools.

### Consuming an MCP Server

On the client side, you connect to an MCP server and make its tools available to your agents:

```csharp
var mcpClient = await McpClientFactory.CreateAsync(new()
{
    Id = "product-catalog",
    Name = "Product Catalog",
    TransportType = TransportType.Sse,
    Location = "http://localhost:5050/mcp"
});

// Add MCP tools to your kernel
var tools = await mcpClient.ListToolsAsync();
kernel.Plugins.AddFromMcpTools(tools);
```

Now your agents can search products, look up details, and interact with your catalog, all through the standardized MCP protocol.

## Real Example: Building a Support Agent System

Let's build something real: a customer support system with three agents (triage, billing, and technical), backed by your product catalog via MCP, and deployed with Aspire.

### Project Structure

```
src/
  AppHost/
  ServiceDefaults/
  SupportApi/              # HTTP API for chat interface
  AgentOrchestrator/       # The multi-agent system
  ProductCatalogMcp/       # MCP server for product data
```

### The Agent Orchestrator Service

```csharp
// src/AgentOrchestrator/Program.cs
var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();

// AI model via Microsoft.Extensions.AI
builder.Services.AddChatClient(new AzureOpenAIChatClient(
    new Uri(builder.Configuration["AzureOpenAI:Endpoint"]!),
    "gpt-4o",
    new DefaultAzureCredential()));

builder.Services.AddSingleton<SupportAgentService>();

var app = builder.Build();
app.MapDefaultEndpoints();

app.MapPost("/api/support/chat", async (
    ChatRequest request,
    SupportAgentService agents,
    CancellationToken ct) =>
{
    var response = await agents.HandleMessageAsync(request.Message, request.SessionId, ct);
    return TypedResults.Ok(new ChatResponse(response));
});

app.Run();
```

### The Agent Service

```csharp
public class SupportAgentService
{
    private readonly Kernel _kernel;
    private readonly ConcurrentDictionary<string, AgentGroupChat> _sessions = new();

    public SupportAgentService(IChatClient chatClient)
    {
        var kernelBuilder = Kernel.CreateBuilder();
        kernelBuilder.Services.AddSingleton(chatClient);
        _kernel = kernelBuilder.Build();
    }

    public async Task<string> HandleMessageAsync(string message, string sessionId, CancellationToken ct)
    {
        var chat = _sessions.GetOrAdd(sessionId, _ => CreateAgentChat());

        chat.AddChatMessage(new ChatMessageContent(AuthorRole.User, message));

        string lastResponse = "";
        await foreach (var response in chat.InvokeAsync(ct))
        {
            lastResponse = response.Content ?? "";
        }

        return lastResponse;
    }

    private AgentGroupChat CreateAgentChat()
    {
        var triage = new ChatCompletionAgent
        {
            Name = "Triage",
            Instructions = """
                You handle customer support requests.
                For billing questions (payments, refunds, invoices): hand off to BillingSpecialist.
                For technical issues (bugs, errors, setup): hand off to TechSpecialist.
                For general questions: answer directly using the product catalog tools.
                """,
            Kernel = _kernel
        };

        var billing = new ChatCompletionAgent
        {
            Name = "BillingSpecialist",
            Instructions = """
                You handle billing and payment questions.
                You can look up orders, process refunds, and explain invoices.
                Be empathetic but efficient.
                """,
            Kernel = _kernel
        };

        var tech = new ChatCompletionAgent
        {
            Name = "TechSpecialist",
            Instructions = """
                You handle technical support questions.
                You can look up product specifications and known issues.
                Provide step-by-step troubleshooting.
                """,
            Kernel = _kernel
        };

        return new AgentGroupChat(triage, billing, tech)
        {
            ExecutionSettings = new()
            {
                SelectionStrategy = new KernelFunctionSelectionStrategy(
                    KernelFunctionFactory.CreateFromPrompt("""
                        Determine which agent should respond next based on the conversation.
                        Agents: Triage, BillingSpecialist, TechSpecialist
                        Return only the agent name.
                        """),
                    _kernel),
                TerminationStrategy = new MaximumIterationTerminationStrategy(6)
            }
        };
    }
}
```

### The AppHost

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var postgres = builder.AddPostgres("postgres");
var catalogDb = postgres.AddDatabase("catalogdb");

var productMcp = builder.AddProject<Projects.ProductCatalogMcp>("product-mcp")
    .WithReference(catalogDb);

var orchestrator = builder.AddProject<Projects.AgentOrchestrator>("agent-orchestrator")
    .WithReference(productMcp);

var supportApi = builder.AddProject<Projects.SupportApi>("support-api")
    .WithReference(orchestrator);

builder.Build().Run();
```

### What the Aspire Dashboard Shows You

When you run this and send a support message, the dashboard reveals the entire flow:


1. HTTP POST to SupportApi
2. SupportApi calls AgentOrchestrator
3. Triage agent evaluates the message
4. If it's a billing question, the selection strategy routes to BillingSpecialist
5. BillingSpecialist calls the ProductCatalogMcp tools to look up order data
6. Response flows back through the chain

Every AI model call shows up as a span in the trace: the prompt, the response, token counts, latency. Every MCP tool call is visible. You can see exactly which agent handled the request and why.

This observability is why Aspire integration matters for multi-agent apps. Without it, debugging "why did the agent give a wrong answer" is guesswork. With it, you trace the exact decision chain.

## Agent Design Principles for .NET

After building several multi-agent systems, these principles consistently produce better results:

**Keep agents focused.** An agent that does one thing well is better than an agent that does five things poorly. The triage/specialist pattern works because each agent has a narrow scope.

**Use tools, not knowledge.** Don't put product details in the agent's instructions. Give the agent a tool to look up product details. Tools are always current. Instructions get stale.

**Set iteration limits.** Multi-agent conversations can loop forever if two agents keep handing work back and forth. Always set `MaximumIterationTerminationStrategy` with a reasonable cap.

**Log everything.** Use `Microsoft.Extensions.AI`'s telemetry middleware to capture every model call. When a multi-agent system behaves unexpectedly, the logs are the only way to understand why.

**Test agent behavior, not implementation.** Don't unit test that Agent A hands off to Agent B. Test that a billing question gets a billing answer. The routing is an implementation detail.

## Testing Multi-Agent Apps

Testing agent-powered applications requires a different approach than traditional unit tests. You're testing probabilistic behavior, not deterministic functions.

```csharp
public class SupportAgentTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    [Theory]
    [InlineData("I need a refund for order #123", "billing")]
    [InlineData("The app crashes when I click save", "technical")]
    [InlineData("What products do you have?", "catalog")]
    public async Task HandleMessage_RoutesToCorrectDomain(string message, string expectedDomain)
    {
        var client = factory.CreateClient();
        var response = await client.PostAsJsonAsync("/api/support/chat",
            new { Message = message, SessionId = Guid.NewGuid().ToString() });

        var result = await response.Content.ReadFromJsonAsync<ChatResponse>();

        // Assert the response contains domain-relevant content
        // Not exact string matching (LLM output varies), but domain verification
        result.Should().NotBeNull();
        result!.Response.Should().NotBeNullOrEmpty();
    }
}
```

For more rigorous testing, use `Microsoft.Extensions.AI.Evaluations` to score agent responses against expected criteria:

```csharp
var evaluator = new RelevanceEvaluator(chatClient);
var score = await evaluator.EvaluateAsync(
    question: "I need a refund",
    answer: agentResponse,
    context: "Customer support billing domain");

score.Score.Should().BeGreaterThan(0.7);
```

## Where This Is Going

The Microsoft Agent Framework is in its early days. The APIs will evolve. But the patterns are stable: focused agents, tool-based knowledge, orchestrated workflows, observable execution. These patterns work regardless of which framework version you're running.

The combination of Microsoft.Extensions.AI (unified model access), MCP (standardized tool integration), the Agent Framework (multi-agent orchestration), and Aspire (deployment and observability) gives .NET developers a complete stack for building production agent systems. No other ecosystem has this level of integration between the AI layer and the application platform.

Whether you're building a customer support bot, an internal knowledge assistant, or an automated code review pipeline, the building blocks are the same. Define your agents. Give them tools. Orchestrate their interactions. Observe the results. Iterate.

That's multi-agent development in .NET. Not hype. Just engineering.
