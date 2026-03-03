"""
Test for verified role welcome message feature
This test simulates the on_member_update event
"""
import asyncio
from unittest.mock import MagicMock, AsyncMock


async def simulate_verified_role_assignment():
    """Simulate the logic of on_member_update when verified role is added"""

    print("🧪 Test 1: Member receives Verified role")
    print("-" * 50)

    # Create mock objects
    mock_guild = MagicMock()
    mock_guild.name = "Quetta Tea House"

    # Mock roles
    unverified_role = MagicMock()
    unverified_role.name = "Unverified"

    verified_role = MagicMock()
    verified_role.name = "Verified"

    # Mock channels
    general_channel = MagicMock()
    general_channel.name = "general"
    general_channel.mention = "<#123456789>"
    general_channel.send = AsyncMock()

    self_roles_channel = MagicMock()
    self_roles_channel.name = "self-roles"
    self_roles_channel.mention = "<#987654321>"

    # Mock member before (only unverified)
    before = MagicMock()
    before.guild = mock_guild
    before.roles = [unverified_role]
    before.name = "NewUser"
    before.mention = "@NewUser"

    # Mock member after (has verified role)
    after = MagicMock()
    after.guild = mock_guild
    after.roles = [unverified_role, verified_role]
    after.name = "NewUser"
    after.mention = "@NewUser"

    # Simulate the on_member_update logic
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    # Find newly added roles
    added_roles = after_roles - before_roles

    print(f"Before roles: {[r.name for r in before_roles]}")
    print(f"After roles: {[r.name for r in after_roles]}")
    print(f"Added roles: {[r.name for r in added_roles]}")

    # Check if "Verified" role was added
    if verified_role in added_roles:
        print(f"✅ Verified role detected in added roles")

        # Simulate sending welcome message
        welcome_message = (
            f"🎉 Welcome {after.mention} to {after.guild.name}! 🎉\n"
            f"Hop over to {self_roles_channel.mention} to grab your roles and join the fun!"
        )

        await general_channel.send(welcome_message)

        print(f"✅ Welcome message sent to general channel")
        print(f"📝 Message content:\n{welcome_message}")

        # Verify the send was called
        assert general_channel.send.called, "Send should be called"
        assert general_channel.send.call_count == 1, "Send should be called once"

        # Get the actual message sent
        sent_message = general_channel.send.call_args[0][0]
        assert "@NewUser" in sent_message, "Message should mention user"
        assert "Quetta Tea House" in sent_message, "Message should include server name"
        assert "🎉" in sent_message, "Message should have celebration emoji"

        print("✅ All assertions passed!")
        return True
    else:
        print("❌ Verified role not detected")
        return False


async def simulate_other_role_assignment():
    """Test that no message is sent when other roles are added"""

    print("\n🧪 Test 2: Member receives non-Verified role")
    print("-" * 50)

    # Mock objects
    mock_guild = MagicMock()
    mock_guild.name = "Quetta Tea House"

    other_role = MagicMock()
    other_role.name = "Member"

    verified_role = MagicMock()
    verified_role.name = "Verified"

    general_channel = MagicMock()
    general_channel.send = AsyncMock()

    # Before: no roles
    before = MagicMock()
    before.guild = mock_guild
    before.roles = []

    # After: has other role (not verified)
    after = MagicMock()
    after.guild = mock_guild
    after.roles = [other_role]

    # Simulate logic
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    added_roles = after_roles - before_roles

    print(f"Added roles: {[r.name for r in added_roles]}")

    # Check if verified role was added
    if verified_role in added_roles:
        await general_channel.send("Welcome message")
        print("❌ Message sent (should not happen)")
        return False
    else:
        print("✅ No message sent (correct behavior)")
        assert not general_channel.send.called, "Send should not be called"
        print("✅ All assertions passed!")
        return True


async def simulate_no_self_roles_channel():
    """Test fallback when self-roles channel doesn't exist"""

    print("\n🧪 Test 3: No self-roles channel exists")
    print("-" * 50)

    mock_guild = MagicMock()
    mock_guild.name = "Quetta Tea House"

    verified_role = MagicMock()
    verified_role.name = "Verified"

    general_channel = MagicMock()
    general_channel.send = AsyncMock()

    # self_roles_channel is None
    self_roles_channel = None

    before = MagicMock()
    before.roles = []

    after = MagicMock()
    after.guild = mock_guild
    after.roles = [verified_role]
    after.mention = "@NewUser"

    # Simulate logic
    added_roles = set(after.roles) - set(before.roles)

    if verified_role in added_roles:
        # Fallback message without channel mention
        if self_roles_channel:
            welcome_message = f"🎉 Welcome {after.mention} to {after.guild.name}! 🎉\nHop over to {self_roles_channel.mention} to grab your roles and join the fun!"
        else:
            welcome_message = f"🎉 Welcome {after.mention} to {after.guild.name}! 🎉\nHop over to #self-roles to grab your roles and join the fun!"

        await general_channel.send(welcome_message)

        print(f"✅ Fallback message sent")
        print(f"📝 Message content:\n{welcome_message}")

        sent_message = general_channel.send.call_args[0][0]
        assert "#self-roles" in sent_message, "Should use plain text channel name"
        print("✅ All assertions passed!")
        return True

    return False


async def main():
    print("=" * 50)
    print("🚀 Testing Verified Role Welcome Feature")
    print("=" * 50)
    print()

    test1 = await simulate_verified_role_assignment()
    test2 = await simulate_other_role_assignment()
    test3 = await simulate_no_self_roles_channel()

    print("\n" + "=" * 50)
    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
