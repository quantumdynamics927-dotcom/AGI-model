"""
QAGI Research Assistant
=======================

Interactive tool for complex scientific inquiry using QAGI with governance framework.

Usage:
    python qagi_research_assistant.py --question "Why does benzene have lower entanglement entropy?"
"""

import argparse
import json
from typing import Dict, Any
from pathlib import Path


class QAGIResearchAssistant:
    """Structured research assistant using QAGI with governance framework."""
    
    def __init__(self, template_path: str = "qagi_complex_research_template.md"):
        self.template_path = template_path
        self.load_template()
    
    def load_template(self):
        """Load the QAGI complex research template."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.template = f.read()
            print("✅ Loaded QAGI complex research template")
        except FileNotFoundError:
            print(f"❌ Template not found: {self.template_path}")
            self.template = None
    
    def generate_prompt(self, domain: str, current_hypothesis: str, 
                       question: str) -> str:
        """Generate a structured prompt for QAGI."""
        if not self.template:
            raise ValueError("Template not loaded")
        
        # Replace placeholders in template
        prompt = self.template.replace("{domain}", domain)
        prompt = prompt.replace("{current_hypothesis}", current_hypothesis)
        prompt = prompt.replace("{question}", question)
        
        return prompt
    
    def validate_response_structure(self, response: str) -> Dict[str, Any]:
        """Validate that QAGI response follows required structure."""
        required_sections = [
            "THEORY HYPOTHESIS",
            "MECHANISM PROPOSAL", 
            "COMPETING HYPOTHESES",
            "NULL MODELS",
            "METRICS FRAMEWORK",
            "EXPERIMENT DESIGN",
            "FALSIFICATION CONDITIONS",
            "LIMITATIONS AND ASSUMPTIONS"
        ]
        
        results = {
            'valid_structure': True,
            'missing_sections': [],
            'forbidden_outputs': [],
            'governance_compliance': True
        }
        
        # Check for required sections
        for section in required_sections:
            if f"### {section}" not in response:
                results['missing_sections'].append(section)
                results['valid_structure'] = False
        
        # Check for forbidden outputs
        forbidden_phrases = [
            "proof of consciousness",
            "universal truth",
            "fundamental law",
            "deeper order in the universe"
        ]
        
        for phrase in forbidden_phrases:
            if phrase.lower() in response.lower():
                results['forbidden_outputs'].append(phrase)
                results['governance_compliance'] = False
        
        return results
    
    def save_research_note(self, question: str, response: str, 
                          validation_results: Dict[str, Any]):
        """Save research note with governance metadata."""
        # Create filename from question
        safe_filename = "".join(c for c in question if c.isalnum() or c in (' ','-','_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')[:50]
        
        note_data = {
            'question': question,
            'response': response,
            'validation': validation_results,
            'governance_status': 'APPROVED' if validation_results['governance_compliance'] else 'REQUIRES_REVIEW'
        }
        
        filename = f"qagi_research_notes/{safe_filename}.json"
        Path("qagi_research_notes").mkdir(exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(note_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Research note saved: {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(description='QAGI Research Assistant')
    parser.add_argument('--question', required=True, 
                       help='Research question for QAGI')
    parser.add_argument('--domain', default='General Scientific Inquiry',
                       help='Research domain')
    parser.add_argument('--hypothesis', default='None specified',
                       help='Current working hypothesis')
    
    args = parser.parse_args()
    
    # Initialize assistant
    assistant = QAGIResearchAssistant()
    
    # Generate prompt
    prompt = assistant.generate_prompt(
        domain=args.domain,
        current_hypothesis=args.hypothesis,
        question=args.question
    )
    
    print("🤖 QAGI PROMPT GENERATED")
    print("=" * 50)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("=" * 50)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Copy the prompt above")
    print("2. Paste it into your QAGI interface")
    print("3. Obtain QAGI's response")
    print("4. Run: python qagi_research_assistant.py --validate-response <response_file>")
    
    # Save prompt for reference
    prompt_file = f"qagi_prompts/{args.question.replace(' ', '_')[:30]}.md"
    Path("qagi_prompts").mkdir(exist_ok=True)
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"\n💾 Prompt saved to: {prompt_file}")


def validate_response(response_file: str):
    """Validate a QAGI response file."""
    try:
        with open(response_file, 'r', encoding='utf-8') as f:
            response = f.read()
    except FileNotFoundError:
        print(f"❌ Response file not found: {response_file}")
        return
    
    assistant = QAGIResearchAssistant()
    validation = assistant.validate_response_structure(response)
    
    print("🔍 QAGI RESPONSE VALIDATION")
    print("=" * 50)
    
    if validation['valid_structure']:
        print("✅ Response follows required structure")
    else:
        print("❌ Response missing sections:")
        for section in validation['missing_sections']:
            print(f"   - {section}")
    
    if validation['forbidden_outputs']:
        print("❌ Forbidden outputs detected:")
        for output in validation['forbidden_outputs']:
            print(f"   - {output}")
    
    if validation['governance_compliance']:
        print("✅ Governance compliance: APPROVED")
    else:
        print("❌ Governance compliance: REQUIRES_REVIEW")
    
    # Extract question from response for filename
    question = response.split('\n')[0][:50] if response else "unknown_question"
    assistant.save_research_note(question, response, validation)


if __name__ == "__main__":
    import sys
    
    if "--validate-response" in sys.argv:
        # Validate mode
        response_file = sys.argv[sys.argv.index("--validate-response") + 1]
        validate_response(response_file)
    else:
        # Generate prompt mode
        main()