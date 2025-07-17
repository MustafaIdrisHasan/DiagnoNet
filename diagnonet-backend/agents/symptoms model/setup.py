#!/usr/bin/env python3
"""
Medical AI Diagnosis System Setup Script
Handles environment setup, dependency installation, and model preparation
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🏥 {title}")
    print("=" * 60)

def run_command(command, description):
    """Run a command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print_header("PYTHON VERSION CHECK")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 10:
        print("❌ Python 3.10+ required for optimal compatibility")
        print("⚠️ Some features may not work with older Python versions")
        return False
    else:
        print("✅ Python version compatible")
        return True

def install_core_dependencies():
    """Install core Python dependencies"""
    print_header("CORE DEPENDENCIES INSTALLATION")
    
    # Install core requirements
    success = run_command(
        "pip install -r requirements.txt",
        "Installing core dependencies"
    )
    
    return success

def install_scispacy_models():
    """Install ScispaCy models for medical NLP"""
    print_header("SCISPACY MODELS INSTALLATION")
    
    models = [
        {
            "name": "en_core_sci_md",
            "url": "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz",
            "description": "Core scientific model"
        },
        {
            "name": "en_ner_bc5cdr_md", 
            "url": "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bc5cdr_md-0.5.3.tar.gz",
            "description": "Biomedical NER model"
        }
    ]
    
    all_success = True
    
    for model in models:
        print(f"\n📥 Installing {model['name']} ({model['description']})...")
        success = run_command(
            f"pip install {model['url']}",
            f"Installing {model['name']}"
        )
        
        if not success:
            print(f"⚠️ Failed to install {model['name']}")
            print("   System will fall back to simplified NLP processor")
            all_success = False
    
    return all_success

def verify_installation():
    """Verify that all components are working"""
    print_header("INSTALLATION VERIFICATION")
    
    try:
        # Test core imports
        print("🔍 Testing core imports...")
        from medical_ai_api import MedicalAIAPI
        print("✅ Core API import successful")
        
        # Test system initialization
        print("🔍 Testing system initialization...")
        api = MedicalAIAPI()
        
        if api.ready:
            print("✅ Medical AI system initialized successfully")
            
            # Test basic functionality
            print("🔍 Testing basic functionality...")
            result = api.analyze("test fever and cough")
            
            if 'symptoms' in result and 'predictions' in result:
                print("✅ Basic analysis functionality working")
                return True
            else:
                print("❌ Basic analysis failed")
                return False
        else:
            print("❌ Medical AI system failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def create_example_script():
    """Create an example usage script"""
    print_header("CREATING EXAMPLE SCRIPT")
    
    example_code = '''#!/usr/bin/env python3
"""
Example usage of Medical AI Diagnosis System
"""

from medical_ai_api import MedicalAIAPI

def main():
    """Example usage demonstration"""
    print("🏥 Medical AI Example Usage")
    print("=" * 40)
    
    # Initialize the system
    api = MedicalAIAPI()
    
    if not api.ready:
        print("❌ System not ready")
        return
    
    # Example analyses
    examples = [
        "I have severe chest pain and shortness of breath",
        "Patient presents with fever, cough, and fatigue",
        "Experiencing headache and nausea for 2 days"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\\nExample {i}: {example}")
        print("-" * 40)
        
        result = api.analyze(example)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
        
        # Display results
        symptoms = result['symptoms']['detected']
        primary = result['predictions']['primary']
        urgency = result['assessment']['urgency_level']
        confidence = result['assessment']['overall_confidence']
        
        print(f"Symptoms: {', '.join(symptoms)}")
        if primary:
            print(f"Primary Diagnosis: {primary['disease']}")
            print(f"Confidence: {primary['confidence_percentage']:.1f}%")
        print(f"Urgency: {urgency}")
        print(f"Overall Confidence: {confidence:.1%}")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open("example_usage.py", "w") as f:
            f.write(example_code)
        print("✅ Created example_usage.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create example script: {e}")
        return False

def setup_environment():
    """Complete environment setup"""
    print_header("MEDICAL AI DIAGNOSIS SYSTEM SETUP")
    print("Setting up production-ready medical AI environment...")
    
    success_steps = 0
    total_steps = 5
    
    # Step 1: Check Python version
    if check_python_version():
        success_steps += 1
    
    # Step 2: Install core dependencies
    if install_core_dependencies():
        success_steps += 1
    
    # Step 3: Install ScispaCy models
    if install_scispacy_models():
        success_steps += 1
    else:
        print("⚠️ ScispaCy installation had issues, but system will work with fallback NLP")
        success_steps += 0.5  # Partial success
    
    # Step 4: Verify installation
    if verify_installation():
        success_steps += 1
    
    # Step 5: Create example script
    if create_example_script():
        success_steps += 1
    
    # Final report
    print_header("SETUP COMPLETE")
    print(f"Setup progress: {success_steps}/{total_steps} steps completed")
    
    if success_steps >= 4:
        print("🎉 SETUP SUCCESSFUL!")
        print("\n📋 Next steps:")
        print("1. Run tests: python test_medical_ai.py")
        print("2. Try example: python example_usage.py")
        print("3. Check API documentation in README.md")
        print("4. Start integration with your diagnosis models")
        
        print("\n🔧 Quick test:")
        print("python -c \"from medical_ai_api import analyze_symptoms; print(analyze_symptoms('fever and cough'))\"")
        
    else:
        print("⚠️ SETUP INCOMPLETE")
        print("Some components may not work correctly.")
        print("Check error messages above and resolve issues.")
        print("\n💡 Common solutions:")
        print("- Ensure Python 3.10+ is installed")
        print("- Check internet connection for model downloads")
        print("- Try running with administrator/sudo privileges")
    
    return success_steps >= 4

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Medical AI Setup Script")
    parser.add_argument("--skip-models", action="store_true",
                       help="Skip ScispaCy model installation")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing installation")
    
    args = parser.parse_args()
    
    if args.verify_only:
        success = verify_installation()
    else:
        success = setup_environment()
    
    sys.exit(0 if success else 1)
