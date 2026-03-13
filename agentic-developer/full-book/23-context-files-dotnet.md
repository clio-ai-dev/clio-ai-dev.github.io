# Chapter 23: Context Files for .NET Projects

*This is where context engineering gets specific. General AGENTS.md advice is fine, but .NET has its own conventions, its own patterns, and its own ways to confuse an agent. This chapter gives you copy-paste-ready templates for every major .NET project type.*

## Why .NET Needs Specific Context

C# is a language that evolves fast. Between nullable reference types, file-scoped namespaces, primary constructors, global usings, and collection expressions, a codebase written in 2024 looks dramatically different from one written in 2021. Agents trained on years of Stack Overflow and GitHub data will happily generate code in any of these styles, often mixing them within the same file.


That's the problem. Without explicit guidance, your agent will:

- Use block-scoped namespaces in a project that uses file-scoped
- Ignore nullable reference types and litter your code with `null!` suppressions
- Use traditional constructors when you've adopted primary constructors
- Add `using` statements that your global usings already cover
- Generate `var` everywhere or nowhere, depending on which training data dominates

A good .NET context file eliminates all of this. One file, loaded automatically, and every agent interaction produces code that matches your project.

## The .NET Conventions Section

Every .NET context file needs a section that locks down the language-level decisions. Here's the baseline:

```markdown
## C# Conventions
- Target: .NET 9 / C# 13
- Use file-scoped namespaces (one namespace per file, no braces)
- Use primary constructors for dependency injection
- Enable nullable reference types (already in .csproj). Never use null! suppression.
- Use global usings (see GlobalUsings.cs). Don't add usings that are already global.
- Use collection expressions: [] not new List<T>(), [..existing] for spread
- Use raw string literals for multi-line strings (three quotes)
- Use pattern matching over type checks and casts
- Prefer records for immutable data types and DTOs
- Use required keyword for properties that must be set at construction
- Use init-only setters for immutable properties on classes
```

This section alone prevents 80% of the style inconsistencies agents introduce. Let's look at what each of these buys you.

### Nullable Reference Types

This is the single most common source of agent-generated warnings. Agents will write code like:

```csharp
public class OrderService
{
    private readonly IOrderRepository _repository; // CS8618 warning

    public OrderService(IOrderRepository repository)
    {
        _repository = repository;
    }
}
```

When your project uses primary constructors, the agent should write:

```csharp
public class OrderService(IOrderRepository repository)
{
    public async Task<Order?> GetOrderAsync(int id) =>
        await repository.GetByIdAsync(id);
}
```

No field declarations. No null warnings. Cleaner code. But the agent won't do this unless you tell it to.

### Global Usings

Every .NET project accumulates a set of namespaces used in nearly every file. If your `GlobalUsings.cs` already includes `System.Text.Json` and `Microsoft.EntityFrameworkCore`, an agent adding those usings to individual files creates noise. Call out your global usings explicitly:

```markdown
## Global Usings (already configured, don't re-add)
- System.Text.Json
- Microsoft.EntityFrameworkCore
- Microsoft.AspNetCore.Mvc
- FluentValidation
- MediatR
```

### Primary Constructors

Primary constructors are the clearest example of a feature where agents need explicit direction. The syntax is still new enough that many training examples use the old pattern. Be specific:

```markdown
## Dependency Injection
Use primary constructors for all DI. Do NOT create private readonly fields manually.

Yes:
```csharp
public class OrderHandler(IOrderRepository repository, ILogger<OrderHandler> logger)
```

No:
```csharp
public class OrderHandler
{
    private readonly IOrderRepository _repository;
    private readonly ILogger<OrderHandler> _logger;
    
    public OrderHandler(IOrderRepository repository, ILogger<OrderHandler> logger)
    {
        _repository = repository;
        _logger = logger;
    }
}
```
```

## ASP.NET Core Minimal API Template

Minimal APIs are the default for new ASP.NET Core projects. Here's a complete AGENTS.md template:

```markdown
# AGENTS.md

## Project Overview
REST API for [describe your domain]. Built with ASP.NET Core Minimal APIs.

## Tech Stack
- .NET 9 / ASP.NET Core
- EF Core 9 with PostgreSQL (Npgsql)
- FluentValidation for request validation
- Scalar for API documentation (not Swagger/Swashbuckle)
- xUnit + FluentAssertions + NSubstitute for testing
- Docker Compose for local dependencies

## Build & Run
```bash
dotnet build
dotnet test
dotnet run --project src/Api
```

## Project Structure
```
src/Api/
  Features/
    Orders/
      CreateOrder.cs        # Endpoint + handler + request/response
      GetOrder.cs
      ListOrders.cs
    Products/
      ...
  Data/
    AppDbContext.cs
    Migrations/
  Common/
    Extensions/
    Middleware/
