# Chapter 27: Security Review with Agents

*Part VII: The Discipline*

Security review is the task most developers skip and most teams underinvest in. Not because they don't care, but because it's tedious, specialized, and easy to defer. "We'll do a security pass before launch" becomes "we'll fix it if something breaks."

Agents change the economics of security review. Not because they replace security experts (they don't), but because they make first-pass security scanning nearly free. The effort drops from "schedule a meeting with the security team" to "run the agent before you push." That's a meaningful shift.

This chapter covers how to use agents for systematic security review: what they catch, what they miss, and how to build a workflow that makes security a continuous habit instead of a quarterly event.

## The OWASP Top 10 with Agent Eyes

The OWASP Top 10 is the standard checklist for web application security. Let's walk through each category and how well agents handle it.

### What Agents Catch Well

**Injection (A03:2021).** Agents are excellent at spotting SQL injection, command injection, and LDAP injection vulnerabilities. They can trace data flow from user input to database queries and flag unsanitized usage. This is pattern matching at scale, exactly what LLMs excel at.

```csharp
// An agent will flag this immediately
public async Task<User> GetUser(string username)
{
    var query = $"SELECT * FROM Users WHERE Username = '{username}'";
    return await _db.QueryFirstAsync<User>(query);
}
```

The fix is obvious to the agent too: parameterized queries, or better yet, an ORM. Agents catch these with near-100% accuracy because the pattern is unambiguous.

**Security Misconfiguration (A05:2021).** Agents are surprisingly good at catching misconfigurations in startup code, middleware ordering, CORS policies, and header settings. They know the correct patterns and can spot deviations.

```csharp
// Agent will flag: CORS allows any origin
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});
```

**Vulnerable and Outdated Components (A06:2021).** This is where agents shine brightest. They can scan your `.csproj` files, `package.json`, `requirements.txt`, or any dependency manifest and cross-reference against known vulnerability databases. More on this in the dependency auditing section below.

**Identification and Authentication Failures (A07:2021).** Agents catch weak password policies, missing rate limiting on login endpoints, tokens stored in local storage, and missing HTTPS enforcement. These are well-documented anti-patterns that agents have seen thousands of times in training data.

### What Agents Catch Sometimes

**Broken Access Control (A01:2021).** Agents can spot missing `[Authorize]` attributes and obvious authorization gaps. But they struggle with business logic authorization, the kind where "managers can only see their own team's data" is buried in a requirements document the agent has never read.

**Cryptographic Failures (A02:2021).** Agents know that MD5 is broken and that you shouldn't roll your own crypto. They'll flag weak hashing algorithms and hardcoded encryption keys. But subtle cryptographic issues (timing attacks, improper IV reuse, weak random number generation in security contexts) get missed more often than not.

**Server-Side Request Forgery (A10:2021).** Agents can flag obvious SSRF patterns where user input directly controls a URL being fetched. They miss the subtle cases where URLs are constructed through multiple layers of indirection.

### What Agents Miss

**Insecure Design (A04:2021).** This is the category where agents fail most consistently. Insecure design is about architectural decisions: missing threat modeling, insufficient separation of concerns, no defense in depth. An agent reviewing code can't tell you that your architecture lacks a proper trust boundary. That requires understanding the system holistically, something that needs a human security architect.


**Software and Data Integrity Failures (A08:2021).** CI/CD pipeline security, unsigned updates, deserialization attacks in complex chains. Agents might catch `BinaryFormatter` usage (a known .NET vulnerability), but they won't evaluate whether your deployment pipeline has proper integrity checks.

**Security Logging and Monitoring Failures (A09:2021).** Agents can check if you're logging authentication events, but they can't evaluate whether your monitoring is sufficient to detect an active breach. This requires operational context agents don't have.

## Dependency Vulnerability Auditing

This is the lowest-effort, highest-value security task you can hand to an agent. Here's the workflow:

### The Prompt

```
Audit all NuGet dependencies in this solution for known vulnerabilities.

For each project:
1. List all direct dependencies and their versions
2. Check if any have known CVEs
3. Flag any packages that are more than 2 major versions behind
4. Identify packages that are deprecated or unmaintained
5. Check for packages with known supply chain concerns

Output a table: Package | Current Version | Latest Version | Vulnerabilities | Risk Level
```

### Combining with CLI Tools

Agents work even better when they can run `dotnet list package --vulnerable --include-transitive`:

```
Run `dotnet list package --vulnerable --include-transitive` on the solution.
Parse the output and for each vulnerable package:
1. Explain the vulnerability in plain language
2. Assess the impact on our specific application
3. Recommend the upgrade path
4. Flag any breaking changes in the upgrade
```

This is the kind of task that would take a developer an hour of research per vulnerability. The agent does it in minutes, with reasonable accuracy. You still need to verify the upgrade paths, but the research phase is nearly eliminated.

### Transitive Dependencies Matter

Direct dependencies are easy. Transitive dependencies are where the real risk lives. Your app uses PackageA, which depends on PackageB v2.1, which has a critical vulnerability. You'd never know without scanning the full dependency tree.

Agents handle this well because they can parse the `dotnet list package --include-transitive` output and cross-reference each package. The key insight: tell the agent to focus on transitive vulnerabilities specifically, because those are the ones humans consistently miss.

## Secrets Detection

Hardcoded secrets in code and configuration files remain one of the most common security failures. Agents are excellent at catching them.

### The Prompt

```
Scan the entire repository for hardcoded secrets, API keys, connection strings,
passwords, tokens, and credentials.

Check:
- Source code files (*.cs, *.js, *.ts, *.py)
- Configuration files (appsettings*.json, *.config, *.yaml, *.env)
- Infrastructure files (*.tf, *.bicep, docker-compose*.yml)
- Test files (often overlooked but still risky)
- Documentation (README files sometimes contain real credentials)

For each finding:
1. File and line number
2. Type of secret (API key, password, connection string, etc.)
3. Risk level (is this a production credential or a test value?)
4. Recommended remediation (environment variable, key vault, user secrets)
```

### What Agents Catch

Agents reliably catch:

- Connection strings with passwords: `Server=prod-db;Password=hunter2`
- API keys in config: `"ApiKey": "sk-proj-abc123..."`
- Hardcoded JWTs and bearer tokens
- AWS/Azure/GCP credentials in any format
- Private keys (PEM format, XML format)
- Passwords in comments ("// TODO: remove this password: admin123")

### The False Positive Problem

Agents over-report. They'll flag placeholder values (`"YOUR_API_KEY_HERE"`), test fixtures, and example configurations. This is annoying but preferable to under-reporting. Build a simple workflow: the agent flags everything, you triage quickly, and the few false positives take seconds to dismiss.

A good follow-up prompt:

```
From the secrets you found, separate them into three categories:
1. CRITICAL: Looks like a real production credential
2. REVIEW: Could be real, needs human verification
3. LIKELY SAFE: Test values, placeholders, or examples
```

This reduces your triage time significantly.

## Security-Focused Code Review Prompts

Beyond scanning for specific vulnerability categories, you can use agents for general security-focused code review. Here are prompts that work well.

### For API Endpoints

```
Review this API endpoint for security concerns:

1. Input validation: Is all user input validated before processing?
2. Authorization: Are there proper access controls? Can users access
   other users' data?
3. Rate limiting: Is this endpoint protected against abuse?
4. Data exposure: Does the response include more data than necessary?
5. Error handling: Do error messages leak internal details?
6. Logging: Are security-relevant events logged?

Be specific. Point to exact lines of code.
```

### For Authentication Flows

```
Review this authentication implementation:

1. Password handling: Proper hashing? Salt? Work factor?
2. Token management: Secure generation? Proper expiration? Refresh flow?
3. Session handling: Secure cookies? CSRF protection? Session fixation?
4. Account enumeration: Can an attacker determine if an account exists?
5. Brute force protection: Rate limiting? Account lockout? CAPTCHA?
6. MFA implementation: Proper TOTP? Recovery codes?
```

### For Data Access Layers

```
Review this data access code for security:

1. SQL injection: Any raw queries with string concatenation?
2. Mass assignment: Can users set fields they shouldn't (isAdmin, price)?
3. IDOR: Can users access resources by manipulating IDs?
4. Data filtering: Is tenant isolation enforced at the query level?
5. Sensitive data: Are passwords, tokens, or PII properly handled?
```

## The Systematic Security Review Workflow


Here's the workflow I recommend. It runs in under 30 minutes for most codebases and catches the vast majority of low-hanging fruit.

### Phase 1: Automated Scanning (5 minutes)

Run the agent with this prompt:

```
Perform a security scan of this codebase:

1. Run `dotnet list package --vulnerable --include-transitive`
2. Scan all files for hardcoded secrets
3. Check all API endpoints for missing [Authorize] attributes
4. Review middleware ordering in Program.cs for security issues
5. Check CORS, HTTPS, and header security configuration

Produce a findings report sorted by severity.
```

The agent runs the CLI commands, scans the codebase, and produces a report. You skim the report, noting anything critical.

### Phase 2: Targeted Review (15 minutes)

Pick the highest-risk areas identified in Phase 1 and run focused reviews:

```
Deep review the authentication controller at src/Api/Controllers/AuthController.cs.
Check for all OWASP authentication failures.
```

```
Review the payment processing service at src/Domain/Payments/PaymentService.cs.
Focus on input validation, error handling, and data exposure.
```

### Phase 3: Threat Modeling Assist (10 minutes)

This is where agents help you think, not just scan:

```
Based on the codebase structure, identify the top 5 attack vectors
an external attacker would target. For each:
1. The attack vector
2. Current defenses (if any)
3. Recommended mitigations
```

Agents produce surprisingly useful threat models for well-structured codebases. They won't match a dedicated security architect's analysis, but they'll identify the obvious attack surfaces you might overlook when you're deep in feature work.

## Real Example: Security Review of an API Endpoint

Let's walk through a concrete example. Here's a payment endpoint that an agent might review:

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class PaymentsController : ControllerBase
{
    private readonly IPaymentService _paymentService;
    private readonly ILogger<PaymentsController> _logger;

    public PaymentsController(
        IPaymentService paymentService,
        ILogger<PaymentsController> logger)
    {
        _paymentService = paymentService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> ProcessPayment(PaymentRequest request)
    {
        _logger.LogInformation(
            "Processing payment for card {CardNumber}, amount {Amount}",
            request.CardNumber, request.Amount);

        var result = await _paymentService.ProcessAsync(request);

        if (!result.Success)
            return BadRequest(new { error = result.ErrorMessage, details = result.Exception?.ToString() });

        return Ok(result);
    }
}

public record PaymentRequest(
    string CardNumber,
    string Cvv,
    int ExpiryMonth,
    int ExpiryYear,
    decimal Amount,
    string Currency);
```

### Agent Findings

A well-prompted agent will identify these issues:

**CRITICAL: PCI violation in logging.** The `LogInformation` call logs the full card number. This violates PCI DSS requirements. Card numbers must never appear in logs. The agent flags this immediately because it's a well-known anti-pattern.

**CRITICAL: Missing authorization.** No `[Authorize]` attribute on the controller or action. Anyone can call this endpoint. The agent catches missing authorization attributes reliably.

**HIGH: Exception details in error response.** `result.Exception?.ToString()` returns the full stack trace to the caller. This leaks internal implementation details that help attackers. The agent recommends returning a generic error message and logging the exception server-side.

**HIGH: No input validation.** No validation on `CardNumber` format, `Amount` range (negative amounts?), `Currency` whitelist, or `ExpiryMonth`/`ExpiryYear` sanity checks. The agent suggests adding `[Required]`, `[Range]`, `[RegularExpression]`, and a FluentValidation validator.

**MEDIUM: No rate limiting.** Payment endpoints are high-value targets for card testing attacks. The agent recommends `[EnableRateLimiting("payment")]` or equivalent middleware.

**MEDIUM: CVV in the request model.** If this request model is logged or serialized anywhere, the CVV is exposed. The agent suggests a `[JsonIgnore]` attribute on CVV for serialization, or better yet, tokenizing the card data before it reaches your API.

**LOW: No idempotency key.** Without an idempotency mechanism, retried requests could process duplicate payments. The agent suggests adding an `IdempotencyKey` header.

### The Fixed Version

After the agent applies its recommendations:

```csharp
[ApiController]
[Route("api/v1/[controller]")]
[Authorize]
[EnableRateLimiting("payment")]
public class PaymentsController : ControllerBase
{
    private readonly IPaymentService _paymentService;
    private readonly ILogger<PaymentsController> _logger;

    public PaymentsController(
        IPaymentService paymentService,
        ILogger<PaymentsController> logger)
    {
        _paymentService = paymentService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> ProcessPayment(
        [FromBody] PaymentRequest request,
        [FromHeader(Name = "Idempotency-Key")] string? idempotencyKey)
    {
        _logger.LogInformation(
            "Processing payment for card ending {LastFour}, amount {Amount} {Currency}",
            request.CardNumber[^4..], request.Amount, request.Currency);

        var result = await _paymentService.ProcessAsync(request, idempotencyKey);

        if (!result.Success)
        {
            _logger.LogWarning("Payment failed: {Error}", result.ErrorMessage);
            return BadRequest(new { error = "Payment processing failed." });
        }

        return Ok(new { transactionId = result.TransactionId, status = "approved" });
    }
}

public record PaymentRequest
{
    [Required]
    [CreditCard]
    public required string CardNumber { get; init; }

    [Required]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    public required string Cvv { get; init; }

    [Range(1, 12)]
    public required int ExpiryMonth { get; init; }

    [Range(2024, 2040)]
    public required int ExpiryYear { get; init; }

    [Range(0.01, 999999.99)]
    public required decimal Amount { get; init; }

    [Required]
    [RegularExpression("^[A-Z]{3}$")]
    public required string Currency { get; init; }
}
```

Six of the seven findings are mechanical fixes. The agent handled them all correctly. The seventh (CVV tokenization) is an architectural decision that requires human judgment about your payment provider integration.

## What Agents Catch Well vs. What They Miss

Let me be direct about this, because overselling agent security capabilities is dangerous.

### Agents Are Reliable For

- **Known vulnerability patterns.** SQL injection, XSS, CSRF, hardcoded secrets, weak hashing. These are well-documented, pattern-based, and agents have seen millions of examples.
- **Configuration errors.** Missing HTTPS, overly permissive CORS, incorrect middleware ordering, debug settings in production configs.
- **Dependency vulnerabilities.** Cross-referencing package versions against CVE databases.
- **Missing security controls.** No authorization, no rate limiting, no input validation, no CSRF tokens.
- **Data exposure.** Logging sensitive data, returning too much in API responses, verbose error messages.

### Agents Are Unreliable For

- **Business logic authorization.** "Can this user see this data?" depends on business rules the agent doesn't know.
- **Architectural security.** Trust boundaries, defense in depth, network segmentation. These require system-level thinking.
- **Novel attack vectors.** Zero-day patterns, creative exploitation chains, attacks specific to your domain.
- **Compliance.** HIPAA, PCI DSS, GDPR requirements beyond obvious data handling. Agents know the regulations exist but can't audit compliance reliably.
- **Timing and race conditions.** TOCTOU bugs, race conditions in concurrent code, timing side channels. These are subtle and agents miss them consistently.
- **Supply chain attacks.** Typosquatting packages, compromised maintainers, malicious build scripts. Agents can check known vulnerabilities but can't evaluate trust.

### The First-Pass Filter Model

The right mental model: agents are a first-pass security filter. They catch the obvious stuff quickly and cheaply. This raises the floor of your security posture dramatically, because "obvious stuff" is what causes most breaches.

But they don't raise the ceiling. For that, you need security experts, penetration testing, formal threat modeling, and architectural review. The agent handles the 80% of findings that are mechanical. Humans handle the 20% that require judgment.

The mistake is treating agent security review as sufficient. It's not. It's necessary but not sufficient. The discipline is knowing the difference: let agents handle the scanning, flagging, and obvious fixes. Reserve your (or your security team's) attention for the architectural decisions, business logic authorization, and novel threats that agents can't evaluate.


## Building the Habit

The best security review is the one that actually happens. Agents make it happen by reducing the cost to near zero.

Add security review to your agent workflow:
1. Before every PR, run a security-focused agent review on changed files
2. Weekly, run a full dependency audit
3. Monthly, run a comprehensive codebase security scan
4. Quarterly, have a human security expert review the agent's findings and your threat model

The agent handles steps 1-3. Step 4 is where human expertise compounds the value. The agent's continuous scanning keeps the codebase clean between expert reviews. The expert reviews catch what agents miss and improve your agent prompts for next time.

That's the security review workflow. Agents as a continuous, cheap, reliable first pass. Humans for the judgment calls. Together, they create a security posture that neither achieves alone.
