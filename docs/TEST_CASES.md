# Test Cases Documentation

**Project**: Quetta Tea Bot
**Version**: 1.6.3
**Date**: March 1, 2026

---

## Test Case Format

Each test case follows this structure:
- **TC-ID**: Unique test case identifier
- **Category**: Test category (Smoke/Unit/Integration/E2E/Performance)
- **Feature**: Feature being tested
- **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Preconditions**: Setup required before test
- **Test Steps**: Detailed steps to execute
- **Expected Result**: What should happen
- **Actual Result**: What actually happened
- **Status**: Pass/Fail
- **Automated**: Yes/No

---

## Smoke Tests (11 Test Cases)

### TC-SM-001: Project Structure Validation
- **Category**: Smoke
- **Feature**: Project Setup
- **Priority**: P0
- **Preconditions**: Project cloned
- **Test Steps**:
  1. Check if `src/` directory exists
  2. Check if `tests/` directory exists
  3. Check if `data/` directory exists
  4. Check if `reports/` directory exists
- **Expected Result**: All directories exist
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/test_smoke.py::test_project_structure_exists`

### TC-SM-002: Source Files Validation
- **Category**: Smoke
- **Feature**: Project Setup
- **Priority**: P0
- **Preconditions**: Project cloned
- **Test Steps**:
  1. Check if `src/main_bot.py` exists
  2. Check if `src/ramadan_features.py` exists
  3. Check if `src/api_helpers.py` exists
  4. Check if `src/question_bank.py` exists
- **Expected Result**: All source files exist
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/test_smoke.py::test_source_files_exist`

### TC-SM-003: Bot Data JSON Validation
- **Category**: Smoke
- **Feature**: Data Persistence
- **Priority**: P0
- **Preconditions**: Project cloned
- **Test Steps**:
  1. Check if `data/bot_data.json` exists
  2. Validate JSON structure
  3. Check for required keys
- **Expected Result**: Valid JSON with correct structure
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/test_smoke.py::test_bot_data_json_valid`

---

## Unit Tests (4 Test Cases)

### TC-UN-001: Iftar Countdown Calculation
- **Category**: Unit
- **Feature**: Ramadan - Iftar Countdown
- **Priority**: P1
- **Preconditions**: RamadanBot instantiated with mock time
- **Test Steps**:
  1. Set fake time to 5:00 PM PKT
  2. Set Maghrib time to 6:00 PM PKT
  3. Call `get_iftar_countdown()`
  4. Verify countdown shows "1 hour"
- **Expected Result**: Countdown shows exactly 1 hour
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/features/test_iftar_countdown.py::test_iftar_countdown_calculation`

### TC-UN-002: Sehri Reminder Trigger
- **Category**: Unit
- **Feature**: Ramadan - Sehri Reminder
- **Priority**: P1
- **Preconditions**: RamadanBot with mock time at 4:45 AM
- **Test Steps**:
  1. Set fake time to 4:45 AM PKT (15 min before Fajr)
  2. Set Fajr time to 5:00 AM PKT
  3. Call `process_prayer_time_check()`
  4. Verify sehri reminder is triggered
- **Expected Result**: Sehri reminder triggered at exactly 15 min before Fajr
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/features/test_scheduler_logic.py::test_sehri_reminder_trigger`

### TC-UN-003: Iftar Reminder Trigger
- **Category**: Unit
- **Feature**: Ramadan - Iftar Reminder
- **Priority**: P1
- **Preconditions**: RamadanBot with mock time at Maghrib
- **Test Steps**:
  1. Set fake time to 6:00 PM PKT (Maghrib time)
  2. Call `process_prayer_time_check()`
  3. Verify iftar reminder is triggered
- **Expected Result**: Iftar reminder triggered at exact Maghrib time
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/features/test_scheduler_logic.py::test_iftar_reminder_trigger`

### TC-UN-004: No Event at Random Time
- **Category**: Unit
- **Feature**: Ramadan - Scheduler Logic
- **Priority**: P2
- **Preconditions**: RamadanBot with mock time at 10:00 AM
- **Test Steps**:
  1. Set fake time to 10:00 AM PKT (no prayer time)
  2. Call `process_prayer_time_check()`
  3. Verify no reminder is triggered
