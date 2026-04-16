"""
Simple validation of final phi research note
"""

# Read the file
with open('d:/AGI-GH-REPO-11326/AGI-model/final_phi_research_note.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("Checking content...")
print(f"'hypothesis' found: {'hypothesis' in content.lower()}")
print(f"'null model' found: {'null model' in content.lower()}")
print(f"'validation' found: {'validation' in content.lower()}")
print(f"'FORMAL HYPOTHESIS' found: {'FORMAL HYPOTHESIS' in content}")
print(f"'NULL MODELS' found: {'NULL MODELS' in content}")

# Check for overclaiming words
overclaim_words = ["prove", "demonstrate", "confirm", "verify", "achieved"]
found_overclaims = []
for word in overclaim_words:
    if word in content.lower():
        found_overclaims.append(word)

if found_overclaims:
    print(f"Overclaiming words found: {found_overclaims}")
else:
    print("No overclaiming words found")

print("\nFirst 300 characters:")
print(repr(content[:300]))