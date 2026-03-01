# FitFinder - Architecture & UML Documentation

## 1️⃣ Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ENTITY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────┐                                         │
│  │           User (Entity)        │                                         │
│  ├────────────────────────────────┤                                         │
│  │ - id: Long                     │                                         │
│  │ - userid: String <<unique>>    │                                         │
│  │ - password: String             │                                         │
│  │ - createdAt: LocalDateTime     │                                         │
│  ├────────────────────────────────┤                                         │
│  │ + onCreate()                   │                                         │
│  └────────────────────────────────┘                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        DTO/REQUEST LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────┐     ┌────────────────────────────────┐  │
│  │   TryOnRequest                 │     │   TryOnComboRequest            │  │
│  ├────────────────────────────────┤     ├────────────────────────────────┤  │
│  │ - humanImage: MultipartFile     │     │ - humanImage: MultipartFile   │  │
│  │ - clothImage: MultipartFile     │     │ - clothImage: MultipartFile   │  │
│  │ - garmentType: String           │     │ - bottomClothImage: MultiFile │  │
│  │                                 │     │ - garmentType: String         │  │
│  └────────────────────────────────┘     └────────────────────────────────┘  │
│                                                                             │
│  ┌────────────────────────────────────────┐                                 │
│  │   ApiResponse<T>                       │                                 │
│  ├────────────────────────────────────────┤                                 │
│  │ - success: Boolean                     │                                 │
│  │ - message: String                      │                                 │
│  │ - data: T                              │                                 │
│  │ - error: String                        │                                 │
│  │ - note: String                         │                                 │
│  ├────────────────────────────────────────┤                                 │
│  │ + <static> success(data: T): ApiResp   │                                 │
│  │ + <static> error(error: String): ApiResp│                                │
│  └────────────────────────────────────────┘                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPOSITORY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────┐                                  │
│  │   UserRepository                        │                                  │
│  │   <<interface>> extends JpaRepository   │                                  │
│  ├────────────────────────────────────────┤                                  │
│  │ + findByUserid(userid): Optional<User> │                                  │
│  │ + existsByUserid(userid): boolean      │                                  │
│  │ + save(user): User                     │                                  │
│  │ + findById(id): Optional<User>         │                                  │
│  │ + delete(user): void                   │                                  │
│  └────────────────────────────────────────┘                                  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │   UserService                         │  │  VirtualTryOnService         │ │
│  ├──────────────────────────────────────┤  ├──────────────────────────────┤ │
│  │ - userRepository: UserRepository     │  │ - tryOnService               │ │
│  │ - passwordEncoder: PasswordEncoder   │  │ - httpClient: OkHttpClient   │ │
│  │                                      │  │ - gson: Gson                 │ │
│  ├──────────────────────────────────────┤  ├──────────────────────────────┤ │
│  │ + authenticate(u,p): Optional<User>  │  │ + processSingleTryOn()       │ │
│  │ + registerUser(u,p): User            │  │ + processComboTryOn()        │ │
│  │ + getUserByUserid(u): Optional<User> │  │ + processMiragicSingle()     │ │
│  │                                      │  │ + processMiragicCombo()      │ │
│  │                                      │  │ + pollMiragicJob()           │ │
│  │                                      │  │ + processLocalSingleTryOn()  │ │
│  │                                      │  │ + processLocalComboTryOn()   │ │
│  │                                      │  │                              │ │
│  └──────────────────────────────────────┘  └──────────────────────────────┘ │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTROLLER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────┐  ┌──────────────────────────┐              │
│  │  AuthController             │  │  TryOnController         │              │
│  ├─────────────────────────────┤  ├──────────────────────────┤              │
│  │ - userService              │  │ - tryOnService           │              │
│  ├─────────────────────────────┤  ├──────────────────────────┤              │
│  │ + login(): ResponseEntity   │  │ + trySingle(): ResponseEnt│              │
│  │ + logout(): ResponseEntity  │  │ + tryCombo(): ResponseEntity           │
│  │ + authStatus(): ResponseEnt │  │ - saveTempFile()         │              │
│  │ + register(): ResponseEntity│  │ - cleanupFile()          │              │
│  │                             │  │                          │              │
│  └─────────────────────────────┘  └──────────────────────────┘              │
│                                                                               │
│  ┌────────────────────────────────┐                                          │
│  │  HealthController              │                                          │
│  ├────────────────────────────────┤                                          │
│  │ + health(): ResponseEntity     │                                          │
│  └────────────────────────────────┘                                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        UTILITY LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────┐                          │
│  │   ImageProcessingUtil                          │                          │
│  ├────────────────────────────────────────────────┤                          │
│  │ + <static> createSingleTryOnImage()            │                          │
│  │ + <static> createComboTryOnImage()             │                          │
│  │ - <static> resizeImage()                       │                          │
│  └────────────────────────────────────────────────┘                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Sequence Diagrams

