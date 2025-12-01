# Gherkin BDD Testing - Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT / API CONSUMER                               │
│                     (POST requests with specifications)                      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FLASK API LAYER                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────────┐    │
│  │  /api/bdd/      │  │  /api/bdd/       │  │  /api/bdd/             │    │
│  │  generate       │  │  execute-        │  │  playwright/results/   │    │
│  │                 │  │  playwright      │  │  {task_id}             │    │
│  └────────┬────────┘  └────────┬─────────┘  └───────────┬────────────┘    │
│           │                    │                         │                  │
└───────────┼────────────────────┼─────────────────────────┼──────────────────┘
            │                    │                         │
            ▼                    ▼                         ▼
┌───────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│  BDD Generator    │  │  Task Manager       │  │  Database Service    │
│  ┌─────────────┐  │  │  ┌───────────────┐  │  │  ┌────────────────┐  │
│  │ Natural     │  │  │  │ In-Memory     │  │  │  │ PostgreSQL/    │  │
│  │ Language    │  │  │  │ Task Cache    │  │  │  │ Supabase       │  │
│  │ Parser      │  │  │  │               │  │  │  │                │  │
│  └─────────────┘  │  │  │ - create_task │  │  │  │ - Task Status  │  │
│  ┌─────────────┐  │  │  │ - update_task │  │  │  │ - Results      │  │
│  │ Gherkin     │  │  │  │ - get_task    │  │  │  │ - Metadata     │  │
│  │ Generator   │  │  │  └───────────────┘  │  │  └────────────────┘  │
│  │ (.feature)  │  │  │                     │  │                      │
│  └─────────────┘  │  │  ┌───────────────┐  │  │                      │
│                   │  │  │ File System   │  │  │                      │
│  ┌─────────────┐  │  │  │ Persistence   │  │  │                      │
│  │ Structured  │  │  │  │ (JSON files)  │  │  │                      │
│  │ JSON        │  │  │  └───────────────┘  │  │                      │
│  │ Converter   │  │  │                     │  │                      │
│  └─────────────┘  │  └─────────────────────┘  └──────────────────────┘
└───────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PLAYWRIGHT EXECUTOR ENGINE                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PlaywrightAmazonExecutor                          │   │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐     │   │
│  │  │ Browser      │  │ Event Loop    │  │ Error Handler        │     │   │
│  │  │ Manager      │  │ Manager       │  │                      │     │   │
│  │  │              │  │               │  │ - TargetClosedError  │     │   │
│  │  │ - Init       │  │ - Detect Loop │  │ - Retry Logic        │     │   │
│  │  │ - Launch     │  │ - Create Loop │  │ - Crash Detection    │     │   │
│  │  │ - Context    │  │ - Handle      │  │ - State Validation   │     │   │
│  │  │ - Page       │  │   Conflicts   │  │                      │     │   │
│  │  └──────────────┘  └───────────────┘  └──────────────────────┘     │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │              Step Executors                                 │    │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │    │   │
│  │  │  │   GIVEN     │  │    WHEN     │  │      THEN       │    │    │   │
│  │  │  │             │  │             │  │                 │    │    │   │
│  │  │  │ - Navigate  │  │ - Click     │  │ - Validate      │    │    │   │
│  │  │  │ - Setup     │  │ - Fill      │  │ - Assert        │    │    │   │
│  │  │  │ - Precond.  │  │ - Search    │  │ - Check         │    │    │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────┘    │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHROMIUM BROWSER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Page/Tab 1  │  │  Page/Tab 2  │  │  Context     │  │  DevTools    │   │
│  │              │  │              │  │  (Session)   │  │  Protocol    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TARGET WEB APPLICATION                              │
│                        (e.g., Amazon, Google, etc.)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Test Execution Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          1. TEST SUBMISSION                                   │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
                    POST /api/bdd/generate-and-execute
                    {
                      "specification": {
                        "feature": {...},
                        "scenarios": [...],
                        "configuration": {...}
                      },
                      "async": true
                    }
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     2. TASK CREATION & VALIDATION                             │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Task Manager                                                        │    │
│  │  • Generate UUID task_id                                            │    │
│  │  • Create task record (status: pending)                             │    │
│  │  • Save to file system (results/{task_id}.json)                     │    │
│  │  • Save to database (test_executions table)                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  Response: { "task_id": "abc-123-def", "status": "pending" }                │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     3. BDD GENERATION (if needed)                             │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  EnhancedBDDGenerator                                                │    │
│  │  • Parse specification (natural language or structured)             │    │
│  │  • Generate Gherkin .feature file                                   │    │
│  │  • Save to features/generated/generated_{test_id}.feature           │    │
│  │  • Extract scenarios, steps, tags                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  Generated Feature File:                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Feature: Login Test                                                  │    │
│  │   @smoke @login                                                      │    │
│  │                                                                       │    │
│  │   Scenario: User can login with valid credentials                   │    │
│  │     Given I am on the login page                                     │    │
│  │     When I enter username "user@example.com"                        │    │
│  │     And I enter password "secret123"                                │    │
│  │     And I click the login button                                    │    │
│  │     Then I should see the dashboard                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     4. ASYNC EXECUTION (Background)                           │
│                                                                               │
│  Update Status: running                                                      │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Event Loop Management                                               │    │
│  │  ┌──────────────────────────────────────────────────────────┐       │    │
│  │  │ Check for existing event loop                             │       │    │
│  │  │   ├─ Loop exists? → Create new loop in current thread     │       │    │
│  │  │   └─ No loop? → Use asyncio.run()                         │       │    │
│  │  └──────────────────────────────────────────────────────────┘       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     5. BROWSER INITIALIZATION                                 │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Step 1: Start Playwright                                           │    │
│  │    • await async_playwright().start() [timeout: 30s]               │    │
│  │                                                                       │    │
│  │  Step 2: Check Display Environment                                  │    │
│  │    • If headless=False and no DISPLAY → Force headless=True         │    │
│  │                                                                       │    │
│  │  Step 3: Launch Browser (with retry: 3 attempts)                    │    │
│  │    • Chromium with args: [--disable-blink-features=...]            │    │
│  │    • Verify: browser.is_connected()                                 │    │
│  │                                                                       │    │
│  │  Step 4: Create Context                                             │    │
│  │    • viewport: 1280x720                                             │    │
│  │    • ignore_https_errors: true                                      │    │
│  │                                                                       │    │
│  │  Step 5: Create Page (with retry: 3 attempts)                       │    │
│  │    Attempt 1: Create page + wait 1s + verify                        │    │
│  │    Attempt 2: Wait 1s + retry                                       │    │
│  │    Attempt 3: Switch to headless + recreate browser + retry         │    │
│  │                                                                       │    │
│  │  Step 6: Setup Event Listeners                                      │    │
│  │    • page.on('crash') → Log crash                                   │    │
│  │    • page.on('close') → Log unexpected close                        │    │
│  │                                                                       │    │
│  │  Step 7: Set Timeouts                                               │    │
│  │    • page.set_default_timeout(30000)                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     6. SCENARIO EXECUTION                                     │
│                                                                               │
│  FOR EACH Scenario:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Pre-Check: Validate browser state                                  │    │
│  │    • browser.is_connected() ?                                       │    │
│  │    • page.is_closed() ?                                             │    │
│  │    • browser_crashed flag ?                                         │    │
│  │                                                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Execute GIVEN Steps (Setup)                                 │   │    │
│  │  │  ┌────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  FOR EACH given step:                                   │  │   │    │
│  │  │  │    • Navigate to URL (with retry: 2 attempts)           │  │   │    │
│  │  │  │    • Wait for page load (load/domcontentloaded)         │  │   │    │
│  │  │  │    • Capture response code                              │  │   │    │
│  │  │  │    • Handle TargetClosedError → Stop scenario           │  │   │    │
│  │  │  │    • Record step result (passed/failed)                 │  │   │    │
│  │  │  └────────────────────────────────────────────────────────┘  │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Execute WHEN Steps (Actions)                                │   │    │
│  │  │  ┌────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  FOR EACH when step:                                    │  │   │    │
│  │  │  │    • Check browser state                                │  │   │    │
│  │  │  │    • Execute action:                                    │  │   │    │
│  │  │  │      - click(locator)                                   │  │   │    │
│  │  │  │      - fill(locator, text)                              │  │   │    │
│  │  │  │      - navigate(url)                                    │  │   │    │
│  │  │  │    • Record step result                                 │  │   │    │
│  │  │  └────────────────────────────────────────────────────────┘  │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Execute THEN Steps (Validations)                           │   │    │
│  │  │  ┌────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  FOR EACH then step:                                    │  │   │    │
│  │  │  │    • Check browser state                                │  │   │    │
│  │  │  │    • Execute validation:                                │  │   │    │
│  │  │  │      - element_visible(locator)                         │  │   │    │
│  │  │  │      - element_exists(locator)                          │  │   │    │
│  │  │  │      - text_content(locator, expected)                  │  │   │    │
│  │  │  │      - url_contains(text)                               │  │   │    │
│  │  │  │    • Record step result (passed/failed)                 │  │   │    │
│  │  │  └────────────────────────────────────────────────────────┘  │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                       │    │
│  │  Scenario Result:                                                    │    │
│  │    • status: passed/failed/partial                                  │    │
│  │    • steps: [{step, type, status, message, error}, ...]            │    │
│  │    • start_time, end_time                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  NEXT Scenario...                                                            │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     7. RESULTS AGGREGATION                                    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Calculate Summary                                                   │    │
│  │    • total_scenarios                                                │    │
│  │    • passed_scenarios                                               │    │
│  │    • failed_scenarios                                               │    │
│  │    • pass_rate = (passed / total) * 100                            │    │
│  │                                                                       │    │
│  │  Determine Overall Status                                           │    │
│  │    • all passed → status: "passed"                                  │    │
│  │    • all failed → status: "failed"                                  │    │
│  │    • mixed → status: "partial"                                      │    │
│  │                                                                       │    │
│  │  Collect Metadata                                                    │    │
│  │    • feature info                                                   │    │
│  │    • configuration used                                             │    │
│  │    • timestamps (start_time, end_time)                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     8. BROWSER CLEANUP                                        │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Graceful Shutdown (in finally block)                               │    │
│  │                                                                       │    │
│  │  Step 1: Close Page                                                 │    │
│  │    • Check: page.is_closed() ?                                      │    │
│  │    • If open: await page.close()                                    │    │
│  │    • Ignore errors if already closed                                │    │
│  │                                                                       │    │
│  │  Step 2: Close Context                                              │    │
│  │    • await context.close()                                          │    │
│  │    • Ignore errors if already closed                                │    │
│  │                                                                       │    │
│  │  Step 3: Close Browser                                              │    │
│  │    • Check: browser.is_connected() ?                                │    │
│  │    • If connected: await browser.close()                            │    │
│  │    • Ignore errors if already closed                                │    │
│  │                                                                       │    │
│  │  Step 4: Stop Playwright                                            │    │
│  │    • await playwright.stop()                                        │    │
│  │    • Ignore errors if already stopped                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     9. PERSISTENCE & NOTIFICATION                             │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Save to File System                                                 │    │
│  │    • results/{task_id}.json                                         │    │
│  │    • Complete test results with all scenarios and steps             │    │
│  │                                                                       │    │
│  │  Update Database                                                     │    │
│  │    • test_executions table                                          │    │
│  │    • Set status: completed/failed                                   │    │
│  │    • Store result JSON                                              │    │
│  │    • Update timestamps                                              │    │
│  │    • Store summary metrics:                                         │    │
│  │      - total_scenarios, passed_scenarios, failed_scenarios          │    │
│  │      - pass_rate, response_code, response_status                    │    │
│  │                                                                       │    │
│  │  Update Task Manager                                                │    │
│  │    • In-memory cache                                                │    │
│  │    • task.status = "completed"                                      │    │
│  │    • task.result = {execution_result}                               │    │
│  │    • task.updated_at = now()                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     10. CLIENT RETRIEVAL                                      │
│                                                                               │
│  GET /api/bdd/playwright/results/{task_id}                                   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  3-Tier Lookup:                                                      │    │
│  │    1. Check in-memory cache (task_manager.tasks)                    │    │
│  │    2. Load from file system (results/{task_id}.json)                │    │
│  │    3. Query database (test_executions table)                        │    │
│  │                                                                       │    │
│  │  Return:                                                             │    │
│  │  {                                                                   │    │
│  │    "success": true,                                                 │    │
│  │    "task_id": "abc-123-def",                                        │    │
│  │    "status": "completed",                                           │    │
│  │    "result": {                                                      │    │
│  │      "feature": {...},                                              │    │
│  │      "scenarios": [...],                                            │    │
│  │      "summary": {                                                   │    │
│  │        "total": 5,                                                  │    │
│  │        "passed": 4,                                                 │    │
│  │        "failed": 1,                                                 │    │
│  │        "pass_rate": "80.00%"                                        │    │
│  │      },                                                             │    │
│  │      "status": "partial",                                           │    │
│  │      "start_time": "2025-12-01T15:30:00",                          │    │
│  │      "end_time": "2025-12-01T15:32:45"                             │    │
│  │    }                                                                │    │
│  │  }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          ERROR DETECTION                                      │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │   Exception Type?          │
                    └────────────┬───────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
  ┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
  │ TargetClosed     │  │ TimeoutError   │  │ Other Playwright │
  │ Error            │  │                │  │ Error            │
  └────────┬─────────┘  └────────┬───────┘  └────────┬─────────┘
           │                     │                    │
           │                     │                    │
           ▼                     ▼                    ▼
  ┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
  │ • Log error      │  │ • Log timeout  │  │ • Log error      │
  │ • Check state:   │  │ • Check retry  │  │ • Record details │
  │   - crashed?     │  │   attempts     │  │ • Continue or    │
  │   - closed?      │  │ • Retry step   │  │   fail scenario  │
  │ • Don't retry    │  │   (if < max)   │  │                  │
  │ • Fail scenario  │  │ • Or fail      │  │                  │
  └────────┬─────────┘  └────────┬───────┘  └────────┬─────────┘
           │                     │                    │
           └─────────────────────┼────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Record Error in Results   │
                    │  • step.status = "failed" │
                    │  • step.error = error_msg  │
                    │  • scenario.status = ...   │
                    └────────────┬───────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  Cleanup & Exit Gracefully │
                    │  • Close browser resources │
                    │  • Save partial results    │
                    │  • Update status           │
                    └────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│   Client    │
