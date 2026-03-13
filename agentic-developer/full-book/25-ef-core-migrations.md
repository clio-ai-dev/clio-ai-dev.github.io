# Chapter 25: EF Core Migrations with Agents

*Database schema evolution is one of the highest-risk tasks you can hand to an agent. It's also one of the highest-value. Get the workflow right and agents can generate migrations, seed data, and schema changes faster than you ever could. Get it wrong and you're debugging data loss in production. This chapter gives you the workflow that keeps things safe.*

## Why Migrations Are Different

When an agent writes bad C# code, you catch it in code review or tests. When an agent writes a bad migration, the damage can be permanent. A dropped column, a bad data transform, an irreversible rename. Migrations touch your production data. There's no "undo" button.

That's not a reason to avoid using agents for migrations. It's a reason to have a disciplined workflow around it.

## The Migration Safety Workflow


Every agent-generated migration should follow this sequence:

**Generate → Review → Test → Apply**

No shortcuts. No skipping steps. Here's each one in detail.

### Step 1: Generate

The agent makes changes to your entity classes and then runs the migration command:

```bash
dotnet ef migrations add AddOrderShippingAddress --project src/Api
```

The agent should name migrations descriptively. Not `Migration1` or `Update`. Names should describe what changed: `AddOrderShippingAddress`, `CreateProductCategoryIndex`, `RenameCustomerEmailToContactEmail`.

### Step 2: Review

This is non-negotiable. Read the generated migration file. Every line. The agent created it, but you own it. Look for:

- **Destructive operations**: `DropColumn`, `DropTable`, `DropIndex`. Are they intentional?
- **Data loss risks**: Changing a column type (string to int) can fail or lose data
- **Missing data migrations**: Renaming a column without migrating existing data
- **Performance concerns**: Adding an index on a table with millions of rows without `CONCURRENTLY`
- **Default values**: New non-nullable columns need defaults for existing rows

### Step 3: Test

