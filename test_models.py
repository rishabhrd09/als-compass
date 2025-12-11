"""
Quick test script to verify API keys and test all models
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_api_keys():
    """Check which API keys are configured"""
    print("=" * 50)
    print("  API Key Configuration Check")
    print("=" * 50)
    
    keys = {
        'Claude (Anthropic)': 'ANTHROPIC_API_KEY',
        'OpenAI': 'OPENAI_API_KEY',
        'Gemini (Google)': 'GEMINI_API_KEY',
        'Grok (xAI)': 'XAI_API_KEY'
    }
    
    configured = []
    
    for name, env_var in keys.items():
        key = os.getenv(env_var)
        if key:
            print(f"✅ {name}: {key[:15]}...")
            configured.append(name.split('(')[0].strip())
        else:
            print(f"❌ {name}: Not configured")
    
    print(f"\n📊 {len(configured)}/4 providers configured")
    return [p.lower() for p in configured]

def test_model(provider: str):
    """Test a specific AI model"""
    try:
        print(f"\n🧪 Testing {provider.upper()}...")
        
        from ai_system_unified import UnifiedAISystem
        system = UnifiedAISystem(model_provider=provider)
        
        # Simple test query
        response = system.process_query("What is ALS?")
        
        print(f"✅ {provider.upper()} working!")
        print(f"   Model: {response.get('model_used', 'unknown')}")
        print(f"   Response preview: {response['response'][:80]}...")
        
        return True
    except Exception as e:
        print(f"❌ {provider.upper()} failed: {e}")
        return False

def main():
    # Check keys
    configured_providers = test_api_keys()
    
    if not configured_providers:
        print("\n❌ No API keys configured!")
        print("   Please add at least one API key to your .env file")
        return
    
    # Test each configured provider
    print("\n" + "=" * 50)
    print("  Testing Configured Models")
    print("=" * 50)
    
    results = {}
    for provider in configured_providers:
        results[provider] = test_model(provider)
    
    # Summary
    print("\n" + "=" * 50)
    print("  Test Summary")
    print("=" * 50)
    
    working = [p for p, success in results.items() if success]
    failed = [p for p, success in results.items() if not success]
    
    if working:
        print(f"✅ Working: {', '.join(working)}")
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
    
    print(f"\n📊 {len(working)}/{len(configured_providers)} providers working")
    
    if working:
        print(f"\n🎯 Recommended: {working[0]}")

if __name__ == "__main__":
    main()