│  (HTTP)     │
└──────┬──────┘
       │
       │ POST specification
       ▼
┌─────────────────────────────────────────┐
│           Flask API                      │
│  • Validate request                      │
│  • Generate task_id                      │
│  • Return 202 Accepted                   │
└──────┬──────────────────────────────────┘
       │
       │ task_id
       ▼
┌─────────────────────────────────────────┐
│       Task Manager                       │
│  • Create task record                    │
│  • Initialize status: "pending"         │
└──────┬──────────────────────────────────┘
       │
       ├─────────────────────────────────────────┐
       │                                         │
       ▼                                         ▼
┌─────────────┐                        ┌─────────────────┐
│ File System │                        │    Database     │
│  results/   │                        │ test_executions │
│  {task}.json│                        │     table       │
└──────┬──────┘                        └────────┬────────┘
       │                                        │
       │                                        │
       ▼                                        ▼
   [Persist]                              [Persist]
       │                                        │
       └────────────────┬───────────────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │   Background Execution      │
          │   (Async Thread/Process)    │
          └──────────┬──────────────────┘
                     │
                     │ specification
                     ▼
          ┌─────────────────────────────┐
          │    BDD Generator            │
          │  • Parse spec               │
          │  • Generate .feature        │
          │  • Convert to JSON          │
          └──────────┬──────────────────┘
                     │
                     │ structured_spec
                     ▼
          ┌─────────────────────────────┐
          │  Playwright Executor        │
          │  • Initialize browser       │
          │  • Execute scenarios        │
          │  • Collect results          │
          └──────────┬──────────────────┘
                     │
                     │ execution_results
                     ▼
          ┌─────────────────────────────┐
          │   Results Aggregator        │
          │  • Calculate summary        │
          │  • Format response          │
          └──────────┬──────────────────┘
                     │
                     │ final_results
                     ▼
       ┌─────────────────────────────────┐
       │         Persistence             │
       ├─────────────────┬───────────────┤
       │  File System    │   Database    │
       │  • Save JSON    │   • Update    │
       │  • Update task  │     record    │
       └────────┬────────┴───────┬───────┘
                │                │
                │                │
                ▼                ▼
       ┌─────────────┐  ┌─────────────┐
       │  Task Mgr   │  │  DB Service │
       │  • status:  │  │  • status:  │
       │   completed │  │   completed │
       │  • result   │  │  • result   │
       └──────┬──────┘  └──────┬──────┘
              │                │
              └────────┬───────┘
                       │
                       │ (Client polls)
                       ▼
              ┌─────────────────┐
              │  GET /results/  │
              │    {task_id}    │
              └────────┬────────┘
                       │
                       │ 3-tier lookup
                       ▼
              ┌─────────────────┐
              │  Return Results │
              │  • status       │
              │  • scenarios    │
              │  • summary      │
              └─────────────────┘