```

## C# Conventions
- File-scoped namespaces
- Primary constructors for DI
- Nullable reference types enabled, no null! suppression
- Records for request/response DTOs
- Collection expressions where applicable

## API Patterns
- One file per endpoint: request record, handler, endpoint mapping
- Group endpoints with MapGroup() and extension methods
- Return TypedResults (Results.Ok(), Results.NotFound(), etc.)
- Use .WithName(), .WithTags(), .Produces<T>() for OpenAPI metadata
- Validate requests with FluentValidation endpoint filters
- All routes: /api/v1/{resource}

## Endpoint Structure
Each endpoint file follows this pattern:
```csharp
public static class CreateOrder
{
    public record Request(string CustomerName, List<OrderItem> Items);
    public record Response(int Id, string Status);

    public static void Map(RouteGroupBuilder group) =>
        group.MapPost("/", HandleAsync)
            .WithName(nameof(CreateOrder))
            .Produces<Response>(StatusCodes.Status201Created);

    private static async Task<IResult> HandleAsync(
        Request request,
        AppDbContext db,
        CancellationToken ct)
    {
        // implementation
        return TypedResults.Created($"/api/v1/orders/{order.Id}", new Response(order.Id, order.Status));
    }
}
```

## EF Core
- DbContext: AppDbContext in Data/ folder
- Entity configuration: IEntityTypeConfiguration<T> in separate files
- Migrations via CLI: dotnet ef migrations add <Name> --project src/Api
- No lazy loading. Use explicit .Include() for related data.
- Use DateTimeOffset, not DateTime, for all timestamps

## Testing
- Integration tests with WebApplicationFactory
- Use Testcontainers for PostgreSQL in tests
- Name: MethodName_Scenario_ExpectedResult
- Builder pattern for test data (see tests/Builders/)

## What NOT to Do
- Do NOT use controllers (this is a Minimal API project)
- Do NOT use MediatR (endpoints ARE the handlers)
- Do NOT add Swashbuckle (we use Scalar)
- Do NOT use AutoMapper
- Do NOT modify Program.cs service registration without asking
```

## ASP.NET Core MVC Template

For projects that use controllers (plenty of them still exist, and for good reason):

```markdown
# AGENTS.md

## Project Overview
Web application with API and MVC views for [describe domain].

## Tech Stack
- .NET 9 / ASP.NET Core MVC
- EF Core 9 with SQL Server
- ASP.NET Identity for authentication
- xUnit + WebApplicationFactory for testing

## C# Conventions
- File-scoped namespaces, primary constructors
- Nullable reference types enabled

## Controller Patterns
- One controller per resource/feature area
- Inherit from ControllerBase for APIs, Controller for MVC
- Use [ApiController] attribute on API controllers
- Use [FromRoute], [FromQuery], [FromBody] explicitly
- Return ActionResult<T> from API endpoints
- Keep controllers thin: delegate to services

## Service Layer
- One interface + implementation per feature area
- Register as scoped in DI
- Services handle business logic, controllers handle HTTP concerns
- Return Result<T> from services, not exceptions

## Views (MVC)
- Use Tag Helpers, not HTML helpers
- Partial views in Shared/ for reusable components
- ViewModels for every view (no passing entities to views)
- Client-side validation with jQuery Validation (already configured)
```

## Blazor Template

Blazor projects need special attention because agents frequently confuse Blazor Server, Blazor WebAssembly, and the newer Blazor Web App model:

```markdown
# AGENTS.md

## Project Overview
Blazor Web App with interactive server rendering for [describe domain].

## Tech Stack
- .NET 9 / Blazor Web App (Interactive Server)
- EF Core 9 with SQLite (development), PostgreSQL (production)
- MudBlazor component library
- bUnit for component testing

## Rendering Model
This is a Blazor Web App using Interactive Server rendering.
- Default render mode: InteractiveServer (set in App.razor)
- Static SSR for pages that don't need interactivity
- Do NOT use InteractiveWebAssembly or InteractiveAuto (we don't have a Client project)

## Component Patterns
- One component per file, file-scoped namespace
- Use @inject for DI, not [Inject] attribute
- Use CascadingParameter for shared state (auth, theme)
- Handle async loading with a loading state pattern:
```razor
@if (_items is null)
{
    <MudProgressCircular />
}
else
{
    @foreach (var item in _items) { ... }
}
```
- Dispose services properly: implement IAsyncDisposable when using timers or event subscriptions
- Use EventCallback<T> for child-to-parent communication

## State Management
- Scoped services for per-circuit state
- No Fluxor or other state management libraries
- Use cascading values for cross-component state

## What NOT to Do
- Do NOT use JSInterop unless absolutely necessary
- Do NOT create WASM components (this is server-only)
- Do NOT use NavigationManager.NavigateTo() for same-page updates
- Do NOT put business logic in components (use services)
```

