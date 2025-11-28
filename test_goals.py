#!/usr/bin/env python3
"""Test script to verify goal creation and retrieval."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db_context
from app.agents.mcp import MCPAgent
from app.db.models import User, Goal

def test_goal_creation():
    """Test creating and retrieving goals."""
    
    # Test with a WhatsApp user ID
    test_user_id = "wa_test_1234567890"
    
    print("=" * 60)
    print("Testing Goal Creation and Retrieval")
    print("=" * 60)
    
    with get_db_context() as db:
        # Clean up any existing test user
        existing_user = db.query(User).filter(User.telegram_id == test_user_id).first()
        if existing_user:
            print(f"\n🧹 Cleaning up existing test user: {existing_user.id}")
            db.delete(existing_user)
            db.commit()
        
        # Create agent
        print(f"\n📱 Creating agent for user: {test_user_id}")
        agent = MCPAgent(db, test_user_id)
        
        # Test 1: Check goals before creation
        print("\n📊 Test 1: Checking goals before creation...")
        goals_before = agent.tools.get_active_goals()
        print(f"   Active goals: {len(goals_before)}")
        assert len(goals_before) == 0, "Should have no goals initially"
        print("   ✅ PASSED")
        
        # Test 2: Process a message to create a goal
        print("\n💬 Test 2: Processing message to create goal...")
        test_message = "I want to save ₹50000 for a laptop in 3 months"
        print(f"   Message: '{test_message}'")
        response = agent.process_message(test_message)
        print(f"   Response: {response[:100]}...")
        
        # Test 3: Check if goal was created
        print("\n📊 Test 3: Checking if goal was created...")
        goals_after = agent.tools.get_active_goals()
        print(f"   Active goals: {len(goals_after)}")
        
        if len(goals_after) > 0:
            print("   ✅ PASSED - Goal created!")
            goal = goals_after[0]
            print(f"\n   Goal Details:")
            print(f"   - Title: {goal['title']}")
            print(f"   - Target: ₹{goal['target_amount']:,.0f}")
            print(f"   - Current: ₹{goal['current_amount']:,.0f}")
            print(f"   - Progress: {goal['progress_percentage']:.0f}%")
            if goal['deadline']:
                print(f"   - Deadline: {goal['deadline'][:10]}")
        else:
            print("   ❌ FAILED - No goal created")
            print("\n   Debugging info:")
            # Check if user was created
            user = db.query(User).filter(User.telegram_id == test_user_id).first()
            print(f"   - User exists: {user is not None}")
            if user:
                print(f"   - User ID: {user.id}")
                # Check goals directly
                all_goals = db.query(Goal).filter(Goal.user_id == user.id).all()
                print(f"   - Total goals in DB: {len(all_goals)}")
        
        # Test 4: Test /goals command
        print("\n📊 Test 4: Testing /goals command simulation...")
        goals_list = agent.tools.get_active_goals()
        if goals_list:
            print(f"   ✅ Can retrieve {len(goals_list)} goal(s)")
            for i, g in enumerate(goals_list, 1):
                print(f"   {i}. {g['title']} - ₹{g['current_amount']:,.0f}/₹{g['target_amount']:,.0f}")
        else:
            print("   ⚠️  No goals to display")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_goal_creation()
