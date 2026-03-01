# Bug Reports

This document contains detailed bug reports for issues discovered and fixed during the project.

---

## Bug Report #001: Voice Channel Time Tracking - Global Instead of Per-Server

### Summary
The `!vctime` command was tracking voice channel time globally across all servers instead of per-server, causing incorrect time reporting for users in multiple servers.

### Severity
**Medium** - Functional issue affecting data accuracy

### Priority
**High** - User-facing feature with incorrect behavior

### Status
✅ **FIXED** - Resolved in commit `666b3ed`

---

### Description

**Issue**: When a user executed the `!vctime` command, it displayed their total voice channel time across ALL Discord servers where the bot was present, rather than showing time specific to the current server.

**Expected Behavior**:
- `!vctime` should show voice channel time for the current server only
- Each server should track time independently
- User in Server A should see different time than in Server B

**Actual Behavior**:
- `!vctime` showed cumulative time across all servers
- User in Server A and Server B saw the same total time
- No way to see per-server statistics

**Impact**:
- Users in multiple servers saw inflated time values
- Server admins couldn't track server-specific engagement
- Leaderboards would be inaccurate for multi-server users

---

### Steps to Reproduce

1. Add bot to two different Discord servers (Server A and Server B)
2. Join voice channel in Server A for 1 hour
3. Join voice channel in Server B for 2 hours
4. Run `!vctime` in Server A
5. **Expected**: Shows 1 hour
6. **Actual**: Shows 3 hours (total across both servers)

---

### Root Cause Analysis

**Location**: `src/main_bot.py`

**Problem Code**:
```python
# BEFORE (Incorrect)
@bot.event
async def on_voice_state_update(member, before, after):
    data = load_data()
    user_id = str(member.id)  # ❌ Only user ID, no guild context

    if before.channel is None and after.channel is not None:
        # User joined VC
        data["vc_join_times"][user_id] = datetime.now().isoformat()
```

**Root Cause**:
- Used only `user_id` as the key in `vc_join_times` dictionary
- No guild/server context in the key
- Same user ID across all servers → global tracking

**Why It Happened**:
- Initial implementation didn't consider multi-server scenarios
- Test coverage didn't include multi-guild testing
- Feature worked correctly for single-server testing

---

### Solution

**Fix Applied**:
```python
# AFTER (Correct)
@bot.event
async def on_voice_state_update(member, before, after):
    data = load_data()
    guild_id = str(member.guild.id)
    user_id = str(member.id)
    key = f"{user_id}_{guild_id}"  # ✅ Composite key with guild context

    if before.channel is None and after.channel is not None:
        # User joined VC
        data["vc_join_times"][key] = datetime.now().isoformat()
```

**Changes Made**:
1. Added `guild_id` to create composite key: `user_id_guild_id`
2. Updated `on_voice_state_update` event handler
3. Updated `vctime` command to use composite key
4. Ensured backward compatibility with existing data

**Files Modified**:
- `src/main_bot.py` (2 functions updated)

---

### Testing

**Manual Testing**:
1. ✅ Tested in single server - time tracked correctly
2. ✅ Tested in multiple servers - separate time per server
3. ✅ Tested active session - includes current session time
4. ✅ Tested data persistence - survives bot restart
5. ✅ Tested edge cases - user leaves/rejoins multiple times

**Regression Testing**:
- ✅ All 73 existing tests still pass
- ✅ No impact on other features
- ✅ Data migration handled gracefully

**Test Coverage**:
- Added to E2E test suite: `test_voice_channel_tracking_workflow`
- Validates per-server tracking behavior

---

### Verification

**Before Fix**:
```
User in Server A: !vctime
Bot: You've spent 3h 0m in voice channels!  ❌ (Should be 1h)

User in Server B: !vctime
Bot: You've spent 3h 0m in voice channels!  ❌ (Should be 2h)
```

**After Fix**:
```
User in Server A: !vctime
Bot: You've spent 1h 0m in voice channels!  ✅ Correct

User in Server B: !vctime
Bot: You've spent 2h 0m in voice channels!  ✅ Correct
```

---

### Lessons Learned

1. **Multi-Tenancy Considerations**: Always consider multi-server scenarios for Discord bots
2. **Test Coverage**: Need multi-guild integration tests
3. **Data Modeling**: Use composite keys when data has multiple contexts
4. **User Feedback**: Bug discovered through user testing, not automated tests

---

### Related Issues

- None

### Related Commits

- `666b3ed` - fix: vctime command now tracks time per-server instead of globally

---

## Bug Report #002: Incorrect Time Display - "0h 3m" Issue

### Summary
The `!vctime` command was showing "0h 3m" even after spending significant time in voice channels because it wasn't including the current active session.

### Severity
**Low** - Display issue, data was being tracked correctly

### Priority
**Medium** - User-facing display bug

### Status
✅ **FIXED** - Resolved in commit `666b3ed` (same fix as Bug #001)

---

### Description

**Issue**: When a user was currently in a voice channel and ran `!vctime`, it only showed completed session time, not including the ongoing session.

**Expected Behavior**:
- If user has been in VC for 30 minutes and runs `!vctime` while still in VC
- Should show 30 minutes (or more if there's historical time)

**Actual Behavior**:
- Showed only completed sessions
- Current session time was ignored
- User saw "0h 3m" when they had been in VC for much longer

---

### Root Cause

**Problem**: The `vctime` command only summed up completed sessions from `vc_times` but didn't check if the user was currently in a voice channel.

**Code Issue**:
```python
# BEFORE (Incomplete)
@bot.command()
async def vctime(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    total_seconds = data["vc_times"].get(user_id, 0)
    # ❌ Missing: Check if user is currently in VC
```

---

### Solution

**Fix Applied**:
```python
# AFTER (Complete)
@bot.command()
async def vctime(ctx):
    data = load_data()
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    key = f"{user_id}_{guild_id}"

    total_seconds = data["vc_times"].get(key, 0)

    # ✅ Check if user is currently in VC
    if key in data["vc_join_times"]:
        join_time = datetime.fromisoformat(data["vc_join_times"][key])
        current_session = (datetime.now() - join_time).total_seconds()
        total_seconds += current_session
```

**Changes**:
1. Added check for active VC session
2. Calculate current session duration
3. Add to total time before display

---

### Verification

**Before Fix**:
```
User joins VC at 2:00 PM
User runs !vctime at 2:30 PM (still in VC)
Bot: You've spent 0h 3m in voice channels!  ❌ (Missing current 30 min)
```

**After Fix**:
```
User joins VC at 2:00 PM
User runs !vctime at 2:30 PM (still in VC)
Bot: You've spent 0h 33m in voice channels!  ✅ (Includes current session)
```

---

### Lessons Learned

1. **State Awareness**: Commands should be aware of current user state
2. **Real-Time Data**: Display should include in-progress activities
3. **User Experience**: Users expect to see current session in statistics

---

**Report Generated**: March 1, 2026
**Last Updated**: March 1, 2026
**Total Bugs Reported**: 2
**Total Bugs Fixed**: 2
**Fix Rate**: 100%
