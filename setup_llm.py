#!/usr/bin/env python3
"""
Setup script for LLM configuration
"""

import os
import sys

def setup_groq():
    """Setup Groq API key"""
    print("=== Groq LLM Setup ===")
    print("\n1. Get your free Groq API key:")
    print("   - Go to https://console.groq.com/")
    print("   - Sign up for a free account")
    print("   - Go to 'API Keys' and create a new key")
    print("\n2. Set the API key in PowerShell:")
    print("   $env:GROQ_API_KEY = 'your-groq-api-key-here'")
    print("\n3. Or set it permanently:")
    print("   [System.Environment]::SetEnvironmentVariable('GROQ_API_KEY', 'your-groq-api-key-here', 'User')")
    print("\n4. Restart your terminal and the application")
    
    # Check if key is already set
    if os.getenv("GROQ_API_KEY"):
        print("\n✅ GROQ_API_KEY is already set!")
    else:
        print("\n⚠️  GROQ_API_KEY is not set yet")

def setup_openai():
    """Setup OpenAI API key"""
    print("=== OpenAI LLM Setup ===")
    print("\n1. Get your OpenAI API key:")
    print("   - Go to https://platform.openai.com/")
    print("   - Sign up and add a payment method")
    print("   - Go to 'API Keys' and create a new key")
    print("\n2. Set the API key in PowerShell:")
    print("   $env:OPENAI_API_KEY = 'your-openai-api-key-here'")
    print("\n3. Or set it permanently:")
    print("   [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-openai-api-key-here', 'User')")
    
    # Check if key is already set
    if os.getenv("OPENAI_API_KEY"):
        print("\n✅ OPENAI_API_KEY is already set!")
    else:
        print("\n⚠️  OPENAI_API_KEY is not set yet")

def main():
    print("LLM Configuration Setup")
    print("======================")
    print("\nChoose an LLM provider:")
    print("1. Groq (Recommended - Free & Fast)")
    print("2. OpenAI (Paid - High Quality)")
    print("3. Check current configuration")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        setup_groq()
    elif choice == "2":
        setup_openai()
    elif choice == "3":
        from config.config import LLM_PROVIDER, LLM_MODEL
        print(f"\nCurrent configuration:")
        print(f"  Provider: {LLM_PROVIDER}")
        print(f"  Model: {LLM_MODEL}")
        print(f"  GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set'}")
        print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