Run the migration against a real database. Not SQLite (unless that's your production database). The same engine you use in production:

```bash
# Reset and apply all migrations to a test database
dotnet ef database drop --force --project src/Api
dotnet ef database update --project src/Api
```

If you're using Testcontainers in your test suite, even better. Your integration tests can apply migrations automatically and verify they work.

### Step 4: Apply

Only after review and testing. In a CI/CD pipeline, migrations should apply automatically during deployment. In development, `dotnet ef database update` does the job.

## Teaching Agents to Generate Migrations

The most productive pattern is entity-first: you describe what you want, the agent modifies entity classes and configurations, then generates the migration.

### Adding a New Entity

Prompt:
> "Add a ShippingAddress entity with Street, City, State, ZipCode (all strings, required), and a foreign key to Order. One Order has one ShippingAddress. Generate the migration."

A well-configured agent produces:

```csharp
public class ShippingAddress
{
    public int Id { get; set; }
    public required string Street { get; set; }
    public required string City { get; set; }
    public required string State { get; set; }
    public required string ZipCode { get; set; }
    public int OrderId { get; set; }
    public Order Order { get; set; } = null!;
}
```

```csharp
public class ShippingAddressConfiguration : IEntityTypeConfiguration<ShippingAddress>
{
    public void Configure(EntityTypeBuilder<ShippingAddress> builder)
    {
        builder.HasKey(s => s.Id);
        builder.Property(s => s.Street).HasMaxLength(200).IsRequired();
        builder.Property(s => s.City).HasMaxLength(100).IsRequired();
        builder.Property(s => s.State).HasMaxLength(50).IsRequired();
        builder.Property(s => s.ZipCode).HasMaxLength(20).IsRequired();
    }
}
```

Then adds the `DbSet` to the context and runs `dotnet ef migrations add AddShippingAddress`.

### Adding Relationships

Relationships are where agents start making mistakes. The most common issue: creating bidirectional navigation properties when you only need one direction. Your context file should specify your preference:

```markdown
## EF Core Relationships
- One-to-many: navigation collection on the parent, foreign key on the child
- One-to-one: navigation property on the dependent, foreign key on the dependent
- Many-to-many: explicit join entity (no implicit join tables)
- Only add navigation properties you actually query through
```

### Adding Indexes

Agents rarely add indexes on their own. You need to ask for them explicitly:

> "Add an index on Order.CreatedAt. We query orders by date range frequently."

```csharp
builder.HasIndex(o => o.CreatedAt);
```

For composite indexes:

> "Add a composite index on Order.CustomerId and Order.Status."

```csharp
builder.HasIndex(o => new { o.CustomerId, o.Status });
```

For unique constraints:

```csharp
builder.HasIndex(o => o.OrderNumber).IsUnique();
```

## Seed Data Generation

Agents are excellent at generating seed data. This is one area where you can delegate freely:

> "Generate seed data for 10 product categories with realistic names and descriptions. Use HasData in the entity configuration."

```csharp
public class CategoryConfiguration : IEntityTypeConfiguration<Category>
{
    public void Configure(EntityTypeBuilder<Category> builder)
    {
        builder.HasKey(c => c.Id);
        builder.Property(c => c.Name).HasMaxLength(100).IsRequired();

        builder.HasData(
            new Category { Id = 1, Name = "Electronics", Description = "Computers, phones, and accessories" },
            new Category { Id = 2, Name = "Clothing", Description = "Apparel and fashion items" },
            new Category { Id = 3, Name = "Home & Garden", Description = "Furniture, decor, and outdoor" },
            // ... more categories
        );
    }
}
```

Important: `HasData` requires explicit primary key values. Agents sometimes forget this and leave `Id = 0`, which fails silently or creates duplicates. Call this out in your context file:

```markdown
## Seed Data Rules
- Always specify explicit Id values in HasData
- Start seed data Ids at 1 and increment sequentially
- Keep seed data in the entity's configuration file
- For large seed data sets, use a separate static class
```

## Handling Complex Migrations

Some schema changes can't be expressed as simple add/remove operations. These require manual intervention, and agents need to know when to stop and ask.

### Column Renames

EF Core's migration generator can't tell the difference between "rename a column" and "drop a column and add a new one." If you rename a property on your entity, the generated migration will contain:

```csharp
migrationBuilder.DropColumn(name: "Email", table: "Customers");
migrationBuilder.AddColumn<string>(name: "ContactEmail", table: "Customers");
```

This destroys all existing email data. The correct migration is:

```csharp
migrationBuilder.RenameColumn(
    name: "Email",
    table: "Customers",
    newName: "ContactEmail");
```

Your context file must warn about this:

```markdown
## Migration Safety Rules
- Column renames: NEVER auto-generate. Always use RenameColumn manually.
- Table renames: Same rule. Use RenameTable.
- After generating any migration that involves renamed properties, STOP and flag it for review.
```

### Data Transforms

Sometimes you need to transform data during a migration. Adding a new column that's computed from existing data, splitting a full name into first and last name, converting a string enum to an integer.

These require raw SQL in the migration:

```csharp
migrationBuilder.AddColumn<string>(
    name: "FirstName",
    table: "Customers",
    nullable: true);

migrationBuilder.AddColumn<string>(
    name: "LastName",
    table: "Customers",
    nullable: true);

migrationBuilder.Sql("""
    UPDATE "Customers"
    SET "FirstName" = split_part("FullName", ' ', 1),
        "LastName" = split_part("FullName", ' ', 2)
    WHERE "FullName" IS NOT NULL
    """);

migrationBuilder.DropColumn(name: "FullName", table: "Customers");
```

Agents can write these SQL transforms, but they need explicit instruction. Don't assume the agent will know that a column rename requires data migration. Tell it:

> "Rename the Customer.FullName property to FirstName and LastName (split on space). Generate a migration that preserves existing data."

### Changing Column Types

Converting a `string` column to `int` or changing a `varchar(50)` to `varchar(200)` can be safe or dangerous depending on the database engine and existing data. Widening a string column is usually fine. Narrowing it or changing types is risky.

Your context file should include:

```markdown
## Type Changes
- Widening string columns (50 → 200): safe, generate normally
- Narrowing string columns (200 → 50): STOP and flag. Existing data may be truncated.
- String to numeric: STOP and flag. Requires data validation first.
- Numeric precision changes: STOP and flag.
```

## Common Agent Mistakes with EF Core

These mistakes appear consistently across different agents and models. Document them in your context file and save yourself repeated corrections.


### 1. Forgetting to Add DbSet

The agent creates the entity and configuration but forgets to add `DbSet<NewEntity>` to the DbContext. The migration generates empty.

**Prevention:** Add to your context file: "After creating a new entity, always add a DbSet<T> property to AppDbContext."

### 2. Circular References

The agent creates bidirectional navigation properties that cause serialization loops:

```csharp
public class Order
{
    public List<OrderItem> Items { get; set; }
}

public class OrderItem
{
    public Order Order { get; set; } // Circular reference when serializing
}
```

**Prevention:** "Only add navigation properties you query through. Use foreign key properties (OrderId) without navigation properties when you don't need to load the related entity."

### 3. Missing Cascade Delete Configuration

The agent adds relationships without thinking about what happens when a parent is deleted. EF Core defaults to cascade delete for required relationships, which might not be what you want.

**Prevention:** "Explicitly configure delete behavior for all relationships. Default to Restrict for production safety."

```csharp
builder.HasMany(o => o.Items)
    .WithOne()
    .HasForeignKey(i => i.OrderId)
    .OnDelete(DeleteBehavior.Cascade); // Explicit, not default
```

### 4. Using DateTime Instead of DateTimeOffset

Agents default to `DateTime` because it's more common in training data. For anything stored in a database, `DateTimeOffset` is the safer choice because it preserves timezone information.

**Prevention:** "Use DateTimeOffset for all timestamp properties. Never use DateTime for database-stored dates."

### 5. Not Using Async Methods

The agent writes `context.SaveChanges()` instead of `await context.SaveChangesAsync()`. Or `context.Products.ToList()` instead of `await context.Products.ToListAsync()`.

**Prevention:** "All EF Core operations must use async methods. No .ToList(), .FirstOrDefault(), .SaveChanges(). Always use the Async suffix with await."

### 6. Editing Existing Migrations

Sometimes an agent will modify an already-applied migration instead of creating a new one. This causes the migration history to go out of sync with the database.

**Prevention:** "NEVER edit an existing migration file. Always create a new migration to make changes."

### 7. Missing Indexes on Foreign Keys

EF Core automatically creates indexes for foreign keys in some cases, but agents sometimes add redundant indexes or miss composite indexes that would help query performance.

**Prevention:** "Check that frequently queried columns have indexes. Don't duplicate indexes that EF Core creates automatically for foreign keys."

## The Migration Review Checklist

Use this checklist every time an agent generates a migration:

```markdown
## Migration Review Checklist
- [ ] Read the entire migration file (Up and Down methods)
- [ ] No accidental DropColumn or DropTable operations
- [ ] Column renames use RenameColumn, not drop+add
- [ ] New non-nullable columns have default values for existing rows
- [ ] Indexes are appropriate (not missing, not redundant)
- [ ] String columns have MaxLength configured
- [ ] Delete behaviors are explicitly set
- [ ] Down() method correctly reverses the Up() method
- [ ] Migration name is descriptive
- [ ] Tested against a real database instance
```

Print this out. Tape it next to your monitor. Or better yet, put it in your AGENTS.md so the agent itself checks these items before presenting the migration to you.

## The Bigger Picture

EF Core migrations are a microcosm of the agentic development challenge: agents are fast, capable, and prone to subtle errors that compound over time. A wrong line of C# fails a test. A wrong line in a migration corrupts data.

The solution isn't to avoid agents for migrations. It's to build a workflow that captures the speed benefit while maintaining the safety guarantees. Generate, review, test, apply. Every time. No exceptions.

The developers who get burned by agent-generated migrations are the ones who skip the review step because "it's just adding a column." It's never just adding a column. There's always a default value question, an index question, or a cascade delete question hiding in there. The agent might get it right. But you need to verify.

That verification step is what separates professional agentic development from hoping for the best.
