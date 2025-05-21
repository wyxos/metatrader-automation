# Improved Asyncio Handling in Telegram Client

## Issue Description

The script was experiencing "RuntimeError: Event loop is closed" errors when being stopped. This occurred because Telethon was still doing background work when the asyncio event loop was forcefully closed.

## Solution Implemented

The solution involved two main changes:

1. **Combined client startup and message listening into a single async main() function**
   - This provides a cleaner structure with proper async/await flow
   - All client operations are now contained within a single async context

2. **Replaced manual event loop setup with asyncio.run(main())**
   - The `asyncio.run()` function handles event loop creation and cleanup automatically
   - It ensures proper shutdown of the event loop, even when exceptions occur

## Code Changes

### Before:

```python
# Main function
if __name__ == "__main__":
    # Clear terminal on Windows
    os.system('cls')

    # Set up and run the asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Initialize and run the Telegram client
        loop.run_until_complete(initialize_telegram_client())
        loop.run_until_complete(start_telegram_client())
    except KeyboardInterrupt:
        # Handle graceful shutdown on user interrupt (CTRL+C)
        logging.info("Interrupted by user. Disconnecting client...")
        if client and client.is_connected():
            loop.run_until_complete(client.disconnect())  # Explicitly disconnect
    finally:
        # Always close the loop to clean up resources
        logging.info("Closing event loop...")
        loop.close()
```

### After:

```python
# Main async function that combines client startup and message listening
async def main():
    await initialize_telegram_client()
    try:
        await start_telegram_client()
    except asyncio.CancelledError:
        pass
    finally:
        if client and client.is_connected():
            await client.disconnect()

# Main function
if __name__ == "__main__":
    # Clear terminal on Windows
    os.system('cls')
    
    try:
        # Use asyncio.run for clean startup and shutdown
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown on user interrupt (CTRL+C)
        logging.info("Interrupted by user. Shutting down...")
```

## Benefits

1. **Cleaner Code Structure**
   - The async flow is more logical and easier to follow
   - All client operations are properly contained within the main async function

2. **Proper Exception Handling**
   - Added specific handling for `asyncio.CancelledError` which occurs during shutdown
   - The `finally` block ensures the client is always disconnected properly

3. **Automatic Event Loop Management**
   - `asyncio.run()` handles event loop creation and cleanup automatically
   - Prevents "RuntimeError: Event loop is closed" errors by ensuring proper shutdown sequence

4. **Graceful Shutdown**
   - The client is properly disconnected before the event loop is closed
   - Resources are cleaned up properly, preventing memory leaks

## Conclusion

These changes follow the recommended best practices for asyncio applications and should prevent the "RuntimeError: Event loop is closed" errors that were occurring when the script was stopped. The code is now more robust and handles shutdown scenarios more gracefully.