## Class Library Template

For shared libraries and NuGet packages:

```markdown
# AGENTS.md

## Project Overview
Shared library providing [describe functionality]. Published as NuGet package.

## Tech Stack
- .NET 9 class library (targets net9.0)
- No framework dependencies (this is a pure library)

## Conventions
- File-scoped namespaces
- Primary constructors where appropriate
- XML documentation comments on all public members
- Internal by default. Only make types public if they're part of the API surface.
- Seal classes that aren't designed for inheritance

## Public API Design
- Use interfaces for extensibility points
- Use abstract base classes only when shared implementation is needed
- Provide extension methods for DI registration: services.Add{LibraryName}()
- Follow Microsoft's API design guidelines
- Include [Obsolete] attributes before removing public members

## Testing
- xUnit + FluentAssertions
- Test public API surface only
- 90%+ coverage on core logic

## What NOT to Do
- Do NOT add ASP.NET Core dependencies
- Do NOT add EF Core dependencies (this is a pure library)
- Do NOT use static state
- Do NOT throw exceptions for expected conditions (use Result<T>)
```

## MAUI Template

.NET MAUI projects have a unique structure and agents need to understand the cross-platform constraints:

```markdown
# AGENTS.md

## Project Overview
Cross-platform mobile/desktop app for [describe domain]. Targets Android and iOS.

## Tech Stack
- .NET 9 / .NET MAUI
- CommunityToolkit.Mvvm for MVVM pattern
- CommunityToolkit.Maui for UI helpers
- SQLite-net for local storage
- xUnit + device runners for testing

## Architecture
- MVVM pattern with CommunityToolkit.Mvvm source generators
- ViewModels use [ObservableProperty] and [RelayCommand] attributes
- Services registered in MauiProgram.cs
- Shell-based navigation

## Conventions
- One ViewModel per page
- Use [ObservableProperty] instead of manual INotifyPropertyChanged
- Use [RelayCommand] instead of manual ICommand implementations
- Async commands for all I/O operations
- Platform-specific code in Platforms/ folders only

## Navigation
- Use Shell routing: Shell.Current.GoToAsync()
- Register routes in AppShell.xaml.cs
- Pass parameters with query properties: [QueryProperty]

## What NOT to Do
- Do NOT use code-behind for business logic (keep XAML code-behind minimal)
- Do NOT use Device.BeginInvokeOnMainThread (use MainThread.InvokeOnMainThreadAsync)
- Do NOT add platform-specific code outside Platforms/ folders
- Do NOT use absolute layouts (use Grid or FlexLayout for responsive design)
```

## Architecture-Specific Templates


Beyond project type, your architecture choice dramatically affects what agents need to know. Here are the additions for common .NET architectures.

### Clean Architecture Addition

```markdown
## Architecture: Clean Architecture
```
src/
  Domain/           # Entities, value objects, domain events, interfaces
  Application/      # Use cases, DTOs, validators, interfaces for infra
  Infrastructure/   # EF Core, external APIs, file system, email
  Api/              # Controllers/endpoints, middleware, DI composition
```

### Dependency Rules (NEVER VIOLATE)
- Domain depends on nothing
- Application depends only on Domain
- Infrastructure depends on Application and Domain
- Api depends on all layers but only for DI composition
- NEVER reference Infrastructure from Application

### Where Things Go
- Business rules: Domain entities and domain services
- Use cases/orchestration: Application handlers
- Data access: Infrastructure repositories
- HTTP concerns: Api layer only
```

### Vertical Slice Architecture Addition

```markdown
## Architecture: Vertical Slice
Each feature is a self-contained folder with everything it needs.

```
src/Api/Features/
  Orders/
    CreateOrder.cs      # Command + Handler + Validator + Endpoint
    GetOrder.cs         # Query + Handler + Endpoint
    OrderEntity.cs      # Entity (if feature-specific)
    OrderMappings.cs    # EF Core entity configuration