- **Expected Result**: No events triggered at random time
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/features/test_scheduler_logic.py::test_no_event_at_random_time`

---

## Integration Tests (22 Test Cases)

### TC-IN-001: Fetch Prayer Times - Islamabad
- **Category**: Integration
- **Feature**: Ramadan - Prayer Times API
- **Priority**: P1
- **Preconditions**: Internet connection, Aladhan API available
- **Test Steps**:
  1. Call `fetch_prayer_times("Islamabad")`
  2. Verify response contains prayer times
  3. Validate time format (HH:MM)
  4. Check all 5 prayers present (Fajr, Dhuhr, Asr, Maghrib, Isha)
- **Expected Result**: Valid prayer times returned for Islamabad
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_ramadan_integration.py::test_fetch_prayer_times_islamabad`

### TC-IN-002 to TC-IN-009: Prayer Times - All Cities
- **Category**: Integration
- **Feature**: Ramadan - Prayer Times API
- **Priority**: P1
- **Cities Tested**: Lahore, Karachi, Faisalabad, Rawalpindi, Multan, Peshawar, Quetta
- **Test Steps**: Same as TC-IN-001 for each city
- **Expected Result**: Valid prayer times for all 8 Pakistani cities
- **Status**: ✅ Pass (all 8 cities)
- **Automated**: Yes
- **Test File**: `tests/integration/test_ramadan_integration.py::test_fetch_prayer_times_all_cities`

### TC-IN-010: Fetch Random Hadith
- **Category**: Integration
- **Feature**: Ramadan - Hadith API
- **Priority**: P1
- **Preconditions**: Internet connection, Hadith API available
- **Test Steps**:
  1. Call `fetch_random_hadith()`
  2. Verify response contains hadith text
  3. Validate response structure
  4. Check for Arabic and English text
- **Expected Result**: Valid hadith returned
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_ramadan_integration.py::test_fetch_random_hadith`

### TC-IN-011: Fetch Random Ayat
- **Category**: Integration
- **Feature**: Ramadan - Ayat API
- **Priority**: P1
- **Preconditions**: Internet connection, Quran API available
- **Test Steps**:
  1. Call `fetch_random_ayat()`
  2. Verify response contains verse text
  3. Validate response structure
  4. Check for Arabic and translation
- **Expected Result**: Valid Quranic verse returned
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_ramadan_integration.py::test_fetch_random_ayat`

### TC-IN-012: Trivia Question API
- **Category**: Integration
- **Feature**: Games - Trivia
- **Priority**: P2
- **Preconditions**: Internet connection, Open Trivia DB available
- **Test Steps**:
  1. Call `fetch_trivia_question()`
  2. Verify question and options returned
  3. Validate correct answer present
  4. Check options are shuffled
- **Expected Result**: Valid trivia question with 4 options
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_api_integration.py::test_fetch_trivia_question`

### TC-IN-013: Joke API
- **Category**: Integration
- **Feature**: Entertainment - Jokes
- **Priority**: P3
- **Preconditions**: Internet connection, JokeAPI available
- **Test Steps**:
  1. Call `fetch_joke()`
  2. Verify joke text returned
  3. Validate safe-mode enabled
- **Expected Result**: Clean joke returned
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_api_integration.py::test_fetch_joke`

### TC-IN-014: Bot Data Structure
- **Category**: Integration
- **Feature**: Data Persistence
- **Priority**: P0
- **Preconditions**: bot_data.json exists
- **Test Steps**:
  1. Load bot_data.json
  2. Verify all required keys present
  3. Validate data types
  4. Check structure integrity
- **Expected Result**: Valid data structure with all keys
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_data_integration.py::test_bot_data_json_structure`

### TC-IN-015: Daily Streaks Persistence
- **Category**: Integration
- **Feature**: Progress Tracking - Daily Streaks
- **Priority**: P1
- **Preconditions**: bot_data.json writable
- **Test Steps**:
  1. Save streak data for test user
  2. Reload data from file
  3. Verify streak persisted correctly
  4. Validate data integrity
- **Expected Result**: Streak data persists across saves
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/integration/test_data_integration.py::test_daily_streaks_persistence`

---

## End-to-End Tests (17 Test Cases)

### TC-E2E-001: Complete Ramadan Setup Workflow
- **Category**: E2E
- **Feature**: Ramadan Features
- **Priority**: P1
- **Preconditions**: Bot initialized
- **Test Steps**:
  1. User sets city to Islamabad
  2. User requests prayer times
  3. User checks iftar countdown
  4. User checks sehri countdown
  5. User requests hadith
  6. User requests ayat