### User Login Sequence

```
┌─────────┐        ┌──────────────┐        ┌─────────────┐        ┌──────────┐
│  Client │        │ AuthController│        │ UserService │        │ Database │
└────┬────┘        └──────┬───────┘        └──────┬──────┘        └────┬─────┘
     │                    │                       │                    │
     │ POST /login        │                       │                    │
     │───────────────────>│                       │                    │
     │                    │                       │                    │
     │                    │ authenticate()        │                    │
     │                    │──────────────────────>│                    │
     │                    │                       │ findByUserid()     │
     │                    │                       │───────────────────>│
     │                    │                       │         User       │
     │                    │                       │<───────────────────│
     │                    │                       │                    │
     │                    │                       │ BCrypt.verify()    │
     │                    │                       │ (password)         │
     │                    │                       │                    │
     │                    │                <─────┴────────>          │
     │                    │               Password Match?             │
     │                    │                       │                    │
     │                    │    Optional<User>     │                    │
     │                    │<──────────────────────│                    │
     │                    │                       │                    │
     │   session.setAttribute("user")             │                    │
     │<───────── 200 OK with success ────────────│                    │
     │                    │                       │                    │
```

### Virtual Try-On Single Processing Sequence

```
┌─────────┐        ┌──────────────┐        ┌───────────────────┐        ┌─────────────┐
│  Client │        │ TryOnCtrlr   │        │ TryOnService      │        │ Miragic API │
└────┬────┘        └──────┬───────┘        └─────────┬─────────┘        └────┬────────┘
     │                    │                         │                        │
     │ POST /api/tryon/   │                         │                        │
     │ single             │                         │                        │
     │───────────────────>│                         │                        │
     │ [humanImage]       │                         │                        │
     │ [clothImage]       │                         │                        │
     │                    │ saveTempFile()          │                        │
     │                    │─────────────<─────────>│ File System             │
     │                    │                         │                        │
     │                    │ processSingleTryOn()    │                        │
     │                    │────────────────────────>│                        │
     │                    │                         │                        │
     │                    │                         │ Check API Key          │
     │                    │                         │─────────────<─────────|
     │                    │                         │                        │
     │                    │                         │ if (API_KEY exists)    │
     │                    │                         │                        │
     │                    │                         │ POST Create VTO Job    │
     │                    │                         │───────────────────────>│
     │                    │                         │                        │
     │                    │                         │  {jobId, status}       │
     │                    │                         │<───────────────────────│
     │                    │                         │                        │
     │                    │                         │ pollMiragicJob()       │
     │                    │                         │───────────────────────>│
     │                    │                         │ (polling loop)         │
     │                    │                         │<───────────────────────│
     │                    │                         │  {status: COMPLETED}   │
     │                    │                         │                        │
     │                    │ ApiResponse<Object>     │                        │
     │                    │<────────────────────────│                        │
     │                    │                         │                        │
     │    cleanupFile()   │                         │                        │
     │ (remove tempfiles) |                         │                        │
     │                    │────────<────────────────|                        │
     │                    │                         │                        │
     │   200 OK + Result  │                         │                        │
     │<───────────────────│                         │                        │
     │                    │                         │                        │
```

### Local Fallback Try-On Sequence