```

### Rules
- Features don't reference other features directly
- Shared code goes in Common/ only if used by 3+ features
- Each file can contain the request, handler, and endpoint together
- Don't over-abstract: a little duplication between features is OK
```

## EF Core Conventions

EF Core deserves its own section in every .NET context file. Agents make consistent mistakes with EF Core if you don't specify your patterns:

```markdown
## EF Core Conventions

### DbContext
- One DbContext for the application: AppDbContext
- Entity configurations in separate files: Data/Configurations/{Entity}Configuration.cs
- Use IEntityTypeConfiguration<T>, not Fluent API in OnModelCreating

### Entity Patterns
- Id property is always int (auto-increment) unless domain requires otherwise
- Use DateTimeOffset for all timestamps (CreatedAt, UpdatedAt)
- Soft delete: IsDeleted boolean + global query filter
- Owned types for value objects (Address, Money, etc.)

### Configuration Pattern
```csharp
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);
        builder.Property(o => o.CustomerName).HasMaxLength(200).IsRequired();
        builder.HasMany(o => o.Items).WithOne().HasForeignKey(i => i.OrderId);
        builder.HasIndex(o => o.CreatedAt);
    }
}
```

### Migrations
- Name migrations descriptively: Add_Order_CustomerName_Index
- Never edit existing migrations (create new ones)
- Run migrations: dotnet ef migrations add <Name> --project src/Api
- Test migrations against a real database before merging

### What NOT to Do with EF Core
- Do NOT use lazy loading
- Do NOT call SaveChanges() in repository methods (call it in the handler/service)
- Do NOT use .Find() when you need to include related data (use .Include().FirstOrDefaultAsync())
- Do NOT use string-based Include() overloads
- Do NOT create circular navigation properties
```

## Testing Conventions

Testing is where agents can save you enormous time, or create a mess. Be specific:

```markdown
## Testing

### Frameworks
- xUnit for test runner
- FluentAssertions for assertions
- NSubstitute for mocking
- WebApplicationFactory for integration tests
- Testcontainers for database tests
- Bogus for test data generation

### Unit Test Pattern
```csharp
public class CreateOrderHandlerTests
{
    private readonly IOrderRepository _repository = Substitute.For<IOrderRepository>();
    private readonly CreateOrderHandler _sut;

    public CreateOrderHandlerTests()
    {
        _sut = new CreateOrderHandler(_repository);
    }

    [Fact]
    public async Task Handle_ValidOrder_ReturnsCreatedOrder()
    {
        // Arrange
        var command = new CreateOrderCommand("John Doe", [new OrderItem("Widget", 2)]);
        _repository.AddAsync(Arg.Any<Order>()).Returns(new Order { Id = 1 });

        // Act
        var result = await _sut.Handle(command, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result.Id.Should().Be(1);
        await _repository.Received(1).AddAsync(Arg.Any<Order>());
    }
}
```

### Integration Test Pattern
```csharp
public class CreateOrderEndpointTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client = factory.CreateClient();

    [Fact]
    public async Task CreateOrder_ValidRequest_Returns201()
    {
        // Arrange
        var request = new { CustomerName = "John", Items = new[] { new { Name = "Widget", Quantity = 2 } } };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }
}
```

### Naming Convention
- MethodName_Scenario_ExpectedResult
- Example: Handle_EmptyOrderItems_ReturnsValidationError

### What NOT to Do in Tests
- Do NOT use Thread.Sleep (use async delays if needed, but prefer event-based waiting)
- Do NOT share state between tests (each test is independent)
- Do NOT mock what you don't own (wrap external libraries behind interfaces)
- Do NOT test private methods (test through the public API)
```

## Putting It All Together

The key insight is this: a generic AGENTS.md helps, but a .NET-specific one transforms your workflow. The templates above aren't theoretical. They're distilled from real projects where agents went from producing code that needed heavy editing to producing code that slotted in cleanly.

Start with the template closest to your project type. Copy it. Customize the sections that differ from your conventions. Remove anything that doesn't apply. Then use it for a week and iterate.

The best context files aren't written in one sitting. They grow. Every time an agent makes a mistake that your context file should have prevented, add a line. Every time you correct an agent's output, ask yourself: "Could I have prevented this with a convention in my AGENTS.md?" Usually, the answer is yes.

Your context file is a living document. Treat it like code: version it, review it, improve it. It's the single highest-leverage investment you can make in your agentic .NET development workflow.