- **Expected Result**: All Ramadan features work in sequence
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_ramadan_workflow.py::test_complete_ramadan_setup_workflow`

### TC-E2E-002: Prayer Times City Change Workflow
- **Category**: E2E
- **Feature**: Ramadan - City Selection
- **Priority**: P1
- **Preconditions**: Bot initialized with default city
- **Test Steps**:
  1. User checks current prayer times (Islamabad)
  2. User changes city to Lahore
  3. User checks prayer times again
  4. Verify times changed
  5. User changes back to Islamabad
  6. Verify times reverted
- **Expected Result**: Prayer times update when city changes
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_ramadan_workflow.py::test_prayer_times_city_change_workflow`

### TC-E2E-003: Trivia Game Complete Workflow
- **Category**: E2E
- **Feature**: Games - Trivia
- **Priority**: P2
- **Preconditions**: Bot initialized
- **Test Steps**:
  1. User starts trivia game
  2. Bot posts question with options
  3. User submits answer
  4. Bot validates answer
  5. Bot updates score
  6. User checks leaderboard
  7. Verify score appears
- **Expected Result**: Complete trivia game flow works
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_game_workflow.py::test_trivia_game_complete_workflow`

### TC-E2E-004: Daily Streak Workflow
- **Category**: E2E
- **Feature**: Progress Tracking - Daily Rewards
- **Priority**: P1
- **Preconditions**: Bot initialized, user has no streak
- **Test Steps**:
  1. User claims daily reward (Day 1)
  2. Verify streak = 1
  3. Simulate next day
  4. User claims daily reward (Day 2)
  5. Verify streak = 2
  6. User checks streak status
  7. Verify correct display
- **Expected Result**: Streak increments daily, persists correctly
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_game_workflow.py::test_daily_streak_workflow`

### TC-E2E-005: Pet Adoption and Care Workflow
- **Category**: E2E
- **Feature**: Pet System
- **Priority**: P2
- **Preconditions**: Bot initialized, user has no pet
- **Test Steps**:
  1. User adopts pet
  2. Verify pet created with initial stats
  3. User checks pet status
  4. Verify hunger/happiness levels
  5. User feeds pet
  6. Verify stats updated
  7. User checks pet again
  8. Verify persistence
- **Expected Result**: Complete pet lifecycle works
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_data_workflow.py::test_pet_adoption_and_care_workflow`

### TC-E2E-006: Voice Channel Tracking Workflow
- **Category**: E2E
- **Feature**: Progress Tracking - VC Time
- **Priority**: P1
- **Preconditions**: Bot initialized, user in Server A
- **Test Steps**:
  1. User joins voice channel in Server A
  2. Simulate 30 minutes
  3. User checks vctime in Server A
  4. Verify shows 30 minutes
  5. User joins voice channel in Server B
  6. Simulate 1 hour
  7. User checks vctime in Server B
  8. Verify shows 1 hour (not 1.5 hours)
  9. User checks vctime in Server A again
  10. Verify still shows 30 minutes
- **Expected Result**: VC time tracked per-server correctly
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/e2e/test_data_workflow.py::test_voice_channel_tracking_workflow`

---

## Performance Tests (19 Test Cases)

### TC-PERF-001: Prayer Times Response Time
- **Category**: Performance
- **Feature**: Ramadan - Prayer Times API
- **Priority**: P1
- **Preconditions**: Internet connection
- **Test Steps**:
  1. Call `fetch_prayer_times("Islamabad")`
  2. Measure response time
  3. Verify < 2 seconds
- **Expected Result**: Response time < 2.0 seconds
- **Actual Result**: 0.444 seconds
- **Status**: ✅ Pass (Excellent)
- **Automated**: Yes
- **Test File**: `tests/performance/test_api_performance.py::test_prayer_times_response_time`

### TC-PERF-002: Hadith API Response Time
- **Category**: Performance
- **Feature**: Ramadan - Hadith API
- **Priority**: P1
- **Preconditions**: Internet connection
- **Test Steps**:
  1. Call `fetch_random_hadith()`
  2. Measure response time
  3. Verify < 2 seconds
