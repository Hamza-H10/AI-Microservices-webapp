from transformers import pipeline
import torch


def analyze_sentiment():
    """Interactive sentiment analysis with user input."""

    # 1. Initialize the sentiment analysis pipeline.
    print("Loading sentiment analysis model...")
    classifier = pipeline(
        task="sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1
    )

    device_name = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    print(f"Model loaded successfully on {device_name}!\n")

    print("=== Sentiment Analysis Tool ===")
    print("Enter text to analyze sentiment. Type 'quit' or 'exit' to stop.\n")

    while True:
        # 2. Get user input
        user_input = input("Enter text: ").strip()

        # 3. Check for exit conditions
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thanks for using the sentiment analyzer! Goodbye!")
            break

        # 4. Skip empty inputs
        if not user_input:
            print("Please enter some text to analyze.\n")
            continue

        # 5. Run sentiment analysis
        try:
            # Get first result since we're analyzing one text
            result = classifier(user_input)[0]

            # 6. Display results with color coding
            sentiment = result['label']
            confidence = result['score']

            # Add visual indicators
            emoji = "😊" if sentiment == "POSITIVE" else "😞"
            confidence_bar = "█" * \
                int(confidence * 10) + "░" * (10 - int(confidence * 10))

            print(f"\nResult: {emoji} {sentiment}")
            print(f"Confidence: {confidence:.4f} ({confidence:.1%})")
            print(f"Visual: [{confidence_bar}]")
            print("-" * 40)

        except Exception as e:
            print(f"Error analyzing text: {e}")
            print("Please try again with different text.\n")


if __name__ == "__main__":
    analyze_sentiment()
