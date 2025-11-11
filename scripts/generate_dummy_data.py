"""
Generate dummy transcript data for testing
"""

import json
import random
from pathlib import Path
from datetime import datetime

# Sample dialogue templates
AGENT_GREETINGS = [
    "Hello, thank you for calling. How can I assist you today?",
    "Good morning, this is customer service. How may I help you?",
    "Hi there, thanks for reaching out. What can I do for you?",
    "Hello, welcome to our support line. How can I help?",
]

CUSTOMER_ISSUES = [
    "I'm having trouble with my order",
    "I need to return a product",
    "I haven't received my shipment",
    "There's an issue with my billing",
    "I want to cancel my subscription",
    "The product I received is defective",
    "I was charged incorrectly",
    "I need help with my account",
]

AGENT_RESPONSES = [
    "I understand your concern. Let me help you with that.",
    "I'm sorry to hear about this issue. Let me look into it.",
    "I can definitely help you resolve this. Let me check your account.",
    "Thank you for bringing this to our attention. Let me assist you.",
    "I apologize for the inconvenience. Let me see what I can do.",
]

CUSTOMER_FRUSTRATED = [
    "This is really frustrating. I've been waiting for days.",
    "I'm not satisfied with this service at all.",
    "This is unacceptable. I want to speak to a supervisor.",
    "I've had enough. I want my money back.",
    "This is the worst customer service I've ever experienced.",
]

ESCALATION_TRIGGERS = [
    "I want to speak to a manager",
    "This is ridiculous, I need a supervisor",
    "I'm filing a formal complaint",
    "I want to escalate this issue",
    "Get me your manager right now",
]

REFUND_TRIGGERS = [
    "I want a refund",
    "Give me my money back",
    "I want to return this and get a refund",
    "This doesn't work, I want my money back",
    "Refund my purchase immediately",
]

CHURN_TRIGGERS = [
    "I want to cancel my subscription",
    "I'm switching to a competitor",
    "I'm closing my account",
    "Cancel everything, I'm done",
    "I want to terminate my service",
]


def generate_turn(turn_id, speaker, text, timestamp):
    """Generate a turn dictionary"""
    return {
        "turn_id": turn_id,
        "speaker": speaker,
        "text": text,
        "timestamp": timestamp
    }


