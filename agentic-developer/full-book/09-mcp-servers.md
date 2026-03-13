# Chapter 9: MCP Servers and External Tool Integration

Context files are static. They tell the agent what you know at the time you write them. But agents also need access to things that change: your database schema, your API documentation, your deployment status, your issue tracker. This is where MCP comes in.

The Model Context Protocol (MCP) is a standardized way for AI agents to access external tools and data sources. If AGENTS.md is the employee handbook and skills are the training courses, MCP servers are the access badges, giving the agent permission and ability to interact with systems outside the codebase.

## What MCP Is

MCP is an open protocol created by Anthropic that standardizes how AI models connect to external data sources and tools. The analogy that stuck (for good reason) is "USB for AI agents." Before USB, every peripheral needed its own proprietary connector. Before MCP, every AI tool needed custom integration code for every external system.


MCP provides a common interface. A database MCP server exposes your schema and query capabilities through the same protocol as a GitHub MCP server that exposes issues and PRs. The agent doesn't need to know the implementation details. It speaks MCP, and the server translates.

The protocol has three core concepts:

**Tools:** Functions the agent can call. A database MCP server might expose `query`, `list_tables`, and `describe_table` tools. A GitHub server might expose `list_issues`, `create_pr`, and `get_file`.

**Resources:** Data the agent can read. Database schemas, configuration files, API documentation. Resources are read-only context that helps the agent make better decisions.

**Prompts:** Predefined interaction patterns. A "review this PR" prompt that combines the right resources and tools for a code review workflow.

## Why MCP Matters

Without MCP, connecting an agent to your database requires custom code: a script that queries the schema, formats it as context, and injects it into the agent's prompt. Do the same for your API docs, your CI system, your monitoring dashboard, and you've built a bespoke integration layer that's fragile and tool-specific.

With MCP, you configure a server once and every MCP-compatible agent can use it. Claude Code, Cursor, Windsurf, and other tools all support MCP. Write the integration once, use it everywhere.

For .NET developers specifically, MCP is significant because:

1. **Your database schema is living context.** Agents writing EF Core migrations need to know the current schema. An MCP server that exposes your database schema means the agent always sees the current state, not a stale document.

2. **Your APIs are discoverable.** An MCP server wrapping your Swagger/OpenAPI spec lets agents understand your API surface without you copying documentation into context files.

3. **Your infrastructure is queryable.** Agents can check deployment status, read logs, query monitoring systems, all through standardized tool calls.

## Available MCP Servers


The MCP ecosystem has grown rapidly. Here are the categories most relevant to .NET development.

### Database Servers

The most immediately useful MCP servers for application developers. They expose:
- Table and column listings
- Schema details (types, constraints, relationships)
- Read-only query execution
- Index and performance information

PostgreSQL, SQL Server, MySQL, and SQLite all have MCP servers available. For .NET projects using EF Core, a database MCP server means the agent can inspect the actual database before generating migrations, not just guess from entity classes.

### Source Control Servers

GitHub and GitLab MCP servers expose:
- Repository structure and file contents
- Issues and pull requests
- CI/CD pipeline status
- Branch and tag information

This lets agents check whether CI passed before deploying, read linked issues when reviewing PRs, and understand the full context of a change.

### API and Documentation Servers

Servers that expose your API documentation (OpenAPI/Swagger specs) or internal documentation (Confluence, Notion, or plain markdown). This gives agents access to your API contracts, architecture decisions, and team knowledge without embedding everything in context files.

### Custom Servers

This is where it gets interesting. You can build MCP servers that expose anything: your internal tooling, your deployment pipeline, your feature flag system, your monitoring dashboards. If it has an API, you can wrap it in MCP.

## Building an MCP Server in C#

The MCP C# SDK (in preview since late 2025) makes it straightforward to build custom MCP servers. Let's build one that exposes a database schema, the most common use case for .NET developers.

### Setup

```bash
dotnet new console -n DatabaseMcpServer
cd DatabaseMcpServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Npgsql
```

### A Simple Schema Explorer