```
┌─────────┐        ┌──────────────┐        ┌───────────────────┐        ┌──────────────┐
│  Client │        │ TryOnCtrlr   │        │ TryOnService      │        │   Image Utils  │
└────┬────┘        └──────┬───────┘        └─────────┬─────────┘        └────┬─────────┘
     │                    │                         │                        │
     │ POST /api/tryon/   │                         │                        │
     │ single             │                         │                        │
     │───────────────────>│                         │                        │
     │                    │                         │                        │
     │                    │ saveTempFile()          │                        │
     │                    │────────────────────────>│ File System            │
     │                    │                         │                        │
     │                    │ processSingleTryOn()    │                        │
     │                    │────────────────────────>│                        │
     │                    │                         │                        │
     │                    │                         │ No API Key             │
     │                    │                         │ Local Fallback!        │
     │                    │                         │                        │
     │                    │                         │ createSingleTryOn()    │
     │                    │                         │───────────────────────>│
     │                    │                         │                        │
     │                    │                         │ Read human & cloth     │
     │                    │                         │ Resize cloth           │
     │                    │                         │ Overlay on human       │
     │                    │                         │ Save PNG               │
     │                    │                         │                        │
     │                    │                         │ Output Path            │
     │                    │                         │<───────────────────────│
     │                    │ ApiResponse             │                        │
     │                    │<────────────────────────│                        │
     │                    │                         │                        │
     │    cleanupFile()   │                         │                        │
     │                    │────────<────────────────|                        │
     │                    │                         │                        │
     │   200 OK + Result  │                         │                        │
     │<───────────────────│                         │                        │
```

---

## 3️⃣ Use Case Diagram

```
                          ┌─────────────────────────────┐
                          │      FitFinder System       │
                          └─────────────────────────────┘
                                        
        ┌─────────────────────────────────────────────────────────┐
        │                                                         │
        │                   Use Cases                             │
        │                                                         │
        │    ┌─────────────────────────────────────┐              │
        │    │   Manage User Authentication        │              │
        │    │  ┌───────────────────────────────┐  │              │
        │    │  │ ○ Login                       │  │              │
        │    │  │ ○ Logout                      │  │              │
        │    │  │ ○ Register                    │  │              │
        │    │  │ ○ Check Auth Status           │  │              │
        │    │  └───────────────────────────────┘  │              │
        │    └─────────────────────────────────────┘              │
        │                                                         │
        │    ┌─────────────────────────────────────┐              │
        │    │   Virtual Try-On Operations         │              │
        │    │  ┌───────────────────────────────┐  │              │
        │    │  │ ○ Single Garment Try-On       │  │              │
        │    │  │ ○ Combo Garment Try-On        │  │              │
        │    │  │ ○ Upload Images               │  │              │
        │    │  │ ○ Process with Miragic AI     │  │              │
        │    │  │ ○ Local Fallback Processing   │  │              │
        │    │  │ ○ Poll Job Status             │  │              │
        │    │  │ ○ Download Result Images      │  │              │
        │    │  └───────────────────yo
                           Start
                             │
                             ▼
                    ┌────────────────┐
                    │ User submits   │
                    │ credentials    │
                    └────────┬───────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Validate input      │
                    │ (userid, password)  │
                    └────────┬────────────┘
                             │
                    ┌────────▼─────────┐
                    │ Valid input?     │
                    └────┬──────────┬──┘
                         │ No       │ Yes
                         │          │
                    ┌────▼───┐      └──────┬──────────┐
                    │ Return │             ▼          │
                    │ Error  │    ┌──────────────────┐│
                    └────┬───┘    │ Query database   ││
                         │        │ for user         ││
                         │        └────────┬─────────┘│
                         │                 │          │
                         │        ┌────────▼──────┐   │
                         │        │ User found?   │   │
                         │        └────┬─────┬────┘   │
                         │             │ No  │ Yes    │
                         │        ┌────▼─┐   │        │
                         │        │Return│   │        │
                         │        │Error │   │        │
                         │        └────┬─┘   │        │
                         │             │     │        │
                         │             │     ▼        │
                         │             │  ┌──────────────────────┐
                         │             │  │ BCrypt   verify      │
                         │             │  │ password   hash      │
                         │             │  └────────┬─────────────┘
                         │             │            │
                         │             │  ┌────────▼──────┐
                         │             │  │ Password      │
                         │             │  │ correct?      │
                         │             │  └────┬──────┬───┘
                         │             │       │ No   │   Yes
                         │             │       │      │
                    ┌────▼─────┬────── ─┴┐  ┌──▼──┐   │
                    │           │        │  │Ok   │   │
                    │ Return    │ Return │  │     │   │
                    │ Error     │ Error  │  └──┬ ─┘   │
                    │           │        │     │      │
                    └─────┬─────┴───┬────┘     │      │
                          │         │          │      │
                          │    ┌────▼──────────▼──┐   │
                          │    │ Create HTTP     │   │
                          │    │ Session         │   │
                          │    └────┬────────────┘   │
                          │         │                 │
                          │    ┌────▼──────────────┐  │
                          │    │ Set userid in    │  │
                          │    │ session          │  │
                          │    └────┬─────────────┘  │
                          │         │                 │
                          └─────────┼─────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │ Return success   │
                          │ with JWT token   │
                          └────────┬─────────┘
                                   │
                                   ▼
                                 End
``

--

## 5️⃣ State Diagram - Try-On Job Processing

``
┌────────────────────────────────────────────────────────────────────────────┐
│                        TRY-ON JOB LIFECYCLE                                │
└────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────┐
                            │ CREATED │
                            └────┬────┘
                                 │
                                 │ upload images
                                 ▼
                         ┌──────────────────┐
                         │   PROCESSING     │
                         │  (Miragic API    │
                         │   or Local)      │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
                    │ (poll)      │ (local)      │
                    ▼             ▼              │
            ┌────────────┐  ┌──────────┐         │
            │  POLLED    │  │  PROCESSED         │
            │  (timeout? │  │               │    │
            │   60s)     │  │               │    │
            └─────┬──────┘  └────────┬──────┘    │
                  │                   │          │
     ┌────────────┼───────────────────┼────────────┐  │
     │            │                   │            │  │
     │ TIMEOUT    │ SUCCESS           │ FAILURE    │  │
     │            │                   │            │  │
     ▼            ▼                   ▼            ▼  │
   ┌────┐  ┌──────────────┐  ┌────────────┐  ┌──────┐│
   │FAIL│  │ COMPLETED    │  │ FAILED     │  │ERROR ││
   └─┬──┘  │              │  │            │  └──┬───┘│
     │     │ Result image │  │ Error msg  │     │    │
     │     │ available    │  │            │     │    │
     │     └──────┬───────┘  └────┬───────┘     │    │
     │            │                │            │    │
     └────────────┼────────────────┼────────────┼────┘
                  │                │            │
                  └────────┬───────┴────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  RETURNED   │
                    │  TO CLIENT  │
                    └─────┬───────┘
                          │
                          ▼
                       [END]
```

