#!/usr/bin/env python3
"""
Test script to verify thread safety of the EnhancedUITheme singleton.
"""

import sys
import os
import threading
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_theme import EnhancedUITheme

def test_singleton_thread_safety():
    """Test that the singleton pattern is thread-safe."""
    
    print("=== Thread Safety Test ===")
    
    instances = []
    exceptions = []
    
    def create_instance(thread_id):
        """Create an instance in a separate thread."""
        try:
            print(f"Thread {thread_id}: Starting...")
            time.sleep(0.001)  # Small delay to increase chance of race condition
            instance = EnhancedUITheme()
            instances.append((thread_id, instance, id(instance)))
            print(f"Thread {thread_id}: Created instance {id(instance)}")
            
            # Test some operations
            color = instance.get_color("primary")
            workflow_colors = instance.get_workflow_colors("angebots_workflow")
            print(f"Thread {thread_id}: Operations successful")
        except Exception as e:
            exceptions.append((thread_id, e))
            print(f"Thread {thread_id}: Exception - {e}")
    
    # Create multiple threads to test race conditions
    threads = []
    num_threads = 10
    
    print(f"Creating {num_threads} threads...")
    for i in range(num_threads):
        thread = threading.Thread(target=create_instance, args=(i,))
        threads.append(thread)
    
    # Start all threads simultaneously
    print("Starting all threads...")
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    print("Waiting for threads to complete...")
    for thread in threads:
        thread.join()
    
    # Analyze results
    print(f"\n=== Results ===")
    print(f"Number of instances created: {len(instances)}")
    print(f"Number of exceptions: {len(exceptions)}")
    
    if exceptions:
        print("\nExceptions encountered:")
        for thread_id, exception in exceptions:
            print(f"  Thread {thread_id}: {exception}")
    
    # Check if all instances are actually the same object
    unique_ids = set()
    for thread_id, instance, instance_id in instances:
        unique_ids.add(instance_id)
        print(f"Thread {thread_id}: Instance ID {instance_id}")
    
    print(f"\nUnique instance IDs: {len(unique_ids)}")
    
    if len(unique_ids) == 1:
        print("✅ Thread safety test PASSED - All threads got the same singleton instance")
        return True
    else:
        print("❌ Thread safety test FAILED - Multiple instances created")
        return False

def test_concurrent_theme_switching():
    """Test concurrent theme switching operations."""
    
    print("\n=== Concurrent Theme Switching Test ===")
    
    theme = EnhancedUITheme()
    results = []
    exceptions = []
    
    def switch_themes(thread_id):
        """Switch themes in a separate thread."""
        try:
            for i in range(5):
                theme_name = "light" if i % 2 == 0 else "dark"
                theme.switch_theme(theme_name)
                color = theme.get_color("primary")
                results.append((thread_id, i, theme_name, color))
                time.sleep(0.001)  # Small delay
        except Exception as e:
            exceptions.append((thread_id, e))
    
    # Create multiple threads that switch themes concurrently
    threads = []
    num_threads = 5
    
    for i in range(num_threads):
        thread = threading.Thread(target=switch_themes, args=(i,))
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    print(f"Theme switching operations completed: {len(results)}")
    print(f"Exceptions during theme switching: {len(exceptions)}")
    
    if exceptions:
        print("Exceptions:")
        for thread_id, exception in exceptions:
            print(f"  Thread {thread_id}: {exception}")
    
    # Check final state
    final_color = theme.get_color("primary")
    final_theme = theme._current_theme
    print(f"Final theme: {final_theme}")
    print(f"Final primary color: {final_color}")
    
    if len(exceptions) == 0:
        print("✅ Concurrent theme switching test PASSED")
        return True
    else:
        print("❌ Concurrent theme switching test FAILED")
        return False

if __name__ == "__main__":
    try:
        singleton_test = test_singleton_thread_safety()
        switching_test = test_concurrent_theme_switching()
        
        if singleton_test and switching_test:
            print("\n✅ All thread safety tests PASSED!")
        else:
            print("\n❌ Some thread safety tests FAILED!")
    except Exception as e:
        print(f"\n❌ Critical error during thread safety tests: {e}")
        import traceback
        traceback.print_exc()