```csharp
using ModelContextProtocol;
using ModelContextProtocol.Server;
using Npgsql;

var builder = McpServerBuilder.CreateStdio(args);

builder.AddTool("list_tables", "List all tables in the database",
    async (McpToolContext context) =>
    {
        await using var conn = new NpgsqlConnection(
            Environment.GetEnvironmentVariable("DATABASE_URL"));
        await conn.OpenAsync();

        await using var cmd = new NpgsqlCommand("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """, conn);

        var tables = new List<string>();
        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            tables.Add(reader.GetString(0));
        }

        return McpToolResult.Text(string.Join("\n", tables));
    });

builder.AddTool("describe_table",
    "Describe a table's columns, types, and constraints",
    async (McpToolContext context) =>
    {
        var tableName = context.GetRequiredArgument<string>("table_name");

        await using var conn = new NpgsqlConnection(
            Environment.GetEnvironmentVariable("DATABASE_URL"));
        await conn.OpenAsync();

        await using var cmd = new NpgsqlCommand("""
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                tc.constraint_type
            FROM information_schema.columns c
            LEFT JOIN information_schema.key_column_usage kcu
                ON c.column_name = kcu.column_name
                AND c.table_name = kcu.table_name
            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
            WHERE c.table_name = @tableName
            AND c.table_schema = 'public'
            ORDER BY c.ordinal_position
            """, conn);

        cmd.Parameters.AddWithValue("tableName", tableName);

        var columns = new List<string>();
        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            var name = reader.GetString(0);
            var type = reader.GetString(1);
            var nullable = reader.GetString(2) == "YES" ? "NULL" : "NOT NULL";
            var defaultVal = reader.IsDBNull(3) ? "" : $" DEFAULT {reader.GetString(3)}";
            var constraint = reader.IsDBNull(4) ? "" : $" [{reader.GetString(4)}]";

            columns.Add($"  {name} {type} {nullable}{defaultVal}{constraint}");
        }

        return McpToolResult.Text(
            $"Table: {tableName}\n{string.Join("\n", columns)}");
    });

builder.AddTool("query",
    "Execute a read-only SQL query against the database",
    async (McpToolContext context) =>
    {
        var sql = context.GetRequiredArgument<string>("sql");

        // Safety: only allow SELECT statements
        if (!sql.TrimStart().StartsWith("SELECT", StringComparison.OrdinalIgnoreCase))
        {
            return McpToolResult.Error(
                "Only SELECT queries are allowed for safety.");
        }

        await using var conn = new NpgsqlConnection(
            Environment.GetEnvironmentVariable("DATABASE_URL"));
        await conn.OpenAsync();

        // Wrap in a read-only transaction for additional safety
        await using var tx = await conn.BeginTransactionAsync(
            System.Data.IsolationLevel.ReadCommitted);

        await using var cmd = new NpgsqlCommand(sql, conn, tx);
        await using var reader = await cmd.ExecuteReaderAsync();

        var results = new List<string>();
        var columnNames = Enumerable.Range(0, reader.FieldCount)
            .Select(i => reader.GetName(i))
            .ToList();

        results.Add(string.Join(" | ", columnNames));
        results.Add(new string('-', results[0].Length));

        while (await reader.ReadAsync())
        {
            var values = Enumerable.Range(0, reader.FieldCount)
                .Select(i => reader.IsDBNull(i) ? "NULL" : reader.GetValue(i).ToString()!)
                .ToList();
            results.Add(string.Join(" | ", values));
        }

        return McpToolResult.Text(string.Join("\n", results));
    });

var server = builder.Build();
await server.RunAsync();
```

This is a real, working MCP server. It's about 100 lines of C# and gives any MCP-compatible agent the ability to explore and query your database. The patterns are universal: the same approach works for SQL Server, MySQL, or any data source.

### Configuring the Agent to Use It