---

## 6️⃣ Component Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        FITFINDER SYSTEM COMPONENTS                           │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────┐
  │    FitFinder Web Application    │
  │    (Spring Boot on Port 5000)   │
  └────────────┬────────────────────┘
               │
      ┌────────┴────────────────────┬──────────────┬──────────┐
      │                             │              │          │
      ▼                             ▼              ▼          ▼
┌────────────┐              ┌────────────┐   ┌──────────┐  ┌────────┐
│ Controller │              │   Service  │   │Repository│  │ Config │
│  Layer     │              │   Layer    │   │  Layer   │  │        │
├────────────┤              ├────────────┤   ├──────────┤  ├────────┤
│ • Auth     │              │ • User     │   │ • User   │  │ • Sec. │
│ • TryOn    │              │ • VirtualTry   │ • DB     │  │ • DB   │
│ • Health   │              │   On       │   │          │  │        │
└─────┬──────┘              └─────┬──────┘   └────┬─────┘  └────────┘
      │                           │               │
      │                           │               │
      │                    ┌──── ─▼───────────────▼─────┐
      │                    │                            │
      │                    │    ┌──────────────┐        │
      │                    └────│  Database    │        │
      │                         │  (H2/PgSQL)  │        │
      │                         └──────────────┘        │
      │                                                 │
      ▼                                                 ▼
┌──────────────────┐                          ┌────────────────┐
│  Static Pages    │                          │  Utilities     │
│  (HTML/CSS/JS)   │                          │  • Image Proc  │
│                  │                          │  • API Utils   │
│ • index.html     │                          └────────────────┘
│ • login_page.html│
│ • dashboard.html │                          ┌────────────────┐
│ • about.html     │                          │ External APIs  │
│ • contact.html   │                          │ • Miragic AI   │
│ • tryon.html     │                          │   (Optional)   │
└──────────────────┘                          └────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                 │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────┐
  │      Miragic AI Virtual Try-On API                 │
  │      (Optional - If MIRAGIC_API_KEY set)           │
  │                                                    │
  │  • Single Garment Try-On                           │
  │  • Combo Garment Try-On                            │
  │  • Job Status Polling                              │
  │                                                    │
  │  Base URL: https://backend.miragic.ai              │
  │  Authentication: X-API-Key Header                  │
  └────────────────────────────────────────────────────┘