```

## Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         Component Interactions                          │
└────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐
  │  Flask  │──────────────┐
  │   App   │              │
  └────┬────┘              │
       │                   │
       │ uses              │ uses
       │                   │
       ▼                   ▼
  ┌─────────┐         ┌──────────────┐
  │  Task   │◄────────│  Database    │
  │ Manager │ persist │   Service    │
  └────┬────┘         └──────────────┘
       │
       │ creates/updates
       │
       ▼
  ┌──────────────────┐
  │  Background Job  │
  └────┬─────────────┘
       │
       │ executes
       │
       ▼
  ┌──────────────────┐        ┌────────────────────┐
  │  BDD Generator   │───────►│  Feature Files     │
  └────┬─────────────┘        │  (.feature)        │
       │                      └────────────────────┘
       │ produces
       │
       ▼
  ┌──────────────────┐
  │   Structured     │
  │  Specification   │
  └────┬─────────────┘
       │
       │ consumed by
       │
       ▼
  ┌──────────────────────────────────────────────────┐
  │         Playwright Executor                       │
  │  ┌──────────────┐  ┌──────────────────────────┐ │
  │  │  Event Loop  │  │   Browser Manager        │ │
  │  │   Manager    │  │  • Initialize            │ │
  │  │              │  │  • Launch                │ │
  │  └──────┬───────┘  │  • Create Context/Page   │ │
  │         │          │  • Cleanup               │ │
  │         │          └─────────┬────────────────┘ │
  │         │                    │                   │
  │         │                    │ manages           │
  │         │                    │                   │
  │         ▼                    ▼                   │
  │  ┌────────────────────────────────────────────┐ │
  │  │        Step Execution Engine               │ │
  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
  │  │  │  Given   │  │   When   │  │   Then   │ │ │
  │  │  │ Executor │  │ Executor │  │ Executor │ │ │
  │  │  └──────────┘  └──────────┘  └──────────┘ │ │
  │  └────────────────────┬───────────────────────┘ │
  │                       │                          │
  │                       │ produces                 │
  │                       │                          │
  │                       ▼                          │
  │  ┌────────────────────────────────────────────┐ │
  │  │        Results Collector                   │ │
  │  │  • Scenario results                        │ │
  │  │  • Step results                            │ │
  │  │  • Summary metrics                         │ │
  │  └────────────────────┬───────────────────────┘ │
  └───────────────────────┼─────────────────────────┘
                          │
                          │ returns
                          │
                          ▼
                   ┌──────────────┐
                   │    Results   │
                   │     JSON     │
                   └──────┬───────┘
                          │
                          │ saved by
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌───────────┐  ┌──────────┐  ┌──────────────┐
    │   Task    │  │   File   │  │   Database   │
    │  Manager  │  │  System  │  │   Service    │
    └───────────┘  └──────────┘  └──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Technology Stack                          │
├─────────────────────────────────────────────────────────────┤
│  Layer              │  Technology                           │
├─────────────────────┼───────────────────────────────────────┤
│  Web Framework      │  Flask 3.x                            │
│  ASGI/WSGI Server   │  Gunicorn (multi-worker)              │
│  Browser Automation │  Playwright 1.40.0                    │
│  Browser Engine     │  Chromium 120.0.6099.28               │
│  BDD Framework      │  Gherkin (syntax)                     │
│  Database           │  PostgreSQL (Supabase)                │
│  ORM                │  SQLAlchemy                           │
│  Async Runtime      │  asyncio, nest_asyncio                │
│  API Documentation  │  OpenAPI 3.0.3 / Swagger UI           │
│  Language           │  Python 3.11+                         │
│  Task Management    │  In-memory + File System + Database   │
│  Logging            │  Python logging module                │
└─────────────────────┴───────────────────────────────────────┘
```

## Key Features

### 1. **Async Execution**
- Non-blocking test execution
- Background task processing
- Multiple concurrent tests support

### 2. **3-Tier Result Persistence**
- In-memory cache (fastest)
- File system (survives restarts)
- Database (queryable history)

### 3. **Robust Error Handling**
- TargetClosedError detection
- Automatic retry logic
- Browser crash detection
- State validation

### 4. **Event Loop Management**
- Detects existing loops
- Creates isolated loops
- Handles Gunicorn multi-worker scenarios

### 5. **Browser Stability**
- Retry logic (up to 3 attempts)
- Automatic headless fallback
- Display detection
- Graceful cleanup

### 6. **Comprehensive Reporting**
- Per-step results
- Scenario summaries
- Test execution metrics
- Pass rate calculation