def generate_transcript(transcript_id):
    """Generate a single transcript with turns and events"""
    turns = []
    events = []
    timestamp = 0.0
    
    # Start with agent greeting
    agent_greeting = random.choice(AGENT_GREETINGS)
    turns.append(generate_turn(1, "agent", agent_greeting, timestamp))
    timestamp += random.uniform(1.0, 3.0)
    
    # Customer issue
    customer_issue = random.choice(CUSTOMER_ISSUES)
    turns.append(generate_turn(2, "customer", customer_issue, timestamp))
    timestamp += random.uniform(2.0, 5.0)
    
    # Agent response
    agent_response = random.choice(AGENT_RESPONSES)
    turns.append(generate_turn(3, "agent", agent_response, timestamp))
    timestamp += random.uniform(1.5, 4.0)
    
    # Continue conversation
    num_turns = random.randint(5, 15)
    current_turn = 4
    
    # Determine if this will have an event
    has_event = random.random() < 0.3  # 30% of transcripts have events
    event_type = None
    event_turn = None
    
    if has_event:
        event_choice = random.random()
        if event_choice < 0.4:  # 40% escalations
            event_type = "escalation"
        elif event_choice < 0.7:  # 30% refunds
            event_type = "refund"
        else:  # 30% churn
            event_type = "churn"
    
    for i in range(num_turns):
        if current_turn >= num_turns + 3:
            break
            
        # Alternate speakers
        if i % 2 == 0:
            speaker = "customer"
            # Check if we should trigger an event
            if has_event and event_turn is None and current_turn > 5:
                trigger_chance = random.random()
                if trigger_chance < 0.3:  # 30% chance to trigger event at this point
                    if event_type == "escalation":
                        text = random.choice(ESCALATION_TRIGGERS)
                    elif event_type == "refund":
                        text = random.choice(REFUND_TRIGGERS)
                    else:
                        text = random.choice(CHURN_TRIGGERS)
                    event_turn = current_turn
                else:
                    if random.random() < 0.2:  # 20% chance of frustration
                        text = random.choice(CUSTOMER_FRUSTRATED)
                    else:
                        text = f"Customer response {i+1}: {random.choice(['I see', 'Okay', 'That makes sense', 'I understand', 'Can you explain more?'])}"
            else:
                text = f"Customer response {i+1}: {random.choice(['I see', 'Okay', 'That makes sense', 'I understand', 'Can you explain more?', 'What about...'])}"
        else:
            speaker = "agent"
            text = f"Agent response {i+1}: {random.choice(['Let me check that for you', 'I understand', 'I can help with that', 'Let me verify', 'One moment please'])}"
        
        turns.append(generate_turn(current_turn, speaker, text, timestamp))
        timestamp += random.uniform(1.0, 4.0)
        current_turn += 1
    
    # Add event if triggered
    if event_turn is not None:
        events.append({
            "event_type": event_type,
            "event_label": f"{event_type}_request",
            "turn_id": event_turn,
            "timestamp": turns[event_turn - 1]["timestamp"]
        })
    
    # Closing
    if random.random() < 0.7:  # 70% have closing
        if speaker == "customer":
            turns.append(generate_turn(current_turn, "agent", "Thank you for calling. Have a great day!", timestamp))
        else:
            turns.append(generate_turn(current_turn, "customer", "Thank you for your help. Goodbye.", timestamp))
    
    return {
        "transcript_id": f"call_{transcript_id:05d}",
        "turns": turns,
        "events": events,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "num_turns": len(turns),
            "duration": timestamp,
            "has_event": len(events) > 0
        }
    }


def main():
    """Generate dummy transcript data"""
    print("Generating dummy transcript data...")
    print("This may take a few moments...")
    
    # Create output directory
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate transcripts
    transcripts = []
    num_transcripts = 100  # Reduced to 100 to reduce server load
    
    print(f"Generating {num_transcripts} transcripts...")
    for i in range(1, num_transcripts + 1):
        if i % 10 == 0 or i == num_transcripts:
            print(f"  Generated {i}/{num_transcripts} transcripts...")
        transcript = generate_transcript(i)
        transcripts.append(transcript)
    
    # Save to JSON file
    output_file = output_dir / "dummy_transcripts.json"
    print(f"\nSaving to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transcripts, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_turns = sum(len(t['turns']) for t in transcripts)
    total_events = sum(len(t['events']) for t in transcripts)
    escalations = sum(1 for t in transcripts for e in t['events'] if e.get('event_type') == 'escalation')
    refunds = sum(1 for t in transcripts for e in t['events'] if e.get('event_type') == 'refund')
    churn = sum(1 for t in transcripts for e in t['events'] if e.get('event_type') == 'churn')
    
    print(f"\n✓ Generation complete!")
    print(f"\nStatistics:")
    print(f"  Total transcripts: {num_transcripts}")
    print(f"  Total turns: {total_turns}")
    print(f"  Total events: {total_events}")
    print(f"  Escalations: {escalations}")
    print(f"  Refunds: {refunds}")
    print(f"  Churn: {churn}")
    print(f"\nFile saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
    
    print(f"\nNext steps:")
    print(f"1. Process the data:")
    print(f"   python scripts/process_data.py --input data/raw --pattern 'dummy_transcripts.json' --index")
    print(f"\n2. Or process all JSON files:")
    print(f"   python scripts/process_data.py --input data/raw --pattern '*.json' --index")


if __name__ == "__main__":
    main()