- **Expected Result**: Response time < 2.0 seconds
- **Actual Result**: 1.136 seconds
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/performance/test_api_performance.py::test_hadith_response_time`

### TC-PERF-003: Concurrent API Calls
- **Category**: Performance
- **Feature**: API Performance
- **Priority**: P1
- **Preconditions**: Internet connection
- **Test Steps**:
  1. Make 5 concurrent API calls
  2. Measure total time
  3. Calculate average per request
  4. Verify all succeed
- **Expected Result**: All requests succeed, reasonable time
- **Actual Result**: 5/5 success in 0.227s
- **Status**: ✅ Pass (Excellent)
- **Automated**: Yes
- **Test File**: `tests/performance/test_api_performance.py::test_concurrent_api_calls`

### TC-PERF-004: Cache Performance
- **Category**: Performance
- **Feature**: Caching
- **Priority**: P1
- **Preconditions**: Cache empty
- **Test Steps**:
  1. Make API call (cache miss)
  2. Measure time
  3. Make same API call (cache hit)
  4. Measure time
  5. Compare speedup
- **Expected Result**: Cache hit significantly faster
- **Actual Result**: Miss: 0.199s, Hit: 0.000s (instant)
- **Status**: ✅ Pass (Excellent)
- **Automated**: Yes
- **Test File**: `tests/performance/test_api_performance.py::test_cache_performance`

### TC-PERF-005: Normal Load (10 Users)
- **Category**: Performance
- **Feature**: Load Testing
- **Priority**: P1
- **Preconditions**: Bot running
- **Test Steps**:
  1. Simulate 10 concurrent users
  2. Each makes API requests
  3. Measure success rate
  4. Verify > 80% success
- **Expected Result**: > 80% success rate
- **Actual Result**: 80-100% success rate
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/performance/test_load.py::test_normal_load_10_users`

### TC-PERF-006: Peak Load (20 Users)
- **Category**: Performance
- **Feature**: Load Testing
- **Priority**: P1
- **Preconditions**: Bot running
- **Test Steps**:
  1. Simulate 20 concurrent users
  2. Each makes API requests
  3. Measure success rate
  4. Verify > 50% success
- **Expected Result**: > 50% success rate
- **Actual Result**: 50-70% success rate
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/performance/test_load.py::test_peak_load_20_users`

### TC-PERF-007: Stress Test (50 Users)
- **Category**: Performance
- **Feature**: Stress Testing
- **Priority**: P2
- **Preconditions**: Bot running
- **Test Steps**:
  1. Simulate 50 concurrent users
  2. Each makes API requests
  3. Measure success rate
  4. Verify > 20% success (graceful degradation)
  5. Verify no crashes
- **Expected Result**: > 20% success, no crashes
- **Actual Result**: 20-50% success, stable
- **Status**: ✅ Pass
- **Automated**: Yes
- **Test File**: `tests/performance/test_stress.py::test_high_concurrency_stress`

### TC-PERF-008: Countdown Calculation Speed
- **Category**: Performance
- **Feature**: Ramadan - Countdown
- **Priority**: P2
- **Preconditions**: Bot initialized
- **Test Steps**:
  1. Call countdown calculation
  2. Measure execution time
  3. Verify < 0.1 seconds
- **Expected Result**: < 0.1 seconds
- **Actual Result**: 0.0003 seconds
- **Status**: ✅ Pass (Excellent)
- **Automated**: Yes
- **Test File**: `tests/performance/test_api_performance.py::test_countdown_calculation_speed`

---

## Traceability Matrix

| Requirement | Test Cases | Status |
|-------------|-----------|--------|
| REQ-001: Prayer Times | TC-IN-001 to TC-IN-009, TC-PERF-001 | ✅ Pass |
| REQ-002: Hadith/Ayat | TC-IN-010, TC-IN-011, TC-PERF-002 | ✅ Pass |
| REQ-003: Iftar Countdown | TC-UN-001, TC-E2E-001 | ✅ Pass |
| REQ-004: Sehri Reminder | TC-UN-002, TC-E2E-001 | ✅ Pass |
| REQ-005: Trivia Game | TC-IN-012, TC-E2E-003 | ✅ Pass |
| REQ-006: Daily Streaks | TC-IN-015, TC-E2E-004 | ✅ Pass |
| REQ-007: Pet System | TC-E2E-005 | ✅ Pass |
| REQ-008: VC Tracking | TC-E2E-006 | ✅ Pass |
| REQ-009: Performance | TC-PERF-001 to TC-PERF-008 | ✅ Pass |

---

## Test Execution Summary

**Total Test Cases**: 73
**Executed**: 73
**Passed**: 73
**Failed**: 0
**Blocked**: 0
**Pass Rate**: 100%

**Execution Time**: < 30 seconds
**Last Executed**: March 1, 2026
**Environment**: macOS, Python 3.12.6

---

**Document Version**: 1.0
**Last Updated**: March 1, 2026