```

---

## 6️⃣.1️⃣ Entity-Relationship Diagram (ER Diagram)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FITFINDER DATABASE SCHEMA (ER MODEL)                      │
└──────────────────────────────────────────────────────────────────────────────┘


                         ┌─────────────────────────────┐
                         │         USERS TABLE         │
                         ├─────────────────────────────┤
                         │ PK │ id (BIGINT)            │
                         │    │ ├─ AUTO_INCREMENT      │
                         │    │ ├─ PRIMARY KEY         │
                         │    │ └─ NOT NULL            │
                         ├─────────────────────────────┤
                         │ UQ │ userid (VARCHAR(100))  │
                         │    │ ├─ UNIQUE              │
                         │    │ ├─ NOT NULL            │
                         │    │ └─ Username/LoginID    │
                         ├─────────────────────────────┤
                         │    │ password (VARCHAR)     │
                         │    │ ├─ NOT NULL            │
                         │    │ ├─ BCrypt Hashed       │
                         │    │ └─ For authentication  │
                         ├─────────────────────────────┤
                         │    │ created_at             │
                         │    │ (TIMESTAMP)            │
                         │    │ ├─ NOT NULL            │
                         │    │ ├─ DEFAULT CURRENT     │
                         │    │ └─ Record creation     │
                         ├─────────────────────────────┤
                         │    │ INDEX: idx_userid      │
                         │    │  (for fast lookups)    │
                         └─────────────────────────────┘
                                    │
                                    │ 1:N Relationship
                                    │ (implicit through sessions)
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
                    ▼                                ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │  SESSION STORAGE     │        │   FILE STORAGE       │
        │  (HTTP Sessions)     │        │   (Virtual Try-On)   │
        ├──────────────────────┤        ├──────────────────────┤
        │ • Session ID         │        │ • /tmp (Temp Files)  │
        │ • User ID (FK)       │        │ • /generated_outfits │
        │ • Created/Updated    │        │ • Output Images      │
        │ • Expiration Time    │        │ • Log Files          │
        └──────────────────────┘        └──────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                    RELATED DATA STRUCTURES (In Memory)                       │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │  User (JPA Entity)   │
    ├──────────────────────┤
    │ @Entity              │
    │ @Table("users")      │
    │                      │
    │ Long id              │
    │ String userid        │
    │ String password      │
    │ LocalDateTime        │
    │  createdAt           │
    └──────────────────────┘
              │
              │ Used By
              │
    ┌─────────┴──────────┬──────────────────┬──────────────────┐
    │                    │                  │                  │
    ▼                    ▼                  ▼                  ▼
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│UserService    │TryOnRequest │    │TryOnCombo   │    │ApiResponse<T>│
├──────────┤    ├─────────────┤    │Request      │    ├──────────────┤
│ Service  │    │ DTO         │    ├─────────────┤    │ Response DTO │
│          │    │             │    │ DTO         │    │              │
│Manages:  │    │ • humanImage│    │             │    │ • success    │
│          │    │ • clothImage│    │ • humanImage│    │ • message    │
│• Auth    │    │ • garment   │    │ • clothImage│    │ • data<T>    │
│• CRUD    │    │   Type      │    │ • bottom    │    │ • error      │
│• Validat.│    │             │    │   ClothImage│    │ • note       │
└──────────┘    └─────────────┘    │ • garment   │    └──────────────┘
                                   │   Type      │
                                   └─────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                    RELATIONAL MAPPING OVERVIEW                               │
└──────────────────────────────────────────────────────────────────────────────┘

    Database Layer          ORM Layer           API Layer
    ──────────────          ─────────           ─────────

    users table  ────────┐
                         │
                         ├──→ User Entity ────────────────┐
                         │    (JPA Mapping)               │
                         │                                │
    sessions/tokens  ────┘                                │
                                                        ▼
                                                   Service/Controller
                                                        │
                                                        ├────────────────┐
                                                        │                │
                                                   Request DTO       Response
                                                   (Incoming)        ApiResponse


┌──────────────────────────────────────────────────────────────────────────────┐
│                    CARDINALITY & CONSTRAINTS                                 │
└──────────────────────────────────────────────────────────────────────────────┘

User - Session Relationship:
  • Cardinality: 1:Many (1 User → Many Sessions)
  • Constraint: ON DELETE CASCADE
  • Duration: Session expires after inactivity

User - Try-On Operations:
  • Cardinality: 1:Many (1 User → Multiple Try-Ons)
  • Data: Stored as temporary files (not persisted in DB)
  • Cleanup: Auto-delete after processing

Indexes for Performance:
  • PRIMARY: id (User PK)
  • UNIQUE: userid (Fast login lookup)
  • Regular: created_at (For date range queries)

Constraints:
  • NOT NULL: id, userid, password, created_at
  • UNIQUE: userid (No duplicate users)
  • DEFAULT: created_at = CURRENT_TIMESTAMP
```

