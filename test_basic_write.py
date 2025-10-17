#!/usr/bin/env python3
"""
Test script to debug basic PBus write commands.

This tests if we can successfully write to the amplifier at all.
"""
import asyncio
import sys
sys.path.insert(0, 'custom_components/powersoft_mezzo')

from mezzo_client import MezzoClient

async def main():
    # Replace with your amplifier's IP
    HOST = input("Enter amplifier IP address: ")

    async with MezzoClient(HOST, port=8002, timeout=5.0) as client:
        print(f"Connected to {HOST}:8002")

        # Test 1: Read standby state (should work)
        print("\nTest 1: Reading standby state...")
        try:
            standby = await client.get_standby_state()
            print(f"✅ Standby state: {standby}")
        except Exception as e:
            print(f"❌ Failed to read standby: {e}")
            return

        # Test 2: Read volume (should work)
        print("\nTest 2: Reading volume channel 1...")
        try:
            volume = await client.get_volume(1)
            print(f"✅ Volume CH1: {volume:.2f} ({volume*100:.0f}%)")
        except Exception as e:
            print(f"❌ Failed to read volume: {e}")
            return

        # Test 3: Write volume (THIS is where we might fail)
        print("\nTest 3: Writing volume to 0.5 (50%)...")
        try:
            await client.set_volume(1, 0.5)
            print(f"✅ Volume write succeeded")

            # Verify
            new_volume = await client.get_volume(1)
            print(f"✅ Verified: Volume is now {new_volume:.2f}")
        except Exception as e:
            print(f"❌ Failed to write volume: {e}")
            import traceback
            traceback.print_exc()

        # Test 4: Write mute
        print("\nTest 4: Writing mute to channel 1...")
        try:
            await client.set_mute(1, True)
            print(f"✅ Mute write succeeded")

            # Verify
            is_muted = await client.get_mute(1)
            print(f"✅ Verified: Mute is {is_muted}")

            # Unmute
            await client.set_mute(1, False)
            print(f"✅ Unmute succeeded")
        except Exception as e:
            print(f"❌ Failed to write mute: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