In Claude Code, MCP servers are configured in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "database": {
      "command": "dotnet",
      "args": ["run", "--project", "tools/DatabaseMcpServer"],
      "env": {
        "DATABASE_URL": "Host=localhost;Database=myapp;Username=dev;Password=dev"
      }
    }
  }
}
```

In Cursor, the configuration goes in `.cursor/mcp.json` with a similar structure. The agent now has database access. When you say "look at the orders table schema before writing this migration," the agent can actually do it.

## Security Considerations


MCP servers are powerful. They give agents direct access to your systems. This demands careful thought about security.

### The Principle of Least Privilege

Expose the minimum functionality the agent needs. For a database MCP server:

**Do expose:**
- Schema inspection (tables, columns, types, relationships)
- Read-only queries against development databases
- Index and constraint information

**Don't expose:**
- Write operations (INSERT, UPDATE, DELETE)
- DDL operations (CREATE TABLE, DROP TABLE)
- Production database connections
- Administrative functions (user management, permissions)

The example above enforces read-only access by rejecting non-SELECT queries and wrapping everything in a read-only transaction. This is the right default.

### Environment Separation

Never point an MCP server at a production database during development. Use a development or staging copy. If you need production data for debugging, create a read-only replica connection.

```json
{
  "mcpServers": {
    "database-dev": {
      "command": "dotnet",
      "args": ["run", "--project", "tools/DatabaseMcpServer"],
      "env": {
        "DATABASE_URL": "Host=localhost;Database=myapp_dev;Username=dev;Password=dev"
      }
    }
  }
}
```

The connection string makes the boundary explicit. The agent physically cannot access production because the MCP server isn't configured with production credentials.

### Credential Management

Don't hardcode credentials in MCP configuration files that get committed to source control. Use environment variables, secret managers, or local configuration files that are gitignored.

```json
{
  "mcpServers": {
    "database": {
      "command": "dotnet",
      "args": ["run", "--project", "tools/DatabaseMcpServer"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### Audit Logging

For MCP servers that access sensitive systems, log every tool invocation. This gives you visibility into what the agent is doing and helps you catch unexpected behavior.

```csharp
builder.AddTool("query", "Execute a read-only SQL query",
    async (McpToolContext context) =>
    {
        var sql = context.GetRequiredArgument<string>("sql");

        // Log every query
        Console.Error.WriteLine(
            $"[MCP] Query executed at {DateTime.UtcNow}: {sql}");

        // ... execute query
    });
```

Log to stderr (which goes to the agent's log, not the agent's response) so you have a record without polluting the agent's context.

## Real Workflow: Schema-Aware Migration Generation


Here's where MCP transforms a common workflow. Without MCP, generating a database migration looks like this:

1. Developer asks agent to add a new feature requiring schema changes
2. Agent guesses at the current schema based on entity classes
3. Agent generates a migration that might conflict with existing columns, miss indexes, or duplicate constraints
4. Developer reviews, fixes, and iterates

With a database MCP server, the workflow becomes:

1. Developer asks agent to add a new feature requiring schema changes
2. Agent calls `list_tables` to see the current schema
3. Agent calls `describe_table` for relevant tables to understand existing columns and constraints
4. Agent calls `query` to check for existing indexes and relationships
5. Agent generates a migration that accounts for the actual current state
6. Developer reviews and (usually) approves on the first pass

The difference in quality is significant. The agent isn't guessing. It's working from the same source of truth you'd use: the actual database.

Here's what the agent's internal process looks like:

```
User: "Add a priority field to the Orders table. High, Medium, Low. Default to Medium."

Agent thinks: I should check the current Orders table schema first.

Agent calls: describe_table(table_name: "orders")
Result:
  Table: orders
    id uuid NOT NULL [PRIMARY KEY]
    customer_id uuid NOT NULL [FOREIGN KEY]
    status integer NOT NULL DEFAULT 0
    total_amount numeric(18,2) NOT NULL
    created_at timestamp NOT NULL DEFAULT now()
    updated_at timestamp NULL

Agent thinks: Good, no existing priority column. Status uses integer (enum mapping).
I should use the same pattern for priority. Let me check if there are any
indexes I should be aware of.

Agent calls: query(sql: "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'orders'")
Result:
  orders_pkey | CREATE UNIQUE INDEX orders_pkey ON public.orders USING btree (id)
  ix_orders_customer_id | CREATE INDEX ix_orders_customer_id ON public.orders USING btree (customer_id)

Agent: Now I can generate an accurate migration.
```

The resulting migration is precise because it's based on facts, not assumptions.

## Building Beyond Databases

The database example is the most common, but MCP servers can wrap anything.

### API Documentation Server

Expose your OpenAPI/Swagger spec so agents can understand your API surface:

```csharp
builder.AddTool("list_endpoints", "List all API endpoints",
    async (McpToolContext context) =>
    {
        var spec = await File.ReadAllTextAsync("openapi.json");
        var doc = JsonDocument.Parse(spec);

        var endpoints = new List<string>();
        foreach (var path in doc.RootElement.GetProperty("paths").EnumerateObject())
        {
            foreach (var method in path.Value.EnumerateObject())
            {
                var summary = method.Value.TryGetProperty("summary", out var s)
                    ? s.GetString() : "No description";
                endpoints.Add($"{method.Name.ToUpper()} {path.Name} - {summary}");
            }
        }

        return McpToolResult.Text(string.Join("\n", endpoints));
    });
```

### Feature Flag Server

Let agents check which features are enabled:

```csharp
builder.AddTool("check_feature_flag",
    "Check if a feature flag is enabled in the target environment",
    async (McpToolContext context) =>
    {
        var flag = context.GetRequiredArgument<string>("flag_name");
        var env = context.GetRequiredArgument<string>("environment");

        // Query your feature flag service
        var client = new HttpClient();
        var response = await client.GetAsync(
            $"https://flags.internal/api/flags/{flag}?env={env}");

        var result = await response.Content.ReadAsStringAsync();
        return McpToolResult.Text(result);
    });
```

### CI/CD Status Server

Let agents check build status before deploying:

```csharp
builder.AddTool("check_ci_status",
    "Check the CI/CD pipeline status for a branch",
    async (McpToolContext context) =>
    {
        var branch = context.GetRequiredArgument<string>("branch");

        var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization",
            $"Bearer {Environment.GetEnvironmentVariable("GITHUB_TOKEN")}");

        var response = await client.GetAsync(
            $"https://api.github.com/repos/myorg/myrepo/actions/runs?branch={branch}&per_page=1");

        var json = await response.Content.ReadAsStringAsync();
        return McpToolResult.Text(json);
    });
```

The pattern is always the same: wrap an existing system's API in MCP tools with clear names and descriptions. The agent handles the orchestration.

## Connecting Multiple MCP Servers

Real projects often need multiple MCP servers working together. A typical .NET development setup might include:

```json
{
  "mcpServers": {
    "database": {
      "command": "dotnet",
      "args": ["run", "--project", "tools/DatabaseMcpServer"],
      "env": { "DATABASE_URL": "${DATABASE_URL}" }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./docs"]
    }
  }
}
```

The agent can now:
1. Read the database schema to understand current state
2. Check GitHub issues for requirements
3. Read architecture documentation from the docs folder
4. Generate code that accounts for all of this context

This is context engineering at its most powerful: the agent has access to the same information sources you do.

## When NOT to Use MCP

MCP isn't always the answer. Some situations are better served by simpler approaches.

**Static information:** If your database schema changes rarely and you already document it in your AGENTS.md, an MCP server adds complexity without proportional benefit. Use MCP when the data changes frequently enough that static documentation goes stale.

**Sensitive production systems:** MCP makes it easy for agents to query systems. Maybe too easy. If the risk of an agent accidentally querying your production payment database outweighs the benefit, stick to documentation.

**Simple projects:** A solo developer working on a small API doesn't need an MCP server for their local SQLite database. The overhead of building and maintaining the server exceeds the benefit. MCP shines in larger projects with complex infrastructure.

**When security review hasn't happened:** Don't deploy MCP servers that access sensitive systems without your team reviewing the security implications. The convenience isn't worth the risk if the server has vulnerabilities.

## Key Takeaways

1. **MCP standardizes tool access for agents.** Build an integration once, use it with any MCP-compatible agent. No more custom glue code per tool.

2. **Database MCP servers are the highest-leverage starting point.** Agents that can inspect the actual schema produce dramatically better migrations, queries, and data access code.

3. **Security is non-negotiable.** Read-only access, development databases only, no hardcoded credentials, audit logging. These aren't suggestions.

4. **Building MCP servers in C# is straightforward.** The MCP C# SDK handles the protocol. You just implement the tools.

5. **Start simple.** One MCP server for your database. Add more as you identify real needs. Don't build an MCP server for every system on day one.

6. **MCP completes the active context layer.** Static context (AGENTS.md, rules, skills) plus dynamic context (MCP servers) gives agents a comprehensive understanding of your project and its environment.

With context files, path-scoped rules, skills, and MCP servers, you have the full context engineering toolkit. But there's one more piece that affects everything: the codebase itself. How you structure your code, name your types, organize your files, all of that is context too. The next chapter covers how to design a codebase that makes agents dramatically more effective.