---

## 7️⃣ Deployment Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                             │
└──────────────────────────────────────────────────────────────────────┘

Development Machine (Windows)
│
├── mvn clean package
│
└── Create JAR: fitfinder-java-1.0.0.jar


Deployment Options:

Option 1: Standalone JAR
┌────────────────────────────────────────┐
│ java -jar fitfinder-java-1.0.0.jar     │
│                                        │
│ Embedded Tomcat (Port 5000)            │
│ Built-in H2 Database                   │
│ Suitable for: Small to Medium Scale    │
└────────────────────────────────────────┘

Option 2: Docker Container
┌──────────────────────────────────────────────────────────────┐
│ FROM openjdk:17-slim                                         │
│ COPY fitfinder-java-1.0.0.jar app.jar                        │
│ EXPOSE 5000                                                  │
│ ENTRYPOINT ["java", "-jar", "app.jar"]                       │
│                                                              │
│ docker build -t fitfinder:latest .                           │
│ docker run -p 5000:5000 fitfinder:latest                     │
│                                                              │
│ Suitable for: Cloud Deployment (AWS, Azure, GCP)             │
└──────────────────────────────────────────────────────────────┘

Option 3: Docker Compose Stack
┌──────────────────────────────────────────────────────────────┐
│ Services:                                                    │
│ • fitfinder-app (Spring Boot)                                │
│ • postgres (Database)                                        │
│ • nginx (Reverse Proxy - Optional)                           │
│                                                              │
│ docker-compose up -d                                         │
│                                                              │
│ Suitable for: Full-stack deployment with database            │
└──────────────────────────────────────────────────────────────┘

Option 4: Kubernetes Deployment
┌──────────────────────────────────────────────────────────────┐
│ • Pod: FitFinder Application                                 │
│ • Service: LoadBalancer (Port 5000)                          │
│ • PersistentVolume: Database Storage                         │
│ • ConfigMap: Environment Configuration                       │
│ • Secret: API Keys (MIRAGIC_API_KEY)                         │
│                                                              │
│ kubectl apply -f deployment.yaml                             │
│                                                              │
│ Suitable for: Enterprise/Scalable Deployment                 │
└──────────────────────────────────────────────────────────────┘


Runtime Environment:
┌────────────────────────────────────┐
│        Database                    │
│ ┌───────────────────────────────┐  │
│ │ H2 (Development)              │  │
│ │ PostgreSQL (Production)       │  │
│ │                               │  │
│ │ Tables:                       │  │
│ │ • users (jwt_token, password) │  │
│ └───────────────────────────────┘  │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│    File System                     │
│ ┌───────────────────────────────┐  │
│ │ /tmp - Temporary images       │  │
│ │ /generated_outfits - Results  │  │
│ │ /logs - Application logs      │  │
│ └───────────────────────────────┘  │
└────────────────────────────────────┘
```

---

## 📊 Architecture Summary

**Architectural Pattern**: **3-Tier Architecture** (Layered)
- **Presentation Tier**: REST Controllers + Static HTML
- **Business Tier**: Services (UserService, VirtualTryOnService)
- **Data Tier**: Repository + Database (H2/PostgreSQL)

**Design Patterns Used**:
1. **MVC Pattern**: Controllers → Services → Repository
2. **DTO Pattern**: Request/Response objects
3. **Factory Pattern**: ApiResponse builder
4. **Strategy Pattern**: Local fallback vs. Miragic API
5. **Singleton Pattern**: Service beans
6. **Template Method**: Image processing utilities

**Key Principles**:
- ✅ **Separation of Concerns**: Each layer has specific responsibility
- ✅ **Dependency Injection**: Spring manages all bean dependencies
- ✅ **Security**: BCrypt password hashing, session management
- ✅ **Scalability**: Stateless REST APIs, connection pooling
- ✅ **Error Handling**: Standardized ApiResponse wrapper
- ✅ **Logging**: SLF4J logging throughout

